# 🧠 Using the Meta Agent Task Processor

The Meta Agent Task Processor is a flexible tool that processes natural language tasks by assigning them to specialized agents. You can run it with a single command or interact with it in different modes.

---

## 🧪 Basic Usage

Run the processor with a specific task using the `--task` or `-t` flag:

```bash
python main.py --task "Calculate 15% tip on $45.50"
```

This tells the supervising agent to process the given task by delegating it to the most suitable specialized agent.

---

## 💬 Interactive Mode

To enter an ongoing conversation-style interface where you can continuously input new tasks:

```bash
python main.py --interactive
```

This allows you to work with the system like a chatbot, testing agent behaviors or combining multiple tasks over time.

---

## 🎯 Demo Mode

To run a predefined set of example tasks that demonstrate the agent system:

```bash
python main.py --demo
```

This is useful for showcasing functionality without needing to input tasks manually.

---

## 🧠 Agent Creation Controls

By default, the supervisor agent is allowed to create new agents for tasks that don’t match existing capabilities.

### ✅ Allow new agents (default)

```bash
python main.py --task "Summarize the latest AI trends" --allow-agent-creation
```

This allows the system to dynamically generate a new agent (e.g., `summary_agent`) if none are currently suited for the task.

### ❌ Disable new agents

```bash
python main.py --task "Write me a poem" --no-create-agents
```

This forces the system to use only currently available agents and will reject or defer tasks it can't match.

---

## 🤖 Set the Model

To specify which language model the agents should use (e.g., LLaMA, GPT-style, etc.):

```bash
python main.py --task "Explain quantum entanglement" --model tinyllama
```

Replace `tinyllama` with your configured model name or API alias.

---

## 🧩 Load Specific Agents

You can preload only specific agents at startup using the `--initial-agents` flag:

```bash
python main.py --interactive --initial-agents writing_agent code_agent
```

This is useful for controlled experiments, debugging, or saving memory.

---

## 📋 Available Agents

You can load or reference any of these agents as of now:

- `fun_fact_agent`
- `math_agent`
- `research_agent`
- `writing_agent`
- `code_agent`
- `planning_agent`

---

## 🔁 Combined Example

Run an interactive session with limited agents and no agent creation:

```bash
python main.py --interactive --no-create-agents --initial-agents math_agent writing_agent
```

This will only allow math and writing agents to respond, without generating new ones.

---

## 🆘 Help

You can always view the available options with:

```bash
python main.py --help
```

---

## 🔍 Summary of Flags

| Flag                        | Description                                               |
|-----------------------------|-----------------------------------------------------------|
| `--task`, `-t`              | Run a single task and exit                                |
| `--interactive`, `-i`       | Start interactive prompt                                  |
| `--demo`, `-d`              | Run a demo with predefined tasks                          |
| `--model`, `-m`             | Specify language model (default: `tinyllama`)             |
| `--allow-agent-creation`    | Enable new agent creation (default behavior)              |
| `--no-create-agents`        | Prevent any new agents from being created                 |
| `--initial-agents`          | Specify which agents to preload (space-separated list)    |

---

Use this system to build complex agent ecosystems, test AI delegation, or simulate adaptive task routing in real-time.
