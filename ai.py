import re
import os
import google.genai as genai

from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
if not client:
    raise ValueError("API Key not found! Check your .env file.")

# Configuration
MAX_INPUT_CHARS = 3500 

def clean_noise(text):
    # MUST keep newlines for the regex logic to work well
    lines = text.splitlines()
    noise_patterns = re.compile(r'(decimal|varchar|datetime|table name|field name|bytes|pk|fk|0x[0-9])', re.I)
    
    keep = [l.strip() for l in lines if len(l.strip()) > 5 and not noise_patterns.search(l)]
    return "\n".join(keep)

def extract_between_headers(text):
    # Standard Senior Project Headers
    targets = ["motivation", "problem statement", "objective", "methodology", "conclusion", "results"]
    extracted = []
    
    # Sort targets by where they appear in the text to avoid jumping backwards
    found_positions = []
    for t in targets:
        match = re.search(rf'\b{t}\b', text, re.I)
        if match:
            found_positions.append((match.start(), t))
    
    found_positions.sort() # Order them as they appear in the doc

    for i in range(len(found_positions)):
        start_idx, current_header = found_positions[i]
        
        # Determine where to stop: either the next found header or the end of doc
        if i + 1 < len(found_positions):
            end_idx = found_positions[i+1][0]
        else:
            end_idx = start_idx + 1500 # Cap the final section (Conclusion) to 1500 chars
            
        segment = text[start_idx:end_idx].strip()
        if len(segment) > 20:
            extracted.append(segment)

    return "\n\n".join(extracted)

def generate_summary(raw_text):
    # 1. Clean technical noise
    text = clean_noise(raw_text)

    # 2. Extract specific content
    content = extract_between_headers(text)

    # 3. Fallback if no headers found
    if len(content) < 300:
        content = text[:2000] + "\n[...]\n" + text[-1500:]

    # 4. TOKEN SAVER: Collapse whitespace
    content = re.sub(r'\s+', ' ', content).strip()[:2500]
    prompt = "Summarize project. Format: Problem: Objective: Method: Features: Result: Max 200 words."

    # --- ADD THIS LINE HERE TO CHECK ---
    print("\n" + "="*30 + " TRIMMED TEXT FOR GEMINI " + "="*30)
    print(content)
    print("="*85 + "\n")
    # -----------------------------------
    try:
        # 2. Use the client.models.generate_content method
        response = client.models.generate_content(
            model="gemini-2.5-flash", # Use a 2026 stable model
            contents=f"{prompt} Text:{content}"
        )

        return response.text.strip()

    except Exception as e:
        print("GEMINI ERROR:", e)
        return "Summary unavailable."
    
# Use the client initialized at the top of your ai.py
def extract_clean_keyword(raw_text: str):
    """Refines raw search trends into clean technical topics."""
    try:
        # Use the newer client.models syntax from your example
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=f"Extract the core technical topic from: '{raw_text}'. Return only the topic name (1-3 words)."
        )
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Gemini refinement failed: {e}")
        return raw_text # Fallback to raw text