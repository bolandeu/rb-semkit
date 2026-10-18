# Help standard

How the docstring of a command is written, and how the help document is built from it.

The help document is one JSON file for people: every command of the CLI with its options, arguments and examples, in the
shape of OpenCLI 0.1 with the commands at the root, so that a viewer such as InSpectra renders it as HTML. The CLI builds
it from its code with no hand step: the same code gives the same document, byte for byte. Rendering the HTML is not the
job of the CLI.

## Where each part comes from

```
docstring of the command ──► summary ─────┐
                         ──► description ─┼──► the command in the document
                         ──► examples ────┘
signature of the command ──► options and arguments: name, default, allowed values, repeats or not
```

The text comes from the docstring. Everything a machine can read comes from the signature, never from the text.

## The docstring

```
Paint the targets in one color.

A coat dries before the next one; each target gets every coat.
coats: how many coats each target gets.

Example: tool paint wall --name Ann
-> wall: red, 2 coats
```

1. **Summary.** The first sentence of the docstring, on its first line: what the command gives. It ends with «.».
2. **Description.** The paragraphs after the summary: what the command does, plain and short. The lines of a paragraph
   are joined into one; a list item stays a line of its own.
3. **Option line.** A line «name: text» explains the option or argument `name` (several names: «first, last: text»).
   It goes to that option only, never into the description. List items right after it belong to it.
4. **Example.** A line «Example: <command>», optionally followed by a line «-> <result>» (an ASCII arrow and a space):
   what the command gives. One to three examples per command, each a real short command.

## The document

| Field | Content |
|---|---|
| root | `opencli`, `info`, `commands`, `options`, `arguments`, `examples`: the commands at the root, not under `command` |
| command `description` | the summary as its own first paragraph, then the description; no option line, no example line |
| command `examples` | each example as one string: «<rest>  # -> <result>» (two spaces before `#`), or «<rest>» alone when there is no result line; <rest> is what follows «<program> <command path>» |
| option `description` | the help of the option, then, as its last line, its default and allowed values |
| option argument `arity` | `{"minimum": 1, "maximum": 1}` for an option that does not repeat; `{"minimum": 1}` for one that repeats |
| option argument `acceptedValues` | the allowed values, in the order of the signature |

### The last line of an option

OpenCLI 0.1 has no fields for a default or for allowed values, so the description of an option ends with one line that
gives them, taken from the signature:

```
Default: 10. Allowed: fast, exact, both.
```

- «Default: <value>.» only when the option has a default; a flag shows «Default: off.» (or «Default: on.» when it is on by
  default); a list default is joined by «, ».
- «Allowed: <a>, <b>.» only when the values are fixed (a Literal or an enum), joined by «, » in the order of the
  signature.
- Each part ends with «.»; one space between the two parts; no line when neither applies.

### Examples without the command path

A viewer puts «<program> <command path>» in front of every example by itself, and cannot put an argument before a
subcommand. So an example in the document holds only what follows that prefix: the docstring line
«Example: tool paint wall --name Ann» becomes the string «wall --name Ann».

- The docstring keeps the full command, so a test can run it; the document builder cuts the prefix.
- An example that does not start with «<program> <command path>» breaks the standard: the document is not built, and the
  error names the command and the example.
- A hook of the CLI may bring a docstring example to that form first (a command whose arguments stand before its
  subcommand, as in «tool read IN step»), and may put one line before the description of a command.

### Inherited options

A group may have options that every command below it also takes. A hook of the CLI names them; the document marks them
`recursive` on the group and does not copy them into the subcommands. A hook inherits options only: a positional
argument is never inherited, because a viewer cannot place it before a subcommand.

## Checks

A test of the CLI walks every command and checks: a summary of one line, one to three examples that start with their command path, every option explained,
no option line left in the description, the last line of an option in the format above. A command that does not meet
the standard yet is in one allowlist in that test, with a comment; the list only shrinks.
