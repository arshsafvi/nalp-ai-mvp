import streamlit as st
import requests
import textwrap
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

# --- 1. SETUP ---
load_dotenv()
BACKEND_URL = "https://nalp-backend-gqx3.onrender.com"

st.set_page_config(
    page_title="NALP.ai",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. DARK POP CSS (The "Glow Up") ---
st.html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* BACKGROUND */
    .stApp {
        background-color: #02040a; 
        background-image: radial-gradient(circle at 50% 0%, #1c1c2e 0%, #02040a 60%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    /* LOGO ANIMATION */
    .logo-container { display: flex; align-items: center; cursor: pointer; width: fit-content; padding: 20px 0; }
    .logo-svg { transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); z-index: 999; }
    .logo-text {
        font-family: 'Inter', sans-serif; font-size: 3rem; font-weight: 900; letter-spacing: -2px;
        background: linear-gradient(90deg, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        max-width: 0; opacity: 0; overflow: hidden; white-space: nowrap;
        transform: translateX(-20px); transition: all 0.5s cubic-bezier(0.25, 1, 0.5, 1);
    }
    .logo-container:hover .logo-text { max-width: 300px; opacity: 1; transform: translateX(5px); margin-left: 10px; }
    .logo-container:hover .logo-svg { transform: rotate(-10deg) scale(1.1); }

    /* CUSTOM PILLS (Target Platform) */
    div[data-testid="stPills"] button {
        background-color: #0f1116 !important;
        border: 1px solid #27272a !important;
        color: #94a3b8 !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stPills"] button:hover {
        border-color: #ccff00 !important;
        color: #ccff00 !important;
        transform: translateY(-2px);
    }
    div[data-testid="stPills"] [aria-selected="true"] {
        background-color: rgba(204, 255, 0, 0.15) !important;
        border-color: #ccff00 !important;
        color: #ccff00 !important;
        box-shadow: 0 0 15px rgba(204, 255, 0, 0.2);
    }

    /* TIMELINE STYLES (Execution Steps) */
    .timeline-container {
        position: relative;
        padding-left: 30px;
        margin-top: 20px;
        border-left: 2px solid #27272a;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 25px;
    }
    .timeline-dot {
        position: absolute;
        left: -36px;
        top: 0;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #0f1116;
        border: 2px solid #38bdf8;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }
    .timeline-content {
        background: #0f1116;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 15px;
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* RECEIPT STYLE (Budget) */
    .receipt-box {
        background: #0f1116;
        border: 1px dashed #52525b;
        border-radius: 12px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        color: #a1a1aa;
    }
    .receipt-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .receipt-total {
        border-top: 1px dashed #52525b;
        margin-top: 10px;
        padding-top: 10px;
        color: #ccff00;
        font-weight: 800;
        font-size: 1.1rem;
    }

    /* HISTORY CARD GRID */
    .hist-grid-card {
        background: #0f1116;
        border: 1px solid #27272a;
        border-radius: 16px;
        padding: 20px;
        transition: all 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .hist-grid-card:hover {
        border-color: #c084fc;
        transform: translateY(-4px);
    }

    /* UI UTILS */
    .pro-tip-box {
        background: linear-gradient(90deg, rgba(204, 255, 0, 0.05), transparent);
        border-left: 4px solid #ccff00;
        padding: 20px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 30px;
    }
    
    .tag { font-size: 0.7rem; font-weight: 800; padding: 4px 8px; border-radius: 4px; display:inline-block; color:#000; margin-bottom: 12px; }
    
    /* BUTTON GLOW UP */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 800;
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        color: white;
        border: none;
        padding: 16px;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(124, 58, 237, 0.4);
    }
    
    /* INPUTS */
    .stTextArea textarea, .stTextInput input {
        background-color: #0f1116 !important; border: 1px solid #27272a !important; color: #fff !important; border-radius: 12px; padding: 15px;
    }
    .stTextArea textarea:focus { border-color: #818cf8 !important; box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2) !important; }

    /* LOADING */
    @keyframes neon-pulse { 0% { filter: drop-shadow(0 0 5px rgba(204,255,0,0.5)); transform: scale(1); } 50% { filter: drop-shadow(0 0 20px rgba(204,255,0,0.8)); transform: scale(1.05); } 100% { filter: drop-shadow(0 0 5px rgba(204,255,0,0.5)); transform: scale(1); } }
    .loading-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; animation: fade-in 0.5s ease; }
    .pulsing-logo { animation: neon-pulse 2s infinite ease-in-out; }
    
    header {visibility: hidden;} footer {visibility: hidden;}
</style>
""")

# --- 3. HELPER FUNCTIONS ---
def get_logo_svg(size=40):
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="15" y="15" width="20" height="70" rx="4" fill="#ccff00" />
        <rect x="65" y="15" width="20" height="70" rx="4" fill="#00ffff" />
        <rect x="40" y="15" width="20" height="70" rx="4" fill="#ff00ff" transform="rotate(15 50 50)" style="mix-blend-mode: exclusion;" />
    </svg>
    """

def render_header():
    st.markdown(f"""
    <div style="margin-top: -50px; margin-bottom: 20px; display: flex; align-items: center;">
        <div style="margin-right: 15px;">{get_logo_svg(50)}</div>
        <div>
            <h1 style="
                font-family: 'Inter', sans-serif;
                font-size: 3rem;
                font-weight: 900;
                letter-spacing: 3px;
                text-transform: uppercase;
                background: linear-gradient(90deg, #ccff00, #00ffff); 
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
                line-height: 1;
            ">NALP.AI</h1>
            <p style="
                color: #71717a; 
                font-weight: 600; 
                font-size: 1rem; 
                margin: 5px 0 0 0;
                letter-spacing: 1px;
            ">PLAN BACKWARDS. BUILD FORWARDS.</p>
        </div>
    </div>
    <hr style="border: 0; height: 1px; background-image: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0)); margin-bottom: 30px;">
    """, unsafe_allow_html=True)

def api_call(endpoint, payload):
    try:
        r = requests.post(f"{BACKEND_URL}/{endpoint}", json=payload)
        return r.json() if r.status_code == 200 else None
    except: return None

def api_save_history(app_idea, plan_data):
    item_id = str(uuid.uuid4())[:8]
    payload = {
        "id": item_id, "timestamp": datetime.now().strftime("%b %d"),
        "app_idea": app_idea, "budget": "N/A", "skill": "N/A",
        "plan": json.dumps(plan_data)
    }
    try: requests.post(f"{BACKEND_URL}/save_history", json=payload)
    except: pass

def api_get_history():
    try: return requests.get(f"{BACKEND_URL}/get_history").json()
    except: return []

def get_markdown_download(data, idea):
    md = f"# 🚀 NALP.ai Blueprint: {idea}\n\n"
    md += f"### 💡 Pro Tip\n{data.get('pro_tip', '')}\n\n"
    md += f"### 🛠️ Recommended Stack\n{data.get('stack_reasoning', '')}\n\n"
    md += "### 💰 Cost Breakdown\n"
    for item in data.get('budget_breakdown', []):
        md += f"- **{item.get('item')}**: {item.get('cost')}\n"
    md += "\n### 📝 Build Steps\n"
    for step in data.get('build_steps', []):
        md += f"- {step}\n"
    return md

# --- 4. MAIN ROUTER ---
def main():
    if 'view' not in st.session_state: st.session_state.view = 'home'
    if 'result_data' not in st.session_state: st.session_state.result_data = None
    if 'current_idea' not in st.session_state: st.session_state.current_idea = ""

    render_header()

    # --- VIEW 1: HOME (Idea + Platform) ---
    if st.session_state.view == 'home':
        # --- HISTORY GRID (Interactive) ---
        history_items = api_get_history()
        if history_items:
            st.html("""<div style="font-size:1.2rem; font-weight:600; color:#e4e4e7; margin-bottom:15px;">📂 Recent Plans</div>""")
            
            # Display up to 3 recent items in a grid
            cols = st.columns(3)
            for i, item in enumerate(history_items[:3]):
                with cols[i]:
                    # Visual Card
                    st.html(f"""
                    <div class="hist-grid-card">
                        <div style="font-weight:700; font-size:1.1rem; margin-bottom:5px; color:#fff;">{item['app_idea'][:30]}...</div>
                        <div style="color:#71717a; font-size:0.8rem;">{item['timestamp']}</div>
                    </div>
                    """)
                    # Actual Button (Invisible/Overlaid logic in Streamlit is hard, so we place it below)
                    if st.button("📂 LOAD", key=f"load_{item['id']}", use_container_width=True):
                        st.session_state.current_idea = item['app_idea']
                        st.session_state.result_data = json.loads(item['plan'])
                        st.session_state.view = 'results'
                        st.rerun()
        
        st.html("<br>")
        st.html("""<div style="font-size:1.2rem; font-weight:600; color:#e4e4e7; margin-bottom:10px;">⚡ Start New Plan</div>""")
        
        app_idea = st.text_area("Idea", placeholder="I want to build...", height=140, label_visibility="collapsed")
        
        # MULTI-SELECT PILLS (Native & Clean)
        st.markdown("<div style='margin-top:20px; margin-bottom:5px; color:#71717a; font-weight:700; text-transform:uppercase; font-size:0.85rem;'>Target Platforms</div>", unsafe_allow_html=True)
        platforms = st.pills("Platforms", ["🍎 iOS", "🤖 Android", "💻 Web App", "🖥️ MacOS/Windows"], selection_mode="multi", label_visibility="collapsed")

        # Continue
        st.html("<br>")
        if st.button("ANALYZE IDEA ➔"):
            if app_idea:
                st.session_state.current_idea = app_idea
                st.session_state.selected_platforms = platforms if platforms else ["Any"]
                st.session_state.view = 'analyze'
                st.rerun()
            else:
                st.warning("Please describe your idea.")
        
        # --- FEEDBACK FOOTER ---
        st.html("<br><br><br>") 
        
        f1, f2, f3 = st.columns([1, 2, 1])
        with f2:
            st.link_button("💬 Send Your Suggestions", "https://forms.gle/unSeQby6KiPG53nD9", use_container_width=True)
        
        st.html("<div style='text-align:center; color:#555; font-size:0.8rem; margin-top:10px;'>Help us improve NALP.ai</div>")

    # --- VIEW 2: ANALYZE (Q&A) ---
    elif st.session_state.view == 'analyze':
        st.html("""<div style="font-size:1.5rem; font-weight:800; color:#fff; margin-bottom:10px;">🔍 Deep Dive</div>""")
        st.info(f"Refining: {st.session_state.current_idea}")
        
        # Fetch Questions if missing
        if 'questions' not in st.session_state or not st.session_state.questions:
            with st.spinner("Thinking of questions..."):
                data = api_call("analyze_idea", {"app_idea": st.session_state.current_idea})
                if data: st.session_state.questions = data.get("questions", [])
                else: st.session_state.questions = ["What are the core features?", "Is this for a specific niche?", "Do you need to store payments?"]

        with st.form("qa_form"):
            answers = []
            for i, q in enumerate(st.session_state.questions):
                answers.append(st.text_input(f"Q{i+1}: {q}"))
            
            st.markdown("---")
            
            # Descriptive Settings
            c1, c2 = st.columns(2)
            with c1: 
                budget = st.selectbox("💰 Monthly Budget", ["Free", "$25", "$50", "$100", "$300", "$700", "$1000+"])
                skill = st.selectbox("👨‍💻 Coding Skill", ["No Code", "Beginner", "Intermediate", "Pro"])
            with c2:
                # Rich options with captions
                priority = st.radio("🎯 Priority", 
                    ["Speed", "Quality", "Scale"],
                    captions=["MVP in days", "Polished UX", "Built for millions"],
                    horizontal=True
                )
                vibe = st.radio("🤖 Persona", 
                    ["Senior Engineer", "Brutal Truth", "Supportive Coach"],
                    captions=["Technical & Concise", "Realistic & Critical", "Simple & Encouraging"],
                    horizontal=True
                )

            st.html("<br>")
            submitted = st.form_submit_button("GENERATE BLUEPRINT 🚀")
            
            if submitted:
                vibe_clean = vibe.split(" (")[0] if "(" in vibe else vibe
                st.session_state.payload = {
                    "app_idea": f"{st.session_state.current_idea} (Platforms: {st.session_state.selected_platforms})",
                    "questions": st.session_state.questions,
                    "answers": answers,
                    "budget": budget, "skill": skill, "priority": priority, "vibe": vibe_clean
                }
                st.session_state.view = 'loading'
                st.rerun()

    # --- VIEW 3: LOADING ---
    elif st.session_state.view == 'loading':
        st.html(textwrap.dedent(f"""
        <div class="loading-wrapper">
            <div class="pulsing-logo">{get_logo_svg(100)}</div>
            <div class="loading-text">ARCHITECTING SOLUTION...</div>
        </div>
        """))
        
        data = api_call("generate_plan", st.session_state.payload)
        if data:
            st.session_state.result_data = data
            api_save_history(st.session_state.current_idea, data)
            st.session_state.view = 'results'
        else:
            st.error("Brain Connection Failed.")
            if st.button("Try Again"): st.session_state.view = 'home'
        st.rerun()

    # --- VIEW 4: RESULTS ---
    elif st.session_state.view == 'results':
        data = st.session_state.result_data
        
        # Pro Tip (Golden)
        st.html(textwrap.dedent(f"""
        <div class="pro-tip-box">
            <div style="color:#ccff00; font-weight:800; font-size:0.8rem; margin-bottom:5px; text-transform:uppercase;">💡 Pro Tip</div>
            <div style="font-size:1.1rem; font-weight:500; line-height:1.4;">{data.get('pro_tip', 'Focus on the MVP.')}</div>
        </div>
        """))
        
        # Stack Cards (Clickable Links)
        st.html("""<div style="font-size:1.2rem; font-weight:600; color:#e4e4e7; margin-bottom:15px;">🧩 Recommended Stack</div>""")
        if 'detected_tools' in data:
            cols = st.columns(3)
            colors = ["#ccff00", "#00ffff", "#ff00ff"]
            for idx, tool in enumerate(data['detected_tools']):
                with cols[idx % 3]:
                    # Create a clickable card using HTML <a> tag
                    st.html(textwrap.dedent(f"""
                    <a href="{tool.get('url', '#')}" target="_blank" style="text-decoration:none;">
                        <div class="result-card" style="border-top: 4px solid {colors[idx%3]};">
                            <div class="tag" style="background:{colors[idx%3]};">{tool['type']}</div>
                            <h4 style="color:#fff; margin:10px 0 5px 0;">{tool['name']} ↗</h4>
                            <div style="color:#a1a1aa; font-size:0.9rem;">{tool['best_for']}</div>
                            <div style="margin-top:10px; font-size:0.8rem; color:#555;">{tool['cost']}</div>
                        </div>
                    </a>
                    """))

        st.html("<br>")

        # Cost Breakdown (Receipt Style)
        with st.expander("💰 Cost Breakdown", expanded=True):
            receipt_html = '<div class="receipt-box">'
            total_cost = 0
            for item in data.get('budget_breakdown', []):
                receipt_html += f"""
                <div class="receipt-row">
                    <span>{item.get('item')}</span>
                    <span>{item.get('cost')}</span>
                </div>
                """
            receipt_html += '</div>'
            st.html(receipt_html)

        st.html("<br>")

        # Execution Steps (Vertical Timeline)
        with st.expander("📝 Execution Roadmap", expanded=True):
            timeline_html = '<div class="timeline-container">'
            for step in data.get('build_steps', []):
                timeline_html += f"""
                <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">{step}</div>
                </div>
                """
            timeline_html += '</div>'
            st.html(timeline_html)
        
        st.html("<br>")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            md_file = get_markdown_download(data, st.session_state.current_idea)
            st.download_button("📥 Download Blueprint", md_file, "nalp_blueprint.md", use_container_width=True)
        with c2:
            if st.button("Start New Plan", use_container_width=True):
                st.session_state.view = 'home'
                st.rerun()

if __name__ == "__main__":
    main()