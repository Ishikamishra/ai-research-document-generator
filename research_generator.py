from docx import Document
from datetime import datetime
import time
from config import Config
from ai_provider import get_ai_provider
from news_search import search_recent_news as fetch_recent_news
from docx_formatting import (
    CONTENT_KEYS,
    SECTION_TITLES,
    add_news_sources,
    add_section,
    add_table_of_contents,
    add_title_page,
    configure_document,
)

class ResearchDocumentGenerator:
    def __init__(self, provider=None):
        self.company_name = ""
        self.content = {}
        self.recent_news = []
        
        # Initialize AI provider
        try:
            self.ai_provider = get_ai_provider(provider)
            print(f"✓ Using {self.ai_provider.provider_name} ({self.ai_provider.model})")
        except ValueError as e:
            print(f"❌ {str(e)}")
            raise
    
    def search_recent_news(self, company_name, max_results=None):
        """Search for recent news using DuckDuckGo"""
        if max_results is None:
            max_results = Config.MAX_NEWS_RESULTS
        
        print(f"🔍 Searching recent news for {company_name}...")
        
        try:
            news_items = fetch_recent_news(company_name, max_results=max_results)
            self.recent_news = news_items
            return news_items
        except Exception as e:
            print(f"⚠️ News search failed: {str(e)}")
            return []
    
    def generate_with_ai(self, section, company_name):
        """Generate content using configured AI provider"""
        return self.ai_provider.generate_content(section, company_name, self.recent_news)
    
    def generate_research(self, company_name):
        """Generate complete research document"""
        self.company_name = company_name
        self.content = {}
        self.recent_news = []
        
        print(f"\n🔍 Researching {company_name}...")
        print("=" * 50)
        
        # Step 1: Search recent news (real-time)
        self.search_recent_news(company_name, max_results=Config.MAX_NEWS_RESULTS)
        
        # Step 2: Generate AI content (local, no limits)
        print("📝 Generating company overview...")
        self.content['overview'] = self.generate_with_ai('overview', company_name)
        
        print("📝 Generating products & services...")
        self.content['products'] = self.generate_with_ai('products', company_name)
        
        print("📝 Generating market position...")
        self.content['market'] = self.generate_with_ai('market', company_name)
        
        print("📝 Generating sales position...")
        self.content['sales'] = self.generate_with_ai('sales', company_name)
        
        print("📝 Generating sales AI automation challenges...")
        self.content['challenges'] = self.generate_with_ai('challenges', company_name)
        
        print("📝 Generating news summary...")
        self.content['news_summary'] = self.generate_with_ai('news_summary', company_name)
        
        print("=" * 50)
        print(f"✅ Content generation complete for {company_name}!")
        
        return self.content
    
    def create_word_document(self, output_filename=None):
        """Create professional Word document"""
        import os
        
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"{self.company_name.replace(' ', '')}_Research{timestamp}.docx"
        
        # Use configured output directory
        output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        print(f"\n📄 Creating Word document: {output_path}")
        
        doc = Document()
        configure_document(doc)
        add_title_page(doc, self.company_name)
        add_table_of_contents(doc)
        for number, (title, key) in enumerate(zip(SECTION_TITLES, CONTENT_KEYS), 1):
            add_section(doc, number, title, self.content.get(key, "N/A"))
        add_news_sources(doc, self.recent_news)
        
        doc.save(output_path)
        print(f"✅ Document saved: {output_path}")
        
        return output_path
    
    def run(self, company_name):
        """Run complete research workflow"""
        self.generate_research(company_name)
        output_file = self.create_word_document()
        print(f"\n🎉 Research document for {self.company_name} completed!")
        print(f"📁 Output file: {output_file}")
        return output_file

if __name__ == "__main__":
    print("=" * 60)
    print("AI Research Document Generator")
    print("Powered by Claude, OpenAI, or Gemini + Web Search")
    print("=" * 60)
    
    generator = ResearchDocumentGenerator()
    
    # Get company name
    company = input("\nEnter company name: ").strip()
    
    if not company:
        print("❌ Please enter a company name!")
        exit()
    
    # Generate research document
    output_file = generator.run(company)
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS!")
    print(f"Document created: {output_file}")
    print("=" * 60)