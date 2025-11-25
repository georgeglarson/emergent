# Emergent - Project Summary

## What We Built

An **LLM-first autonomous coding agent** designed around how language models actually think and operate. This agent can work independently for extended periods (hours to days) on coding tasks with minimal human intervention.

## Core Innovation

**Design for the LLM, not the human.**

Traditional coding agents are built for human convenience. This agent is built for **LLM success**:

- Persistent memory that's always in context
- Structured state management
- Reflection loops to prevent drift
- Tools optimized for LLM parsing
- Complete resumability across sessions

## Key Features

### 1. Persistent Memory System
Four markdown files that persist across sessions:
- `goals.md` - Current objectives
- `progress.md` - What's been accomplished
- `decisions.md` - Technical choices and rationale
- `blockers.md` - Current obstacles

These are **always loaded** into the LLM's context, providing continuity.

### 2. Explicit State Management
`.agent_state.json` tracks:
- Current working directory
- Files in context
- Recent actions (last 20)
- Reflection timing
- Total progress

The LLM always knows exactly where it is and what it's done.

### 3. Reflection Loops
Every 10 actions, the agent:
- Reviews recent work
- Assesses progress
- Updates memory
- Adjusts strategy

This prevents "wandering" and maintains focus.

### 4. LLM-Optimized Tools
All tools return structured JSON:
```json
{
  "success": true,
  "summary": "Human-readable summary",
  "data": {...},
  "next_suggestions": ["what to do next"]
}
```

Tools include:
- File operations (search, read, write, list)
- Command execution (with parsed output)
- Project navigation
- Memory management

### 5. Complete Resumability
Stop the agent anytime. When restarted:
- Loads all state and memory
- Reviews recent actions
- Continues from where it left off

No context lost between sessions.

## Architecture

```
emergent/
├── agent_v2.py              # Main agent with function calling
├── state_manager.py         # State and memory management
├── tools/
│   ├── file_tools.py        # File operations
│   └── command_tools.py     # Command execution
├── memory/                  # Persistent memory
│   ├── goals.md
│   ├── progress.md
│   ├── decisions.md
│   └── blockers.md
├── project/                 # Working directory
└── .agent_state.json        # Current state
```

## Proven Results

**Test Task:** "Create a Python script that calculates fibonacci numbers"

**Agent Actions:**
1. Planned implementation approach
2. Wrote `fibonacci.py` with iterative algorithm
3. Added input validation and tests
4. Verified implementation
5. Ran tests (all passed)
6. Updated memory
7. Marked goal complete

**Time:** ~15 seconds  
**Actions:** 6  
**Result:** Working, tested code

## Design Philosophy

### The Problem with Existing Tools

**Aider:** Requires manual `/add` for every file  
**OpenCode:** TUI blocks on LLM calls (TypeScript event loop)  
**Cursor:** No persistent memory across sessions  
**All:** No reflection mechanism for long tasks

### Our Solution

**Autonomous file discovery** - The agent explores the codebase itself  
**Non-blocking architecture** - Python with proper async  
**Persistent memory** - Memory files that survive restarts  
**Reflection loops** - Periodic self-assessment

### Core Insight

> The TUI isn't the feature. Autonomous file discovery is.

Users don't care about fancy interfaces. They care about not having to manually specify every file. They want the agent to **explore, understand, and act** independently.

## Why This Design Works

### For Short Tasks (minutes)
- Fast iteration
- Clear progress tracking
- Automatic verification

### For Long Tasks (hours)
- Reflection prevents drift
- Memory maintains focus
- State enables interruption/resumption

### For Very Long Tasks (days)
- Persistent memory across sessions
- Self-documenting decisions
- Blocker identification

## Technical Choices

**Language:** Python
- Fast iteration
- Best LLM SDK support
- Good subprocess handling
- Async I/O

**Memory Format:** Markdown
- Human-readable
- LLM-friendly
- Version-controllable

**Tool Output:** JSON
- Structured and parseable
- Clear success/failure
- Actionable suggestions

**State Storage:** JSON file
- Simple serialization
- Easy to inspect
- Atomic updates

## Usage

### Basic
```bash
python3.11 agent_v2.py
# Enter goal when prompted
```

### Programmatic
```python
from agent_v2 import AutonomousAgentV2

agent = AutonomousAgentV2()
agent.run(
    initial_goal="Create a REST API for user management",
    max_iterations=100
)
```

### Long-Running
```python
agent.run(
    initial_goal="Build a complete e-commerce backend",
    max_iterations=500  # Allow extended operation
)
```

## Future Enhancements

### Near-term
1. Tree-sitter for structural code editing
2. Better error recovery strategies
3. Multi-file diff preview
4. Cost tracking

### Long-term
1. Semantic code search (vector-based)
2. LSP integration for better navigation
3. Automatic git commits
4. Web search for documentation
5. Multi-agent collaboration

## Comparison Matrix

| Feature | This Agent | Aider | OpenCode | Cursor |
|---------|-----------|-------|----------|--------|
| Autonomous file discovery | ✅ | ❌ | ✅ | ✅ |
| Persistent memory | ✅ | ❌ | ❌ | ❌ |
| Reflection loops | ✅ | ❌ | ❌ | ❌ |
| Resumable sessions | ✅ | ⚠️ | ⚠️ | ✅ |
| LLM-optimized tools | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Multi-day operation | ✅ | ❌ | ❌ | ❌ |
| Non-blocking UI | ✅ | ✅ | ❌ | ✅ |

## Documentation

- **README.md** - Full documentation and design rationale
- **QUICKSTART.md** - Get started in 5 minutes
- **ARCHITECTURE.md** - Technical architecture details
- **DESIGN_INSIGHTS.md** - Deep dive into design decisions
- **example.py** - Example usage patterns

## Requirements

- Python 3.11+
- OpenAI API key
- `ripgrep` (optional, for fast search)
- `tree` (optional, for structure visualization)

## Installation

```bash
pip3 install openai
export OPENAI_API_KEY="your-key"
python3.11 agent_v2.py
```

## The Vision

**Put an LLM in a gitpod with a goal and a week. Let it thrive.**

This agent is designed for that vision:
- It maintains focus over long periods
- It documents its own decisions
- It recovers from errors
- It knows when it's done
- It can be stopped and resumed anytime

## Key Takeaway

**Stop building for humans. Build for LLMs.**

Give them:
- Explicit state they can always see
- Structured data they can parse
- Memory that persists
- Tools that guide next actions
- Reflection to prevent drift

And they will succeed.

---

## Quick Links

- [Full README](README.md)
- [Quick Start Guide](QUICKSTART.md)
- [Architecture Details](ARCHITECTURE.md)
- [Design Philosophy](DESIGN_INSIGHTS.md)
- [Example Usage](example.py)

## License

MIT - Use freely, modify as needed, contribute improvements.

---

**Built with the philosophy:** Design for how LLMs think, not how humans work.
