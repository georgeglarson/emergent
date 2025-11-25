# Quick Start Guide

Get the Emergent running in 5 minutes.

## Prerequisites

```bash
# Ensure Python 3.11+ is installed
python3.11 --version

# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Optional but recommended
sudo apt install ripgrep tree
```

## Installation

```bash
# Clone or copy the emergent directory
cd emergent

# Install OpenAI SDK
pip3 install openai
```

## Run Your First Task

```bash
python3.11 agent_v2.py
```

When prompted, enter a goal:
```
Create a Python script that prints "Hello, World!"
```

Watch the agent work autonomously!

## Example Goals

### Simple Tasks (1-5 minutes)
- "Create a Python script that calculates factorial"
- "Write a function to reverse a string"
- "Create a simple calculator script"

### Medium Tasks (5-15 minutes)
- "Create a REST API with Flask for managing todos"
- "Build a CLI tool for file encryption/decryption"
- "Create a web scraper for news headlines"

### Complex Tasks (15+ minutes)
- "Build a full CRUD application with database"
- "Create a multi-file Python package with tests"
- "Implement a simple web server from scratch"

## Understanding the Output

```
🤖 Autonomous Agent V2 Starting...
============================================================
🎯 Goal set: [your goal]

Iteration 1/20
============================================================
💭 Thinking...              # Agent is reasoning
🔧 Calling: write_file      # Agent is using a tool
   ✓ Wrote hello.py         # Tool succeeded

Iteration 2/20
🔧 Calling: run_command
   ✓ Tests passed

✅ Goal Complete: [summary]
```

## Checking Results

After the agent completes:

```bash
# View the created code
ls -la project/

# Check what the agent did
cat memory/progress.md

# See decisions made
cat memory/decisions.md

# View full state
cat .agent_state.json
```

## Resuming Work

The agent saves state automatically. To resume:

```bash
# Just run again - it will load previous state
python3.11 agent_v2.py
```

Enter a new goal or continue from where it left off.

## Interrupting the Agent

Press `Ctrl+C` to stop the agent gracefully. State is saved automatically.

## Troubleshooting

### "Module not found: openai"
```bash
pip3 install openai
```

### "ripgrep not found"
The agent will still work, but file search will be slower. Install with:
```bash
sudo apt install ripgrep
```

### Agent seems stuck
- Press `Ctrl+C` to stop
- Check `memory/blockers.md` to see what it's struggling with
- Adjust the goal to be more specific

### Token limit errors
- Reduce `max_iterations` parameter
- Clear old state: `rm .agent_state.json`

## Programmatic Usage

```python
from agent_v2 import AutonomousAgentV2

# Create agent
agent = AutonomousAgentV2(workspace_path="/path/to/workspace")

# Run with goal
agent.run(
    initial_goal="Create a web server",
    max_iterations=50  # Adjust based on task complexity
)
```

## Next Steps

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the design
2. Read [README.md](README.md) for full documentation
3. Try increasingly complex goals
4. Experiment with multi-day tasks

## Tips for Success

**Write clear goals:**
- ✅ "Create a Flask API with user authentication"
- ❌ "Make a website"

**Be specific about requirements:**
- ✅ "Create a Python script with tests that validates email addresses"
- ❌ "Write some code"

**Let it work:**
- The agent is designed to be autonomous
- Don't interrupt unless necessary
- Check memory files to see its thinking

**Start small:**
- Test with simple tasks first
- Gradually increase complexity
- Learn what works best

## Advanced: Long-Running Tasks

For tasks that take hours or days:

```python
agent = AutonomousAgentV2()
agent.run(
    initial_goal="Build a complete e-commerce backend with tests",
    max_iterations=500  # Allow many iterations
)
```

The agent will:
- Work through the task step by step
- Reflect every 10 actions
- Update memory with progress
- Handle errors gracefully
- Save state continuously

You can stop and resume anytime without losing context.

---

**Ready to go?** Run `python3.11 agent_v2.py` and give it a goal!
