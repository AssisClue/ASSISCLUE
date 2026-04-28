# Context Memory Block — Operational README

## What this block is

`app/context_memory/` is the system block responsible for turning raw activity into usable context and memory.

It does **not** exist to answer the user directly.  
It exists to:

- read inputs from the system
- classify and extract useful information
- build context products
- store memory through interchangeable backends
- retrieve the right memory depending on the task
- expose a stable service layer to the rest of the app

This block should be understood as the **context and memory engine** of the app.

---

## Main design idea

This block was intentionally built so that:

- context logic is **owned here**
- storage/backends are **replaceable**
- task retrieval is **separate from storage**
- the rest of the app talks to **services**, not to internal files
- future expansions can be added without rewriting the core

Important principle:

**Mem0 is not the architecture.**  
Mem0 is only one possible backend inside this architecture.

---

## What this block currently does

The current implementation already supports:

- input contracts
- internal memory/context models
- session memory
- profile memory
- ingest readers
- normalization helpers
- classification rules
- extraction helpers
- linking
- compaction
- retrieval
- JSON backend
- Mem0 adapter backend
- Qdrant-style index layer
- summaries
- snapshots
- orchestration pipelines
- a service entrypoint
- a successful end-to-end smoke test

This means the block is no longer just a sketch.  
It is already a working modular base.

---

## Folder map

### `contracts/`
Defines the official internal contracts of the block.

Contains:
- context kinds
- input models
- retrieval models
- task types
- backend interfaces
- service interfaces

This folder is where new official block capabilities begin.

---

### `models/`
Defines the internal data objects used by the block.

Contains:
- `MemoryItem`
- `LiveContextSnapshot`
- `RecentContextSnapshot`
- `UserProfileSnapshot`
- `TaskContextPacket`

This folder represents the core internal memory/context shapes.

---

### `session/`
Handles volatile session state.

Contains:
- session events
- short-term rolling memory
- current activity state
- recent session window

This is the “what is happening now / very recently” layer.

---

### `profile/`
Handles more stable user-level memory.

Contains:
- user profile memory
- preference store
- stable fact store
- profile merge rules

This is the right place for things like:
- reply preferences
- style preferences
- stable user facts
- recurring work style notes

---

### `ingest/`
Reads raw sources and converts them into internal input types.

Current sources:
- chat history
- session events
- screenshot notes
- file context
- runtime state

New source types should be added here.

---

### `normalize/`
Cleans and standardizes data before deeper processing.

Contains:
- text cleaning
- event normalization
- metadata normalization
- memory text normalization
- dedupe key helpers

This prevents downstream chaos.

---

### `classify/`
Decides what a piece of input means.

Contains:
- memory kind classification
- source classification
- importance scoring
- recency scoring
- promotion rules
- task routing filters

This is one of the most important folders because it contains a lot of product logic.

---

### `extract/`
Pulls structured value from raw text.

Contains:
- fact extraction
- profile extraction
- project extraction
- topic extraction
- timeline extraction
- relation extraction

If the system must “understand” a new kind of thing, this folder often needs a new extractor.

---

### `builders/`
Builds finished outputs from already-processed pieces.

Contains:
- memory record builder
- live context builder
- recent context builder
- user profile builder
- project context builder
- task context builder
- final context packet builder

These files do not discover new information.  
They assemble clean outputs.

---

### `linking/`
Creates relationships between memory items.

Contains:
- duplicate linking
- relation linking
- timeline linking
- project linking

Used to avoid isolated memory fragments.

---

### `compact/`
Reduces noise and keeps memory useful.

Contains:
- memory compactor
- recent context compactor
- profile compactor
- session compactor
- archive compactor

Used for dedupe, trimming, prioritization, and aging.

---

### `retrieval/`
Searches memory according to task intent.

Contains:
- lexical retrieval
- semantic retrieval
- hybrid retrieval
- retrieval ranker
- retrieval filters
- task-context retrieval
- memory search service

This folder is critical because different tasks should retrieve memory differently.

Example:
- code screenshot analysis
- timeline lookup
- project follow-up
- user preference retrieval

Same memory base, different retrieval behavior.

---

### `backends/`
Implements replaceable storage and index layers.

Contains:

#### `backends/json/`
Robust local fallback.

#### `backends/mem0/`
Mem0 integration layer through an adapter.

#### `backends/qdrant/`
Index/search abstraction for vector-style storage.

The important idea is:
the block should still work even if Mem0 is unavailable.

---

### `summarize/`
Builds human-readable internal summaries from context products.

Contains:
- live context summary
- recent context summary
- daily context summary
- project context summary
- session rollup

Useful for task packets, debug, and future orchestration.

---

### `snapshots/`
Produces reusable prebuilt context snapshots.

Contains:
- live snapshot service
- recent snapshot service
- daily snapshot service
- project snapshot service

This avoids rebuilding everything from scratch every time.

---

### `orchestration/`
Coordinates internal block pipelines.

Contains:
- ingest pipeline
- memory update pipeline
- snapshot pipeline
- retrieval pipeline
- context pipeline

This folder is the internal flow controller of the block.

---

### `services/`
The public access layer for the rest of the app.

Current main entry:
- `context_memory_service.py`

Other parts of the app should depend on this layer, not on internal modules directly.

---

### `runtime/`
Holds path and storage path helpers.

Contains no major business logic.  
Only support structure.

---

## Current state of the block

### What is already validated
A smoke test ran successfully end-to-end.

The test confirmed:
- imports are valid
- structure is valid
- memory items are produced
- live snapshot is produced
- recent snapshot is produced
- profile snapshot is produced
- retrieval returns results
- final context packet is built

This confirms the block is alive as a system, not just as a folder tree.

---

## Known current limitation

The architecture works, but retrieval quality is still basic.

Observed behavior in smoke test:
- the task `SCREENSHOT_CODE` returned a `project_context`
- the more relevant `coding_issue` did not win the ranking

This means:
- the retrieval layer works structurally
- but ranking/filter tuning still needs improvement

So the next improvements should focus on:
- retrieval scoring
- task filter tuning
- better ranking for issue-like items
- better prioritization for screenshot/code tasks

---

## How to extend this block correctly

When adding something new, do **not** rewrite the whole block.

Instead, add the new piece in the correct layer.

### If you add a new source
Add a new reader in:
- `ingest/`

### If you add a new kind of meaning
Extend:
- `classify/`
- maybe `extract/`

### If you add a new context product
Add or extend:
- `models/`
- `builders/`
- `snapshots/`

### If you add a new task behavior
Extend:
- `contracts/task_types.py`
- `classify/task_context_router.py`
- `retrieval/`

### If you add a new backend
Add it in:
- `backends/`

### If you add a new stable user-specific memory type
Usually extend:
- `profile/`
- maybe `extract/`
- maybe `classify/`

---

## Important conceptual separation

There are at least two different memory worlds:

### 1. Inferred memory
Derived by the system from:
- chat history
- session events
- screenshots
- files
- runtime state

This is what the current block mainly supports.

### 2. Explicit editable memory
Created manually by the user.

Examples:
- custom folders
- recipe collections
- personal rule sets
- saved ideas
- editable notes

This is not yet a first-class subsystem here.

If the product later needs:
- user-created folders
- editable collections
- custom grouped notes
- personal special rules

the recommended next expansion is a new sub-block such as:

- `user_spaces/`
or
- `collections/`

That should remain separate from inferred memory.

---

## Recommended future extension

If manual user-managed sections become important, add:

`app/context_memory/user_spaces/`

Suggested purpose:
- user-created collections
- editable saved items
- custom rule groups
- named folders
- manual memory editing

This should sit on top of the current context-memory engine, not replace it.

---

## Rules for working with this block

1. Do not couple the rest of the app directly to Mem0.
2. Do not let random modules read internal stores directly.
3. Always prefer extending a layer over rewriting the block.
4. Keep task retrieval logic separate from backend logic.
5. Keep inferred memory and user-editable memory conceptually separated.
6. Use `services/` as the main integration point.
7. Keep fallback support alive.
8. Prefer adding focused modules over bloating existing files.

---

## What this block should be long-term

Long-term, this block should become:

- the owner of context assembly
- the owner of memory preparation
- the owner of memory retrieval policy
- the adapter point for storage backends
- the stable context provider for the whole app

The rest of the system should be able to ask:

- what is happening now?
- what happened recently?
- what do we know about this project?
- what does the user usually prefer?
- what memory is relevant for this task?

And this block should answer that cleanly.

---

## Final short definition

This block is the app’s structured memory/context engine.

It is designed so that:
- memory logic lives here
- backends can change
- features can grow by extension
- the rest of the app stays clean
- future systems can plug into it without replacing the core