"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.
    """
    listings = load_listings()
    results = []
    
    desc_words = [w.lower() for w in description.split()]

    for item in listings:
        if max_price is not None and item["price"] > max_price:
            continue
        
        if size is not None:
            item_size = item.get("size", "")
            if size.lower() not in item_size.lower():
                continue

        score = 0
        searchable_text = f"{item.get('title', '')} {item.get('description', '')} {item.get('category', '')} " \
                          f"{' '.join(item.get('style_tags', []))} {' '.join(item.get('colors', []))} " \
                          f"{item.get('brand', '')}"
        searchable_text = searchable_text.lower()

        for word in desc_words:
            if word in searchable_text:
                score += 1

        if score > 0:
            results.append((score, item))

    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.
    """
    items = wardrobe.get("items", [])
    item_title = new_item.get("title", "this item")
    item_brand = new_item.get("brand", "")
    item_desc = f"{item_title}" + (f" by {item_brand}" if item_brand else "")
    
    client = _get_groq_client()
    
    if not items:
        prompt = (f"I just bought {item_desc}. "
                  f"Please suggest some general styling ideas and outfit combinations for this new item. "
                  f"Keep it fashionable and concise, around 2-3 sentences.")
    else:
        wardrobe_list = ", ".join([f"{w.get('name', '')} ({w.get('category', '')})" for w in items])
        prompt = (f"I just bought {item_desc}. "
                  f"Suggest 1-2 specific outfit combinations using this new item and the following pieces from my wardrobe: {wardrobe_list}. "
                  f"Keep it fashionable and concise, around 2-3 sentences.")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.
    """
    if not outfit or not outfit.strip():
        return "Got a new piece! Outfit details coming soon."

    client = _get_groq_client()
    item_title = new_item.get("title", "an item")
    price = new_item.get("price", 0.0)
    platform = new_item.get("platform", "a store")

    prompt = (f"Write a 2-4 sentence Instagram/TikTok caption for an OOTD post featuring "
              f"my new '{item_title}' that I got for ${price} off {platform}. "
              f"Here's the outfit styling: {outfit}. "
              f"Make it sound casual, authentic, and specific to the outfit vibe. "
              f"Mention the item name, price, and platform naturally once each. Do not include hashtags.")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )
    return response.choices[0].message.content.strip()
