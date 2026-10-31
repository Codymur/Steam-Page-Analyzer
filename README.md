# 📊 Steam Page Estimator & AI Auditor

A Streamlit app that estimates a Steam game's owner count and revenue from its public store page, then uses an AI model (Llama 3.3 70B via Groq) to suggest how to improve the store page's conversion (visitors → wishlists → sales).

![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **Revenue and owner estimate** — pulls the live review count and price from Steam, then applies the community-standard **Boxleiter method** (reviews × a multiplier = owners) and a net-revenue share (~50% of gross after Steam's cut, refunds and regional pricing).
- **Revenue ledger** — the estimate is shown line by line (reviews → owners → gross → net), so you can see exactly how each number is reached.
- **Adjustable assumptions** — sliders for the multiplier and the share kept, plus a lower / current / higher comparison so the result reads as a range instead of one precise-looking number.
- **AI page audit** — sends the game's title, genres, community tags and short description to the AI model, which returns concrete suggestions for hooks, keywords and clarity. You can regenerate the audit with one click.
- **Clean dashboard** — game header with the store image, genre and tag chips, tabbed results, example links to try, and clear messages for free games, missing reviews or bad links.

## How it works

1. `scraper.py` extracts the App ID from the store URL and collects the title, price, genres, community tags, short description and public review count.
2. `app.py` runs the Boxleiter math on that data and renders the ledger, scenarios and results tabs. Results are kept in Streamlit session state, so moving a slider recalculates instantly without re-fetching data or calling the AI again.
3. `ai_analyzer.py` sends the metadata to Llama 3.3 70B through the Groq API and returns actionable suggestions for improving the page.

## Setup

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your own Groq API key:

```
GROQ_API_KEY=your_key_here
```

Get a free key from the [Groq Console](https://console.groq.com/keys). Your `.env` file is listed in `.gitignore`, so it will never be committed.

## Run it

```bash
streamlit run app.py
```

Paste a Steam store link, for example `https://store.steampowered.com/app/1145360/Hades/`, and click **Analyze** (or press Enter). You can also click one of the example games.

## Tech stack

- [Streamlit](https://streamlit.io/) — UI
- [Requests](https://docs.python-requests.org/) + [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) — fetching and parsing Steam data
- [Groq API](https://console.groq.com/) with Llama 3.3 70B — AI page audit
- [python-dotenv](https://pypi.org/project/python-dotenv/) — loading the API key from `.env`

## ⚠️ Accuracy disclaimer

The multiplier and net-revenue share are **rough industry rules of thumb**, not exact figures. Actual owner counts and net revenue vary a lot by genre, price, region, wishlist conversion and sale history. Treat the numbers as a ballpark, not as a sales report.

## A note on data sourcing

This project reads only publicly available Steam store data (game metadata, price, review count and community tags) at normal single-user request rates. Steam's Subscriber Agreement includes a broad clause on automated access to its site, so treat this as a personal and educational tool. Do not run it at large scale or use it commercially. This project is not affiliated with or endorsed by Valve.

## Known limitations

- Owner and revenue estimates are approximations, not verified sales data.
- Discounts, bundles, regional pricing and sales history are not tracked.
- Free-to-play games show zero sales revenue, because their income comes from in-game purchases that this tool cannot see.
- AI suggestions depend on how complete the page's existing description and tags are, and should be treated as ideas rather than guarantees.

## License

This project is licensed under the [MIT License](LICENSE).