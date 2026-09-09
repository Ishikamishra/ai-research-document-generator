"""
AI Provider Abstraction Layer
Supports Claude, OpenAI, and Google Gemini APIs with a unified interface
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from config import Config


class AIProvider(ABC):
    """Abstract base class for AI content generators"""
    
    def __init__(self):
        self.provider_name = None
        self.model = None
        self.api_key = None
    
    @abstractmethod
    def generate_content(self, section: str, company_name: str, recent_news: Optional[List[Dict]] = None) -> str:
        """Generate content for a specific section"""
        pass
    
    def _get_prompts(self, company_name: str, recent_news: Optional[List[Dict]] = None) -> Dict[str, str]:
        """Get standardized prompts for all sections"""
        return {
            'overview': f"""Write a professional company overview for {company_name} (200-250 words).
Include:
- What the company does
- Industry and sector
- Headquarters location
- Year founded
- Key business areas
- Company size (employees)

Write in professional business language.""",
            
            'products': f"""List the key products and services offered by {company_name}.
Format as bullet points with brief descriptions.
Include 5-7 main products/services.
For each product, mention:
- Product name
- What it does
- Target customers

Write in professional business language.""",
            
            'market': f"""Describe {company_name}'s market position and competitive landscape (200-250 words).
Include:
- Market share and ranking
- Main competitors (name 3-5 competitors)
- Target customer segments
- Competitive advantages
- Market trends affecting the company

Write in professional business language.""",
            
            'sales': f"""Describe {company_name}'s sales position and strategy (200-250 words).
Include:
- Annual revenue (if known) or revenue range
- Sales channels (direct, partners, online, etc.)
- Sales strategy approach
- Key sales markets/regions
- Sales performance trends
- Customer acquisition approach

Write in professional business language.""",
            
            'challenges': f"""Analyze challenges in sales AI automation for {company_name} (250-300 words).
Include:
- Current AI adoption level in sales
- Key challenges in implementing AI automation
- Specific sales processes that need automation
- Technology gaps or limitations
- Data and integration challenges
- Change management and adoption barriers
- Recommendations for improvement

Write in professional business language with actionable insights.""",
            
            'news_summary': f"""Based on these recent news items about {company_name}, write a brief summary (150 words):

{self._format_news(recent_news)}

Summarize the key developments and trends. Write in professional business language."""
        }
    
    def _format_news(self, recent_news: Optional[List[Dict]]) -> str:
        """Format recent news items for inclusion in prompts"""
        if not recent_news:
            return "No recent news available."
        
        formatted = []
        for i, news in enumerate(recent_news, 1):
            title = news.get('title', 'No title')
            snippet = news.get('snippet', '')[:200]
            formatted.append(f"{i}. {title}\n   {snippet}")
        
        return "\n".join(formatted)


class ClaudeProvider(AIProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = 'Claude'
        self.model = Config.CLAUDE_MODEL
        self.api_key = Config.CLAUDE_API_KEY
        
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY is not configured in .env")
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package is required. Install it with: pip install anthropic")
    
    def generate_content(self, section: str, company_name: str, recent_news: Optional[List[Dict]] = None) -> str:
        """Generate content using Claude API"""
        try:
            prompts = self._get_prompts(company_name, recent_news)
            prompt = prompts.get(section, f"Generate information about {company_name}")
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            return f"Error generating {section}: {str(e)}"


class OpenAIProvider(AIProvider):
    """OpenAI API provider"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = 'OpenAI'
        self.model = Config.OPENAI_MODEL
        self.api_key = Config.OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured in .env")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package is required. Install it with: pip install openai")
    
    def generate_content(self, section: str, company_name: str, recent_news: Optional[List[Dict]] = None) -> str:
        """Generate content using OpenAI API"""
        try:
            prompts = self._get_prompts(company_name, recent_news)
            prompt = prompts.get(section, f"Generate information about {company_name}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional business analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating {section}: {str(e)}"


class GeminiProvider(AIProvider):
    """Google Gemini API provider"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = 'Gemini'
        self.model = Config.GEMINI_MODEL
        self.api_key = Config.GEMINI_API_KEY
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in .env")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            raise ImportError("google-generativeai package is required. Install it with: pip install google-generativeai")
    
    def generate_content(self, section: str, company_name: str, recent_news: Optional[List[Dict]] = None) -> str:
        """Generate content using Google Gemini API"""
        try:
            prompts = self._get_prompts(company_name, recent_news)
            prompt = prompts.get(section, f"Generate information about {company_name}")
            
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating {section}: {str(e)}"


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """Factory function to get the appropriate AI provider"""
    provider = provider_name or Config.AI_PROVIDER
    provider = provider.lower()
    
    if provider == 'claude':
        return ClaudeProvider()
    elif provider == 'openai':
        return OpenAIProvider()
    elif provider == 'gemini':
        return GeminiProvider()
    else:
        raise ValueError(f"Unknown AI provider: {provider}. Must be one of: claude, openai, gemini")
