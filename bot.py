import os
import time
import json
import logging
import yaml
import feedparser
from datetime import time as dtime
from transformers import pipeline
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

try:
    load_dotenv()
except Exception as e:
    logging.warning(f"skipping .env loading: {e}")

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
STORAGE_FILE = "sent_articles.json"
CONFIG_FILE = "config.yaml"
MAX_MESSAGE_LENGTH = 4096

# Default configuration if config.yaml is missing or empty
DEFAULT_CONFIG = {
    "rss_feeds": [
        "https://huggingface.co/blog/feed.xml",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://ai.googleblog.com/feeds/posts/default",
        "https://www.deepmind.com/blog/rss.xml",
        "https://www.technologyreview.com/feed/topic/artificial-intelligence/",
        "https://export.arxiv.org/rss/cs.AI",
        "https://export.arxiv.org/rss/cs.LG"
    ],
    "candidate_labels": [
        "AI", "Technology", "Health", "Business", "Sports", "Entertainment", "Politics"
    ]
}

# Load configuration from YAML or fallback to default
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f) or DEFAULT_CONFIG
else:
    config = DEFAULT_CONFIG

RSS_FEED_URLS = config.get("rss_feeds", [])
candidate_labels = config.get("candidate_labels", [])

# Load model
topic_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    revision="d7645e1"
)

def format_article_summary(title, topic, link, summary=None):
    formatted = f"*{title}*\n_Topic: {topic}_\n"
    if summary:
        formatted += f"{summary}\n"
    formatted += f"[Read more]({link})\n"
    return formatted

def load_sent_links():
    if not os.path.exists(STORAGE_FILE):
        return set()
    with open(STORAGE_FILE, "r") as f:
        data = json.load(f)
        return set(data.get("sent_links", []))

def save_sent_links(sent_links):
    with open(STORAGE_FILE, "w") as f:
        json.dump({"sent_links": list(sent_links)}, f)

def split_message(text, max_length=MAX_MESSAGE_LENGTH):
    chunks = []
    while len(text) > max_length:
        split_index = text[:max_length].rfind('\n\n')
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index])
        text = text[split_index:]
    chunks.append(text)
    return chunks

def fetch_articles():
    summaries = []
    now = time.time()
    one_week_ago = now - (7 * 86400)
    sent_links = load_sent_links()
    new_links = set()

    for rss_url in RSS_FEED_URLS:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if not published or time.mktime(published) < one_week_ago:
                continue

            link = entry.link
            if link in sent_links:
                continue

            title = entry.title
            import html
            summary = getattr(entry, "summary", None)
            if summary:
                summary = html.unescape(summary)
            logging.info(f"Classifying topic for article: {title}")
            result = topic_classifier(summary if summary else title, candidate_labels)
            topic = result['labels'][0]
            logging.info(f"Predicted topic: {topic}")

            summaries.append(format_article_summary(title, topic, link, summary=summary))
            new_links.add(link)

    if new_links:
        sent_links.update(new_links)
        save_sent_links(sent_links)

    return summaries

async def send_weekly_summary(context: ContextTypes.DEFAULT_TYPE):
    summaries = fetch_articles()
    if not summaries:
        await context.bot.send_message(chat_id=CHAT_ID, text="No new AI articles found this week.")
        return

    full_text = "\n\n".join(summaries)
    for chunk in split_message(full_text):
        await context.bot.send_message(chat_id=CHAT_ID, text=chunk, parse_mode="Markdown")

async def start(update, context):
    await update.message.reply_text("Hello! I'm your AI Weekly News Bot. I will send you weekly AI news summaries.")

async def update_command(update, context):
    summaries = fetch_articles()
    if not summaries:
        await update.message.reply_text("No new AI articles found.")
        return

    full_text = "\n\n".join(summaries)
    for chunk in split_message(full_text):
        await update.message.reply_text(chunk, parse_mode="Markdown")

def main():
    application = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("update", update_command))
    application.job_queue.run_daily(send_weekly_summary, time=dtime(hour=10, minute=0))
    application.run_polling()

if __name__ == "__main__":
    main()
