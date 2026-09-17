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
            'executive_summary': f"""Write a concise executive summary for {company_name} (150-200 words).
Include:
- Brief company introduction
- Key business highlights
- Market position summary
- Strategic focus areas
- Major achievements or differentiators

Write in professional business language suitable for C-level executives.""",
            
            'company_overview': f"""Write a comprehensive company overview for {company_name} (250-300 words).
Include:
- What the company does
- Industry and sector
- Headquarters location
- Year founded
- Founder/CEO (if known)
- Company size (employees, revenue if known)
- Global presence and operations
- Mission and vision

Write in professional business language.""",
            
            'business_segments': f"""Describe the business segments and brands of {company_name} (250-300 words).
Include:
- Main business divisions/segments
- Key brands and product lines
- Revenue contribution by segment (if known)
- Target markets for each segment
- Brand positioning and strategy

Format with clear sections and bullet points where appropriate.
Write in professional business language.""",
            
            'sales_distribution': f"""Analyze the sales and distribution model of {company_name} (250-300 words).
Include:
- Sales channels (direct, indirect, online, retail, etc.)
- Distribution network and partnerships
- Geographic sales distribution
- Key customers or client segments
- Sales strategy and approach
- Distribution strengths and capabilities

Write in professional business language.""",
            
            'gcc_market': f"""Analyze the GCC (Gulf Cooperation Council) market for {company_name} (300-350 words).
Include:
- GCC market size and presence
- Market growth trends
- CAGR (Compound Annual Growth Rate) if available
- Key GCC markets (UAE, Saudi Arabia, Qatar, etc.)
- Market opportunities in the region
- Competitive landscape in GCC
- Growth drivers and challenges

Write in professional business language with data-driven insights.""",
            
            'ai_transformation': f"""Analyze AI and digital transformation initiatives for {company_name} (300-350 words).
Focus on:
- AI adoption in sales processes
- Digital transformation in distribution
- AI-powered retail initiatives
- Automation in customer engagement
- Digital tools and platforms used
- Impact on efficiency and customer experience
- Future AI/digital roadmap

Write in professional business language with actionable insights.""",
            
            'tech_stack': f"""Describe the current technology stack of {company_name} (250-300 words).
Include:
- Core enterprise systems (ERP, CRM, etc.)
- Sales and marketing technologies
- E-commerce and digital platforms
- Data and analytics tools
- Cloud infrastructure
- Integration and API capabilities
- Technology partnerships

Write in professional business language.""",
            
            'strategic_transformation': f"""Outline strategic transformation and future planning for {company_name} (300-350 words).
Include:
- Strategic priorities and goals
- Transformation initiatives underway
- Future growth plans
- Innovation focus areas
- Market expansion strategies
- Sustainability and ESG initiatives
- Long-term vision (3-5 years)

Write in professional business language with strategic insights.""",
            
            'news_timeline': f"""Based on these recent news items about {company_name}, create a timeline summary (200-250 words):

{self._format_news(recent_news)}

Organize by date if possible. Highlight:
- Major announcements
- Product launches
- Partnerships or acquisitions
- Market expansions
- Leadership changes
- Financial results

Write in professional business language.""",
            
            'key_insights': f"""Provide key insights on growth opportunities and challenges for {company_name} (300-350 words).
Include:

GROWTH OPPORTUNITIES:
- Market expansion opportunities
- Untapped customer segments
- Product/service innovation areas
- Strategic partnership possibilities
- Emerging market trends to leverage

CHALLENGES:
- Competitive pressures
- Market headwinds
- Operational challenges
- Technology gaps
- Regulatory or compliance issues

Write in professional business language with actionable recommendations.""",
            
            'conclusion': f"""Write a comprehensive conclusion for {company_name} research (200-250 words).
Include:
- Summary of company strengths
- Key competitive advantages
- Strategic positioning
- Outlook for future growth
- Final recommendations for stakeholders

Write in professional business language suitable for executive presentation."""
        }
    
    def _format_news(self, recent_news: Optional[List[Dict]]) -> str:
        """Format recent news items for inclusion in prompts"""
        if not recent_news:
            return "No recent news available."
        
        formatted = []
        for i, news in enumerate(recent_news, 1):
            title = news.get('title', 'No title')
            snippet = news.get('snippet', '')[:200]
            url = news.get('url', 'No URL')
            formatted.append(f"{i}. {title}\n   URL: {url}\n   {snippet}")
        
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
                    {"role": "system", "content": "You are a professional business analyst specializing in market research and strategic analysis."},
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
            print(f"✅ Gemini client initialized successfully with model: {self.model}")
        except ImportError as e:
            print(f"❌ Import error: {e}")
            raise ImportError("google-generativeai package is required. Install it with: pip install google-generativeai")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {str(e)}")
            raise Exception(f"Failed to initialize Gemini client: {str(e)}")
    
    def generate_content(self, section: str, company_name: str, recent_news: Optional[List[Dict]] = None) -> str:
        """Generate content using Google Gemini API"""
        try:
            if not hasattr(self, 'client') or self.client is None:
                return f"Error: Gemini client not initialized. Check your API key and model configuration."
            
            prompts = self._get_prompts(company_name, recent_news)
            prompt = prompts.get(section, f"Generate information about {company_name}")
            
            response = self.client.generate_content(prompt)
            
            if response and hasattr(response, 'text'):
                return response.text
            else:
                return f"Error: No response from Gemini API for {section}"
                
        except Exception as e:
            error_msg = f"Error generating {section}: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """Instantiate the AI provider selected by name."""
    normalized = (provider_name or Config.AI_PROVIDER or "gemini").strip().lower()

    if normalized in {"claude", "anthropic"}:
        return ClaudeProvider()
    if normalized in {"openai", "gpt", "chatgpt"}:
        return OpenAIProvider()
    if normalized in {"gemini", "google", "google-gemini"}:
        return GeminiProvider()

    valid = ", ".join(Config.VALID_PROVIDERS)
    raise ValueError(f"Unsupported AI provider: '{provider_name}'. Choose one of: {valid}")