import os
import feedparser
from transformers import pipeline
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from datetime import time
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
try:
    load_dotenv()
except ImportError as e:
    print("python-dotenv not installed, skipping .env loading:", e)

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Load the pre-trained zero-shot classification pipeline
topic_classifier = pipeline("zero-shot-classification")

# Define candidate labels for the topic classifier
candidate_labels = ["AI", "Technology", "Health",
                    "Business", "Sports", "Entertainment", "Politics"]

# Function to fetch RSS feeds and classify the topic
def fetch_articles():
    summaries = []

    # Fetch RSS feeds (replace with your desired feeds)
    rss_url = "https://huggingface.co/blog/feed.xml"
    feed = feedparser.parse(rss_url)

    for entry in feed.entries[:5]:  # Top 5 articles
        title = entry.title
        link = entry.link
        

        # Use the pre-trained model to classify the topic of the article
        logging.info(f"Classifying topic for article: {title}")
        result = topic_classifier(title, candidate_labels)
        topic = result['labels'][0]  # The top predicted label
        logging.info(f"Predicted topic: {topic}")

        # Store article and classified topic
        summaries.append(
            f"Title: {title}\nTopic: {topic}\nRead more: {link}\n"
        )

    return summaries

# Function to send weekly summaries to the chat
async def send_weekly_summary(context: ContextTypes.DEFAULT_TYPE):
    summaries = fetch_articles()
    await context.bot.send_message(chat_id=CHAT_ID, text="\n\n".join(summaries))

# Command to start the bot
async def start(update, context):
    await update.message.reply_text(
        "Hello! I'm your AI Weekly News Bot. I will send you weekly AI news summaries."
    )

# Command to fetch and send article summaries on demand
async def update_command(update, context):
    summaries = fetch_articles()
    await update.message.reply_text("\n\n".join(summaries))

# Add the /update command handler
# (This should be registered in main(), but handler definition goes here)

# Main bot function
def main():
    application = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("update", update_command))

    # Schedule the job to run daily at 10:00
    application.job_queue.run_daily(
        send_weekly_summary,
        time=time(hour=10, minute=0)
    )

    application.run_polling()

if __name__ == "__main__":
    main()
