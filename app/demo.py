import streamlit as st
import sys
import os
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai import generate_reply
from datetime import datetime
from app.cache import get_cached_reply, cache_reply

st.set_page_config(
    page_title="Social Media Reply Generator",
    page_icon="💬",
    layout="centered"
)

# Function with retry logic for rate limits
async def generate_with_retry(platform, post_text, max_retries=3):
    """Generate reply with automatic retry for rate limit errors"""
    # First check if we have a cached response
    cached_reply = get_cached_reply(platform, post_text)
    if cached_reply:
        return cached_reply, True  # Second value indicates it's from cache
    
    # No cache, try to generate with retries
    retries = 0
    while retries <= max_retries:
        try:
            reply = await generate_reply(platform, post_text)
            # Cache the successful response
            cache_reply(platform, post_text, reply)
            return reply, False  # Not from cache
        except Exception as e:
            if "429" in str(e) and retries < max_retries:
                # Rate limit hit - wait with exponential backoff
                wait_time = 2 ** retries + 1  # 1, 3, 7 seconds
                with st.status(f"Rate limit reached. Waiting {wait_time}s and trying again..."):
                    time.sleep(wait_time)
                retries += 1
            else:
                # Either not a rate limit or we've exhausted retries
                raise

st.title("💬 Social Media Reply Generator")
st.subheader("Generate human-like replies to social media posts")

with st.form("reply_form"):
    platform = st.selectbox(
        "Select Platform",
        ["linkedin", "twitter", "instagram"],
        help="Choose the social media platform"
    )
    
    post_text = st.text_area(
        "Enter the social media post",
        height=150,
        help="Paste or type the post you want to reply to"
    )
    
    submitted = st.form_submit_button("Generate Reply")

if submitted and post_text:
    with st.spinner("Generating human-like reply..."):
        try:
            # Use our retry function with ThreadPoolExecutor
            with ThreadPoolExecutor() as executor:
                def run_async_generate():
                    return asyncio.run(generate_with_retry(platform, post_text))
                
                future = executor.submit(run_async_generate)
                reply, from_cache = future.result()
            
            if from_cache:
                st.success("Reply retrieved from cache!")
            else:
                st.success("Reply generated successfully!")
            
            st.markdown("### Generated Reply:")
            st.markdown(f"""<div style='
                background-color: #f0f2f6;
                padding: 15px;
                border-radius: 10px;
                color: #333333;
                font-size: 16px;
                line-height: 1.5;
                border: 1px solid #e0e0e0;
            '>{reply}</div>""", unsafe_allow_html=True)
            
            # Display platform-specific emoji
            platform_emoji = {"linkedin": "💼", "twitter": "🐦", "instagram": "📸"}
            
            st.markdown(f"**Platform:** {platform_emoji.get(platform, '🌐')} {platform.capitalize()}")
            
            
            
        except Exception as e:
            st.error(f"Error generating reply: {str(e)}")

st.markdown("---")
st.markdown("### How it works")
st.markdown("""
This tool uses a sophisticated AI approach to generate authentic-sounding replies:

1. **Post Analysis**: Analyzes the tone, intent, and content of the post
2. **Platform Adaptation**: Tailors the reply style to each platform's unique culture
3. **Human-Like Generation**: Creates responses that avoid common AI patterns
4. **Quality Assurance**: Ensures replies are engaging and relevant
""")