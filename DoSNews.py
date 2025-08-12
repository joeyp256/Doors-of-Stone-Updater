import os
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone # Import timezone for UTC handling

# --- Configuration ---
# IMPORTANT: Replace these with your actual API keys and email credentials.
# It's highly recommended to use environment variables for sensitive information.
# Example: 
#          export GEMINI_API_KEY=
#          export EMAIL_ADDRESS="your_email@example.com" 
#          export EMAIL_PASSWORD=
#          export RECIPIENT_EMAIL="recipient_email@example.com"
#          export REDDIT_CLIENT_ID=
#          export REDDIT_CLIENT_SECRET=	
#          export REDDIT_USER_AGENT=
#          export TWITTER_BEARER_TOKEN=


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS", "your_email@example.com")
SENDER_EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_email_app_password") # Use an app password if using Gmail/Outlook
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "recipient_email@example.com")

# Reddit API credentials (if you implement PRAW)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "YOUR_REDDIT_CLIENT_ID_HERE")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "YOUR_REDDIT_CLIENT_SECRET_HERE")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "DoorsOfStoneNewsCompiler/1.0 (by /u/YourRedditUsername)") # IMPORTANT: Change this to a unique string and your Reddit username

# Twitter API credentials (for Tweepy Client v2)
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "YOUR_TWITTER_BEARER_TOKEN_HERE")

# --- Character Prompts ---
# Define the prompts for each character's voice
CHARACTER_PROMPTS = {
    'Kvothe': """You are Kvothe, the legendary arcanist and adventurer. Summarize the following news about 'The Doors of Stone' in your characteristic poetic, sometimes dramatic, and self-aware voice, as if you are recounting a story. Reflect on the implications of the news for the world and your own journey. Make it sound like a personal letter or journal entry. Please keep the response to a paragraph or two.""",
    'Bast': """You are Bast, Kvothe's loyal fae assistant. Summarize the following news about 'The Doors of Stone' in your charming, slightly mischievous, and sometimes exasperated voice. Express your excitement, concerns, and your need for this sotry to continue. Please keep the response to a paragraph or two. """,
    'Chronicler': """You are the Chronicler, a man on a mission to get the full story of Kvothe. Summerize the following news about 'The Doors of Stone' in a scholoarly, longing manner. You have been waiting for the end of this story for a long time, and you are desparate for news. Please keep the response to a paragraph or two.""",

}

# --- Web Scraping Functions ---

def get_reddit_news():
    """
    Fetches all recent posts from specified subreddits for the last 24 hours.
    Requires 'praw' library.
    """
    print("Fetching all recent posts from Reddit for the last 24 hours...")
    news_snippets = []
    try:
        import praw
        # Initialize Reddit instance
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )

        # Calculate timestamp for 24 hours ago in UTC
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        one_day_ago_timestamp = one_day_ago.timestamp()

        # Search relevant subreddits
        subreddits = ['KingkillerChronicle'] # Add more as needed
        # Keywords are no longer used for filtering, but kept here for reference if needed later.
        # keywords = ['doors of stone', 'patrick rothfuss', 'kingkiller chronicle book 3']

        for sub_name in subreddits:
            subreddit = reddit.subreddit(sub_name)
            # Fetch recent posts (e.g., top 20 new posts)
            # Filter by time, but no longer by specific keywords in title/selftext.
            for submission in subreddit.new(limit=20): # Adjust limit as needed
                if submission.created_utc >= one_day_ago_timestamp:
                    # No keyword filtering applied here, all posts within the last 24 hours are included.
                    news_snippets.append(f"Reddit ({sub_name}): {submission.title} - {submission.url}")
    except ImportError:
        print("PRAW library not found. Skipping Reddit news. Install with: pip install praw")
        news_snippets.append("Reddit (Simulated): Patrick Rothfuss mentioned a new draft in a rare comment.")
        news_snippets.append("Reddit (Simulated): Fan theory about the Chandrian's true motives gained traction.")
    except Exception as e:
        print(f"Error fetching Reddit news: {e}")
        news_snippets.append("Reddit (Error/Simulated): Could not retrieve live Reddit news.")

    return news_snippets

def get_twitter_news():
    """
    Fetches news from Twitter (X.com) for the last 24 hours.
    Requires 'tweepy' library and a Twitter Developer Account with Bearer Token.
    """
    print("Fetching news from Twitter (X.com) for the last 24 hours...")
    news_snippets = []
    try:
        import tweepy
        # Initialize Tweepy Client for Twitter API v2
        # Bearer Token is typically used for read-only access to public data.
        client = tweepy.Client(TWITTER_BEARER_TOKEN)

        # Calculate start_time for the last 24 hours in ISO 8601 format (UTC)
        # Twitter API v2 requires timestamps in 'YYYY-MM-DDTHH:mm:ssZ' format
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        start_time_iso = one_day_ago.isoformat(timespec='seconds') + 'Z'

        # Search for tweets
        # Query for relevant keywords/hashtags
        query = '#DoorsOfStone OR #KingkillerChronicle OR @PatrickRothfuss'
        response = client.search_recent_tweets(
            query,
            tweet_fields=["created_at"], # Request created_at field to confirm time
            start_time=start_time_iso,
            max_results=5 # Adjust as needed, max 100 for recent search
        )

        if response.data:
            for tweet in response.data:
                news_snippets.append(f"Twitter: {tweet.author_id}: {tweet.text} (Created: {tweet.created_at})")
        else:
            print("No recent tweets found matching the query.")

    except ImportError:
        print("Tweepy library not found. Skipping Twitter news. Install with: pip install tweepy")
    except tweepy.TweepyException as e:
        print(f"Error fetching Twitter news (TweepyException): {e}")
        if "401 Unauthorized" in str(e) or "403 Forbidden" in str(e):
            print("Please check your TWITTER_BEARER_TOKEN and ensure your Twitter Developer App has the necessary permissions and access level.")
        news_snippets.append("Twitter (Error/Simulated): Could not retrieve live Twitter news.")
    except Exception as e:
        print(f"An unexpected error occurred fetching Twitter news: {e}")
        news_snippets.append("Twitter (Error/Simulated): Could not retrieve live Twitter news.")

    return news_snippets



def compile_all_news():
    """
    Compiles news from all sources.
    """
    all_news = []
    all_news.extend(get_reddit_news())
    all_news.extend(get_twitter_news())
    return "\n".join(all_news) if all_news else "No new updates found today."

# --- Gemini API Integration ---

def call_gemini_api(prompt):
    """
    Calls the Gemini API to generate content based on the prompt.
    """
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        if result.get('candidates') and len(result['candidates']) > 0 and \
           result['candidates'][0].get('content') and \
           result['candidates'][0]['content'].get('parts') and \
           len(result['candidates'][0]['content']['parts']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"Unexpected API response structure: {result}")
            return "Error: Could not generate summary due to unexpected API response."
    except requests.exceptions.RequestException as e:
        print(f"Network or API error: {e}")
        return f"Error: Failed to connect to Gemini API. {e}"
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return f"Error: Failed to parse API response. {e}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"Error: An unexpected error occurred during Gemini API call. {e}"

def generate_character_summary(news_snippets, character_name='Kvothe'):
    """
    Generates a news summary in the voice of the selected character.
    """
    character_prompt = CHARACTER_PROMPTS.get(character_name, CHARACTER_PROMPTS['Kvothe'])
    full_prompt = f"{character_prompt}\n\nNews Snippets:\n{news_snippets}\n\nSummary:"
    print(f"Generating summary in {character_name}'s voice...")
    summary = call_gemini_api(full_prompt)
    return summary

def generate_simple_summary(news_snippets):
    """
    Generates a basic, simple rundown of the news in a neutral tone.
    """
    prompt = f"Provide a concise, neutral, and factual summary of the following news snippets about 'The Doors of Stone'. Focus on key updates and avoid speculative language.\n\nNews Snippets:\n{news_snippets}\n\nSimple Rundown:"
    print("Generating simple rundown...")
    summary = call_gemini_api(prompt)
    return summary

# --- Email Sending Function ---

def send_email(subject, body, to_email, from_email, from_password):
    """
    Sends an email with the given subject and body.
    """
    print(f"Attempting to send email to {to_email}...")
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # For Gmail: 'smtp.gmail.com', 587
        # For Outlook: 'smtp.office365.com', 587
        # Check your email provider's SMTP settings
        server = smtplib.SMTP('smtp.gmail.com', 587) # Example for Gmail
        server.starttls()  # Enable TLS encryption
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Email sending failed: Authentication error. Check your email address and app password.")
        print("For Gmail, you might need to generate an 'App password' for third-party apps.")
        return False
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

# --- Main Application Logic ---

def main():
    """
    Main function to run the news compilation and email sending process.
    """
    print(f"--- Running Doors of Stone News Compiler ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")

    # 1. Compile news from various sources
    compiled_news = compile_all_news()
    print("\n--- Compiled News ---")
    print(compiled_news)

    # 2. Choose a random character for the voice (or set a specific one)
    import random
    character_names = list(CHARACTER_PROMPTS.keys())
    selected_character = random.choice(character_names)
    print(f"\n--- Selected Character: {selected_character} ---")

    # 3. Generate summary in character's voice using Gemini
    character_summary = generate_character_summary(compiled_news, selected_character)
    print("\n--- Generated Summary ---")
    print(character_summary)

    # 4. Generate a basic, simple rundown using Gemini
    simple_rundown = generate_simple_summary(compiled_news)
    print("\n--- Generated Simple Rundown ---")
    print(simple_rundown)

    # 5. Prepare and send the email
    email_subject = f"Your Daily Doors of Stone Update (from {selected_character})"
    email_body = f"Greetings,\n\nHere is your daily update on 'The Doors of Stone', brought to you in the voice of {selected_character}:\n\n"
    email_body += character_summary
    email_body += "\n\n"

    # Add the basic rundown
    email_body += "--- Basic Rundown ---\n"
    email_body += simple_rundown
    email_body += "\n\n" # Add a line break for separation

    email_body += "\n\nMay your curiosity be sated, and your patience rewarded.\n\n"
    email_body += f"- The Doors of Stone News Compiler ({selected_character}'s Voice)"
    email_body += f"\n\n--- Raw News Snippets ---\n{compiled_news}"

    send_email(email_subject, email_body, RECIPIENT_EMAIL, SENDER_EMAIL, SENDER_EMAIL_PASSWORD)

    print("\n--- Process Completed ---")

if __name__ == "__main__":
    main()
