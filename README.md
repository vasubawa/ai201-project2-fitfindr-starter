# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.

---

## Tool Inventory

*   `search_listings(description: str, size: str | None = None, max_price: float | None = None) -> list[dict]`: Finds matching items in the mock dataset.
*   `suggest_outfit(new_item: dict, wardrobe: dict) -> str`: Suggests an outfit pairing the new item with the existing wardrobe.
*   `create_fit_card(outfit: str, new_item: dict) -> str`: Generates a short social media caption.
*   `compare_price(item: dict) -> str`: Compares item price to dataset average.
*   `check_trends(item: dict) -> str`: Generates a brief trend report based on style tags.

## Planning Loop

1. Parse user query for description, size, and max price.
2. Call `search_listings`.
3. If no results, retry without the size constraint. If still no results, retry without the price constraint.
4. If results are found, call `compare_price` and `check_trends`.
5. Call `suggest_outfit` using the found item and the user's wardrobe.
6. Call `create_fit_card` using the outfit suggestion.
7. Return combined results.

## State Management

A `session` dictionary is created at the start of the loop. It stores the parsed query, search results, selected item, wardrobe, and tool outputs. This dictionary is passed between tools. The user's wardrobe is persistently saved between sessions in `data/style_profile.json`.

## Error Handling

*   **`search_listings`**: Returns `[]` if no matches are found. The loop detects this and retries. *Example:* Searching "designer ballgown size XXS under $5" fails, triggers retry logic, and returns a clean error message instead of crashing.
*   **`suggest_outfit`**: If the wardrobe is empty, falls back to general styling advice.
*   **`create_fit_card`**: Returns `"Got a new piece! Outfit details coming soon."` if the outfit string is missing.
*   **`compare_price` / `check_trends`**: Return default fallback strings on error.

## Spec Reflection

*   **Helpful:** Defining exact inputs/outputs in `planning.md` made implementation fast and structured.
*   **Divergence:** Added dynamic retry logic in `agent.py` instead of sticking to the strict linear flow initially planned.

## AI Usage

*   **Instance 1:** AI suggested basic string splitting to parse user queries. I overrode it and directed it to use Python's `re` (regex) module for accuracy.
*   **Instance 2:** AI generated overly long prompts for the `suggest_outfit` tool. I revised the prompt to strictly limit output to 2-3 sentences.
