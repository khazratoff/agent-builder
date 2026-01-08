# Installation Guide

Complete installation instructions for the Multi-Agent System.

## Prerequisites

- **Python 3.8 or higher**
  - Check your version: `python --version` or `python3 --version`
  - Download from: https://www.python.org/downloads/

- **pip** (Python package manager)
  - Usually comes with Python
  - Check: `pip --version` or `pip3 --version`

- **OpenAI API Key**
  - Sign up at: https://platform.openai.com/
  - Get your API key: https://platform.openai.com/api-keys

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd /Users/izzatillo_khazratov/Desktop/agent-builder
```

### 2. (Optional but Recommended) Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `langchain` - Agent framework
- `langchain-openai` - OpenAI integration
- `langchain-core` - Core components
- `langgraph` - Graph workflows
- `openai` - OpenAI API client
- `python-dotenv` - Environment management
- `duckduckgo-search` - Web search
- `typing-extensions` - Type hints

**Expected output:**
```
Successfully installed langchain-X.X.X langchain-openai-X.X.X ...
```

### 4. Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key:

```bash
# Open in your favorite editor
nano .env
# or
vim .env
# or
code .env  # VS Code
```

Add your key:
```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

**Important:**
- Replace `sk-your-actual-openai-api-key-here` with your real API key
- Don't add quotes around the key
- Don't share this file or commit it to git

### 5. Verify Installation

Test that everything is installed correctly:

```bash
python -c "import langchain, langgraph, openai; print('✓ All dependencies installed!')"
```

You should see: `✓ All dependencies installed!`

### 6. Run the System

```bash
python src/main.py
```

You should see:

```
╔══════════════════════════════════════════════════════════════╗
║          🤖 Multi-Agent System with LangGraph 🤖             ║
║          A Flexible, OOP-Based Agent Architecture           ║
╚══════════════════════════════════════════════════════════════╝

🔧 Initializing multi-agent system...
✓ Registered agent: file_operations
✓ Registered agent: research
✓ Supervisor workflow built with 2 agents

✅ System ready! Type /help for commands or enter your request.

You:
```

## Troubleshooting

### "command not found: python"

Try `python3` instead:
```bash
python3 --version
python3 src/main.py
```

### "No module named 'langchain'"

Dependencies not installed. Run:
```bash
pip install -r requirements.txt
```

If that fails, try:
```bash
pip3 install -r requirements.txt
```

### "OPENAI_API_KEY not found"

Make sure:
1. You created the `.env` file: `cp .env.example .env`
2. You added your actual API key to `.env`
3. You saved the file

Check the file contents:
```bash
cat .env
```

Should show:
```
OPENAI_API_KEY=sk-...your key...
```

### "Permission denied"

On macOS/Linux, you might need:
```bash
chmod +x src/main.py
```

### "Module import errors"

Make sure you're running from the project root directory:
```bash
pwd
# Should show: /Users/izzatillo_khazratov/Desktop/agent-builder

# If not, navigate there:
cd /Users/izzatillo_khazratov/Desktop/agent-builder
```

### Virtual Environment Issues

If you activated a virtual environment but things aren't working:

```bash
# Deactivate
deactivate

# Recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

## Verifying Your Installation

Run these checks:

### 1. Check Python Version
```bash
python --version  # or python3 --version
# Should be 3.8 or higher
```

### 2. Check Dependencies
```bash
pip list | grep langchain
# Should show langchain, langchain-openai, langchain-core
```

### 3. Check Environment
```bash
cat .env
# Should show your OPENAI_API_KEY
```

### 4. Test Imports
```bash
cd src
python -c "from core.base_agent import BaseAgent; print('✓ Core imports working')"
python -c "import agents; print('✓ Agents loading')"
cd ..
```

### 5. Run the System
```bash
python src/main.py
```

## Alternative: Using pip install

You can also install the package:

```bash
pip install -e .
```

This makes the package available system-wide (or venv-wide).

## Next Steps

Once installed successfully:

1. **Try the examples**:
   ```bash
   python examples/add_custom_agent.py
   ```

2. **Read the docs**:
   - Start with [QUICKSTART.md](QUICKSTART.md)
   - Then [docs/TUTORIAL.md](docs/TUTORIAL.md)

3. **Build your first agent**:
   - Follow the tutorial
   - Create your own custom agent

## Getting Help

If you're stuck:

1. Check this installation guide again
2. Read [QUICKSTART.md](QUICKSTART.md)
3. Look at [docs/README.md](docs/README.md)
4. Check the error message carefully - it often tells you what's wrong

## Common Installation Scenarios

### Scenario 1: Clean Install on macOS
```bash
cd /Users/izzatillo_khazratov/Desktop/agent-builder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Add API key
python src/main.py
```

### Scenario 2: System-wide Install
```bash
cd /Users/izzatillo_khazratov/Desktop/agent-builder
pip3 install -r requirements.txt
cp .env.example .env
nano .env  # Add API key
python3 src/main.py
```

### Scenario 3: Development Install
```bash
cd /Users/izzatillo_khazratov/Desktop/agent-builder
python3 -m venv venv
source venv/bin/activate
pip install -e .  # Editable install
cp .env.example .env
nano .env  # Add API key
python src/main.py
```

## Success!

If you see the welcome banner and "System ready!" message, you're all set!

Try your first request:
```
You: What is LangGraph?
```

Happy learning! 🚀
