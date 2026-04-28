Command Core Block
What this block is

This block is the command brain of the assistant.

Its job is to take a normal user phrase such as:

“add a note saying buy milk”
“remove this rule”
“read my notes”
“activate Rick”

and convert that phrase into a structured internal command that the system can understand and route safely.

This is not the UI, not the LLM, not memory itself, and not MCP by itself.
This block sits in the middle and answers a simple question:

“What exactly is the user trying to do?”

Why this block exists

The assistant already has many real parts:

listeners
routing
runtime queues
spoken query flow
screen actions
personas
memory layers
MCP tools
JSON runtime/state/debug files
Qdrant as semantic search support

What was still weak was the mutation / command layer, especially for natural commands like:

add
change
remove
read
list
move
rename
activate

Before this block, the system had partial pieces, aliases, and routing behavior, but it did not yet have a small, clean, central place dedicated to:

parsing command intent
validating action/target pairs
deciding if confirmation is required
dispatching the command to the correct handler

That is exactly what this block is for.

Main idea

The user should speak naturally.

The system should translate the phrase into a clean internal structure like:

action
target
payload
destination
options
confidence
confirmation requirement

Example:

User phrase

add note buy milk

Internal meaning

action: add
target: notes
payload.text: buy milk

Another example:

User phrase

activate Rick

Internal meaning

action: activate
target: persona
payload.item_name: Rick

So this block is the layer that transforms raw language into a command envelope that the rest of the system can work with.

What this block does today

Right now, this block provides a working command skeleton.

It already does these things:

defines canonical actions
defines canonical targets
normalizes simple aliases
parses a natural-ish command string
builds a structured command object
validates if an action is allowed for a target
applies confirmation policy
routes the command to a target handler
returns a normalized result object

That means this block already gives the system a clean backbone for commands, even though some target handlers are still placeholders.

What this block does NOT do yet

This block is not finished business logic yet.

At this stage, it does not fully implement real persistence or full execution for all domains.

For example, it does not yet fully:

write real notes into the final storage layer
update real rules/prompts/projects end-to-end
remove stored items from production storage
move items across spaces
rename stored entities in final storage
activate persona through the full live runtime service
log command execution into runtime files
expose the whole command layer through MCP

Right now, the command core is the safe, clean internal base.
The next work is connecting this base to the real system pieces.

Design decision behind this block

The chosen design is:

one shared action vocabulary + target-specific handlers

That means:

we do not create a separate parser vocabulary for each department
we do not invent completely different verbs for notes vs rules vs prompts
we use a common top-level action model:
add
change
remove
read
list
move
rename
activate

Then each target/domain decides:

whether that action is allowed
how it should be validated
how it should be executed

This keeps the system small, consistent, and scalable.

Why this design is better

Because the assistant needs one common language for commands.

If each department invents its own command logic, the system becomes harder to maintain and much harder to extend.

With this design, we get:

one parser vocabulary
one command envelope
one confirmation policy
one validation flow
one reusable result shape
domain-specific execution only where needed

So this block acts like a traffic controller for commands.

Folder and files

This block currently lives here:

app/system_support/commands/

Current files:

app/system_support/commands/
  command_contract.py
  command_models.py
  command_parser.py
  command_service.py
  command_confirmation_policy.py
  command_target_registry.py
  command_result_builder.py
  command_handlers.py
File-by-file explanation
app/system_support/commands/command_contract.py

This file defines the core vocabulary of the block.

It contains:

canonical actions
canonical targets
action aliases
target aliases
default target by action

This is the central rules file for “how the system names things”.

Examples:

save -> add
delete -> remove
use -> activate
note -> notes
app/system_support/commands/command_models.py

This file defines the main data structures used by the command block.

It contains structured objects for:

payload
destination
parsed command
command result

This is the typed internal shape used by parsing, routing, validation, and result building.

app/system_support/commands/command_parser.py

This file converts raw user text into a ParsedCommand.

Its job is to:

detect action
detect target
extract payload text
estimate confidence
infer destination hints
mark confirmation requirement

This is the first real interpretation layer.

Important note:
the current parser is intentionally simple and should be improved later.
For now it gives a clean starting point.

app/system_support/commands/command_service.py

This file is the main entry point of the block.

When the rest of the system wants to process a command, this file is the one to call.

Its job is to:

parse the text
reject invalid commands
validate action/target compatibility
stop for confirmation if needed
find the correct handler
execute the handler
build a normalized result

This is the orchestrator of the command block.

app/system_support/commands/command_confirmation_policy.py

This file contains the logic for when a command should require confirmation.

Today it is conservative.

Examples:

remove -> confirmation
move -> confirmation
rename -> confirmation
risky change with patch data -> confirmation

This exists to keep destructive actions safer.

app/system_support/commands/command_target_registry.py

This file defines which targets accept which actions.

Example idea:

notes can accept add, change, remove, read, list, move, rename
help can accept read, list
state can accept read, list
persona can accept read, list, change, activate

This is important because not every action makes sense for every target.

app/system_support/commands/command_result_builder.py

This file creates a uniform result object.

Instead of every handler returning random shapes, this file gives consistent results for:

success
error
confirmation required

This will be very useful later for:

runtime logs
UI display
spoken responses
MCP/tool responses
app/system_support/commands/command_handlers.py

This file contains the current target handlers.

Right now many handlers are still placeholders, but this is where target-specific execution starts.

Examples:

notes handler
rules handler
prompts handler
persona handler
memory handler
state handler

This file is the bridge between the command core and real business logic.

Later, some of these handlers may move into more specific service files, but for now this is a good staging point.

How the block works step by step

The full flow is:

1. User says something

Example:

add note buy milk

2. command_service.run_command() is called

This is the main public entry point.

3. The parser reads the text

It tries to detect:

action
target
payload
destination
confidence
4. The command is validated

The system checks:

is the command structurally valid?
is the action allowed for that target?
5. Confirmation policy is applied

If the action is risky, the system returns a confirmation-needed result instead of executing it directly.

6. The correct handler is selected

Example:

notes -> notes handler
persona -> persona handler
7. The handler returns its output

For now, many are placeholder responses.

8. A normalized result is returned

The system always returns a clean structured result.

Public entry point

The main way to use this block is:

from app.system_support.commands.command_service import run_command

Example:

from app.system_support.commands.command_service import run_command

result = run_command("add note buy milk")
print(result)

That is the main testable interface of the whole block.

Example behaviors
Example 1

Input:

add note buy milk

Expected direction:

action detected: add
target detected: notes
payload text: buy milk
Example 2

Input:

read rules

Expected direction:

action: read
target: rules
Example 3

Input:

activate Rick

Expected direction:

action: activate
target: default persona target
payload/item name: Rick
Example 4

Input:

remove note old reminder

Expected direction:

action: remove
target: notes
confirmation required: yes
How this block should be used in the system

This block should be used as the command normalization core.

The intended role is:

user phrase comes from listener / routing / spoken input
command core interprets the phrase
command core returns structured intent
handler layer connects that intent to real services/storage/runtime

So this block should sit before real execution, not replace execution.

It should be the safe translation layer between language and system actions.

Relationship with MCP

This block is related to MCP, but it is not the same thing.

MCP is:

a standardized system/tool interface layer

This command block is:

the internal command interpretation layer

How they fit together:

the command block decides what the user wants to do
MCP can later expose or consume some of those actions cleanly
MCP is a good façade for tool access
command core is a good brain for natural command parsing

So later, some command executions may go through MCP-backed services, especially for clean read/write tool access.
But the parser itself should not become raw MCP glue code.

Relationship with Qdrant

This block should not treat Qdrant as the main write target for commands like:

add
change
remove

Qdrant belongs more to:

semantic retrieval
disambiguation
evidence ranking
better read/search behavior

For mutation commands, the safer first write target is:

JSON / user_spaces / controlled services

So:

write path -> system storage / user spaces / services
smart read path -> memory layer / Qdrant / semantic support

This distinction is important and should be kept.






Ya avanzado
notes real write
persona activation real
edit_mode gate
confirmation/edit_mode flow
result/error consistency


Pendiente
parser mejor
payload/destination mejor
más targets reales
runtime trace/log
tests formales
posible MCP facade después