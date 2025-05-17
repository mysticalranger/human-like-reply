import csv
import os
import sys
import asyncio
import time
import random
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add the project root to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import from app
from app.ai import generate_reply
from app.db import save_reply
from mistralai.models.sdkerror import SDKError

load_dotenv()

# This path is relative to where the script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "posts - Sheet1.csv")

# Track which posts we've already processed
PROGRESS_FILE = os.path.join(SCRIPT_DIR, "import_progress.txt")

async def generate_reply_with_retry(platform, post_text, max_retries=5):
    """Generate a reply with retry logic for rate limits"""
    retries = 0
    base_delay = 2  # Start with a 2-second delay
    
    while retries <= max_retries:
        try:
            return await generate_reply(platform, post_text)
        except SDKError as e:
            if "429" in str(e) and retries < max_retries:
                # Calculate delay with exponential backoff and jitter
                delay = base_delay * (2 ** retries) + random.uniform(0, 1)
                print(f"Rate limit hit, retrying in {delay:.2f} seconds...")
                time.sleep(delay)
                retries += 1
            else:
                raise  # Re-raise if it's not a rate limit or we've exhausted retries

async def import_posts():
    # Get last processed index
    last_processed = -1
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            try:
                last_processed = int(f.read().strip())
                print(f"Resuming from post {last_processed + 1}")
            except ValueError:
                pass

    try:
        with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                # Skip already processed rows
                if i <= last_processed:
                    continue
                    
                platform = row["platform"]
                
                # Normalize platform name
                if platform.lower() == "insta":
                    platform = "instagram"
                
                post_text = row["post_text"]
                print(f"Processing {i+1}: {platform} - {post_text[:40]}...")
                
                # Add a pause between requests to avoid rate limits
                if i > 0:
                    time.sleep(3)  # Wait 3 seconds between requests
                
                try:
                    # Generate reply using your AI function with retry logic
                    generated_reply = await generate_reply_with_retry(platform, post_text)
                    timestamp = datetime.now(timezone.utc).isoformat()
                    reply_record = {
                        "platform": platform,
                        "post_text": post_text,
                        "generated_reply": generated_reply,
                        "timestamp": timestamp
                    }
                    await save_reply(reply_record)
                    print(f"Imported {i+1}: {platform} - {post_text[:40]}...")
                    
                    # Update progress
                    with open(PROGRESS_FILE, 'w') as f:
                        f.write(str(i))
                    
                except Exception as e:
                    print(f"Error processing post {i+1}: {str(e)}")
                    # Don't break the loop, try the next post
                    
    except FileNotFoundError:
        print(f"Error: CSV file not found at {CSV_PATH}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Script directory: {SCRIPT_DIR}")
        print("Please make sure the CSV file is in the correct location.")

if __name__ == "__main__":
    asyncio.run(import_posts())