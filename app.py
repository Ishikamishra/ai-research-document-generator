import streamlit as st
import ollama
from duckduckgo_search import DDGS
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
import os
import io

# Page config
st.set_page_config(
    page_title="AI Research Document Generator",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 AI Research Document Generator")
st.markdown("**Generate professional company research documents in 2-3 minutes!**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This tool generates comprehensive research documents including:
    - Company Overview
    - Products & Services
    - Market Position
    - Sales Position
    - Sales AI Automation Challenges
    - Recent News & Developments
    
    **Powered by:** Ollama (Local AI) + Web Search
    """)
    
    st.header("📝 Instructions")
    st.markdown("""
    1. Enter company name
    2. Click 'Generate Research'
    3. Wait 2-3 minutes
    4. Download the document
    """)

# Main content
company_name = st.text_input(
    "Enter Company Name:",
    placeholder="e.g., Microsoft, Diageo, Salesforce",
    help="Enter the name of the company you want to research"
)

def search_recent_news(company_name, max_results=5):
    """Search for recent news using DuckDuckGo"""
    try:
        query = f"{company_name} news 2026"
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        news_items = []
        for result in results[:5]:
            news_items.append({
                'title': result.get('title', 'No title'),
                'url': result.get('href', 'No URL'),
                'snippet': result.get('body', 'No snippet')
            })
        
        return news_items
    except Exception as e:
        st.error(f"News search failed: {str(e)}")
        return []

def generate_with_ai(section, company_name, recent_news=None):
    """Generate content using Ollama"""
    
    prompts = {
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
        
        {recent_news}
        
        Summarize the key developments and trends. Write in professional business language."""
    }
    
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': prompts[section]}]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error generating {section}: {str(e)}"

def create_word_document(company_name, content, recent_news):
    """Create Word document and return as bytes"""
    
    doc = Document()
    
    # Title
    title = doc.add_heading(f"{company_name}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph("Research Document")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.style.font.size = Pt(16)
    subtitle.style.font.bold = True
    
    doc.add_paragraph(f"\nGenerated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    doc.add_paragraph("Prepared by: AI Research Document Generator")
    doc.add_paragraph("_" * 50)
    
    # Sections
    doc.add_heading("1. Company Overview", level=1)
    doc.add_paragraph(content.get('overview', 'N/A'))
    
    doc.add_heading("2. Products & Services", level=1)
    doc.add_paragraph(content.get('products', 'N/A'))
    
    doc.add_heading("3. Market Position", level=1)
    doc.add_paragraph(content.get('market', 'N/A'))
    
    doc.add_heading("4. Sales Position", level=1)
    doc.add_paragraph(content.get('sales', 'N/A'))
    
    doc.add_heading("5. Challenges in Sales AI Automation", level=1)
    doc.add_paragraph(content.get('challenges', 'N/A'))
    
    doc.add_heading("6. Recent News & Developments", level=1)
    doc.add_paragraph(content.get('news_summary', 'N/A'))
    
    if recent_news:
        doc.add_heading("Recent News Sources:", level=2)
        for i, news in enumerate(recent_news, 1):
            p = doc.add_paragraph()
            p.add_run(f"{i}. ").bold = True
            p.add_run(news.get('title', 'No title'))
            p.add_run(f"\n   URL: {news.get('url', 'N/A')}\n")
    
    doc.add_paragraph("\n" + "_" * 50)
    doc.add_paragraph("Generated by AI Research Document Generator")
    
    # Save to bytes
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    return buffer

# Generate button
if st.button("🚀 Generate Research Document", type="primary"):
    if not company_name:
        st.warning("⚠️ Please enter a company name!")
    else:
        with st.spinner(f"🔍 Researching {company_name}... This takes 2-3 minutes."):
            try:
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Search news
                status_text.text("Step 1/6: Searching recent news...")
                recent_news = search_recent_news(company_name, max_results=5)
                progress_bar.progress(15)
                
                # Step 2-6: Generate content
                status_text.text("Step 2/6: Generating company overview...")
                content = {}
                content['overview'] = generate_with_ai('overview', company_name)
                progress_bar.progress(30)
                
                status_text.text("Step 3/6: Generating products & services...")
                content['products'] = generate_with_ai('products', company_name)
                progress_bar.progress(45)
                
                status_text.text("Step 4/6: Generating market position...")
                content['market'] = generate_with_ai('market', company_name)
                progress_bar.progress(60)
                
                status_text.text("Step 5/6: Generating sales position...")
                content['sales'] = generate_with_ai('sales', company_name)
                progress_bar.progress(75)
                
                status_text.text("Step 6/6: Generating AI challenges & news summary...")
                content['challenges'] = generate_with_ai('challenges', company_name)
                content['news_summary'] = generate_with_ai('news_summary', company_name, recent_news)
                progress_bar.progress(100)
                
                status_text.text("✅ Creating document...")
                
                # Create document
                doc_bytes = create_word_document(company_name, content, recent_news)
                
                st.success(f"✅ Research document for **{company_name}** generated successfully!")
                
                # Download button
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{company_name.replace(' ', '_')}_Research_{timestamp}.docx"
                
                st.download_button(
                    label="📥 Download Document (.docx)",
                    data=doc_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary"
                )
                
                # Show recent news
                if recent_news:
                    st.markdown("---")
                    st.subheader("📰 Recent News Found:")
                    for i, news in enumerate(recent_news, 1):
                        with st.expander(f"{i}. {news.get('title', 'No title')}"):
                            st.markdown(f"**URL:** {news.get('url', 'N/A')}")
                            st.markdown(f"{news.get('snippet', 'No snippet')}")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.error("Make sure Ollama is running and llama3.2 model is installed.")

# Footer
st.markdown("---")
st.markdown("**Built with ❤️ using Streamlit, Ollama, and DuckDuckGo Search**")