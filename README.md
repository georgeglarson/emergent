# Emergent

**The agent that builds itself**

Emergent is an LLM-first autonomous coding agent designed around how language models actually think and operate. Unlike traditional agents with predefined tools and fixed architectures, Emergent starts with simple markdown files and the ability to write code. It builds the tools it needs, when it needs them.

Give Emergent a goal and a week. Watch it build its own infrastructure.

---

## Philosophy

**Complexity from simplicity.** Emergent embodies the principle that sophisticated behavior can arise from simple foundations.

Most AI coding agents come with elaborate tool suites and rigid frameworks. Emergent takes a different approach:

- **Start simple** - Four markdown files and basic file operations
- **Grow organically** - Agent creates tools as requirements emerge
- **Self-optimize** - Agent improves its own infrastructure over time
- **Everything is a file** - Following the Unix philosophy

When Emergent needs vector search, it builds Qdrant integration. When it needs optimization, it writes the code. The agent doesn't just use tools—it creates them.

---

## Core Innovation

### 1. Structured Memory System

Four markdown files that persist across sessions:

- **`goals.md`** - Current objectives
- **`progress.md`** - What's been accomplished  
- **`decisions.md`** - Technical choices and rationale
- **`blockers.md`** - Current obstacles

These files are always loaded into the LLM's context, providing continuity and focus.

### 2. Forced Reflection Loops

Every 10 actions, the agent:
- Reviews recent work
- Assesses progress toward goals
- Updates memory with insights
- Adjusts strategy if needed

This prevents context drift and maintains focus over extended runs.

### 3. LLM-Optimized Tool Responses

All tools return structured JSON:

```json
{
  "success": true,
  "summary": "Human-readable summary",
  "data": {...},
  "next_suggestions": ["what to do next"]
}
```

Tools guide the agent toward the next logical action.

### 4. Complete Resumability

Stop the agent anytime. When restarted:
- Loads all state and memory
- Reviews recent actions  
- Continues from where it left off

No context lost between sessions. Perfect for multi-day tasks.

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/emergent.git
cd emergent

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"
```

### Basic Usage

```bash
# Run the agent
python agent_v2.py
```

When prompted, enter your goal:
```
Enter your goal: Create a Python script that calculates fibonacci numbers
```

The agent will work autonomously until the goal is complete.

### Programmatic Usage

```python
from agent_v2 import AutonomousAgentV2

agent = AutonomousAgentV2()
agent.run(
    initial_goal="Build a REST API for user management",
    max_iterations=100
)
```

### Long-Running Tasks

```python
agent.run(
    initial_goal="Create a complete documentation search engine with vector embeddings",
    max_iterations=500  # Allow extended operation
)
```

---

## How It Works

### The Agent Loop

1. **Load context** - State and memory files
2. **Think** - LLM decides next action
3. **Act** - Execute tool via function calling
4. **Record** - Update state and memory
5. **Reflect** - Every 10 actions, assess progress
6. **Repeat** - Until goal complete

### Memory Evolution

**Day 1:** Simple file-based memory
- Four markdown files
- grep for search
- Works perfectly

**Day 3:** Agent realizes limitations
- "I have 500 code examples"
- "grep is too slow"
- Agent writes Qdrant integration

**Day 5:** Agent optimizes
- "Keep recent actions in markdown"
- "Use Qdrant for long-term knowledge"
- Agent creates hybrid system

**You don't design this upfront. The agent evolves it.**

---

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

### Key Components

**State Manager** - Handles persistent state and memory files
- Loads/saves agent state
- Manages memory files
- Tracks reflection timing

**File Tools** - LLM-optimized file operations
- Search files (ripgrep integration)
- Read/write files
- List directory contents
- Get project structure

**Command Tools** - Execute shell commands with error analysis
- Run commands with timeout
- Parse output and errors
- Provide actionable suggestions

---

## Design Philosophy

### For the LLM, Not the Human

Traditional coding agents are built for human convenience. Emergent is built for **LLM success**.

**What LLMs need:**
- Explicit state they can always see
- Structured data they can parse
- Memory that persists
- Tools that guide next actions
- Reflection to prevent drift

**What Emergent provides:**
- `.agent_state.json` - Always visible state
- Structured JSON responses - Easy to parse
- Markdown memory files - Persistent and readable
- `next_suggestions` in tool output - Guidance
- Forced reflection loops - Self-correction

### Everything is a File

Following the Unix philosophy, Emergent treats memory as files:

**Benefits:**
- Agent can read its own memory (`cat memory/goals.md`)
- Agent can write its own memory (just write text)
- Human-readable debugging (no vector space visualization)
- Version controllable (`git log memory/decisions.md`)

**When files aren't enough:**
The agent writes code to build better tools. It's not using your pre-built memory system—it's using files, and it can evolve them into whatever it needs.

### Start Simple, Grow Smart

Don't pre-build elaborate infrastructure. Start with the simplest thing that works:
- Four markdown files
- `.agent_state.json`
- grep for search

When that breaks, the agent has the tools to fix it:
- Can write Python code
- Can install packages
- Can create new tools
- Can refactor its own memory system

**The agent owns its infrastructure.**

---

## Comparison with Other Agents

| Feature | Emergent | Agent Zero | Aider | Cursor |
|---------|----------|------------|-------|--------|
| Autonomous file discovery | ✅ | ✅ | ❌ | ✅ |
| Structured memory | ✅ | ⚠️ | ❌ | ❌ |
| Reflection loops | ✅ | ❌ | ❌ | ❌ |
| Resumable sessions | ✅ | ⚠️ | ⚠️ | ✅ |
| LLM-optimized tools | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Multi-day operation | ✅ | ⚠️ | ❌ | ❌ |
| Self-evolving tools | ✅ | ✅ | ❌ | ❌ |

### What Makes Emergent Different

**Agent Zero:** General-purpose framework with multi-agent hierarchy. Emergent is focused on extended autonomous operation with structured memory.

**Aider:** Requires manual `/add` for every file. Emergent explores the codebase autonomously.

**Cursor:** No persistent memory across sessions. Emergent maintains continuity over days.

**All others:** No explicit reflection mechanism. Emergent forces self-assessment every 10 actions.

---

## Use Cases

### Development Projects
```
Goal: "Create a React dashboard with real-time data visualization"
```
Emergent will plan the architecture, write components, set up state management, and create the dashboard.

### Data Analysis
```
Goal: "Analyze Q3 sales data and create trend reports with visualizations"
```
Emergent will load data, perform analysis, generate insights, and create reports.

### System Administration
```
Goal: "Set up a monitoring system for web servers with alerting"
```
Emergent will research solutions, write configuration, set up monitoring, and test alerts.

### Research Tasks
```
Goal: "Gather and summarize recent AI papers about chain-of-thought prompting"
```
Emergent will search, read papers, extract insights, and create comprehensive summaries.

---

## Tested Example

Emergent successfully completed this task autonomously:

**Goal:** "Create a Python script that calculates fibonacci numbers"

**Actions Taken:**
1. Updated decisions memory with implementation approach
2. Wrote `fibonacci.py` with iterative implementation
3. Included input validation and test function
4. Read the file to verify
5. Ran tests to confirm correctness
6. Updated progress memory
7. Marked goal as complete

**Result:** Working fibonacci calculator in 6 actions, ~15 seconds.

---

## Advanced Features

### Custom System Prompts

Modify the system prompt in `agent_v2.py` to change behavior:

```python
def _get_system_prompt(self) -> str:
    return """You are an autonomous coding agent...
    
    [Your custom instructions here]
    """
```

### Tool Extension

Add new tools by:
1. Creating tool implementation in `tools/`
2. Adding tool schema to `tools_schema` in `agent_v2.py`
3. Adding execution logic to `_execute_tool()`

### Memory Customization

Add new memory files:
1. Create file in `memory/` directory
2. Update `StateManager` to load/save it
3. Include in context summary

---

## Requirements

- Python 3.11+
- OpenAI API key
- `ripgrep` (optional, for fast file search)
- `tree` (optional, for structure visualization)

---

## Roadmap

### Near-term
- [ ] Tree-sitter integration for structural code editing
- [ ] Better error recovery strategies
- [ ] Multi-file diff preview before applying changes
- [ ] Cost tracking and optimization

### Long-term
- [ ] Semantic code search (vector-based)
- [ ] LSP integration for better navigation
- [ ] Automatic git commits with meaningful messages
- [ ] Web search for documentation lookup
- [ ] Multi-agent collaboration

---

## Contributing

Emergent is designed to be simple and hackable. Contributions are welcome!

**Areas for contribution:**
- New tool implementations
- Memory system improvements
- Reflection strategy refinements
- Documentation and examples
- Testing and benchmarking

---

## License

MIT - Use freely, modify as needed, contribute improvements.

---

## Philosophy in Practice

> "Most AI agents come with pre-built tools and fixed architectures. Emergent starts with nothing but markdown files and the ability to write code. It builds the tools it needs, when it needs them. Vector databases, optimization systems, custom workflows—they emerge from the task requirements, not from pre-planning."

> "Give Emergent a goal and a week. Watch it build its own infrastructure."

---

**Built with the philosophy:** Design for how LLMs think, not how humans work.

**Emergent** - Complexity from simplicity.
