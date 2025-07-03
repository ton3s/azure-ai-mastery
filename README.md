# Azure AI Mastery - Multi-Agent Character Platform

A Python application for learning Azure AI services and Semantic Kernel agent frameworks through building a multi-agent character conversation platform.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
cd azure-ai-mastery

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Azure OpenAI

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Add your Azure OpenAI credentials:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

### 3. Run Tests

Verify your setup:

```bash
# Test framework imports and configuration
python tests/test_frameworks.py

# Test character agents
python tests/test_agents.py
```

### 4. Try the Example

```bash
python examples/basic/simple_conversation.py
```

## 📁 Project Structure

```
azure-ai-mastery/
├── config/                 # Configuration management
├── agents/                 # Agent framework
│   ├── base_agent.py      # Base agent class with memory
│   └── character_agent.py # Character-specific agents
├── characters/            # Character definitions (JSON)
├── examples/              # Example implementations
├── tests/                 # Test scripts
└── learning_modules/      # Learning exercises
```

## 🧪 Key Features

- **Semantic Kernel Integration**: Full integration with Azure OpenAI
- **Character Agent System**: Personality-driven agents with memory
- **Memory Management**: Short-term and long-term memory with relationships
- **Azure Services**: Ready for Azure Functions, Cosmos DB integration
- **Test Coverage**: Comprehensive tests for all components

## 📚 Learning Path

1. **Basic**: Simple character conversations
2. **Intermediate**: Multi-agent interactions
3. **Advanced**: Complex scenarios with memory persistence

## 🛠️ Troubleshooting

### Import Errors
- Ensure you're using Python 3.10-3.12
- Activate your virtual environment
- Run `pip install -r requirements.txt`

### Azure OpenAI Errors
- Verify your `.env` file has correct credentials
- Check your deployment names match
- Ensure your API key has proper permissions

### Semantic Kernel Issues
- The project uses direct Azure OpenAI calls due to SK API limitations
- We've bypassed SK's incomplete chat completion methods
- If you encounter issues, run: `python test_setup.py`

### Quick Test
Run the test script to verify your setup:
```bash
python test_setup.py
```

## 🎯 Next Steps

1. Create more character files in `/characters`
2. Build multi-agent conversation scenarios
3. Implement Cosmos DB persistence
4. Deploy to Azure Functions

## 📝 Notes

- All dependencies are pinned to compatible versions
- The framework is designed for extensibility
- Character memories persist during runtime only (add Cosmos DB for persistence)