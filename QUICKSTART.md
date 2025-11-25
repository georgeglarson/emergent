# Emergent - Quick Start

Get Emergent running in 5 minutes.

---

## Prerequisites

- Python 3.11+
- Venice.ai account with Diem (or OpenAI API key as fallback)
- Basic command line knowledge

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/georgeglarson/emergent.git
cd emergent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set API Key

**For Venice.ai (recommended):**
```bash
export VENICE_API_KEY="your-venice-api-key"
```

**For OpenAI (fallback):**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

---

## Basic Usage

### Single Session

Run the agent for a single task:

```bash
python agent_v2.py
```

When prompted, enter your goal:
```
Enter your goal: Create a Python script that generates fibonacci numbers
```

The agent will work autonomously until complete.

---

## 24/7 Operation

### Run for 24 Hours

```bash
python continuous.py "Build a REST API for a todo app" --hours 24
```

This will:
- Run for 24 hours
- Restart every ~1 hour automatically
- Log all activity to `continuous_operation.log`
- Save stats to `operation_stats.json`

### Run for a Weekend

```bash
python continuous.py "Create a blog platform with admin panel" --hours 48
```

Give it Friday evening, check back Monday morning.

### Run for a Week

```bash
python continuous.py "Build a complete documentation search engine" --hours 168
```

Yes, really. Let it run all week.

---

## Monitoring

### Watch Live Logs

```bash
tail -f continuous_operation.log
```

### Check Progress

```bash
cat operation_stats.json
```

Shows:
- Sessions completed
- Total actions
- Files created
- Tests passed

### Check Memory

```bash
cat memory/progress.md
cat memory/decisions.md
```

See what the agent is thinking.

---

## Examples

### Example 1: Quick Script

```bash
python agent_v2.py
# Goal: Create a Python script that fetches weather data from an API
```

**Expected time:** 10-20 minutes

---

### Example 2: Web API

```bash
python continuous.py "Build a Flask API with user authentication" --hours 6
```

**Expected time:** 6 hours

---

### Example 3: Full Project

```bash
python continuous.py "Create a markdown-based wiki with search and tagging" --hours 48
```

**Expected time:** 48 hours (weekend project)

---

## Configuration

### Adjust Session Length

```bash
python continuous.py "your goal" \
  --session-iterations 100  # More iterations per session
```

### Adjust Timeout

```bash
python continuous.py "your goal" \
  --session-timeout 7200  # 2 hours per session
```

### Custom Workspace

```bash
python continuous.py "your goal" \
  --workspace /path/to/workspace
```

---

## Stopping the Agent

### Graceful Stop

Press `Ctrl+C` once. The agent will:
- Finish current action
- Save state
- Exit cleanly

### Force Stop

Press `Ctrl+C` twice for immediate exit.

**State is always saved**, so you can resume anytime.

---

## Resuming

The agent automatically resumes from where it left off:

```bash
# Run for 12 hours
python continuous.py "Build API" --hours 12

# Stop it (Ctrl+C)

# Resume later - it continues from memory
python continuous.py "Build API" --hours 12
```

No need to repeat the goal - it's in `memory/goals.md`.

---

## Troubleshooting

### "No module named 'openai'"

```bash
pip install openai
```

### "VENICE_API_KEY not found"

```bash
export VENICE_API_KEY="your-key"
```

Or use OpenAI:
```bash
export OPENAI_API_KEY="your-key"
```

### Agent seems stuck

Check the logs:
```bash
tail -f continuous_operation.log
```

The auto-restart will kick in within 30 minutes if truly stuck.

### Want to start fresh

```bash
rm .agent_state.json
rm memory/*.md
```

This clears all state and memory.

---

## Next Steps

- Read the full [README](README.md) for architecture details
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical deep dive
- Read [DESIGN_INSIGHTS.md](DESIGN_INSIGHTS.md) for philosophy

---

## The Core Idea

**Traditional agents:** Help you write code (minutes, supervised)

**Emergent:** Write code for you (days, autonomous)

**Give it a goal. Let it work while you sleep. Check back to see what emerged.**

---

Built for [Venice.ai](https://venice.ai) - Because your inference doesn't stop. Why should your agent?
