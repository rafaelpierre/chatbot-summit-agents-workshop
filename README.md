## Loan Originator Agent

This project implements a Loan Originator Agent using OpenAI's GPT-4.1 model to evaluate user intents and recommend suitable loan products based on their financial needs. The agent is designed to interact with users, understand their requirements, and provide tailored loan options.

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
