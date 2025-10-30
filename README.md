## Loan Originator Agent

This project implements a Loan Originator Agent using OpenAI's GPT-4.1 model to evaluate user intents and recommend suitable loan products based on their financial needs. The agent is designed to interact with users, understand their requirements, and provide tailored loan options.

### Project Structure

```
vibe-to-live-workshop/
├── backend/                          # Main application directory
│   ├── src/
│   │   ├── agent/                    # Agent definitions (multi-agent chain)
│   │   │   ├── intent.py            # Intent Investigation Agent (router)
│   │   │   ├── profiler.py          # Loan Profiler Agent (information gatherer)
│   │   │   ├── evaluator.py         # Product Evaluator Agent (decision maker)
│   │   │   └── context.py           # Shared conversation context
│   │   │
│   │   ├── guardrails/              # Input validation and safety
│   │   │   └── input_guardrails.py  # LLM-based input guardrail implementation
│   │   │
│   │   ├── models/                  # Model configuration
│   │   │   └── completions.py       # OpenAI model factory
│   │   │
│   │   └── services/                # Application orchestration
│   │       └── chat_service.py      # Main conversation loop + Phoenix setup
│   │
│   ├── pyproject.toml               # Python dependencies
│   └── uv.lock                      # Lock file for reproducible builds
│
├── .devcontainer/                   # Development container configuration
│   └── devcontainer.json            # VS Code devcontainer settings
│
├── .env.example                     # Environment variable template
└── README.md                        # This file
```

### Key Components

- **Agent Chain**: Intent → Profiler → Evaluator (sequential handoff pattern)
- **Guardrails**: Input validation using GPT-4.1-mini (agent-as-guardrail pattern)
- **Observability**: Phoenix/Arize integration for agent tracing (student exercise)
- **Structured Outputs**: Pydantic schemas with Literal types for type safety
- **Session Management**: SQLite-based conversation persistence

### Getting started

You can find the instructions to set up here: [Vibe to Live: Build and Deploy Agent AI Products](https://wood-farmhouse-ac7.notion.site/Vibe-to-Live-Build-and-Deploy-Agent-AI-Products-29c77f1588908055ab3adb5d67e6f713)

### Running this code

#### Quickstart

* Using Github Codespaces (recommended)
    * Fork this repo
    * Go to your fork
    * Click the green "Code" button and select "Open with Codespaces"
* Using devcontainers with VS Code
    * Install [VS Code](https://code.visualstudio.com/)
    * Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
    * Clone this repo
    * Open the cloned repo in VS Code
    * Reopen the project in a container when prompted
* Add your OpenAI API key to a `.env` file in the root of the project:
    ```bash
    OPENAI_API_KEY=your_openai_api_key_here
    ```
* Add your Phoenix API key and endpoint to the `.env` file:
    ```bash
    PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/...
    PHOENIX_API_KEY=your_phoenix_api_key_here
    ```
* **IMPORTANT**: make sure you add your keys to `.env` and not to `.env.example`!
* Run the app using `uv`:
    ```bash
    cd backend
    uv run src/services/chat_service.py
    ```

### Questions to explore

* Have a chat with the Loan Originator Agent and test its responses to various loan requests.
* What happens when you ask for products that are not related to loans? E.g. credit cards
* What happens when you ask a question unrelated to financial products? E.g. "What's the weather like today?"
* What happens when you ask the current agent to hand over to the `Product Evaluator Agent`?
* How do we know the agent inputs, outputs, and which agent handed over control to which other agent?
