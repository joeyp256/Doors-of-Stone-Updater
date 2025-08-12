# Doors of Stone News Compiler

This project is a Python script that compiles recent news about the (hopefully) upcoming 3rd book in the Kingkiller Chronicles series(we still don't know what king gets killed) "The Doors of Stone" from various sources like Reddit and Twitter, generates summaries in the voices of different characters from the book series using the Gemini API, and sends a daily email with the compiled information. I didn't want to pay for a Twitter dev account, so I have only tested the Reddit side, which works great. 

## Features

  - **Multi-Source News Scraping:** Gathers the latest news from specified subreddits and Twitter accounts related to "The Doors of Stone" and Patrick Rothfuss.
  - **Character-Driven Summaries:** Uses the Gemini API to create unique summaries of the news in the distinct voices of Kvothe, Bast, and Chronicler.
  - **Automated Email Reports:** Compiles the summaries and a simple news rundown into an email and sends it to a specified recipient.
  - **Secure Configuration:** Designed to use environment variables for all sensitive credentials (API keys, email passwords), ensuring they are not hard-coded and exposed in the repository.

## Getting Started

To run this project, you need to set up the required dependencies and environment variables.

### Prerequisites

  - Python 3.6 or higher
  - `requests` library
  - `praw` library (for Reddit scraping)
  - `tweepy` library (for Twitter scraping)
  - An account with access to the Gemini API, a Reddit developer account, and a Twitter (X.com) developer account.
  - An email account with SMTP access (e.g., Gmail with an app password).

You can install the required Python libraries by running:

```bash
pip install requests praw tweepy
```

### Configuration

This script relies on environment variables for all sensitive information. **Do not hard-code these values in the script.**

Before running the script, set the following environment variables:

  - `GEMINI_API_KEY`: Your API key for the Gemini API.
  - `EMAIL_ADDRESS`: The email address you will use to send the reports.
  - `EMAIL_PASSWORD`: The app-specific password for your email account (eyou will probably have to generate this, link for how is here: https://support.google.com/mail/answer/185833?hl=en)
  - `RECIPIENT_EMAIL`: The email address where the reports will be sent.
  - `REDDIT_CLIENT_ID`: Your Reddit developer client ID.
  - `REDDIT_CLIENT_SECRET`: Your Reddit developer client secret.
  - `REDDIT_USER_AGENT`: A unique user agent string for your Reddit application.
  - `TWITTER_BEARER_TOKEN`: Your bearer token for the Twitter API v2.

You can set these variables in your shell or use a `.env` file and a library like `python-dotenv` for local development.

### Running the Script

Once you have installed the dependencies and set your environment variables, you can run the script from your terminal:

```bash
python DoSNews.py
```

This will run the full process: scraping, generating summaries, and sending the email. You can automate this process by scheduling it to run daily using a tool like `cron` (on Linux/macOS) or Task Scheduler (on Windows).
