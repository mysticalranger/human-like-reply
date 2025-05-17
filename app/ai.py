import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable not set!")

MODEL_NAME = "mistral-small-latest"

client = Mistral(api_key=api_key)

async def analyze_post(post_text: str) -> dict:
    """Analyze the post to determine tone, intent, and context"""
    
    analysis_prompt = """Analyze this social media post in detail with the following structure:
    1) TONE: The primary emotional tone (excited, professional, casual, frustrated, etc.)
    2) INTENT: The main purpose (sharing information, asking question, celebrating, venting, etc.)
    3) TOPICS: Key topics, entities, or concepts mentioned
    4) AUDIENCE: The likely intended audience (professionals, friends, specific community, etc.)
    5) CONTEXT: Any contextual elements (event references, trending topics, etc.)
    
    Format your analysis as JSON with these exact keys: tone, intent, topics, audience, context.
    """
    
    messages = [
        {"role": "system", "content": analysis_prompt},
        {"role": "user", "content": post_text}
    ]
    
    response = client.chat.complete(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.3,
        max_tokens=200
    )
    
    try:
        import json
        analysis_text = response.choices[0].message.content.strip()
        analysis = json.loads(analysis_text)
        return analysis
    except:
        # Fallback if JSON parsing fails
        return {
            "tone": "neutral",
            "intent": "sharing",
            "topics": ["general"],
            "audience": "general public",
            "context": "social media post"
        }

async def personalize_reply(platform: str, post_text: str, analysis: dict) -> str:
    """Generate a persona-specific reply based on platform and analysis"""
    
    # Define platform-specific personas
    personas = {
        "linkedin": "a thoughtful professional with expertise in the post topic",
        "twitter": "a witty, engaged user who likes quick, impactful exchanges",
        "instagram": "a supportive, visual-oriented person who uses emojis naturally"
    }
    
    persona = personas.get(platform.lower(), "a typical social media user")
    
    persona_prompt = f"""
    You are {persona} responding to a post on {platform}.
    
    The post has the following characteristics:
    - Tone: {analysis.get('tone', 'neutral')}
    - Intent: {analysis.get('intent', 'sharing')}
    - Main topics: {', '.join(analysis.get('topics', ['general']))}
    - Target audience: {analysis.get('audience', 'general')}
    
    Craft a reply that:
    1. Shows authentic engagement with the specific content
    2. Matches the communication style of {platform}
    3. Adds meaningful perspective or asks a thoughtful question
    4. Sounds completely human (varied sentence structure, natural language patterns)
    
    Avoid:
    - Generic responses that could apply to any post
    - Overly formal language or academic tone
    - Excessive enthusiasm or too many exclamation marks
    - Obviously AI-generated patterns like "As an AI language model..."
    """
    
    messages = [
        {"role": "system", "content": persona_prompt},
        {"role": "user", "content": post_text}
    ]
    
    response = client.chat.complete(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.7,
        max_tokens=120
    )
    
    return response.choices[0].message.content.strip()

async def refine_reply(draft_reply: str, platform: str) -> str:
    """Refine the draft reply to ensure it's truly authentic and platform-appropriate"""
    
    refinement_prompt = f"""
    Review this draft reply for {platform} and improve it to sound completely authentic:
    
    "{draft_reply}"
    
    Make these specific improvements:
    1. Adjust length to match typical {platform} replies (shorter for Twitter, more detailed for LinkedIn)
    2. Add natural language elements (informal contractions, casual phrasing where appropriate)
    3. Remove any AI-like patterns or overly perfect language
    4. Ensure it doesn't sound like a template
    
    Return only the refined reply text with no explanations.
    """
    
    messages = [
        {"role": "system", "content": refinement_prompt},
        {"role": "user", "content": draft_reply}
    ]
    
    response = client.chat.complete(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.5,
        max_tokens=120
    )
    
    return response.choices[0].message.content.strip()

async def generate_reply(platform: str, post_text: str) -> str:
    """Generate a human-like reply using an advanced 3-stage approach"""
    
    # Stage 1: Analyze the post in detail
    analysis = await analyze_post(post_text)
    
    # Stage 2: Generate a persona-based draft reply
    draft_reply = await personalize_reply(platform, post_text, analysis)
    
    # Stage 3: Refine the reply for maximum authenticity
    final_reply = await refine_reply(draft_reply, platform)
    
    return final_reply
