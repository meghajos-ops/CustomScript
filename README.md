# CustomScript

> An original programming language and development environment built from scratch in Python.

CustomScript is a small experimental programming language designed around simple commands, readable syntax, measurements, controlled randomness, history, error recovery, hardware-style memory, and a custom development environment called **NOVA**.

CustomScript is **not intended to be Python with renamed keywords**. Its syntax and features are designed around its own ideas, including `maybe`, `rewind`, `|>` scopes, measurement units, `fast_ram`, and CustomScript-native error handling.

---

## 🚀 Current Version

**CustomScript 0.1**

CustomScript 0.1 is the first public development release.

The current language includes:

- Output
- Variables
- Arithmetic
- Measurement units
- Random values
- Conditions
- `otherwise`
- `|>` scopes
- History and `rewind`
- `attempt` / `rescue`
- `fast_ram`
- User input with `ask`
- CustomScript diagnostics
- NOVA development environment
- Syntax highlighting
- Autocomplete
- Search
- Multi-file development features
- CustomScript-specific error messages

---

# 🧠 What Is CustomScript?

CustomScript started as a Python project that interprets its own programming language.

Instead of writing Python code such as:

```python
print("Hello, World!")

CustomScript uses:

reveal/Hello, World!/

The goal is not simply to recreate Python.

CustomScript has its own concepts and syntax.

For example:

maybe wind = 10 ~ 25

creates a dynamic value in a range.

Measurements can be written directly:

let distance = 120meters
let time = 6seconds
let speed = distance / time

History can be changed with:

rewind lives by 2 steps

And memory can be explicitly reserved and accessed:

fast_ram byte memory[8]

fast_ram write memory[0] = 255
fast_ram read memory[0]

These are intended to be part of CustomScript's identity.

✨ Features
Output

Use reveal to display information.

reveal/Hello, World!/

You can also reveal variables:

let score = 100

reveal//score//

CustomScript supports both normal output and variable output.

📦 Variables

Variables are created with let.

let score = 100
let damage = 25
let remaining = score - damage

Variables can then be revealed:

reveal//score//
reveal//remaining//

Example output:

100
75

Variables can contain numbers, decimal values, negative values, and measured values.

➕ Arithmetic

CustomScript supports:

+
-
*
/

Example:

let score = 100
let damage = 25
let remaining = score - damage

let doubled = score * 2
let divided = score / 2

Results can be revealed:

reveal//remaining//
reveal//doubled//
reveal//divided//

CustomScript also handles decimal results.

For example:

100 / 2

can produce:

50.0

Division by zero is handled by the interpreter as an error instead of silently producing an invalid result.

📏 Measurement Units

One of CustomScript's built-in concepts is measurement.

Values can contain units directly:

let distance = 120meters
let time = 6seconds

Measurements can participate in calculations:

let speed = distance / time

Result:

20.0meters/seconds

This allows CustomScript programs to represent simple physical measurements without manually storing the unit separately.

Examples:

50meters
10seconds
25kilometers
5minutes

Units are part of the value internally.

🎲 Dynamic Values — maybe

CustomScript has a native dynamic-value system called maybe.

Example:

maybe wind = 10 ~ 25

This creates a value that can vary within the specified range.

You can reveal it normally:

reveal//wind//

A result may look like:

12 (Dynamic)

Running the program again can produce a different value.

This is intentionally different from simply writing Python's random-number syntax.

🔀 Conditions

CustomScript uses suppose for conditional logic.

Example:

let health = 100

suppose health > 50
|> reveal/Still healthy!/

Supported comparisons include:

==
>
<
>=
<=

Examples:

suppose health == 100
|> reveal/Health is exactly 100!/

suppose health > 50
|> reveal/Health is above 50!/

suppose health < 150
|> reveal/Health is below 150!/

suppose health >= 100
|> reveal/Health is at least 100!/

suppose health <= 100
|> reveal/Health is at most 100!/
➡️ |> Scope

CustomScript uses:

|>

to define the scope of a command or block.

For example:

suppose health > 50
|> reveal/Still healthy!/

The |> syntax is intentionally part of CustomScript's own block design.

It is not Python indentation.

This allows CustomScript to visually show which command belongs to a condition or other scoped operation.

🔄 Otherwise

If a suppose condition is not met, otherwise can provide an alternative scope.

Example:

suppose health > 50
|> reveal/Healthy!/

otherwise
|> reveal/Needs help!/

If the condition is false, the otherwise section runs.

⏪ Rewind

CustomScript has a built-in history system.

Variables can keep previous states, allowing a program to travel backward through a variable's history.

Example:

let lives = 3
let lives = 2
let lives = 1

rewind lives by 2 steps

reveal//lives//

Result:

[Time Travel] 'lives' rewound 2 steps.
3

rewind is one of CustomScript's unique features.

It is not simply an alias for a normal Python feature.

The interpreter keeps variable history so that previous states can be recovered.

🛡️ Error Recovery

CustomScript provides:

attempt

and:

rescue

for handling runtime problems.

Example:

attempt

|> reveal//variable_that_does_not_exist//

rescue

|> reveal/An error was caught!/

If the attempted section produces an error, CustomScript can enter the rescue section instead of terminating the entire program.

This allows programs to recover from certain runtime errors.

Example:

attempt

|> reveal//missing_variable//

rescue

|> reveal/The problem was caught!/

reveal/Program continued!/

The program can continue after the rescue section.

💾 Fast RAM

CustomScript includes a simple hardware-style memory system called fast_ram.

Memory can be reserved with:

fast_ram byte memory[8]

This reserves 8 byte-sized memory slots.

Writing to RAM

Use:

fast_ram write memory[0] = 255

Additional slots can be written:

fast_ram write memory[1] = 42
fast_ram write memory[2] = 100
Reading RAM

Use:

fast_ram read memory[0]

Example:

fast_ram byte memory[8]

fast_ram write memory[0] = 255
fast_ram write memory[1] = 42

fast_ram read memory[0]
fast_ram read memory[1]

Output:

[Hardware] Reserved 8 bytes for 'memory'
[Hardware] memory[0] = 255
[Hardware] memory[1] = 42

The RAM system is intentionally explicit and hardware-inspired.

⌨️ User Input

CustomScript supports user input with:

ask

Basic input:

ask name

The user enters a value through the CustomScript/NOVA input interface.

The value can then be revealed:

reveal//name//
Number Input

Input can specify a type:

ask age as number

This tells CustomScript that the value should be treated as a number.

Measured Input

Input can also use a unit:

ask distance as meters

The entered value can then become a measured CustomScript value.

For example:

ask distance as meters
reveal//distance//
📝 Comments

Comments can be written using:

//

Example:

// This is a comment

let score = 100

// Display the score
reveal//score//

Comments are intended for notes and explanations inside CustomScript programs.

🧮 Complete Example

Here is a small program using several CustomScript features together:

// CustomScript example

let health = 100
let damage = 25
let remaining = health - damage

reveal/Player health:/
reveal//remaining//

suppose remaining > 50
|> reveal/Player is still healthy!/

otherwise
|> reveal/Player needs help!/

maybe wind = 10 ~ 25

reveal/Wind value:/
reveal//wind//

fast_ram byte memory[4]

fast_ram write memory[0] = 255

reveal/RAM value:/
fast_ram read memory[0]
📚 Quick Reference
Feature	Syntax
Output	reveal/Hello/
Reveal variable	reveal//name//
Variable	let name = value
Dynamic value	maybe name = 10 ~ 25
Addition	a + b
Subtraction	a - b
Multiplication	a * b
Division	a / b
Unit	120meters
Condition	suppose condition
Scoped command	|> command
Alternative	otherwise
History	rewind name by 2 steps
Error handling	attempt / rescue
RAM reservation	fast_ram byte memory[8]
RAM write	fast_ram write memory[0] = 255
RAM read	fast_ram read memory[0]
Input	ask name
Number input	ask age as number
Unit input	ask distance as meters
Comment	// comment
🐍 CustomScript vs Python

CustomScript can perform some tasks that Python can perform, but the syntax and design are intentionally different.

For example:

Python
score = 100

if score > 50:
    print("High score")
else:
    print("Low score")
CustomScript
let score = 100

suppose score > 50
|> reveal/High score!/

otherwise
|> reveal/Low score!/
Output

Python:

print("Hello")

CustomScript:

reveal/Hello/
Variables

Python:

score = 100

CustomScript:

let score = 100
Input

Python:

name = input()

CustomScript:

ask name
Number Input

Python:

age = int(input())

CustomScript:

ask age as number
Conditions

Python:

if score > 50:
    print("Good")

CustomScript:

suppose score > 50
|> reveal/Good/
Error Recovery

Python:

try:
    ...
except:
    ...

CustomScript:

attempt

|> ...

rescue

|> ...
Random Values

Python normally requires a random-number system.

CustomScript:

maybe number = 1 ~ 100
History

Python does not have a built-in equivalent to CustomScript's variable history system.

CustomScript:

rewind score by 2 steps
Memory

Python normally does not expose a simple language-level command resembling CustomScript's fast_ram system.

CustomScript:

fast_ram byte memory[8]

fast_ram write memory[0] = 255

fast_ram read memory[0]
🖥️ NOVA

CustomScript is designed to be used with NOVA, the CustomScript development environment.

NOVA provides the development interface for writing and running CustomScript programs.

The interface includes:

CustomScript editor
Line numbers
Syntax highlighting
Output/terminal area
Run controls
File/project navigation
Search
Autocomplete
Diagnostics
Clickable error locations
CustomScript-aware code suggestions
Status information

NOVA is designed around CustomScript rather than trying to reproduce another programming environment.

🎨 Syntax Highlighting

NOVA recognizes CustomScript syntax and visually separates different parts of a program.

Examples include:

let
maybe
suppose
otherwise
attempt
rescue
reveal
rewind
fast_ram
ask
numbers
units
operators
comments
strings
|> scopes

The goal is to make CustomScript readable while maintaining its own visual identity.

⚠️ Diagnostics

NOVA includes CustomScript-aware diagnostics.

Instead of simply displaying a Python traceback, NOVA can identify problems in CustomScript source code.

Diagnostics can identify issues such as:

Undefined variables
Variables used before definition
Unknown CustomScript instructions
Invalid condition references
Other runtime errors

Diagnostics are designed around CustomScript terminology.

💡 Autocomplete

NOVA provides suggestions for CustomScript commands and keywords.

Examples include:

reveal
let
maybe
rewind
suppose
otherwise
attempt
rescue
fast_ram
byte
write
read
ask

Variables defined in the current program can also be suggested.

The autocomplete system intentionally focuses on CustomScript syntax instead of filling the editor with Python keywords.

🔎 Search

NOVA includes code search functionality for finding text inside the editor.

This is useful when working with larger CustomScript programs.

📁 Project Development

The current CustomScript project is written in Python.

The main interpreter/development environment is contained in:

CustomScript.py

The project also uses a Python virtual environment locally.

The virtual environment is intentionally excluded from the Git repository.

🧪 Testing

CustomScript 0.1 has been tested with a regression script covering the major language systems.

The test suite includes tests for:

Basic output
Variables
Negative numbers
Decimal numbers
Units
Division
Multiplication
Random values
Equality
Greater-than comparisons
Less-than comparisons
Greater-than-or-equal comparisons
Less-than-or-equal comparisons
otherwise
False conditions
rewind
fast_ram
RAM writes
RAM reads
attempt
rescue
Program continuation after rescue
Final calculations

Example test output includes:

TEST PASS: equality ==
TEST PASS: greater than >
TEST PASS: less than <
TEST PASS: greater/equal >=
TEST PASS: less/equal <=
TEST PASS: otherwise executed

RAM testing:

[Hardware] Reserved 8 bytes for 'memory'
[Hardware] memory[0] = 255
[Hardware] memory[1] = 42
[Hardware] memory[2] = 100

Error recovery testing:

TEST PASS: rescue caught the error
Execution continued after rescue!

The complete regression suite is used to make sure new changes do not accidentally break existing CustomScript behavior.

🧱 Project Philosophy

CustomScript is being developed around several principles.

1. CustomScript should remain its own language

CustomScript should not become:

Python, but the keywords have different names.

Features should have their own concepts and behavior.

2. Existing syntax matters

The language already has a recognizable identity:

reveal
let
maybe
suppose
otherwise
|>
rewind
attempt
rescue
fast_ram
ask

Future development should build around these ideas.

3. The language should stay readable

CustomScript programs should be understandable without requiring extremely complicated syntax.

For example:

let distance = 120meters
let time = 6seconds
let speed = distance / time

reveal//speed//

is intended to be readable directly.

4. Features should have a reason to exist

New features should not be added simply because another programming language has them.

A feature should fit CustomScript's design.

🛣️ Development Roadmap

CustomScript 0.1 is the beginning of the project.

Future development is planned in stages.

Phase 1 — IDE

Planned development includes:

Error highlighting
Clickable errors
Autocomplete
Proper search
Code folding
Real multi-file tabs
Project explorer improvements
Phase 2 — Language

Future language development may expand CustomScript with additional concepts such as:

Strings
Booleans
Lists
Additional input systems
More CustomScript-native programming structures

New features will be designed around CustomScript rather than directly copying Python syntax.

Phase 3 — Interpreter

The interpreter can eventually move toward a more formal architecture.

Possible components include:

Source Code
     ↓
Tokenizer
     ↓
Parser
     ↓
Syntax Structure
     ↓
Interpreter
     ↓
Runtime

This would make the language easier to expand while keeping its syntax under control.

Possible future improvements include:

Better expression parsing
Parentheses
Operator precedence
More formal type handling
Expanded unit handling
Better error locations
More structured runtime behavior
Phase 4 — Developer Tools

Future NOVA development can include:

Debugger
Breakpoints
Variable inspector
Step-over
Step-into
Runtime profiling

These features would be designed specifically around CustomScript execution.

Phase 5 — Larger Ecosystem

Longer-term possibilities include:

Modules
Imports
Standard library
File operations
Additional data structures
Documentation/help system
CustomScript project files
Packaging CustomScript programs
Distribution tools

These are future ideas and are not necessarily part of CustomScript 0.1.

📦 Version Plan

The project is currently organized around incremental releases.

CustomScript 0.1

Current foundational language and NOVA environment.

CustomScript 0.2

Potential language expansion.

CustomScript 0.3

Potentially larger programming concepts.

CustomScript 0.4

Potential tokenizer/parser/AST architecture.

CustomScript 0.5

Potential debugging tools.

CustomScript 1.0

A future stable language release.

The exact contents of future versions may change as the language develops.

🧑‍💻 Running CustomScript

CustomScript 0.1 is currently distributed as Python source code.

You need Python installed on your computer.

The primary program is:

CustomScript.py

Run it with Python:

python CustomScript.py

On systems where python points to a different installation, the appropriate Python command may be required.

📥 Getting the Source

The project is hosted on GitHub.

You can download the repository and obtain the CustomScript source code.

The current repository contains the project source and Git configuration while excluding local development files such as the Python virtual environment and PyCharm configuration.

🔒 Repository Files

The repository intentionally ignores files that are specific to a developer's local computer.

For example:

.idea/
.venv/
__pycache__/
*.pyc

These files are not required to run the CustomScript source itself and should not be treated as part of the language.

🧪 Example Program

Here is a larger example combining several current features:

// ========================================
// CustomScript Example
// ========================================

reveal/Welcome to CustomScript!/

let health = 100
let damage = 25
let remaining = health - damage

reveal/Health remaining:/
reveal//remaining//

suppose remaining > 50
|> reveal/Health is above 50!/

otherwise
|> reveal/Health is low!/

maybe wind = 10 ~ 25

reveal/Dynamic wind value:/
reveal//wind//

let distance = 120meters
let time = 6seconds
let speed = distance / time

reveal/Calculated speed:/
reveal//speed//

fast_ram byte memory[8]

fast_ram write memory[0] = 255
fast_ram write memory[1] = 42

reveal/Memory values:/
fast_ram read memory[0]
fast_ram read memory[1]

reveal/CustomScript test complete!/
🧭 Language Philosophy

CustomScript is intentionally experimental.

The project is about exploring what a programming language can look like when it is designed around its own ideas instead of simply following an existing language.

Some CustomScript concepts are intentionally unusual.

For example:

rewind

treats variable history as part of the language.

maybe

provides a built-in dynamic value concept.

fast_ram

makes memory access an explicit language feature.

|>

provides CustomScript's own scoped-command structure.

These features are part of the reason CustomScript exists.

🤝 Contributing

CustomScript is currently an early-stage project.

Before contributing major changes, consider the project's core goals:

Keep CustomScript recognizable as its own language.
Avoid simply copying another language's syntax.
Preserve existing CustomScript behavior unless there is a deliberate reason to change it.
Test existing features after interpreter changes.
Prefer clear syntax and predictable behavior.
Keep NOVA focused on CustomScript development.
🐛 Bug Reports

If you find a bug, include:

The CustomScript code that caused it
What you expected to happen
What actually happened
Any NOVA diagnostic or terminal output
Your Python version if relevant
Your operating system

Example:

CustomScript:

let score = 100
reveal//score//

Expected:
100

Actual:
[error/output here]

This makes problems much easier to reproduce.

📋 Current Language Cheat Sheet
// OUTPUT
reveal/Hello!/
reveal//variable//

// VARIABLES
let score = 100

// RANDOM / DYNAMIC VALUES
maybe wind = 10 ~ 25

// UNITS
let distance = 120meters
let time = 6seconds

// MATH
let total = a + b
let difference = a - b
let result = a * b
let speed = distance / time

// CONDITIONS
suppose score == 100
|> reveal/Perfect!/

suppose score > 50
|> reveal/Above 50!/

// OTHERWISE
otherwise
|> reveal/Condition was false!/

// HISTORY
rewind score by 2 steps

// ERROR RECOVERY
attempt
|> reveal//something//

rescue
|> reveal/Error recovered!/

// MEMORY
fast_ram byte memory[8]

fast_ram write memory[0] = 255
fast_ram read memory[0]

// INPUT
ask name
ask age as number
ask distance as meters

// COMMENTS
// This is a comment
📜 License

The project's licensing status will be specified in the repository as the project moves toward a formal public release.

Until a license is added, the source code should not automatically be assumed to grant permission for unrestricted redistribution, modification, or commercial use.

📌 Project Status

CustomScript 0.1 is an early public development release.

The core interpreter and NOVA environment are functional, and the current language has been tested across its major implemented systems.

The project is still evolving.

The syntax, runtime behavior, IDE features, and project structure may change between versions.

🌟 Why CustomScript?

Programming languages don't have to all look the same.

CustomScript is an experiment in creating a language with its own:

Syntax
Runtime behavior
Measurement system
Dynamic values
Variable history
Error recovery
Memory model
Development environment

The project started as a Python program.

It grew into an interpreter.

The interpreter grew into a language.

And the language is now being developed alongside its own IDE:

NOVA.

CustomScript
Write differently.
Think differently.
Build your own language.
