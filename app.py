import streamlit as st
from docx import Document
from datetime import datetime
import os
import io
from config import Config
from ai_provider import get_ai_provider
from docx_formatting import (
    CONTENT_KEYS,
    SECTION_TITLES,
    add_news_sources,
    add_section,
    add_table_of_contents,
    add_title_page,
    configure_document,
)
from news_search import search_recent_news as fetch_recent_news

# Page config
st.set_page_config(
    page_title="AI Research Document Generator",
    page_icon="📊",
    layout="wide"
)

# Display configuration info in sidebar (optional debug info)
with st.sidebar:
    st.subheader("🤖 AI Provider Selection")
    
    # Provider selector
    provider_options = {
        "Claude (claude-3-haiku)": "claude",
        "OpenAI (gpt-4o-mini)": "openai",
        "Gemini (gemini-3.6-flash)": "gemini"
    }
    
    selected_label = st.selectbox(
        "Choose AI Provider:",
        options=list(provider_options.keys()),
        index=list(provider_options.values()).index(Config.AI_PROVIDER) if Config.AI_PROVIDER in provider_options.values() else 2
    )
    selected_provider = provider_options[selected_label]
    
    # Show API key status
    st.markdown("**API Key Status:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        status = "✅" if Config.CLAUDE_API_KEY else "❌"
        st.metric("Claude", status)
    with col2:
        status = "✅" if Config.OPENAI_API_KEY else "❌"
        st.metric("OpenAI", status)
    with col3:
        status = "✅" if Config.GEMINI_API_KEY else "❌"
        st.metric("Gemini", status)
    
    if st.checkbox("🔧 Show Configuration", value=False):
        st.subheader("Current Configuration")
        config_info = Config.display_config()
        for key, value in config_info.items():
            st.code(f"{key}: {value}")

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
    
    **Powered by:** Claude, OpenAI, or Gemini APIs + DuckDuckGo Search
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

def search_recent_news(company_name, max_results=None):
    """Search for recent news using DuckDuckGo"""
    if max_results is None:
        max_results = Config.MAX_NEWS_RESULTS
    
    try:
        return fetch_recent_news(company_name, max_results=max_results)
    except Exception as e:
        st.error(f"News search failed: {str(e)}")
        return []

def generate_with_ai(section, company_name, recent_news=None, provider=None):
    """Generate content using configured AI provider"""
    try:
        ai_provider = get_ai_provider(provider)
        return ai_provider.generate_content(section, company_name, recent_news)
    except Exception as e:
        return f"Error generating {section}: {str(e)}"

def create_word_document(company_name, content, recent_news):
    """Create Word document and return as bytes"""
    
    doc = Document()

    configure_document(doc)
    add_title_page(doc, company_name)
    add_table_of_contents(doc)
    for number, (title, key) in enumerate(zip(SECTION_TITLES, CONTENT_KEYS), 1):
        add_section(doc, number, title, content.get(key, "N/A"))
    add_news_sources(doc, recent_news)
    
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
                content['overview'] = generate_with_ai('overview', company_name, provider=selected_provider)
                progress_bar.progress(30)
                
                status_text.text("Step 3/6: Generating products & services...")
                content['products'] = generate_with_ai('products', company_name, provider=selected_provider)
                progress_bar.progress(45)
                
                status_text.text("Step 4/6: Generating market position...")
                content['market'] = generate_with_ai('market', company_name, provider=selected_provider)
                progress_bar.progress(60)
                
                status_text.text("Step 5/6: Generating sales position...")
                content['sales'] = generate_with_ai('sales', company_name, provider=selected_provider)
                progress_bar.progress(75)
                
                status_text.text("Step 6/6: Generating AI challenges & news summary...")
                content['challenges'] = generate_with_ai('challenges', company_name, provider=selected_provider)
                content['news_summary'] = generate_with_ai('news_summary', company_name, recent_news, provider=selected_provider)
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
                st.error("Please check that your API key for the selected provider is configured in .env")

# Footer
st.markdown("---")
st.markdown("**Built with ❤️ using Streamlit, Claude/OpenAI/Gemini APIs, and DuckDuckGo Search**")