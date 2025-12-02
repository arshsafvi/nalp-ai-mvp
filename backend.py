from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import warnings
import json
import glob
import random
from datetime import datetime

# Suppress the annoying search warning
warnings.filterwarnings("ignore", category=RuntimeWarning) 
from duckduckgo_search import DDGS

load_dotenv()
app = FastAPI()

# --- 1. UPGRADED KNOWLEDGE BASE (Now with URLs) ---
TOOL_PRICING = {
    "Lovable": {"type": "Frontend AI", "cost": "$20/mo", "url": "https://lovable.dev", "best_for": "Visuals first, zero code"},
    "FlutterFlow": {"type": "Mobile Builder", "cost": "$30/mo", "url": "https://flutterflow.io", "best_for": "Native mobile apps"},
    "Bubble": {"type": "Web Builder", "cost": "$29/mo", "url": "https://bubble.io", "best_for": "Complex logic without code"},
    "v0 (Vercel)": {"type": "UI Gen", "cost": "Free", "url": "https://v0.dev", "best_for": "React/Tailwind components"},
    "Replit": {"type": "Full Stack", "cost": "$25/mo", "url": "https://replit.com", "best_for": "Zero to MVP, Python/Node"},
    "Cursor": {"type": "AI Editor", "cost": "$20/mo", "url": "https://cursor.com", "best_for": "Pro coding, refactoring"},
    "Bolt": {"type": "Web Prototyper", "cost": "Free", "url": "https://bolt.new", "best_for": "Instant full-stack web apps"},
    "Railway": {"type": "Hosting", "cost": "$5/mo", "url": "https://railway.app", "best_for": "Easy backend deployment"},
    "Supabase": {"type": "Database", "cost": "Free Tier", "url": "https://supabase.com", "best_for": "Postgres, Auth, Realtime"},
    "Firebase": {"type": "Backend", "cost": "Free Tier", "url": "https://firebase.google.com", "best_for": "Mobile backends"},
    "Make": {"type": "Automation", "cost": "Free Tier", "url": "https://make.com", "best_for": "Connecting apps together"},
    "Pinecone": {"type": "Vector DB", "cost": "Free Tier", "url": "https://pinecone.io", "best_for": "AI Memory/Embeddings"},
    "Hugging Face": {"type": "AI Models", "cost": "Free Tier", "url": "https://huggingface.co", "best_for": "Hosting open-source LLMs"},
    "Resend": {"type": "Email", "cost": "Free Tier", "url": "https://resend.com", "best_for": "Transactional emails"},
    "Clerk": {"type": "Auth", "cost": "Free Tier", "url": "https://clerk.com", "best_for": "User Logins"},
    "OpenAI API": {"type": "LLM", "cost": "Pay-as-you-go", "url": "https://openai.com/api", "best_for": "Intelligence"},
}

# Create a text list for the AI to read
AVAILABLE_TOOLS_TXT = "\n".join([f"- {name}: {info['best_for']} ({info['cost']})" for name, info in TOOL_PRICING.items()])

CONSULTANT_SYSTEM_PROMPT = f"""You are a Senior Solutions Architect. Your job is to build concrete, actionable tech stacks.

## YOUR TOOLBOX (You MUST pick from this list):
{AVAILABLE_TOOLS_TXT}

## STRICT RULES (DO NOT BREAK):
1. **NO GENERIC ADVICE:** Do not say "Use a database." You MUST say "Use Supabase."
2. **NO ABSTRACTIONS:** Do not say "Implement Authentication." Say "Set up Clerk for authentication."
3. **CONNECT THE DOTS:** Explain exactly how Tool A talks to Tool B (e.g., "Use Make to send data from FlutterFlow to Supabase").
4. **BUDGET CONSCIOUS:** If the user budget is low, DO NOT recommend expensive enterprise tools.
"""

# --- 2. DATA MODELS ---
class IdeaRequest(BaseModel):
    app_idea: str

class PlanRequest(BaseModel):
    app_idea: str
    questions: list[str] = []
    answers: list[str] = []
    budget: str
    skill: str
    priority: str
    vibe: str = "Senior Engineer"

# --- 3. HISTORY SYSTEM ---
HISTORY_DIR = "history"
if not os.path.exists(HISTORY_DIR): os.makedirs(HISTORY_DIR)

class HistoryItem(BaseModel):
    id: str; timestamp: str; app_idea: str; budget: str; skill: str; plan: str 

# --- 4. HELPERS ---
def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key: raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")
    return genai.Client(api_key=api_key)

def perform_live_search(query: str, max_results=3):
    print(f"🔎 Searching: {query}")
    try:
        results = DDGS().text(query, max_results=max_results)
        return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        print(f"Search Error: {e}")
        return "No live search results available. Rely on internal knowledge."

# --- 5. ENDPOINTS ---
@app.get("/")
def health_check(): return {"status": "online", "model": "gemini-1.5-pro"}

@app.post("/analyze_idea")
def analyze_idea(request: IdeaRequest):
    client = get_client()
    
    # Updated Prompt: Force 3-5 distinct, non-generic questions
    prompt = f"""
    Analyze this app idea: "{request.app_idea}"
    
    Task: Generate 3 to 5 specific, technical clarifying questions.
    
    Constraints:
    - Do NOT ask "Who is the target audience?" (Assume we know).
    - Do NOT ask "What is the budget?" (We already know).
    - Ask about: Technical complexity, Real-time needs, Data volume, or specific integrations.
    - Be curious and challenging.
    
    Output Format: Just the questions, numbered 1-5.
    """
    try:
        # Using 1.5-pro for smarter questions with higher temp for randomness
        response = client.models.generate_content(
            model="gemini_2.5-flash", 
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.9)
        )
        text = response.text if response.text else ""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        questions = [l.lstrip('0123456789.-*) ').strip() for l in lines]
        return {"questions": questions[:5]} # Cap at 5
    except Exception as e:
        return {"questions": ["Does this app need real-time chat?", "Will users upload videos/images?", "Do you need a web admin panel?"]}

@app.post("/generate_plan")
def generate_plan(request: PlanRequest):
    client = get_client()
    
    # 1. Search (Specific Query)
    search_res = perform_live_search(f"best no-code tools to build {request.app_idea} 2025")
    
    # 2. Vibe
    vibe_map = {
        "Brutal Truth": "Be blunt. If the budget is too low for the idea, SAY IT. Call out technical bottlenecks.",
        "Supportive Coach": "Be encouraging. Break complex terms into simple analogies.",
        "Senior Engineer": "Be concise. Focus on scalability, latency, and data structure."
    }
    vibe_instr = vibe_map.get(request.vibe, vibe_map["Senior Engineer"])

    # 3. Context Construction
    qa_context = "User skipped questions."
    if len(request.questions) > 0 and len(request.answers) > 0:
        qa_context = "\n".join([f"Q: {q} -> A: {a}" for q, a in zip(request.questions, request.answers)])

    # 4. The "Strict Mode" Prompt
    prompt = f"""
    APP IDEA: {request.app_idea}
    
    USER CONSTRAINTS:
    - Budget: {request.budget}
    - Skill Level: {request.skill}
    - Priority: {request.priority}
    
    USER ANSWERS:
    {qa_context}
    
    LIVE SEARCH CONTEXT:
    {search_res}
    
    {vibe_instr}
    
    Your Goal: Create a specific, actionable build plan using the Available Tools and Search Results.
    
    JSON OUTPUT FORMAT (Strict JSON only):
    {{
        "pro_tip": "A single, specific 'Golden Nugget' of advice for this exact idea.",
        "stack_reasoning": "A short paragraph explaining why this specific stack fits the budget/skill constraints. Mention the search results if relevant.",
        "tools_list": ["Tool Name 1", "Tool Name 2", "Tool Name 3"],
        "budget_breakdown": [
            {{"item": "Tool Name 1", "cost": "$X/mo"}},
            {{"item": "Tool Name 2", "cost": "$Y/mo"}},
            {{"item": "Total Estimated Cost", "cost": "$Z/mo"}}
        ],
        "build_steps": [
            "Step 1: Go to [Specific Tool] and create a project...",
            "Step 2: Connect [Specific Tool] to [Other Tool] using...",
            "Step 3: ..."
        ],
        "copy_paste_prompt": "A detailed prompt the user can paste into the AI Tool (like Replit or Cursor) to start building immediately."
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", # Using the smarter model
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        data = json.loads(response.text)
        
        # Match tools with URLs for the frontend
        detected = []
        all_text = str(data).lower()
        for tool, info in TOOL_PRICING.items():
            if tool.lower() in all_text:
                # Add the tool, but ensure we have the URL
                info_copy = info.copy()
                info_copy['name'] = tool
                detected.append(info_copy)
        
        data['detected_tools'] = detected
        return data

    except Exception as e:
        print(f"LLM Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- HISTORY ENDPOINTS ---
@app.post("/save_history")
def save_history(item: HistoryItem):
    with open(f"{HISTORY_DIR}/{item.id}.json", "w") as f: json.dump(item.dict(), f)
    return {"status": "saved"}

@app.get("/get_history")
def get_history():
    h = []
    for f in glob.glob(f"{HISTORY_DIR}/*.json"):
        try: h.append(json.load(open(f)))
        except: continue
    return sorted(h, key=lambda x: x['timestamp'], reverse=True)

@app.delete("/delete_history/{item_id}")
def delete_history(item_id: str):
    try: os.remove(f"{HISTORY_DIR}/{item_id}.json"); return {"status": "deleted"}
    except: raise HTTPException(status_code=404)