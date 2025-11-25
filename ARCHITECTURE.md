# Autonomous Agent Architecture

## Design Philosophy

This agent is designed **LLM-first** - optimized for how language models actually perceive, reason, and operate, not for human convenience.

## Core Principles

1. **Persistent Memory** - The agent maintains structured memory files that are always in context
2. **Explicit State** - Current position, open files, and recent changes are always visible
3. **Reflection Loops** - Periodic self-assessment to combat context drift
4. **Structured Output** - Tools return LLM-friendly JSON, not human logs
5. **Self-Organization** - The agent creates and maintains its own workspace structure
6. **Immediate Feedback** - Actions have visible consequences (tests, diffs, validation)

## Workspace Structure

```
emergent/
├── memory/                 # Persistent memory (always in context)
│   ├── goals.md           # Current objectives and success criteria
│   ├── progress.md        # What has been accomplished
│   ├── decisions.md       # Key decisions and rationale
│   └── blockers.md        # Current obstacles and challenges
├── project/               # The actual codebase being worked on
├── scratch/               # Temporary experiments and tests
├── notes/                 # Understanding and documentation
├── plans/                 # Structured plans and next steps
├── .agent_state.json      # Current state (files, context, position)
└── tools/                 # Agent tools and utilities
```

## State Management

The agent maintains a `.agent_state.json` file with:
- Current working directory
- Files currently in context
- Recent actions (last 20)
- Current phase of work
- Token usage tracking
- Last reflection timestamp

This state is **always** loaded at the start of each iteration.

## Memory System

Four core memory files that persist across sessions:

### goals.md
- Primary objective
- Success criteria
- Constraints and requirements
- Current focus area

### progress.md
- Completed tasks
- Working features
- Test results
- Milestones reached

### decisions.md
- Technical choices made
- Alternatives considered
- Rationale for decisions
- Lessons learned

### blockers.md
- Current obstacles
- Failed approaches
- Missing information
- Questions to resolve

## Agent Loop

```python
while not done:
    # 1. Load state and memory
    state = load_state()
    memory = load_memory()
    
    # 2. Build context (state + memory always included)
    context = build_context(state, memory)
    
    # 3. LLM decides next action
    action = llm_decide(context)
    
    # 4. Execute action with tools
    result = execute_tool(action)
    
    # 5. Update state
    state.add_action(action, result)
    save_state(state)
    
    # 6. Reflection check (every N actions)
    if state.actions_since_reflection >= 10:
        reflect_and_summarize()
        update_memory()
    
    # 7. Check if goal achieved
    done = check_completion()
```

## Tool Design

All tools return **structured JSON** optimized for LLM parsing:

```json
{
  "success": true,
  "summary": "Found 3 matches",
  "data": {
    "matches": [
      {"file": "auth.rs", "line": 45, "context": "..."}
    ]
  },
  "next_suggestions": ["Read auth.rs", "Check imports"]
}
```

## Core Tools

1. **search_files** - Ripgrep-based code search with structured results
2. **read_file** - Read with syntax highlighting and structure info
3. **edit_file** - Apply diffs with validation and rollback
4. **run_command** - Execute with parsed output and error handling
5. **analyze_structure** - Get project overview (tree-sitter or LSP)
6. **update_memory** - Write to memory files
7. **create_plan** - Generate structured action plans

## Reflection System

Every 10 actions, the agent:
1. Reviews recent actions and results
2. Summarizes progress toward goal
3. Updates memory files
4. Identifies blockers
5. Adjusts strategy if needed

This prevents the agent from "wandering" or forgetting its purpose.

## Resumability

The agent can be stopped and restarted at any time. On restart:
1. Load `.agent_state.json`
2. Read all memory files
3. Review last N actions
4. Continue from where it left off

No context is lost between sessions.

## Token Management

- State file: ~500 tokens
- Memory files: ~2000 tokens
- Recent actions: ~1000 tokens
- Tool outputs: ~2000 tokens
- Leaves ~90k tokens for reasoning (with 100k context models)

## Success Criteria

The agent succeeds if:
1. It can work autonomously for hours/days
2. It makes consistent progress toward goals
3. It recovers from errors gracefully
4. It maintains coherent memory across sessions
5. It knows when to ask for help (blockers.md)
