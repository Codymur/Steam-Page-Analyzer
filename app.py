import html
import re

import streamlit as st

from scraper import scrape_steam_page
from ai_analyzer import generate_page_feedback

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Steam Page Estimator",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #16202d;
    --panel: #1d2b3c;
    --line: #2f4259;
    --text: #dfe7f0;
    --muted: #8fa1b5;
    --blue: #66c0f4;
    --amber: #f0b74f;
    --radius: 6px;
}

html, body, .stApp, .stMarkdown, button, input, textarea {
    font-family: 'Bricolage Grotesque', system-ui, sans-serif;
}
/* Keep Streamlit's icon font intact (status check mark, expander arrows) */
[data-testid="stIconMaterial"], .material-symbols-rounded, [class*="material-symbols"] {
    font-family: 'Material Symbols Rounded' !important;
}
.stApp { background: var(--bg); }
.block-container { max-width: 1120px; padding-top: 2.4rem; padding-bottom: 4rem; }
#MainMenu, footer { visibility: hidden; }

h1, h2, h3 { font-family: 'Bricolage Grotesque', sans-serif; letter-spacing: -0.02em; }

/* Intro */
.intro h1 { font-size: clamp(2rem, 4.5vw, 3rem); font-weight: 700; margin: 0 0 .35rem 0; padding: 0; color: var(--text); }
.intro p { color: var(--muted); font-size: 1.05rem; margin: 0 0 1.4rem 0; max-width: 62ch; }

/* Inputs */
[data-testid="stForm"] { border: none; padding: 0; }
.stTextInput input { background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); color: var(--text); }
.stTextInput input:focus { border-color: var(--blue); box-shadow: 0 0 0 1px var(--blue); }
button[kind="primary"], button[kind="primaryFormSubmit"] {
    background: var(--blue); color: #0f1822; border: none; border-radius: var(--radius); font-weight: 700;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover { background: #8dd2f8; color: #0f1822; }
button[kind="secondary"] {
    background: transparent; border: 1px solid var(--line); border-radius: var(--radius); color: var(--muted);
}
button[kind="secondary"]:hover { border-color: var(--blue); color: var(--blue); }

/* Game header */
.game { display: grid; grid-template-columns: minmax(0, 300px) 1fr; gap: 1.6rem; margin: 1.8rem 0 1.2rem 0; align-items: start; }
.game img { width: 100%; border-radius: var(--radius); border: 1px solid var(--line); display: block; }
.game h2 { font-size: 1.9rem; margin: 0 0 .5rem 0; padding: 0; color: var(--text); }
.game .facts { display: flex; flex-wrap: wrap; gap: .5rem 1rem; color: var(--muted); margin-bottom: .8rem; align-items: center; }
.game .price { color: var(--amber); font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.chips { display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: .8rem; }
.chip { border: 1px solid var(--line); border-radius: 4px; padding: .12rem .55rem; font-size: .85rem; color: var(--muted); }
.chip.genre { border-color: var(--blue); color: var(--blue); }
.desc { color: var(--text); border-left: 3px solid var(--line); padding-left: .9rem; margin: 0; max-width: 70ch; line-height: 1.55; }
@media (max-width: 760px) { .game { grid-template-columns: 1fr; } }

/* Ledger: the one memorable element */
.ledger { background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); padding: 1.3rem 1.5rem 1.5rem 1.5rem; }
.ledger .row { display: grid; grid-template-columns: 1.6rem 1fr auto; gap: .5rem; padding: .55rem 0; border-bottom: 1px dashed var(--line); align-items: baseline; }
.ledger .op { color: var(--muted); font-family: 'JetBrains Mono', monospace; }
.ledger .lab { color: var(--muted); }
.ledger .val { font-family: 'JetBrains Mono', monospace; text-align: right; color: var(--text); }
.ledger .row.sub .lab, .ledger .row.sub .val { color: var(--text); font-weight: 600; }
.ledger .total { padding-top: 1.2rem; }
.ledger .total .lab { color: var(--text); font-size: 1.05rem; }
.ledger .total .big { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--amber); font-size: clamp(2.3rem, 5.5vw, 3.5rem); line-height: 1.1; margin-top: .2rem; }
.ledger .total .note { color: var(--muted); font-size: .9rem; margin-top: .3rem; }

/* Scenario table */
.scen { width: 100%; border-collapse: collapse; margin-top: .4rem; }
.scen th { text-align: left; color: var(--muted); font-weight: 500; font-size: .9rem; border-bottom: 1px solid var(--line); padding: .45rem .3rem; }
.scen td { padding: .55rem .3rem; border-bottom: 1px dashed var(--line); font-family: 'JetBrains Mono', monospace; font-size: .92rem; color: var(--text); }
.scen td:first-child { font-family: 'Bricolage Grotesque', sans-serif; color: var(--muted); }
.scen tr.base td { color: var(--amber); }

.small { color: var(--muted); font-size: .88rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

EXAMPLES = {
    "Hades": "https://store.steampowered.com/app/1145360/Hades/",
    "Vampire Survivors": "https://store.steampowered.com/app/1794680/Vampire_Survivors/",
    "Balatro": "https://store.steampowered.com/app/2379780/Balatro/",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_app_id(url: str):
    match = re.search(r"/app/(\d+)", url)
    return match.group(1) if match else None


def fmt_money(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 10_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def esc(text: str) -> str:
    return html.escape(str(text or ""))


def estimate(reviews: int, price: float, multiplier: float, share: float) -> dict:
    owners = int(reviews * multiplier)
    gross = owners * price
    return {"owners": owners, "gross": gross, "net": gross * share}


def ledger_html(reviews, multiplier, price, share) -> str:
    est = estimate(reviews, price, multiplier, share)

    def row(op, label, value, sub=False):
        cls = "row sub" if sub else "row"
        return (
            f'<div class="{cls}"><span class="op">{op}</span>'
            f'<span class="lab">{label}</span><span class="val">{value}</span></div>'
        )

    parts = [
        '<div class="ledger">',
        row("", "Public reviews", f"{reviews:,}"),
        row("×", "Reviews-to-owners multiplier", f"{multiplier}"),
        row("=", "Estimated owners", f"{est['owners']:,}", sub=True),
        row("×", "Store price (USD)", f"${price:,.2f}"),
        row("=", "Gross revenue", f"${est['gross']:,.0f}", sub=True),
        row("×", "Share kept after Steam's cut, refunds and regional pricing", f"{share:.0%}"),
        '<div class="total"><div class="lab">Estimated net revenue</div>',
        f'<div class="big">${est["net"]:,.0f}</div>',
        '<div class="note">Rough estimate, not reported sales.</div></div>',
        "</div>",
    ]
    return "".join(parts)


def scenario_table(reviews, price, multiplier, share) -> str:
    low = max(1, round(multiplier * 2 / 3))
    high = round(multiplier * 1.5)
    rows = []
    for name, m, cls in (("Lower", low, ""), ("Your setting", multiplier, "base"), ("Higher", high, "")):
        est = estimate(reviews, price, m, share)
        rows.append(
            f'<tr class="{cls}"><td>{name}</td><td>{m}x</td>'
            f'<td>{est["owners"]:,}</td><td>{fmt_money(est["net"])}</td></tr>'
        )
    return (
        '<table class="scen"><thead><tr><th>Case</th><th>Multiplier</th><th>Owners</th><th>Net revenue</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def game_header_html(data: dict, url: str) -> str:
    app_id = get_app_id(url)
    img = ""
    if app_id:
        src = f"https://cdn.akamai.steamstatic.com/steam/apps/{app_id}/header.jpg"
        img = f'<img src="{src}" alt="{esc(data["title"])} header image" onerror="this.style.display=\'none\'">'

    price = data["price"]
    price_txt = "Free to play" if price == 0 else f"${price:,.2f}"
    genres = "".join(f'<span class="chip genre">{esc(g)}</span>' for g in data["genres"])
    tags = "".join(f'<span class="chip">{esc(t)}</span>' for t in data["tags"][:8])
    desc = f'<p class="desc">{esc(data["description"])}</p>' if data["description"] else ""

    return (
        '<div class="game">'
        f"<div>{img}</div>"
        "<div>"
        f'<h2>{esc(data["title"])}</h2>'
        f'<div class="facts"><span class="price">{price_txt}</span><span>{data["reviews"]:,} public reviews</span></div>'
        f'<div class="chips">{genres}{tags}</div>'
        f"{desc}"
        "</div></div>"
    )


def run_ai(data: dict) -> str:
    try:
        return generate_page_feedback(data["title"], data["description"], data["genres"], data["tags"])
    except Exception as exc:  # keep the dashboard alive if the AI provider fails
        return f"The AI audit could not be generated: {exc}"


def set_example(url: str):
    st.session_state.url_input = url
    st.session_state.autorun = True


# ---------------------------------------------------------------------------
# Intro + input
# ---------------------------------------------------------------------------
st.session_state.setdefault("url_input", "")

st.markdown(
    '<div class="intro"><h1>Steam page estimator</h1>'
    "<p>Paste a Steam store link to estimate a game's owners and revenue, "
    "then get AI suggestions for turning more store visitors into wishlists.</p></div>",
    unsafe_allow_html=True,
)

with st.form("analyze"):
    input_col, button_col = st.columns([5, 1], vertical_alignment="bottom")
    with input_col:
        st.text_input(
            "Steam store link",
            key="url_input",
            placeholder="https://store.steampowered.com/app/1145360/Hades/",
        )
    with button_col:
        submitted = st.form_submit_button("Analyze", type="primary", use_container_width=True)

st.markdown('<span class="small">No link handy? Try one:</span>', unsafe_allow_html=True)
example_cols = st.columns([1, 1.7, 1, 5])
for col, (name, link) in zip(example_cols, EXAMPLES.items()):
    col.button(name, on_click=set_example, args=(link,), key=f"ex_{name}", use_container_width=True)

# ---------------------------------------------------------------------------
# Run analysis
# ---------------------------------------------------------------------------
autorun = st.session_state.pop("autorun", False)
if submitted or autorun:
    url = st.session_state.url_input.strip()
    if not url:
        st.warning("Paste a Steam store link first, for example https://store.steampowered.com/app/1145360/Hades/")
    else:
        with st.status("Reading the store page...", expanded=False) as status:
            data = scrape_steam_page(url)
            if data.get("error"):
                status.update(label="Could not read that page", state="error")
                st.error(f"{data['error']} Check that the link is a store page like /app/1145360/Game_Name/.")
                st.stop()

            data.setdefault("tags", [])
            data["reviews"] = data.get("reviews") or 0
            data["price"] = data.get("price") or 0.0
            data["genres"] = data.get("genres") or []
            data["description"] = data.get("description") or ""

            status.update(label="Writing the AI audit...")
            ai_text = run_ai(data)
            status.update(label=f"Done: {data['title']}", state="complete")

        st.session_state.result = {"url": url, "data": data, "ai": ai_text}

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
result = st.session_state.get("result")
if result:
    data = result["data"]
    st.markdown(game_header_html(data, result["url"]), unsafe_allow_html=True)

    tab_estimate, tab_audit, tab_method = st.tabs(["Revenue estimate", "AI page audit", "How it's calculated"])

    # --- Revenue estimate -------------------------------------------------
    with tab_estimate:
        left, right = st.columns([3, 2], gap="large")

        with right:
            st.markdown("**Adjust the assumptions**")
            multiplier = st.slider(
                "Reviews-to-owners multiplier",
                min_value=10,
                max_value=80,
                value=30,
                help="Estimated owners per public review. Rules of thumb vary by genre, price and audience.",
            )
            share_pct = st.slider(
                "Share kept after Steam's cut (%)",
                min_value=30,
                max_value=80,
                value=50,
                step=5,
                help="Steam takes 30%. Refunds and regional pricing lower what you keep further.",
            )
            share = share_pct / 100

            if data["reviews"] > 0 and data["price"] > 0:
                st.markdown("**What if the multiplier is off?**")
                st.markdown(
                    scenario_table(data["reviews"], data["price"], multiplier, share),
                    unsafe_allow_html=True,
                )

        with left:
            if data["reviews"] == 0:
                st.warning(
                    "No public reviews were found, so owners and revenue show as zero. "
                    "The game may be unreleased, or Steam did not return a review count."
                )
            if data["price"] == 0:
                st.info("This game is free to play, so revenue from sales is zero. Its income comes from in-game purchases, which this tool cannot see.")
            st.markdown(
                ledger_html(data["reviews"], multiplier, data["price"], share),
                unsafe_allow_html=True,
            )

    # --- AI audit ----------------------------------------------------------
    with tab_audit:
        with st.container(border=True):
            st.markdown(result["ai"])
        if st.button("Regenerate audit", key="regen"):
            with st.spinner("Writing a new audit..."):
                st.session_state.result["ai"] = run_ai(data)
            st.rerun()

    # --- Method ------------------------------------------------------------
    with tab_method:
        st.markdown(
            f"""
**1. Owners.** The Boxleiter method assumes each public review stands for a fixed number of owners.
Here, {data['reviews']:,} reviews × {multiplier} = **{int(data['reviews'] * multiplier):,} owners**.

**2. Gross revenue.** Owners × the current store price in USD.
Discounts, bundles and regional prices are not tracked, so this is an upper-bound style figure.

**3. Net revenue.** Steam keeps 30% of each sale. Refunds and cheaper regional pricing reduce what's left,
so the default keeps about 50% of gross. You can change this in the sliders.

**What this can't tell you.** These numbers are rules of thumb. Real sales depend on genre, wishlist conversion,
discount history and how many players leave reviews. Use the result as a ballpark, not as a sales report.
"""
        )

st.markdown(
    '<p class="small" style="margin-top:3rem">Built from public Steam store data. '
    "Not affiliated with or endorsed by Valve.</p>",
    unsafe_allow_html=True,
)