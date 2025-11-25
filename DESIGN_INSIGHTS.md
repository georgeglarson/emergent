# Design Insights: Building for LLMs, Not Humans

## The Core Realization

**The TUI isn't the feature.** Autonomous file discovery is.

Users don't actually care about fancy terminal interfaces. What they care about is not having to manually specify every file the agent should look at (like Aider's `/add` command). They want the agent to **explore, discover, and understand** the codebase on its own.

The TUI in tools like OpenCode is just a **signal** that says "this tool can navigate files autonomously." But a simple CLI that prints what it's doing works just as well.

## What LLMs Actually Need

### 1. Persistent, Visible State

LLMs have no inherent memory between API calls. They need:

- **Explicit state files** that are always loaded into context
- **Recent action history** so they know what they just did
- **Current position** in the filesystem and task

This is why we have `.agent_state.json` and memory files that are **always** in context.

### 2. Structured Feedback

LLMs struggle with unstructured text. They need:

- **JSON responses** from tools, not raw command output
- **Clear success/failure** indicators
- **Parsed errors** with file paths and line numbers extracted
- **Next action suggestions** to guide reasoning

Example of bad tool output:
```
Error: File not found
Traceback (most recent call last):
  File "main.py", line 45, in <module>
    ...
```

Example of good tool output:
```json
{
  "success": false,
  "summary": "File not found: config.json",
  "data": {
    "missing_file": "config.json",
    "searched_in": "/project"
  },
  "next_suggestions": [
    "Create config.json",
    "Check if file is in a different directory"
  ]
}
```

### 3. Reflection Mechanisms

LLMs drift over long contexts. They need:

- **Periodic self-assessment** (every N actions)
- **Memory updates** to record insights
- **Strategy adjustments** based on progress

Without reflection, the agent "forgets" its goal and starts wandering.

### 4. Resumability

For multi-day tasks, LLMs need:

- **Complete state serialization** to disk
- **Memory files** that persist across sessions
- **Action history** to understand what happened before

The agent should be able to "wake up" and continue seamlessly.

## Design Principles

### Principle 1: State is Always Explicit

Never rely on the LLM to "remember" anything. Everything goes in:
- `.agent_state.json` for current position and recent actions
- `memory/*.md` for long-term knowledge and decisions

### Principle 2: Tools Return Structured Data

Every tool returns:
```json
{
  "success": bool,
  "summary": "Human-readable summary",
  "data": {...},  // Structured data
  "next_suggestions": [...]  // What to do next
}
```

This makes it easy for the LLM to:
- Check if the action succeeded
- Parse relevant data
- Decide the next action

### Principle 3: Reflection Over Repetition

Instead of letting the LLM run 100 actions in a row:
- Force reflection every 10 actions
- Update memory with insights
- Reassess the approach

This prevents:
- Infinite loops
- Context drift
- Forgotten goals

### Principle 4: The Agent Owns Its Workspace

The agent creates and maintains:
- `memory/` for its thoughts
- `scratch/` for experiments
- `notes/` for understanding

This gives it a "place to think" that persists.

## What Makes File Editing Hard?

### Problem 1: LLMs Want to Rewrite Everything

LLMs are bad at precise edits. They want to rewrite entire files, which:
- Loses user changes
- Creates merge conflicts
- Breaks working code

**Solution:** Use structured editing (tree-sitter) or explicit diff format.

### Problem 2: No Verification Loop

LLMs don't know if their edit worked unless you tell them.

**Solution:** Automatic verification:
- Run tests after edits
- Show diffs before applying
- Validate syntax before writing

### Problem 3: Context Limits

Can't load entire codebase into context.

**Solution:** Smart file selection:
- Start with error traces
- Follow imports
- Use grep to find relevant files
- Drop files when done

### Problem 4: State Tracking

LLM doesn't know what files are "open" or what's changed.

**Solution:** Explicit state:
- `files_in_context` list
- Recent edits in action history
- Diff tracking

## Why Python?

**Pragmatic choice:**
- Fast iteration during development
- Best LLM SDK support (OpenAI, Anthropic)
- Good subprocess handling
- Async I/O with `asyncio`

**Not Rust because:**
- Slower to iterate
- Overkill for gluing tools together
- Better for production, not prototyping

**Not TypeScript because:**
- Event loop blocking issues
- TUI freezes during LLM calls
- Runtime overhead

**Not Bash because:**
- Need structured data handling
- Complex state management
- LLM SDK integration

## The Orchestrator Pattern

Instead of the LLM trying to construct perfect commands:

```python
# Bad: LLM tries to write grep commands
"Run: grep -r 'User' --include='*.py' project/"

# Good: LLM uses a tool
search_files(query="User", file_pattern="*.py")
```

The tool handles:
- Command construction
- Error handling
- Output parsing
- Result structuring

The LLM just decides **what** to search for, not **how**.

## Comparison to Existing Tools

### Aider
- **Problem:** Requires manual `/add` for every file
- **Our approach:** Autonomous file discovery

### OpenCode
- **Problem:** TUI blocks on LLM calls (TypeScript event loop)
- **Our approach:** Python with proper async, no TUI needed

### Cursor
- **Problem:** No persistent memory across sessions
- **Our approach:** Memory files that persist

### All of them
- **Problem:** No reflection mechanism
- **Our approach:** Forced reflection every 10 actions

## Future Improvements

### 1. Tree-sitter Integration
Instead of text-based editing:
```python
# Current: Replace lines 45-67
edit_file("auth.py", find="old code", replace="new code")

# Better: Structural editing
edit_function("auth.py", "login", new_body="...")
```

### 2. Semantic Search
Instead of grep:
```python
# Current: Text search
search_files("User")

# Better: Semantic search
find_similar_code("user authentication logic")
```

### 3. Multi-file Diffs
Preview all changes before applying:
```python
# Show what will change
preview_changes()

# Apply if good
apply_changes()

# Rollback if bad
rollback()
```

### 4. Cost Tracking
Monitor token usage and API costs:
```python
{
  "tokens_used": 45000,
  "estimated_cost": "$0.23",
  "actions_taken": 15
}
```

## Key Insight

**Design for how LLMs think, not how humans work.**

- LLMs need explicit state → `.agent_state.json`
- LLMs need structured data → JSON tool responses
- LLMs drift over time → Reflection loops
- LLMs lose context → Memory files

Build the environment the LLM needs to thrive, and it will.

## The Week-Long Test

The ultimate test: Put the agent in a gitpod with a goal and a week. Does it:

1. ✅ Make consistent progress?
2. ✅ Maintain focus on the goal?
3. ✅ Recover from errors?
4. ✅ Update its memory?
5. ✅ Know when it's done?

If yes to all, the design works.

---

**Bottom line:** Stop building for humans. Build for LLMs. Give them the structure, memory, and tools they need. Let them thrive.
