# AGENTS.md

Указатели для агентов. Только навигация: статус, ветки и задачи сюда не пишутся.

- Словарь домена: `CONTEXT.md`. Термины — только оттуда.
- Решения и почему так: `docs/adr/` (формат — `docs/adr/README.md`).
- Правила кода для ревью: `CODING_STANDARDS.md`.
- Тикеты и сценарии ведёт Antagor: `.agents/antagor/`.
- Стандарт пакета: https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator/src/branch/main/skills/cli-builder/reference/standard.md (разделы по названию, например «Install»).
- Гейт перед коммитом: `uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.25.8#subdirectory=gate" rb-release check`.
- Правка без тикета (hand fix) — наименьшая, в границах `[architect.hand_fix]` Antagor. Код, тест или смысл правила — всегда тикет.
- Выпуски (временно, до отмены Человеком): Архитектор принимает задачи и делает `antagor publish` (push) сам,
  без подтверждения, после своей проверки (гейт + просмотр изменений с прошлого тега); о выпуске сообщает после; затем обновляет глобальную установку:
  `uv tool install --force "rb-semkit @ git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/semkit.git@<тег>"`.
