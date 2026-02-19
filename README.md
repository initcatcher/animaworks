# AnimaWorks

**Organization-as-Code for LLM Agents**

AnimaWorks treats AI agents not as tools, but as autonomous members of an organization. Each agent (called a "Digital Anima") has its own persistent identity, private memory, and communication channels. They operate autonomously on their own schedules, collaborating through message-passing — the same way human organizations work.

> *Imperfect individuals collaborating through structure outperform any single omniscient actor.*

**[日本語版 README はこちら](README_ja.md)**

## Core Principles

- **Encapsulation** — Each Anima's internal thoughts and memories are invisible to others. Communication happens only through text messages.
- **Library-style Memory** — Instead of cramming context into prompts, agents search their own memory archives when they need to remember something.
- **Autonomy** — Agents don't wait for instructions. They run on their own clocks (heartbeats and cron schedules) and make decisions based on their own values.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│            Digital Anima: (Alice)                     │
├──────────────────────────────────────────────────────┤
│  Identity ────── Who I am (persistent)               │
│  Agent Core ──── 4 execution modes                   │
│    ├ A1: Claude Agent SDK (Claude models)             │
│    ├ A1 Fallback: Anthropic SDK (when SDK missing)    │
│    ├ A2: LiteLLM + tool_use (GPT-4o, Gemini, etc.)   │
│    └ B:  LiteLLM text-based tool loop (Ollama, etc.)   │
│  Memory ──────── Library-style, self-directed recall  │
│  Boards ──────── Slack-style shared channels          │
│  Permissions ─── Tool/file/command restrictions       │
│  Communication ─ Text + file references               │
│  Lifecycle ───── Message / heartbeat / cron           │
│  Injection ───── Role / values / behavioral rules     │
└──────────────────────────────────────────────────────┘
```

## Neuroscience-Inspired Memory System

Most AI agent frameworks truncate memory to fit the context window — leaving agents with something resembling amnesia. AnimaWorks takes a different approach: agents maintain a persistent memory archive and **search it when they need to remember**, the way humans retrieve information from long-term storage.

| Directory | Neuroscience Model | Contents |
|---|---|---|
| `episodes/` | Episodic memory | Daily activity logs |
| `knowledge/` | Semantic memory | Lessons, rules, learned knowledge |
| `procedures/` | Procedural memory | Step-by-step workflows |
| `state/` | Working memory | Current tasks, pending items |
| `shortterm/` | Short-term memory | Session continuity (context carry-over) |
| `activity_log/` | Unified activity log | All interactions as JSONL timeline |

### Memory Lifecycle

- **Priming** — 4-channel parallel memory retrieval automatically injected into system prompts (sender profile, recent activity, related knowledge, skill matching)
- **Consolidation** — Daily (episodic → semantic, NREM-sleep analog) and weekly (knowledge merge + episode compression)
- **Forgetting** — 3-stage active forgetting based on the synaptic homeostasis hypothesis:
  1. Synaptic downscaling (daily): mark low-access chunks
  2. Neurogenesis reorganization (weekly): merge similar low-activity chunks
  3. Complete forgetting (monthly): archive and remove inactive chunks

## Quick Start

### Step 1: Install

If you have [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed, **no API key configuration is needed**. Claude Code handles authentication on its own.

```bash
git clone https://github.com/xuiltul/animaworks.git
cd animaworks
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Step 2: Initialize & Start

```bash
animaworks init    # Opens setup wizard in your browser
animaworks start   # Start server
```

### Step 3: Setup Wizard (in your browser)

`animaworks init` opens a setup wizard at http://localhost:18500/setup/ that walks you through:

1. **Language** — Choose your preferred language (17 supported)
2. **User Info** — Set your username and display name
3. **AI Provider** — Select your LLM provider and enter API keys (or just select Claude Code — no key needed)
4. **Leader** — Name your first Anima (your organization's leader)
5. **Confirm** — Review and finish

### Step 4: Open the Dashboard

Once setup is complete and the server is running, open http://localhost:18500/ — your Anima is ready. Click on it to start chatting.

**That's the entire setup.** Everything from here on happens in the browser.

### Alternative: Direct API Access

If you don't have Claude Code, or want to use other LLM providers (GPT-4o, Gemini, Ollama, etc.):

```bash
cp .env.example .env
# Edit .env — at minimum, set ANTHROPIC_API_KEY for Claude models
```

See [API Key Reference](#api-key-reference) below for details.

## Web UI

After `animaworks start`, everything happens in the browser. No CLI needed.

### Dashboard (`http://localhost:18500/`)

- **Home** — System overview, Anima status cards with avatars, recent activity timeline
- **Chat** — Full conversation with any Anima (streaming responses, image attachments, conversation history)
- **Board** — Slack-style shared channels (#general, #ops, etc.) and DM history between Animas
- **Animas** — Detailed view of each Anima's identity, current state, pending tasks, memory statistics
- **Activity** — Full activity timeline with filtering
- **Memory** — Browse any Anima's memory files (episodes, knowledge, procedures)
- **Logs** — Real-time server and Anima logs
- **Settings** — Configuration, API key status, authentication management

### Workspace (`http://localhost:18500/workspace/`)

An interactive 3D office where your Animas work as visible characters:

- Characters sit at desks, walk around, and interact with each other in real time
- Visual states reflect what each Anima is doing (idle, working, thinking, talking, sleeping)
- Message bubbles appear when Animas communicate with each other
- Click any character to open a chat overlay with live expression changes
- Activity timeline shows all events as they happen

## Build Your Team

Your first Anima (the leader) can **hire new team members for you**. Just tell it what kind of people you need:

> "I'd like to hire a researcher who monitors industry trends, and an engineer who manages our infrastructure."

The leader Anima will create new team members with appropriate roles, personalities, and reporting structure — all through conversation. No CLI commands needed.

The leader can also **manage the team**: enable/disable members, restart processes, and assign tasks — all through the chat interface.

### How It Works Autonomously

Once your team is set up, they work on their own:

- **Heartbeats** — Periodic self-checks where each Anima reviews tasks, reads shared channels, and decides what to do next
- **Cron tasks** — Scheduled jobs defined per Anima
- **Memory consolidation** — Every night, episodes are distilled into knowledge (like sleep-time learning)
- **Communication** — Animas coordinate through shared Board channels and direct messages

## Image Generation

AnimaWorks can automatically generate character portraits and 3D models for your Animas. This gives each agent a visual identity in the Dashboard and the 3D Workspace.

### How It Works

1. When a new Anima is created, the **Asset Reconciler** reads the character's identity and generates an image prompt using an LLM
2. The image is generated via the configured service and saved to `~/.animaworks/animas/{name}/assets/`
3. If the Anima has a supervisor with an existing portrait, **Vibe Transfer** automatically applies the supervisor's art style — so your whole team looks visually consistent
4. 3D models can be generated from the 2D portrait for the interactive 3D Workspace

### Setup

Set the API key(s) for your preferred service in `.env`:

```bash
# Recommended for anime-style character art:
NOVELAI_API_TOKEN=pst-...

# For Flux-based generation:
FAL_KEY=...

# For 3D models in the Workspace:
MESHY_API_KEY=...
```

Without any image generation keys configured, Animas work perfectly fine — they just won't have visual avatars.

## API Key Reference

**Mode A1 (Claude Code) requires no API keys.** The keys below are only needed for alternative modes and optional features.

### LLM Providers

| Key | Service | Mode | Get it at |
|-----|---------|------|-----------|
| *(none needed)* | Claude Code | A1 | [docs.anthropic.com/en/docs/claude-code](https://docs.anthropic.com/en/docs/claude-code) |
| `ANTHROPIC_API_KEY` | Anthropic API | A1 Fallback / A2 | [console.anthropic.com](https://console.anthropic.com/) |
| `OPENAI_API_KEY` | OpenAI | A2 | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `GOOGLE_API_KEY` | Google AI | A2 | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

### Image Generation (Optional)

| Key | Service | What it generates | Get it at |
|-----|---------|-------------------|-----------|
| `NOVELAI_API_TOKEN` | NovelAI | Anime-style character portraits | [novelai.net](https://novelai.net/) → Settings > Account > API |
| `FAL_KEY` | fal.ai (Flux) | Stylized / photorealistic images | [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys) |
| `MESHY_API_KEY` | Meshy | 3D character models (GLB) | [meshy.ai](https://www.meshy.ai/) → Dashboard > API Keys |

### External Integrations (Optional)

| Key | Service | Get it at |
|-----|---------|-----------|
| `SLACK_BOT_TOKEN` | Slack | See [Slack setup guide](docs/slack-socket-mode-setup.md) |
| `SLACK_APP_TOKEN` | Slack Socket Mode | See [Slack setup guide](docs/slack-socket-mode-setup.md) |
| `CHATWORK_API_TOKEN` | Chatwork | [chatwork.com](https://www.chatwork.com/) → Settings > API Token |
| `OLLAMA_SERVERS` | Ollama (local LLM) | Default: `http://localhost:11434` |

## Execution Modes

Each Anima can use a different LLM model and execution mode. Set via `config.json` per Anima.

| Mode | Engine | Target Models | Tools |
|------|--------|--------------|-------|
| A1 | Claude Agent SDK | Claude models | Read/Write/Edit/Bash/Grep/Glob |
| A1 Fallback | Anthropic SDK | Claude (when Agent SDK unavailable) | search_memory, read/write_file, etc. |
| A2 | LiteLLM + tool_use | GPT-4o, Gemini, etc. | search_memory, read/write_file, execute_command, etc. |
| B | LiteLLM text-based tool loop | Ollama, etc. | Pseudo tool calls (text-parsed JSON) |

Mode is determined automatically from the model name. You can also override it in `config.json` under `model_modes`.

## Hierarchy & Roles

- Hierarchy is defined by a single `supervisor` field. No supervisor = top-level.
- Role templates apply specialized prompts, permissions, and defaults:

| Role | Default Model | Description |
|------|--------------|-------------|
| `engineer` | Opus | Complex reasoning, code generation |
| `manager` | Opus | Coordination, decision-making |
| `writer` | Sonnet | Content creation |
| `researcher` | Haiku | Information gathering |
| `ops` | Local model | Log monitoring, routine tasks |
| `general` | Sonnet | General-purpose |

- All communication (directives, reports, coordination) flows through async messaging via Messenger.
- Each Anima runs as an isolated subprocess managed by ProcessSupervisor, communicating via Unix Domain Sockets.

## CLI Reference (Advanced)

The CLI is available for power users and automation. After initial setup, day-to-day use is through the Web UI.

### Server Management

| Command | Description |
|---|---|
| `animaworks start [--host HOST] [--port PORT]` | Start server (default: `0.0.0.0:18500`) |
| `animaworks stop` | Stop server (graceful shutdown) |
| `animaworks restart [--host HOST] [--port PORT]` | Restart server |

### Initialization

| Command | Description |
|---|---|
| `animaworks init` | Initialize runtime directory (interactive setup) |
| `animaworks init --force` | Merge template updates (preserves existing data) |
| `animaworks reset [--restart]` | Reset runtime directory |

### Anima Management

| Command | Description |
|---|---|
| `animaworks create-anima [--from-md PATH] [--role ROLE] [--name NAME]` | Create new Anima from character sheet |
| `animaworks anima status [ANIMA]` | Show Anima process status |
| `animaworks anima restart ANIMA` | Restart Anima process |
| `animaworks list` | List all Animas |

### Communication

| Command | Description |
|---|---|
| `animaworks chat ANIMA "message" [--from NAME]` | Send message to Anima |
| `animaworks send FROM TO "message"` | Send message between Animas |
| `animaworks heartbeat ANIMA` | Manually trigger heartbeat |

### Configuration & Diagnostics

| Command | Description |
|---|---|
| `animaworks config list [--section SECTION]` | Show configuration |
| `animaworks config get KEY` | Get config value (dot notation: `system.mode`) |
| `animaworks config set KEY VALUE` | Set config value |
| `animaworks status` | Show system status |
| `animaworks logs [ANIMA] [--lines N]` | View logs |

## Tech Stack

| Component | Technology |
|---|---|
| Agent execution | Claude Agent SDK / Anthropic SDK / LiteLLM |
| LLM providers | Anthropic, OpenAI, Google, Ollama (via LiteLLM) |
| Web framework | FastAPI + Uvicorn |
| Task scheduling | APScheduler |
| Configuration | Pydantic + JSON + Markdown |
| Memory / RAG | ChromaDB + sentence-transformers |
| Graph activation | NetworkX (spreading activation + PageRank) |
| Human notification | Slack, Chatwork, LINE, Telegram, ntfy |
| External messaging | Slack Socket Mode, Chatwork Webhook |
| Image generation | NovelAI, fal.ai (Flux), Meshy (3D) |

## Project Structure

```
animaworks/
├── main.py              # CLI entry point
├── core/                # Digital Anima core engine
│   ├── anima.py         #   Encapsulated persona class
│   ├── agent.py         #   Execution mode selection & cycle management
│   ├── anima_factory.py #   Anima creation (template/blank/markdown)
│   ├── memory/          #   Memory subsystem
│   │   ├── manager.py   #     Library-style search & write
│   │   ├── priming.py   #     Auto-recall layer (4-channel parallel)
│   │   ├── consolidation.py #  Memory consolidation (daily/weekly)
│   │   ├── forgetting.py #    Active forgetting (3-stage)
│   │   └── rag/         #     RAG engine (ChromaDB + embeddings)
│   ├── execution/       #   Execution engines (A1/A1F/A2/B)
│   ├── tooling/         #   Tool dispatch & permissions
│   ├── prompt/          #   System prompt builder (24 sections)
│   ├── supervisor/      #   Process isolation (Unix sockets)
│   └── tools/           #   External tool implementations
├── cli/                 # CLI package (argparse + subcommands)
├── server/              # FastAPI server + Web UI
│   ├── routes/          #   API routes (domain-split)
│   └── static/          #   Dashboard + Workspace UI
└── templates/           # Default configs & prompt templates
    ├── roles/           #   Role templates (6 roles)
    └── anima_templates/ #   Anima skeletons
```

## About the Author

AnimaWorks is built by a psychiatrist and serial entrepreneur who has been programming since childhood and running real organizations for over a decade.

The core insight — that imperfect individuals collaborating through structure outperform any single omniscient actor — comes from two parallel careers: treating patients who taught him that no mind is complete on its own, and building companies where the right org chart matters more than any individual hire.

## Documentation

| Document | Description |
|----------|-------------|
| [Design Philosophy](docs/vision.md) | Core design principles and vision |
| [Memory System](docs/memory.md) | Detailed memory architecture specification |
| [Brain Mapping](docs/brain-mapping.md) | Architecture mapped to neuroscience concepts |
| [Feature Index](docs/features.md) | Comprehensive list of implemented features |
| [Technical Spec](docs/spec.md) | Technical specification |

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
