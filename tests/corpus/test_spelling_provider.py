"""sk.LanguageTool against a fake LanguageTool server in the test: batches, offsets, retries and errors."""

from __future__ import annotations

import dataclasses
import json
import threading
import time
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core import datastore
from rb_semkit.core.errors import ProviderError

Answer = Callable[[int, str], tuple[int, dict, float]]  # the request number and its text → status, body, delay


class FakeServer:
    """A LanguageTool /v2/check that answers by `answer` and records each request."""

    def __init__(self, answer: Answer) -> None:
        self.answer = answer
        self.forms: list[dict[str, list[str]]] = []
        self.texts: list[str] = []
        self.started: list[float] = []
        self.busy = 0
        self.most_busy = 0
        self.lock = threading.Lock()

    def handle(self, request: BaseHTTPRequestHandler) -> None:
        form = parse_qs(request.rfile.read(int(request.headers["Content-Length"])).decode())
        with self.lock:
            number = len(self.texts)
            self.forms.append(form)
            self.texts.append(form["text"][0])
            self.started.append(time.monotonic())
            self.busy += 1
            self.most_busy = max(self.most_busy, self.busy)
        status, body, delay = self.answer(number, form["text"][0])
        time.sleep(delay)
        with self.lock:
            self.busy -= 1
        payload = json.dumps(body).encode()
        try:
            request.send_response(status)
            request.send_header("Content-Length", str(len(payload)))
            request.end_headers()
            request.wfile.write(payload)
        except OSError:
            pass  # the client gave up waiting


@pytest.fixture
def serve() -> Iterator[Callable[[Answer], tuple[FakeServer, sk.LanguageTool]]]:
    servers: list[ThreadingHTTPServer] = []

    def start(answer: Answer) -> tuple[FakeServer, sk.LanguageTool]:
        fake = FakeServer(answer)

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                fake.handle(self)

            def log_message(self, format: str, *args: object) -> None:
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        servers.append(server)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        settings = dataclasses.replace(
            sk.LanguageToolSettings.bundled(),
            url=f"http://127.0.0.1:{server.server_address[1]}/v2/check",
            timeout=0.5,
            batch_lines=2,
            retries=2,
            backoff=0.05,
        )
        return fake, sk.LanguageTool(settings)

    yield start
    for server in servers:
        server.shutdown()
        server.server_close()


def misspelt(text: str, word: str, replacement: str) -> dict:
    """A LanguageTool match of each `word` in `text`, offsets over the whole text."""
    start, matches = text.find(word), []
    while start >= 0:
        matches.append({"offset": start, "length": len(word), "replacements": [{"value": replacement}]})
        start = text.find(word, start + 1)
    return {"matches": matches}


def answer_ok(number: int, text: str) -> tuple[int, dict, float]:
    return 200, misspelt(text, "дивн", "диван"), 0.1


def test_lines_go_in_batches_at_most_two_at_a_time_and_offsets_map_back_to_each_phrase(serve) -> None:
    fake, provider = serve(answer_ok)
    phrases = pd.Series(["стол", "купить дивн", "дивн угловой", "стул", "дивн", "кресло"])

    result = sk.typo_correction(phrases, provider=provider)

    assert result.tolist() == ["стол", "купить диван", "диван угловой", "стул", "диван", "кресло"]
    assert sorted(fake.texts) == sorted(["стол\nкупить дивн", "дивн угловой\nстул", "дивн\nкресло"])
    assert fake.most_busy == 2


def test_the_request_asks_for_the_spelling_rule_of_the_language_only(serve) -> None:
    fake, provider = serve(lambda number, text: (200, {"matches": []}, 0.0))

    assert provider.check(["стол"]) == [[]]
    assert fake.forms == [
        {"language": ["ru-RU"], "text": ["стол"], "enabledRules": ["MORFOLOGIK_RULE_RU_RU"], "enabledOnly": ["true"]}
    ]


def test_a_5xx_answer_is_retried_with_a_growing_pause(serve) -> None:
    fake, provider = serve(lambda number, text: (503, {}, 0.0) if number < 2 else answer_ok(number, text))

    assert provider.check(["купить дивн"]) == [[sk.Misspelling(7, 4, ("диван",))]]
    first_pause, second_pause = fake.started[1] - fake.started[0], fake.started[2] - fake.started[1]
    assert first_pause >= 0.05
    assert second_pause >= 0.1


def test_a_server_that_keeps_failing_raises_a_provider_error_naming_the_provider(serve) -> None:
    fake, provider = serve(lambda number, text: (500, {}, 0.0))

    with pytest.raises(ProviderError, match="languagetool") as raised:
        provider.check(["стол"])

    assert raised.value.status == 500
    assert len(fake.texts) == 3


def test_a_timeout_is_retried_then_raises_and_no_partial_result_is_returned(serve) -> None:
    fake, provider = serve(lambda number, text: (200, {"matches": []}, 2.0 if "стул" in text else 0.0))

    with pytest.raises(ProviderError, match="languagetool"):
        sk.is_typo(pd.Series(["стол", "кресло", "стул"]), provider=provider)

    assert sum("стул" in text for text in fake.texts) == 3


def test_a_4xx_answer_is_not_retried(serve) -> None:
    fake, provider = serve(lambda number, text: (400, {}, 0.0))

    with pytest.raises(ProviderError, match="languagetool") as raised:
        provider.check(["стол"])

    assert raised.value.status == 400
    assert len(fake.texts) == 1


def test_the_bundled_settings_wait_a_minute_for_a_cold_server_and_send_1000_lines_two_at_a_time() -> None:
    settings = sk.LanguageToolSettings.bundled()

    assert settings.timeout >= 60
    assert (settings.batch_lines, settings.parallel) == (1000, 2)
    assert settings.url.startswith("https://")


def test_an_answer_that_is_no_check_result_raises_a_provider_error(serve) -> None:
    _, provider = serve(lambda number, text: (200, {"error": "busy"}, 0.0))

    with pytest.raises(ProviderError, match="no LanguageTool check result"):
        provider.check(["стол"])


def test_a_url_that_is_not_http_is_refused() -> None:
    settings = dataclasses.replace(sk.LanguageToolSettings.bundled(), url="file:///etc/passwd")

    with pytest.raises(sk.InvalidArguments, match="url"):
        sk.LanguageTool(settings)


def test_a_settings_file_without_a_setting_is_refused_naming_it(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "corpus").mkdir()
    (tmp_path / "corpus" / "languagetool.toml").write_text('url = "https://example.org/v2/check"\n', encoding="utf-8")
    monkeypatch.setattr(datastore, "DATA_DIR", tmp_path)

    with pytest.raises(sk.InvalidArguments, match="timeout"):
        sk.LanguageToolSettings.bundled()
