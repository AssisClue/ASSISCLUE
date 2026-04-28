This folder is the app’s “powers list” (a catalog). It tells the assistant what actions exist, and gives each action the info needed to route it to the right part of the app.



What’s inside
capability_spec.py: defines the CapabilitySpec shape (the “recipe card” for one power): capability_id, action_name, where it belongs (block_id), where to send it (target_queue, target_runner), which code handles it (handler_key), and if it’s on/off (enabled).
default_capabilities.py: the actual default list of powers (currently things like screenshots, “show runtime status”, and “stop talking”).
capability_registry.py: builds quick lookup tables so the app can find a capability by capability_id or by action_name.
__init__.py: makes it easy for the rest of the app to import: list_capabilities(), find_capability_by_id(), find_capability_by_action_name(), CapabilitySpec.
How it connects to the assistant app (real usages in your code)
Voice/command matching: app\live_listeners\primary_listener\command_matcher.py uses find_capability_by_id() / find_capability_by_action_name() so a spoken command can turn into a known “capability”.
Running display actions: app\display_actions\runners\display_action_runner_registry.py uses find_capability_by_action_name() to pick the right handler (like screenshot capture, screenshot analyze, show status, stop talking).
MCP tools (tool interface): app\mcp\adapters\capabilities_adapter.py + app\mcp\services\capabilities_mcp_service.py expose read-only tools like list_capabilities and get_capability_by_action_name (also documented in app\mcp\docs\TOOLS.md).
In one sentence
This folder is the assistant’s central “menu of allowed actions”, and other parts of the app use it to recognize commands and route them to the correct runner/handler.




----------------

These are the main files that “touch” (use) app\capabilities\:

app\live_listeners\primary_listener\command_matcher.py
Turns what you say into a action_name, then uses capabilities to find the right “power” (by capability_id or action_name).

app\router_dispatch\route_rules.py
Decides “where should this go?” If the action is a known capability, it picks the target_queue + target_runner from the capability.

app\router_dispatch\route_event_builder.py
Builds the routed event and fills in missing capability info (like capability_id, block_id, handler_key) using the capabilities list.

app\display_actions\runners\display_action_runner_registry.py
When an action is a display-type capability (screenshots, status, stop talking), it uses handler_key to pick the correct function to run.

app\mcp\adapters\capabilities_adapter.py + app\mcp\services\capabilities_mcp_service.py
Lets the tool-system ask “what capabilities exist?” (list_capabilities, get_capability_by_action_name) in a read-only way.

About “system_support commands”: they help with parsing/command rules, but the direct capability lookups happen in command_matcher.py and then routing happens in route_rules.py.


8:24 PM



Use app\capabilities\ when you want the assistant to run a known “button-like action” (a fixed power), like:

take a screenshot
analyze last screenshot
show runtime status
stop talking
Don’t use it when the user is just asking a normal question (chat). In that case it should go to the “answering” system, not an action runner.

Where this is explained in the app:

app\router_dispatch\route_rules.py decides:
primary_command → tries to find a matching capability and route it to its target_queue/target_runner
primary_quick_question → routes to spoken_queries (normal assistant answering)
command_core commands → do not use capabilities routing (they get ignored by that route)
Simple idea: Capabilities = the app’s “menu of actions”. If it’s not on the menu, it’s treated like normal conversation (or ignored if it’s a special command_core thing).

