from duckduckgo_search import DDGS

try:
    with DDGS() as ddgs:
        results = list(ddgs.text("Microsoft news 2026", max_results=3))
    
    print("✅ DuckDuckGo Search Working!")
    print(f"Found {len(results)} results")
    for r in results:
        print(f"\n- {r.get('title', 'No title')}")
except Exception as e:
    print(f"❌ Error: {str(e)}")