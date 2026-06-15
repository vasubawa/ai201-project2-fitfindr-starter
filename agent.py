"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

import re
from tools import search_listings, suggest_outfit, create_fit_card, compare_price, check_trends


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
        "price_comparison": None,    # stretch: compare_price result
        "trend_report": None,        # stretch: check_trends result
        "fallback_message": None,    # stretch: if a retry happened
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.
    """
    # Step 1: Initialize the session
    session = _new_session(query, wardrobe)
    
    # Step 2: Parse the user's query
    parsed = {"description": query, "size": None, "max_price": None}
    
    price_match = re.search(r'under\s+\$(\d+(?:\.\d{2})?)', query, re.IGNORECASE)
    if price_match:
        parsed["max_price"] = float(price_match.group(1))
        parsed["description"] = parsed["description"].replace(price_match.group(0), "")
        
    size_match = re.search(r'size\s+([a-zA-Z0-9]+)', query, re.IGNORECASE)
    if size_match:
        parsed["size"] = size_match.group(1)
        parsed["description"] = parsed["description"].replace(size_match.group(0), "")
        
    parsed["description"] = re.sub(r'\s+', ' ', parsed["description"]).strip(', ')
    # Clean up common conversational filler at the start
    parsed["description"] = re.sub(r'^(looking for a|looking for|i want|i need|find me a|find me|a )\s+', '', parsed["description"], flags=re.IGNORECASE).strip()
    session["parsed"] = parsed
    
    # Step 3: Call search_listings
    results = search_listings(parsed["description"], parsed["size"], parsed["max_price"])
    
    # Retry Logic with Fallback (Stretch Feature)
    if not results:
        # First retry: remove size constraint
        if parsed.get("size"):
            results = search_listings(parsed["description"], size=None, max_price=parsed.get("max_price"))
            if results:
                session["fallback_message"] = f"Couldn't find size '{parsed['size']}', but found these options instead."
                
        # Second retry: remove price constraint
        if not results and parsed.get("max_price"):
            results = search_listings(parsed["description"], size=None, max_price=None)
            if results:
                session["fallback_message"] = "Couldn't find items in your budget, but found these instead."

    session["search_results"] = results
    
    if not results:
        session["error"] = "I couldn't find anything matching your search, even after relaxing size and price filters. Please try different keywords."
        return session
        
    # Step 4: Select the item to use
    session["selected_item"] = results[0]
    
    # Step 4.5: Stretch Tools
    session["price_comparison"] = compare_price(session["selected_item"])
    session["trend_report"] = check_trends(session["selected_item"])
    
    # Step 5: Call suggest_outfit
    session["outfit_suggestion"] = suggest_outfit(session["selected_item"], session["wardrobe"])
    
    # Step 6: Call create_fit_card
    session["fit_card"] = create_fit_card(session["outfit_suggestion"], session["selected_item"])
    
    # Step 7: Update Style Profile Memory (Stretch Feature)
    if session["selected_item"] and isinstance(session.get("wardrobe"), dict):
        new_wardrobe_item = {
            "name": session["selected_item"].get("title", "New thrifted item"),
            "category": session["selected_item"].get("category", "clothing")
        }
        if "items" in session["wardrobe"]:
            session["wardrobe"]["items"].append(new_wardrobe_item)
            
        from utils.data_loader import save_style_profile
        save_style_profile(session["wardrobe"])
    
    # Step 8: Return the session
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
