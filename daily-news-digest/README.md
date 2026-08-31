# Daily News Digest

An automated daily news digest that fetches top headlines across seven
categories (Tech, Sports, Finance, World Politics, India, Andhra Pradesh
in English, and Andhra Pradesh in Telugu), renders them into a styled
HTML page, publishes the page via GitHub Pages, screenshots it, and
sends the screenshot to a Telegram chat — all on an automatic daily
schedule via GitHub Actions.

## How it works

1. **`scripts/fetch_news.py`** — pulls the top 5 headlines per category
   using RSS feeds (mostly Google News RSS search feeds, plus
   TechCrunch for Tech and BBC Sport for Sports) and saves them to
   `data/news.json`.
2. **`scripts/generate_html.py`** — renders `data/news.json` through the
   Jinja2 template at `templates/digest.html` into `docs/index.html`
   (a dark-gradient, color-coded-by-category page using Poppins and
   Noto Sans Telugu fonts).
3. **`scripts/screenshot.py`** — uses Playwright to take a full-page
   screenshot of `docs/index.html`, saved as `digest.png`.
4. **`scripts/send_telegram.py`** — sends `digest.png` to a Telegram
   chat via the Bot API, with a caption linking to the live GitHub
   Pages URL.
5. **`.github/workflows/daily-news.yml`** — runs all of the above every
   day at **01:00 UTC (6:30 AM IST)**, commits the updated
   `data/news.json` and `docs/index.html` back to the repo, and can
   also be triggered manually.

## Setup instructions

### 1. Create the repository

Create a new GitHub repository (public or private) and push this
project's contents to it — the workflow expects the layout exactly as
provided (`.github/workflows/`, `scripts/`, `templates/`, `data/`,
`docs/`, `requirements.txt`).

```bash
git init
git add .
git commit -m "Initial commit: daily news digest"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### 2. Enable GitHub Pages from `/docs`

1. In your repository, go to **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a
   branch**.
3. Set **Branch** to `main` and the folder to **`/docs`**.
4. Save. GitHub will give you a live URL that looks like:
   `https://<your-username>.github.io/<your-repo>/`

   > Note: `docs/index.html` doesn't exist until the workflow runs at
   > least once (see step 4 below), so Pages will show a 404 until
   > then.

### 3. Add the 3 required secrets

Go to **Settings → Secrets and variables → Actions → New repository
secret** and add:

| Secret name          | Value                                                        |
|-----------------------|--------------------------------------------------------------|
| `TELEGRAM_BOT_TOKEN`  | Token from [@BotFather](https://t.me/BotFather)               |
| `TELEGRAM_CHAT_ID`    | The chat/group/channel ID the digest should be sent to        |
| `PAGE_URL`            | Your live GitHub Pages URL, e.g. `https://<user>.github.io/<repo>/` |

**How to get a Telegram bot token and chat ID:**
1. Message [@BotFather](https://t.me/BotFather) on Telegram, send
   `/newbot`, and follow the prompts to get your bot token.
2. Add the bot to the target chat/group/channel (or message it
   directly for a private chat).
3. Send any message to the bot/chat, then visit
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in a
   browser to find the `chat.id` value in the JSON response.

### 4. Run the workflow manually to test

1. Go to the **Actions** tab in your repository.
2. Select the **Daily News Digest** workflow in the left sidebar.
3. Click **Run workflow** (top right) → **Run workflow** again to
   confirm.
4. Watch the run — it should fetch news, generate `docs/index.html`,
   screenshot it, commit the changes, and send the screenshot to your
   Telegram chat.
5. Once it succeeds, refresh your GitHub Pages URL to see the live
   digest, and check Telegram for the photo message.

After this first successful manual run, the workflow will continue to
run automatically every day at 01:00 UTC (6:30 AM IST).

## Local development

You can also run each step locally:

```bash
pip install -r requirements.txt
playwright install --with-deps chromium

python scripts/fetch_news.py
python scripts/generate_html.py
python scripts/screenshot.py

export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
export PAGE_URL="https://<user>.github.io/<repo>/"
python scripts/send_telegram.py
```

## Project structure

```
daily-news-digest/
├── .github/
│   └── workflows/
│       └── daily-news.yml      # Scheduled + manual workflow
├── data/
│   └── news.json               # Latest fetched headlines (generated)
├── docs/
│   └── index.html              # Published digest page (generated, served by GitHub Pages)
├── scripts/
│   ├── fetch_news.py           # Step 1: fetch headlines via RSS
│   ├── generate_html.py        # Step 2: render HTML from news.json
│   ├── screenshot.py           # Step 3: screenshot the HTML page
│   └── send_telegram.py        # Step 4: send screenshot to Telegram
├── templates/
│   └── digest.html             # Jinja2 template used by generate_html.py
├── requirements.txt
└── README.md
```

## Customizing categories

To add, remove, or change categories/queries, edit the `CATEGORIES`
dictionary in `scripts/fetch_news.py` and the matching entry in the
`CATEGORY_META` dictionary in `scripts/generate_html.py` (for the
icon/color/font used on the page).
