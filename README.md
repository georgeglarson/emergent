# Emergent

**The agent that works while you sleep.**

Built for [Venice.ai](https://venice.ai) - because when you hold Diem, your inference doesn't stop. Why should your agent?

---

## The Problem

You hold Diem at Venice.ai. You have unlimited (or very cheap) inference. But your AI coding agent stops when you close your laptop.

**What if it didn't?**

What if you could give it a goal on Monday morning, let it work all week, and check back Friday to see what it built?

That's Emergent.

---

## Philosophy

Traditional AI coding agents are built for **expensive, metered inference** (OpenAI, Anthropic). Every token costs money, so they're designed for short, supervised tasks with humans in the loop.

**Emergent is different.**

It's built for **unlimited inference environments** where the constraint isn't cost—it's **reliability**.

When inference is free, the question becomes:
> "How do we keep an agent working productively for days without human intervention?"

That's what Emergent solves.

---

## Core Features

### 1. 24/7 Autonomous Operation

Emergent is designed to run continuously for days or weeks:

- **Auto-restart** - Restarts every hour to prevent freezes
- **Loop detection** - Detects when agent is stuck repeating actions
- **Watchdog timer** - Restarts if no progress for 30 minutes
- **Progress tracking** - Monitors meaningful work, not just activity

### 2. Structured Memory System

Four markdown files that persist across restarts:

- **`goals.md`** - Current objectives
- **`progress.md`** - What's been accomplished  
- **`decisions.md`** - Technical choices and rationale
- **`blockers.md`** - Current obstacles

The agent never forgets what it's working on.

### 3. Forced Reflection Loops

Every 10 actions (or 5 with unlimited inference), the agent:
- Reviews recent work
- Assesses progress toward goals
- Updates memory with insights
- Adjusts strategy if stuck

This prevents context drift over long runs.

### 4. Complete Resumability

Stop the agent anytime. When restarted:
- Loads all state and memory
- Reviews recent actions  
- Continues from where it left off

Perfect for multi-day tasks.

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/georgeglarson/emergent.git
cd emergent

# Install dependencies
pip install -r requirements.txt

# Set your Venice API key
export VENICE_API_KEY="your-venice-key"
```

### Basic Usage

```bash
# Run for a single session
python agent_v2.py
```

When prompted, enter your goal:
```
Enter your goal: Create a REST API for a todo app
```

### Continuous Operation (24/7)

```bash
# Run for 24 hours with automatic restarts
python continuous.py "Build a documentation search engine" --hours 24
```

The agent will:
- Run for 24 hours
- Restart every ~1 hour
- Log all activity
- Track progress
- Recover from errors

### Weekend Project

```bash
# Give it the weekend
python continuous.py "Create a complete blog platform with admin panel" --hours 48
```

Come back Monday. See what it built.

---

## Why Venice.ai?

### The Economics

**OpenAI/Anthropic:**
- $0.01-0.10 per 1K tokens
- 24 hours = thousands of dollars
- Not viable for extended operation

**Venice.ai:**
- Unlimited inference (with Diem)
- 24 hours = $0 (or very cheap)
- **Actually viable** for week-long tasks

### The Use Case

**Traditional agents:** "Help me write this function"  
**Emergent:** "Build this entire project while I sleep"

**Traditional agents:** Minutes, supervised  
**Emergent:** Days, autonomous

**Traditional agents:** Expensive per-token  
**Emergent:** Unlimited inference

---

## How It Works

### The Continuous Operation Loop

```python
while time < deadline:
    # Start fresh session
    agent = EmergentAgent()
    
    # Run for ~1 hour (50 iterations)
    agent.run(goal, max_iterations=50)
    
    # Agent exits, state persists to disk
    # Memory files remain
    
    # Restart loads state, continues
    # Can't get stuck forever
```

### Reliability Features

**Loop Detection:**
```python
# Detects: action → action → action (stuck)
# Detects: A → B → A → B → A → B (alternating loop)
# Forces reflection or restart
```

**Watchdog Timer:**
```python
# No progress for 30 minutes?
# Restart the agent
# Load state, try different approach
```

**Progress Tracking:**
```python
# Files created/modified
# Tests passed
# Commands run successfully
# Real work, not just activity
```

---

## Architecture

```
emergent/
├── agent_v2.py              # Main agent (Venice API first)
├── continuous.py            # 24/7 operation runner
├── reliability.py           # Loop detection, watchdog
├── state_manager.py         # State and memory
├── tools/
│   ├── file_tools.py        # File operations
│   └── command_tools.py     # Command execution
└── memory/                  # Persistent memory
    ├── goals.md
    ├── progress.md
    ├── decisions.md
    └── blockers.md
```

---

## Use Cases

### Weekend Projects

Friday evening:
```bash
python continuous.py "Build a markdown blog generator with themes" --hours 48
```

Monday morning: Check what it built.

### Background Work

While you work on the frontend:
```bash
python continuous.py "Implement the entire backend API with auth and database" --hours 24
```

### Research Tasks

```bash
python continuous.py "Research and implement the best approach for real-time notifications" --hours 12
```

### Backlog Clearing

```bash
python continuous.py "Fix all TODOs in the codebase and add tests" --hours 72
```

---

## Comparison with Other Agents

| Feature | Emergent | Aider | Cursor | Agent Zero |
|---------|----------|-------|--------|------------|
| 24/7 operation | ✅ | ❌ | ❌ | ⚠️ |
| Auto-restart | ✅ | ❌ | ❌ | ❌ |
| Loop detection | ✅ | ❌ | ❌ | ❌ |
| Watchdog timer | ✅ | ❌ | ❌ | ❌ |
| Structured memory | ✅ | ❌ | ❌ | ⚠️ |
| Optimized for unlimited inference | ✅ | ❌ | ❌ | ⚠️ |
| Venice.ai first | ✅ | ❌ | ❌ | ❌ |

**Emergent is the only agent designed specifically for unlimited inference environments.**

---

## Configuration

### Venice API (Default)

```bash
export VENICE_API_KEY="your-key"
python agent_v2.py
```

Uses Venice's `llama-3.3-70b` model by default.

### OpenAI (Fallback)

```bash
export OPENAI_API_KEY="your-key"
# Don't set VENICE_API_KEY
python agent_v2.py
```

Falls back to OpenAI's `gpt-4.1-mini` if Venice key not found.

### Continuous Operation Settings

```bash
python continuous.py "your goal" \
  --hours 24 \              # How long to run
  --session-iterations 50 \ # Actions per session
  --session-timeout 3600    # Max time per session (seconds)
```

---

## Monitoring

### Real-time Logs

```bash
tail -f continuous_operation.log
```

### Progress Stats

```bash
cat operation_stats.json
```

Shows:
- Sessions completed
- Total actions taken
- Files created/modified
- Tests passed
- Errors encountered

---

## Who Is This For?

**Emergent makes sense if you have:**
- ✅ Access to Venice.ai with Diem
- ✅ Unlimited or very cheap inference
- ✅ Tasks that take days, not minutes
- ✅ Tolerance for autonomous operation

**Emergent probably doesn't make sense if:**
- ❌ You're paying OpenAI/Anthropic per-token
- ❌ You need immediate, supervised results
- ❌ You have limited API budgets

**Emergent is a tool for the post-scarcity inference world.**

---

## Roadmap

### v0.2 (Current)
- [x] Venice.ai API integration
- [x] 24/7 continuous operation
- [x] Auto-restart logic
- [x] Loop detection
- [x] Watchdog timer
- [x] Progress tracking

### v0.3 (Next)
- [ ] Tree-sitter for structural code editing
- [ ] Better error recovery strategies
- [ ] Multi-file diff preview
- [ ] Cost tracking (even for unlimited)
- [ ] Web dashboard for monitoring

### v0.4 (Future)
- [ ] Semantic code search
- [ ] LSP integration
- [ ] Automatic git commits
- [ ] Multi-agent collaboration

---

## Contributing

Emergent is designed to be simple and hackable. Contributions welcome!

**Areas for contribution:**
- Venice model optimizations
- Better reliability strategies
- Monitoring and observability
- Documentation and examples

---

## License

MIT - Use freely, modify as needed, contribute improvements.

---

## The Vision

> "You hold Diem at Venice.ai. Your inference doesn't stop. Why should your agent?"

**Give Emergent a goal and a week. Let it work while you sleep. Check back to see what emerged.**

---

**Emergent** - Built for the post-scarcity inference world.

🌐 [Venice.ai](https://venice.ai) | 📦 [GitHub](https://github.com/georgeglarson/emergent)
