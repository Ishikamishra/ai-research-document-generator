"""
Configuration module for AI Research Document Generator
Loads and manages environment variables from .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, verbose=False)


class Config:
    """Configuration class for managing app settings"""
    
    # ============================================
    # AI PROVIDER CONFIGURATION
    # ============================================
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini').lower()
    VALID_PROVIDERS = ['claude', 'openai', 'gemini']
    
    # Provider-specific API keys
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Default models for each provider
    CLAUDE_MODEL = 'claude-3-haiku-20240307'  # Fast and cost-effective
    OPENAI_MODEL = 'gpt-4o-mini'              # Fast and cost-effective
    GEMINI_MODEL = 'gemini-3.6-flash'         # Current Gemini model
    
    # ============================================
    # STREAMLIT CONFIGURATION
    # ============================================
    STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
    STREAMLIT_SERVER_HEADLESS = os.getenv('STREAMLIT_SERVER_HEADLESS', 'false').lower() == 'true'
    STREAMLIT_SERVER_RUNONCE = os.getenv('STREAMLIT_SERVER_RUNONCE', 'false').lower() == 'true'
    
    # ============================================
    # APPLICATION SETTINGS
    # ============================================
    MAX_NEWS_RESULTS = int(os.getenv('MAX_NEWS_RESULTS', '5'))
    GENERATION_TIMEOUT = int(os.getenv('GENERATION_TIMEOUT', '180'))
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './generated_documents')
    
    @classmethod
    def get_api_key(cls, provider=None):
        """Get API key for specified provider or current provider"""
        provider = provider or cls.AI_PROVIDER
        provider = provider.lower()
        
        if provider == 'claude':
            return cls.CLAUDE_API_KEY
        elif provider == 'openai':
            return cls.OPENAI_API_KEY
        elif provider == 'gemini':
            return cls.GEMINI_API_KEY
        return None
    
    @classmethod
    def get_model(cls, provider=None):
        """Get default model for specified provider or current provider"""
        provider = provider or cls.AI_PROVIDER
        provider = provider.lower()
        
        if provider == 'claude':
            return cls.CLAUDE_MODEL
        elif provider == 'openai':
            return cls.OPENAI_MODEL
        elif provider == 'gemini':
            return cls.GEMINI_MODEL
        return None
    
    @classmethod
    def validate(cls):
        """Validate configuration and log warnings if needed"""
        errors = []
        warnings = []
        
        # Check AI provider is valid
        if cls.AI_PROVIDER not in cls.VALID_PROVIDERS:
            errors.append(f"AI_PROVIDER '{cls.AI_PROVIDER}' is invalid. Must be one of: {', '.join(cls.VALID_PROVIDERS)}")
        
        # Check that at least one API key is configured
        if not any([cls.CLAUDE_API_KEY, cls.OPENAI_API_KEY, cls.GEMINI_API_KEY]):
            errors.append("No API keys configured. Please set at least one of: CLAUDE_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY")
        
        # Check that selected provider has API key
        current_key = cls.get_api_key()
        if not current_key:
            provider = cls.AI_PROVIDER
            warnings.append(f"Selected provider '{provider}' has no API key configured. Set {provider.upper()}_API_KEY or change AI_PROVIDER.")
        
        # Check numeric values
        if cls.MAX_NEWS_RESULTS < 1:
            warnings.append(f"MAX_NEWS_RESULTS should be >= 1, got {cls.MAX_NEWS_RESULTS}")
        
        if cls.GENERATION_TIMEOUT < 30:
            warnings.append(f"GENERATION_TIMEOUT is quite low: {cls.GENERATION_TIMEOUT}s")
        
        # Create output directory if it doesn't exist
        try:
            os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        except Exception as e:
            warnings.append(f"Could not create OUTPUT_DIR: {str(e)}")
        
        return errors, warnings
    
    @classmethod
    def display_config(cls):
        """Display current configuration (for debugging)"""
        config_info = {
            'AI_PROVIDER': cls.AI_PROVIDER.upper(),
            'PROVIDER_MODEL': cls.get_model(),
            'MAX_NEWS_RESULTS': cls.MAX_NEWS_RESULTS,
            'GENERATION_TIMEOUT': cls.GENERATION_TIMEOUT,
            'OUTPUT_DIR': cls.OUTPUT_DIR,
            'CLAUDE_API_KEY': '✓ Set' if cls.CLAUDE_API_KEY else '✗ Not set',
            'OPENAI_API_KEY': '✓ Set' if cls.OPENAI_API_KEY else '✗ Not set',
            'GEMINI_API_KEY': '✓ Set' if cls.GEMINI_API_KEY else '✗ Not set',
        }
        return config_info


# Validate configuration on import
errors, warnings = Config.validate()

if errors:
    import sys
    print("❌ Configuration Errors:")
    for error in errors:
        print(f"  - {error}")
    print("\nPlease check your .env file and configure required variables.")
    # Don't exit here to allow tests/setup to run

if warnings:
    print("⚠️ Configuration Warnings:")
    for warning in warnings:
        print(f"  - {warning}")
