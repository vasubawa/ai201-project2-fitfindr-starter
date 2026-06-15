import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from tools import search_listings, suggest_outfit, create_fit_card, compare_price, check_trends

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_suggest_outfit_empty_wardrobe():
    new_item = {"title": "Vintage Levi's 501", "brand": "Levi's"}
    wardrobe = {"items": []}
    result = suggest_outfit(new_item, wardrobe)
    assert isinstance(result, str)
    assert len(result) > 0

def test_suggest_outfit_with_wardrobe():
    new_item = {"title": "Vintage Levi's 501", "brand": "Levi's"}
    wardrobe = {"items": [{"name": "White ribbed tank top", "category": "tops"}]}
    result = suggest_outfit(new_item, wardrobe)
    assert isinstance(result, str)
    assert len(result) > 0

def test_create_fit_card_empty_outfit():
    new_item = {"title": "Vintage Levi's 501", "price": 38.00, "platform": "depop"}
    result = create_fit_card("", new_item)
    assert result == "Got a new piece! Outfit details coming soon."

def test_create_fit_card_valid_outfit():
    new_item = {"title": "Vintage Levi's 501", "price": 38.00, "platform": "depop"}
    outfit = "Pair these jeans with a white ribbed tank top for a classic summer look."
    result = create_fit_card(outfit, new_item)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "38" in result or "38.0" in result
    assert "depop" in result.lower()

def test_compare_price_no_category():
    item = {"title": "Vintage Tee", "price": 20.0} # no category
    result = compare_price(item)
    assert result == "No category to compare price against."

def test_compare_price_valid():
    # Use an item that definitely has a category in listings
    item = {"id": "test_id", "title": "Vintage Tee", "price": 10.0, "category": "tops"}
    result = compare_price(item)
    assert isinstance(result, str)
    assert "average price" in result.lower()

def test_check_trends():
    item = {"category": "bottoms", "style_tags": ["y2k", "low-rise"]}
    result = check_trends(item)
    assert isinstance(result, str)
    assert len(result) > 0
