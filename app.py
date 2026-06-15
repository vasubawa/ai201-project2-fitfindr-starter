"""
app.py

Gradio interface for FitFindr. The layout and wiring are already set up —
your job is to fill in handle_query() so it calls run_agent() and maps
the session results to the three output panels.

Run with:
    python app.py

Then open the localhost URL shown in your terminal (usually http://localhost:7860,
but check your terminal — the port may differ).
"""

import gradio as gr

from agent import run_agent
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe, load_style_profile


# ── query handler ─────────────────────────────────────────────────────────────

def handle_query(user_query: str, wardrobe_choice: str) -> tuple[str, str, str]:
    """
    Called by Gradio when the user submits a query.
    """
    if not user_query or not user_query.strip():
        return "Please provide a query.", "", ""
        
    if "Saved profile" in wardrobe_choice:
        wardrobe = load_style_profile()
        if not wardrobe:
            wardrobe = get_empty_wardrobe()
    elif "Empty wardrobe" in wardrobe_choice:
        wardrobe = get_empty_wardrobe()
    else:
        wardrobe = get_example_wardrobe()
        
    session = run_agent(user_query, wardrobe)
    
    if session.get("error"):
        return session["error"], "", ""
        
    item = session["selected_item"]
    listing_text = ""
    if session.get("fallback_message"):
        listing_text += f"⚠️ {session['fallback_message']}\n\n"
        
    listing_text += f"{item.get('title', 'Unknown')} — ${item.get('price', 0)} on {item.get('platform', 'Unknown')}\n"
    if "brand" in item and item["brand"]:
        listing_text += f"Brand: {item['brand']}\n"
    if "size" in item and item["size"]:
        listing_text += f"Size: {item['size']}\n"
    if "condition" in item and item["condition"]:
        listing_text += f"Condition: {item['condition']}\n\n"
    if "description" in item and item["description"]:
        listing_text += f"{item['description']}\n\n"
        
    if session.get("price_comparison"):
        listing_text += f"💰 Price Check: {session['price_comparison']}\n"
    if session.get("trend_report"):
        listing_text += f"📈 Trend Check: {session['trend_report']}\n"
        
    outfit_suggestion = session.get("outfit_suggestion") or ""
    fit_card = session.get("fit_card") or ""
    
    return listing_text, outfit_suggestion, fit_card


# ── interface ─────────────────────────────────────────────────────────────────

EXAMPLE_QUERIES = [
    "vintage graphic tee under $30",
    "90s track jacket in size M",
    "flowy midi skirt under $40",
    "black combat boots size 8",
    "designer ballgown size XXS under $5",   # deliberate no-results test
]

def build_interface():
    with gr.Blocks(title="FitFindr") as demo:
        gr.Markdown("""
# FitFindr 🛍️
Find secondhand pieces and get outfit ideas based on your wardrobe.
Describe what you're looking for — include size and price if you want to filter.
        """)

        with gr.Row():
            query_input = gr.Textbox(
                label="What are you looking for?",
                placeholder="e.g. vintage graphic tee under $30, size M",
                lines=2,
                scale=3,
            )
            wardrobe_choice = gr.Radio(
                choices=["Example wardrobe", "Saved profile (from previous session)", "Empty wardrobe (new user)"],
                value="Example wardrobe",
                label="Wardrobe",
                scale=1,
            )

        submit_btn = gr.Button("Find it", variant="primary")

        with gr.Row():
            listing_output = gr.Textbox(
                label="🛍️ Top listing found",
                lines=8,
                interactive=False,
            )
            outfit_output = gr.Textbox(
                label="👗 Outfit idea",
                lines=8,
                interactive=False,
            )
            fitcard_output = gr.Textbox(
                label="✨ Your fit card",
                lines=8,
                interactive=False,
            )

        gr.Examples(
            examples=[[q, "Example wardrobe"] for q in EXAMPLE_QUERIES],
            inputs=[query_input, wardrobe_choice],
            label="Try these queries",
        )

        submit_btn.click(
            fn=handle_query,
            inputs=[query_input, wardrobe_choice],
            outputs=[listing_output, outfit_output, fitcard_output],
        )
        query_input.submit(
            fn=handle_query,
            inputs=[query_input, wardrobe_choice],
            outputs=[listing_output, outfit_output, fitcard_output],
        )

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch()
