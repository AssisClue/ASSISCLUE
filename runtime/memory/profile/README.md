Small README version
runtime/memory/profile/user_profile.json

Purpose: short summary of the user
Type: memory snapshot
Stores: preferences, stable facts, projects, work style
Not for: service status, live mode, or assistant persona
Related to: context_memory
Not mainly related to: app/personas
Best simple definition:

This file is the assistant’s short profile about you.
Not the assistant personality, and not raw memory history.

If you want, next I can explain the difference between:

memory_items.json
user_profile.json
live_context.json
recent_context.json
in one very simple table.

####

What I found:

user_profile.json belongs to app/context_memory/...
persona logic belongs to app/personas/...
So:

user_profile.json = memory about you
app/personas = identity/style of the assistant
Simple version:

profile = what the assistant knows about your preferences
persona = how the assistant behaves/speaks
Who creates it
Main pieces connected to it:

app/context_memory/models/user_profile_snapshot.py
app/context_memory/builders/user_profile_builder.py
app/context_memory/backends/json/json_profile_store.py
app/context_memory/runtime/context_memory_runtime_service.py
That means:

the system collects profile info
builds a snapshot
saves it into this JSON file
