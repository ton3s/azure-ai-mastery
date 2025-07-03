import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.azure_config import config


def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        import semantic_kernel as sk
        print("✓ semantic_kernel imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import semantic_kernel: {e}")
        return False
    
    try:
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
        print("✓ AzureChatCompletion imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import AzureChatCompletion: {e}")
        return False
    
    try:
        from azure.identity import DefaultAzureCredential
        print("✓ azure.identity imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import azure.identity: {e}")
        return False
    
    try:
        import pydantic
        print(f"✓ pydantic imported successfully (version: {pydantic.VERSION})")
    except ImportError as e:
        print(f"✗ Failed to import pydantic: {e}")
        return False
    
    return True


def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    # Check if .env exists
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print("✗ .env file not found. Please create it from .env.example")
        return False
    
    # Test config values
    if not config.azure_openai_endpoint:
        print("✗ AZURE_OPENAI_ENDPOINT not set")
        return False
    print(f"✓ Azure OpenAI Endpoint: {config.azure_openai_endpoint}")
    
    if not config.azure_openai_api_key:
        print("✗ AZURE_OPENAI_API_KEY not set")
        return False
    print(f"✓ Azure OpenAI API Key: {'*' * 8}...")
    
    print(f"✓ Deployment: {config.azure_openai_deployment_name}")
    print(f"✓ API Version: {config.azure_openai_api_version}")
    
    return True


async def test_semantic_kernel():
    """Test Semantic Kernel setup"""
    print("\nTesting Semantic Kernel...")
    
    try:
        import semantic_kernel as sk
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
        
        # Create kernel
        kernel = sk.Kernel()
        print("✓ Kernel created successfully")
        
        # Add Azure OpenAI service
        kernel.add_service(
            AzureChatCompletion(
                service_id="chat",
                deployment_name=config.azure_openai_deployment_name,
                endpoint=config.azure_openai_endpoint,
                api_key=config.azure_openai_api_key,
            )
        )
        print("✓ Azure OpenAI service added successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Semantic Kernel test failed: {e}")
        return False


async def test_azure_openai_connection():
    """Test Azure OpenAI connection"""
    print("\nTesting Azure OpenAI connection...")
    
    try:
        import semantic_kernel as sk
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
        
        kernel = sk.Kernel()
        
        kernel.add_service(
            AzureChatCompletion(
                service_id="chat",
                deployment_name=config.azure_openai_deployment_name,
                endpoint=config.azure_openai_endpoint,
                api_key=config.azure_openai_api_key,
            )
        )
        
        # Test with a simple prompt
        response = await kernel.invoke_prompt(
            function_name="test",
            plugin_name="test",
            prompt="Say 'Hello, Semantic Kernel is working!' if you can read this.",
        )
        
        print(f"✓ Azure OpenAI responded: {response}")
        return True
        
    except Exception as e:
        print(f"✗ Azure OpenAI connection failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Azure AI + Semantic Kernel Framework Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
        print("\n⚠️  Import tests failed. Please check your dependencies.")
        return
    
    # Test configuration
    if not test_configuration():
        all_passed = False
        print("\n⚠️  Configuration tests failed. Please check your .env file.")
        return
    
    # Test async components
    loop = asyncio.get_event_loop()
    
    # Test Semantic Kernel
    if not loop.run_until_complete(test_semantic_kernel()):
        all_passed = False
    
    # Test Azure OpenAI
    if not loop.run_until_complete(test_azure_openai_connection()):
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Your environment is ready.")
    else:
        print("❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()