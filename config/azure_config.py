import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class AzureConfig(BaseSettings):
    """Azure configuration settings"""
    
    # Azure OpenAI settings
    azure_openai_endpoint: str = Field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        description="Azure OpenAI endpoint URL"
    )
    azure_openai_api_key: str = Field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""),
        description="Azure OpenAI API key"
    )
    azure_openai_deployment_name: str = Field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo-learning"),
        description="Azure OpenAI deployment name"
    )
    azure_openai_embedding_deployment_name: str = Field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-learning"),
        description="Azure OpenAI embedding deployment name"
    )
    azure_openai_api_version: str = Field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        description="Azure OpenAI API version"
    )
    
    # Azure Cosmos DB settings
    cosmos_db_endpoint: Optional[str] = Field(
        default_factory=lambda: os.getenv("COSMOS_DB_ENDPOINT"),
        description="Cosmos DB endpoint"
    )
    cosmos_db_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("COSMOS_DB_KEY"),
        description="Cosmos DB key"
    )
    cosmos_db_database_name: str = Field(
        default_factory=lambda: os.getenv("COSMOS_DB_DATABASE_NAME", "ai_agents_db"),
        description="Cosmos DB database name"
    )
    cosmos_db_container_name: str = Field(
        default_factory=lambda: os.getenv("COSMOS_DB_CONTAINER_NAME", "conversations"),
        description="Cosmos DB container name"
    )
    
    # Azure Resource settings
    azure_resource_group: str = Field(
        default_factory=lambda: os.getenv("AZURE_RESOURCE_GROUP", "teamly-ai-learning-rg"),
        description="Azure resource group"
    )
    azure_subscription_id: Optional[str] = Field(
        default_factory=lambda: os.getenv("AZURE_SUBSCRIPTION_ID"),
        description="Azure subscription ID"
    )
    
    # Application settings
    log_level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Logging level"
    )
    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development"),
        description="Environment name"
    )
    character_data_path: str = Field(
        default_factory=lambda: os.getenv("CHARACTER_DATA_PATH", "./characters"),
        description="Path to character data files"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
config = AzureConfig()