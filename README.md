# AI Weekly Telegram Bot

A Python-based Telegram bot that sends weekly AI news summaries. The bot fetches content via **RSS feeds** and light **web scraping** from reliable sources like **Hugging Face**, **TechCrunch**, and others. It sends a brief summary with the article title, description, and a link to the full content.

## Features

- Fetches AI news from top sources using RSS feeds
- Light web scraping for additional content
- Weekly summaries sent via Telegram
- Easy setup with minimal dependencies
- Deployed on **Azure App Service (Free Tier)**

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/ai-weekly-bot.git
   cd ai-weekly-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a new bot with [BotFather](https://core.telegram.org/bots#botfather) on Telegram and get the **API Token**.

4. Set up environment variables:
   - `TELEGRAM_API_TOKEN`: Your Telegram bot API token
   - `RSS_FEED_URLS`: List of RSS feed URLs for AI news sources (e.g., Hugging Face, TechCrunch)

5. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

- The bot will automatically send a weekly summary of the latest AI news.
- You can configure the bot to check specific RSS feeds and scrape additional sites as needed.

## Deployment

For continuous operation, deploy the bot on a platform like **Azure App Service** (Free Tier) or any other cloud service that supports Python.

## Contributing

Feel free to fork the repository and submit pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
