Web Commands Architecture Overview
The command system in app/system_support/commands is designed to be extensible, using a JSON-based catalog system for specialized administrative and web actions.

Core Components
1. Command Catalogs (catalogs/ folder)
This is the most important folder for adding new "Web Commands".

administrative_web_commands.json
: Contains definitions for browser control, URL opening, and web searching.
administrative_core_commands.json
: Contains system-level commands like screenshots, repeating responses, and persona switching.
2. The Matcher (administrative_command_matcher.py)
This file is the "Ear" of the administrative system. It loads the JSON files and compares the user's spoken or typed text against the aliases defined in the JSON. It handles:

Exact matches (e.g., "open browser")
Prefix matches with payloads (e.g., "open website google.com" where "open website" is the alias and "google.com" is the payload).
3. The Bridge (administrative_command_bridge.py)
Once a command is matched, the bridge decides where to send it. It maps the action_name from the JSON to a route_family (like webautomation or display_actions).

4. Generic Command Core (command_service.py, command_parser.py)
This is a parallel system used for "Primary Vocabulary" commands like adding notes or changing rules. It uses a more manual NLU approach defined in command_contract.py.

3-Step Guide to Create New Web Commands
To add a new command (e.g., "Refresh Page"), you need to modify exactly 3 files:

Step 1: Register the Command (The List)
File: 
administrative_web_commands.json
 Add the command ID and the natural language phrases (aliases) that should trigger it.

json
{
  "command_id": "browser_refresh",
  "action_name": "browser_refresh",
  "aliases": [
    "refresh page",
    "reload page",
    "update page"
  ]
}
Step 2: Set the Route (The Bridge)
File: 
administrative_command_bridge.py
 Tell the system that this action belongs to the browser/web automation family.

python
# Inside _build_routing_hint()
if clean_action == "browser_refresh":
    return {
        "route_family": "webautomation",
        "target_runner": "display_actions",
        "handler_key": "browser_refresh",
        "payload_text": clean_payload,
    }
Step 3: Write the Code (The Runner)
File: 
administrative_command_runners.py
 Add the actual Python logic to control the browser (using the session.page object).

python
# Inside run_administrative_browser_command()
if action_name == "browser_refresh":
    session = runtime.get_session()
    if session:
        session.page.reload()
        return {"ok": True, "message": "Page refreshed"}
    return {"ok": False, "error": "no_session"}
Summary of Files
catalogs/administrative_web_commands.json: Where the list lives.
administrative_command_bridge.py: Connects the list to the logic.
administrative_command_runners.py: Where the browser logic is written.