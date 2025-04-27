import streamlit as st
import json
import os
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import base64
from io import BytesIO

from courtroom.simulation_manager import create_simulation, SimulationManager
from agents.plaintiff_agent import PlaintiffAgent
from agents.defendant_agent import DefendantAgent
from agents.judge_agent import JudgeAgent
from agents.witness_agent import WitnessAgent
from utils.tts import TTSEngine
from utils.stt import STTEngine

st.set_page_config(page_title="Lex Orion - Indian Court Simulator", page_icon="logo.jpeg", layout="wide")

# Function to load and encode the logo
def get_base64_encoded_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error loading logo: {e}")
        return None

# Get the base64 encoded logo
logo_base64 = get_base64_encoded_image("logo.png")
logo_html = ""

if logo_base64:
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="Lex Orion Logo" style="height:60px;">'
else:
    # Fallback text if image fails to load
    logo_html = '<div style="height:60px;width:60px;background:#e10600;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:bold;border-radius:50%;">LO</div>'

# Inject custom CSS for dark theme and branding
st.markdown(
    f'''
    <style>
    body, .stApp {{
        background-color: #000 !important;
        color: #fff !important;
    }}
    .stApp {{
        background: #000 !important;
    }}
    .stButton>button, .stTextInput>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div>div {{
        background: #111 !important;
        color: #fff !important;
        border: 2px solid #e10600 !important;
        border-radius: 8px !important;
    }}
    .stButton>button:hover {{
        background: #e10600 !important;
        color: #fff !important;
        border: 2px solid #fff !important;
    }}
    .stProgress > div > div > div > div {{
        background-color: #e10600 !important;
    }}
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
        color: #e10600 !important;
    }}
    .stAlert, .stSuccess, .stInfo, .stWarning, .stError {{
        background: #111 !important;
        color: #fff !important;
        border-left: 5px solid #e10600 !important;
    }}
    .stAlert a, .stSuccess a, .stInfo a, .stWarning a, .stError a {{
        color: #e10600 !important;
        text-decoration: underline !important;
    }}
    .stSidebar {{
        background: #000 !important;
        color: #fff !important;
    }}
    .stSidebar .stHeader {{
        color: #e10600 !important;
    }}
    .stSidebar .stSubheader {{
        color: #fff !important;
    }}
    .stSidebar .stMarkdown {{
        color: #fff !important;
    }}
    .stSidebar .stTextInput>div>input, .stSidebar .stTextArea>div>textarea, .stSidebar .stSelectbox>div>div>div>div {{
        background: #111 !important;
        color: #fff !important;
        border: 2px solid #e10600 !important;
        border-radius: 8px !important;
    }}
    .stSidebar .stButton>button {{
        background: #e10600 !important;
        color: #fff !important;
        border: 2px solid #fff !important;
    }}
    .stSidebar .stButton>button:hover {{
        background: #fff !important;
        color: #e10600 !important;
        border: 2px solid #e10600 !important;
    }}
    .stMarkdown {{
        color: #fff !important;
    }}
    .opening-statement {{
        background-color: #000 !important;
        color: #e10600 !important;
        border-left: 4px solid #fff !important;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }}
    .opening-statement p {{
        color: #fff !important;
    }}
    .phase-transition div {{
        background-color: #111 !important;
        color: #fff !important;
    }}
    .phase-transition div.active {{
        background-color: #e10600 !important;
    }}
    /* Add styling for all phase animations */
    .examination, .evidence, .objection, .closing, .judgment {{
        background-color: #000 !important;
        color: #fff !important;
        border-left: 4px solid #e10600 !important;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }}
    .examination h3, .evidence h3, .objection h3, .closing h3, .judgment h3 {{
        color: #e10600 !important;
    }}
    /* Style for all Streamlit info/warning/error messages */
    .element-container .stAlert {{
        background-color: #111 !important;
        color: #fff !important;
        border-left: 5px solid #e10600 !important;
    }}
    /* Override specific alert colors */
    .element-container .stInfo {{
        border-left: 5px solid #e10600 !important;
    }}
    .element-container .stSuccess {{
        border-left: 5px solid #00c853 !important;
    }}
    .element-container .stWarning {{
        border-left: 5px solid #ffd600 !important;
    }}
    .element-container .stError {{
        border-left: 5px solid #e10600 !important;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    @keyframes pulse {{
        0% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.05); opacity: 0.9; }}
        100% {{ transform: scale(1); opacity: 1; }}
    }}
    @keyframes glow {{
        0% {{ box-shadow: 0 0 5px #e10600; }}
        50% {{ box-shadow: 0 0 20px #e10600; }}
        100% {{ box-shadow: 0 0 5px #e10600; }}
    }}
    @keyframes slideIn {{
        from {{ transform: translateX(-100%); }}
        to {{ transform: translateX(0); }}
    }}
    @keyframes scaleIn {{
        from {{ transform: scale(0); }}
        to {{ transform: scale(1); }}
    }}
    @keyframes slideInFromBottom {{
        from {{ transform: translateY(100%); opacity: 0; }}
        to {{ transform: translateY(0); opacity: 1; }}
    }}
    /* Make selectbox options visible */
    .stSelectbox>div>div>div>ul {{
        background-color: #111 !important;
        color: #fff !important;
    }}
    .stSelectbox>div>div>div>ul>li {{
        background-color: #111 !important;
        color: #fff !important;
    }}
    .stSelectbox>div>div>div>ul>li:hover {{
        background-color: #e10600 !important;
        color: #fff !important;
    }}
    </style>
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
        {logo_html}
        <span style="font-size:2.5rem;font-weight:bold;color:#e10600;letter-spacing:2px;">Lex Orion</span>
    </div>
    ''', unsafe_allow_html=True)

# --- Animation Classes ---
class CourtroomAnimation:
    def __init__(self):
        self.characters = {
            "judge": {"position": (0.5, 0.15), "speaking": False},
            "plaintiff_lawyer": {"position": (0.2, 0.4), "speaking": False},
            "defendant_lawyer": {"position": (0.8, 0.4), "speaking": False},
            "witness": {"position": (0.5, 0.4), "speaking": False},
            "plaintiff": {"position": (0.1, 0.6), "speaking": False},
            "defendant": {"position": (0.9, 0.6), "speaking": False},
        }
        self.courtroom_bg = self.create_courtroom_bg()
        self.current_speaker = None
        self.animation_frames = []
        self.animation_speed = 0.5

    def create_courtroom_bg(self):
        """Create a simple courtroom background"""
        fig, ax = plt.subplots(figsize=(8, 4.8))  # Reduced size
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        # Draw judge bench
        ax.add_patch(plt.Rectangle((0.3, 0.05), 0.4, 0.1, color='brown'))
        
        # Draw witness stand
        ax.add_patch(plt.Rectangle((0.45, 0.35), 0.1, 0.1, color='brown'))
        
        # Draw lawyers' tables
        ax.add_patch(plt.Rectangle((0.1, 0.35), 0.2, 0.05, color='brown'))
        ax.add_patch(plt.Rectangle((0.7, 0.35), 0.2, 0.05, color='brown'))
        
        # Draw audience area
        ax.add_patch(plt.Rectangle((0.1, 0.6), 0.8, 0.3, color='lightgray', alpha=0.5))
        
        ax.axis('off')
        return fig

    def draw_character(self, ax, role, is_speaking=False):
        """Draw a character on the courtroom"""
        char_info = self.characters.get(role, {"position": (0.5, 0.5), "speaking": False})
        x, y = char_info["position"]
        
        # Body
        color = '#e10600' if role == 'judge' else 'white' if 'lawyer' in role else '#e10600'
        ax.add_patch(plt.Circle((x, y), 0.05, color=color))
        
        # Head
        ax.add_patch(plt.Circle((x, y-0.07), 0.03, color='tan'))
        
        # Speech bubble if speaking
        if is_speaking:
            ax.annotate("Speaking", xy=(x, y-0.12), 
                        xytext=(x+0.15, y-0.15),
                        arrowprops=dict(arrowstyle="->", color='white'),
                        bbox=dict(boxstyle="round,pad=0.3", fc="#e10600", alpha=0.9))

    def animate_phase(self, phase, speaking_role=None):
        """Animate the current phase of the trial"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        # Draw courtroom background - updated to black
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color='black', alpha=1.0))
        
        # Draw judge bench
        ax.add_patch(plt.Rectangle((0.3, 0.05), 0.4, 0.1, color='#333'))
        
        # Draw witness stand
        ax.add_patch(plt.Rectangle((0.45, 0.35), 0.1, 0.1, color='#333'))
        
        # Draw lawyers' tables
        ax.add_patch(plt.Rectangle((0.1, 0.35), 0.2, 0.05, color='#333'))
        ax.add_patch(plt.Rectangle((0.7, 0.35), 0.2, 0.05, color='#333'))
        
        # Draw audience area
        ax.add_patch(plt.Rectangle((0.1, 0.6), 0.8, 0.3, color='#111', alpha=0.9))
        
        # Draw phase-specific elements
        if phase == 'opening':
            ax.text(0.5, 0.9, "Opening Statements", ha='center', fontsize=14, color='white', 
                   bbox=dict(facecolor='#e10600', alpha=0.8, boxstyle='round'))
        elif phase == 'examination':
            ax.text(0.5, 0.9, "Witness Examination", ha='center', fontsize=14, color='white',
                   bbox=dict(facecolor='#e10600', alpha=0.8, boxstyle='round'))
        elif phase == 'evidence':
            ax.text(0.5, 0.9, "Evidence Presentation", ha='center', fontsize=14, color='white',
                   bbox=dict(facecolor='#e10600', alpha=0.8, boxstyle='round'))
            ax.add_patch(plt.Rectangle((0.45, 0.45), 0.1, 0.05, color='#e10600', alpha=0.8))
        elif phase == 'objection':
            ax.text(0.5, 0.9, "Objection Phase", ha='center', fontsize=14, color='white',
                   bbox=dict(facecolor='#e10600', alpha=0.8, boxstyle='round'))
            if speaking_role and 'lawyer' in speaking_role.lower():
                ax.text(0.5, 0.75, "OBJECTION!", ha='center', fontsize=16, color='#e10600', weight='bold',
                       bbox=dict(facecolor='white', alpha=0.9, boxstyle='round,pad=0.5'))
        elif phase == 'closing':
            ax.text(0.5, 0.9, "Closing Arguments", ha='center', fontsize=14, color='white',
                   bbox=dict(facecolor='#e10600', alpha=0.8, boxstyle='round'))
        elif phase == 'judgment':
            ax.text(0.5, 0.9, "Judgment", ha='center', fontsize=14, color='white',
                   bbox=dict(facecolor='#e10600', alpha=0.8, boxstyle='round'))
            ax.add_patch(plt.Rectangle((0.3, 0.02), 0.4, 0.13, color='#333', linewidth=3, edgecolor='#e10600'))
        elif phase == 'completed':
            ax.text(0.5, 0.9, "Case Closed", ha='center', fontsize=14, color='white',
                   bbox=dict(facecolor='#e10600', alpha=0.8, boxstyle='round'))
            ax.text(0.5, 0.5, "JUSTICE SERVED", ha='center', fontsize=20, color='#e10600', weight='bold',
                   bbox=dict(facecolor='black', alpha=0.8, boxstyle='round,pad=0.5', edgecolor='white'))
            
        # Draw characters
        for role, info in self.characters.items():
            self.draw_character(ax, role, is_speaking=(role.lower() == speaking_role.lower() if speaking_role else False))
            
        ax.axis('off')
        
        # Convert plot to image for Streamlit
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        st.image(buf, use_column_width=True)
        plt.close(fig)
        
    def animate_confetti(self):
        """Display animated confetti for case completion"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        # Set black background
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color='black', alpha=1.0))
        
        # Create and display confetti
        confetti_colors = ['#e10600', 'white', '#e10600', 'white', '#e10600', 'white']
        for _ in range(100):
            x = np.random.rand()
            y = np.random.rand()
            color = np.random.choice(confetti_colors)
            ax.add_patch(plt.Rectangle((x, y), 0.02, 0.01, color=color, alpha=0.7))
            
        ax.text(0.5, 0.5, "CASE CLOSED", ha='center', fontsize=24, color='white', weight='bold',
               bbox=dict(facecolor='#e10600', alpha=0.9, boxstyle='round,pad=0.5'))
        ax.axis('off')
        
        # Convert plot to image for Streamlit
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        st.image(buf, use_column_width=True)
        plt.close(fig)
        
class CourtroomProceedingAnimation:
    def __init__(self):
        self.phase_animations = {
            'opening': self.animate_opening,
            'examination': self.animate_examination,
            'evidence': self.animate_evidence,
            'objection': self.animate_objection,
            'closing': self.animate_closing,
            'judgment': self.animate_judgment
        }
        
    def animate_opening(self, role):
        """Animation for opening statements"""
        st.markdown("""
        <div class="opening-statement">
            <h3>Opening Statements Phase</h3>
            <p>Present your opening statement to the court. Explain your client's position and what you intend to prove.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_examination(self, role):
        """Animation for witness examination"""
        st.markdown("""
        <div class="examination" style="animation: slideIn 1s ease-out;">
            <h3>Witness Examination Phase</h3>
            <p>Witnesses will now be called to testify and be examined by the lawyers.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_evidence(self, role):
        """Animation for evidence presentation"""
        st.markdown("""
        <div class="evidence" style="animation: scaleIn 1s ease-in-out;">
            <h3>Evidence Presentation Phase</h3>
            <p>The lawyers will now present and discuss key evidence in the case.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_objection(self, role):
        """Animation for objections"""
        st.markdown("""
        <div class="objection" style="animation: pulse 0.5s infinite;">
            <h3>Objection Phase</h3>
            <p>Lawyers may raise objections to evidence or testimony that violates legal procedures.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_closing(self, role):
        """Animation for closing arguments"""
        st.markdown("""
        <div class="closing" style="animation: slideInFromBottom 1s ease-out;">
            <h3>Closing Arguments Phase</h3>
            <p>The lawyers will now present their final arguments summarizing their case.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_judgment(self, role):
        """Animation for judgment"""
        st.markdown("""
        <div class="judgment" style="animation: glow 2s infinite;">
            <h3>Judgment Phase</h3>
            <p>The judge will now deliver the final verdict based on the evidence and arguments presented.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_phase(self, phase, role=None):
        """Select and run the appropriate animation for the current phase"""
        if phase in self.phase_animations:
            self.phase_animations[phase](role)
        else:
            st.write(f"Phase: {phase}")

# --- Helper functions ---
def load_users():
    # Return a default user dict with admin/1234 if users.json is missing or removed
    return {"admin": {"password": "1234", "transcripts": []}}

def load_cases():
    with open('data/cases.json', 'r') as f:
        return json.load(f)["cases"]

def get_case_by_id(case_id):
    for case in load_cases():
        if case["case_id"] == case_id:
            return case
    return None

def get_speaker_role(role):
    """Convert UI role to character role for animation"""
    mapping = {
        "Judge": "judge",
        "Plaintiff Lawyer": "plaintiff_lawyer",
        "Defendant Lawyer": "defendant_lawyer",
        "Witness": "witness"
    }
    return mapping.get(role, None)

# --- Streamlit App ---

# Initialize TTS and STT engines
if 'tts_engine' not in st.session_state:
    st.session_state.tts_engine = TTSEngine()
if 'stt_engine' not in st.session_state:
    st.session_state.stt_engine = STTEngine()

# Initialize animations
if 'courtroom_anim' not in st.session_state:
    st.session_state.courtroom_anim = CourtroomAnimation()
if 'proceeding_anim' not in st.session_state:
    st.session_state.proceeding_anim = CourtroomProceedingAnimation()

# --- Login ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if not st.session_state.logged_in:
    st.subheader("Login")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            users = load_users()
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.username = username
                # Add animation for successful login
                st.markdown("""
                <div style="text-align:center; animation: fadeIn 1s;">
                    <h3 style="color: green;">Login Successful!</h3>
                    <p>Welcome to the Indian Court Simulator</p>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)  # Short delay for animation effect
                st.rerun()
            else:
                st.error("Invalid username or password.")
    st.stop()

# --- Case Selection ---
if 'selected_case_id' not in st.session_state:
    st.session_state.selected_case_id = None
if not st.session_state.selected_case_id:
    st.subheader("Select a Case")
    cases = load_cases()
    case_options = []
    
    # Create visual case cards
    cols = st.columns(3)
    for i, case in enumerate(cases):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="border:1px solid #fff; padding:10px; border-radius:5px; margin:5px; animation: fadeIn 1s {i*0.2}s; background:#000;">
                <h4 style="color:#e10600;">{case['title']}</h4>
                <p><strong style="color:#fff;">Type:</strong> <span style="color:#fff;">{case['case_type']}</span></p>
                <p><strong style="color:#fff;">Parties:</strong> <span style="color:#fff;">{case['parties']['plaintiff']} vs. {case['parties']['defendant']}</span></p>
            </div>
            """, unsafe_allow_html=True)
    
    case_titles = [f"{case['case_id']}: {case['title']}" for case in cases]
    case_choice = st.selectbox("Choose a case", case_titles)
    if st.button("Confirm Case"):
        st.session_state.selected_case_id = case_choice.split(':')[0]
        st.rerun()
    st.stop()

case = get_case_by_id(st.session_state.selected_case_id)

# --- Role Selection ---
roles = ["Judge", "Plaintiff Lawyer", "Defendant Lawyer", "Witness"]
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None
if not st.session_state.selected_role:
    st.subheader("Choose Your Role")
    
    # Visual role selection cards
    cols = st.columns(4)
    role_icons = {
        "Judge": "⚖️", 
        "Plaintiff Lawyer": "👨‍💼", 
        "Defendant Lawyer": "👩‍💼", 
        "Witness": "👁️"
    }
    
    role_descs = {
        "Judge": "Preside over the court, rule on objections, and deliver the final judgment",
        "Plaintiff Lawyer": "Represent the plaintiff, present evidence and arguments",
        "Defendant Lawyer": "Represent the defendant, present evidence and arguments",
        "Witness": "Provide testimony when called upon by the lawyers"
    }
    
    for i, role in enumerate(roles):
        with cols[i]:
            st.markdown(f"""
            <div style="border:1px solid #fff; padding:15px; border-radius:5px; text-align:center; 
                      animation: fadeIn 0.5s {i*0.2}s; cursor:pointer; height:200px; background:#000;">
                <h1>{role_icons[role]}</h1>
                <h4 style="color:#e10600;">{role}</h4>
                <p style="font-size:0.8em; color:#fff;">{role_descs[role]}</p>
            </div>
            """, unsafe_allow_html=True)
    
    role = st.selectbox("Select your role", roles)
    if st.button("Confirm Role"):
        st.session_state.selected_role = role
        # Animation for role confirmation
        st.markdown(f"""
        <div style="text-align:center; animation: fadeIn 1s;">
            <h3 style="color:#e10600;">You selected: {role}</h3>
            <p style="color:#fff;">Preparing the courtroom...</p>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)  # Short delay for animation effect
        st.rerun()
    st.stop()

# --- Simulation Setup ---
if 'simulation' not in st.session_state:
    # Prepare case_data for simulation manager
    case_data = {
        "case_id": case["case_id"],
        "title": case["title"],
        "type": case["case_type"],
        "plaintiff": case["parties"]["plaintiff"],
        "defendant": case["parties"]["defendant"],
        "description": case["description"],
        "judge_data": {"name": "Justice Rao", "experience": "20 years", "specialization": "Civil Law"},
        "plaintiff_lawyer_data": {"name": "Adv. Mehta", "experience": "15 years", "specialization": "Contracts"},
        "defendant_lawyer_data": {"name": "Adv. Singh", "experience": "12 years", "specialization": "Contracts"},
        "witnesses": case["witnesses"],
        "evidence": case["evidence"]
    }
    st.session_state.simulation = create_simulation(case_data)
    st.session_state.simulation_state = 'not_started'
    st.session_state.transcript = []
    st.session_state.current_phase = 'opening'
    st.session_state.evidence_presented = []
    st.session_state.selected_witness = None
    st.session_state.current_speaker = None

    # Add fake transcript if case is first one and user is defendant lawyer
    if st.session_state.selected_case_id == "1" and st.session_state.selected_role == "Defendant Lawyer":
        # Define detailed opening statement for defendant lawyer
        defendant_opening = """Your Honor, ElectroTech Ltd. has built its reputation on quality products and fair customer service policies. Our warranty terms are clear, transparent, and explained to all customers at the time of purchase.

In this case, the plaintiff, Mr. Sharma, purchased a premium television that was properly installed and functioning correctly. Unfortunately, within a week, the television sustained physical damage. Our technician, Mr. Raj Patel, with over seven years of experience servicing our products, thoroughly examined the television and documented clear signs of impact damage - damage that is explicitly excluded from our warranty coverage.

We will present evidence showing the detailed technical report confirming impact damage, not manufacturing defect; photographic evidence of the damage pattern consistent with external force; the warranty agreement signed by Mr. Sharma clearly excluding physical damage; and records showing Mr. Sharma declined our accidental damage protection plan which would have covered this incident.

We empathize with Mr. Sharma's frustration, but ElectroTech cannot be held liable for damage that occurred after the product left our control. Our position is that we have acted in accordance with our clearly stated warranty policy, and this claim should be dismissed. Thank you, Your Honor."""
        
        fake_transcript = [
            {"speaker": "Judge", "content": "Court is now in session. We are here today for case number 1: Consumer Dispute - Mr. Sharma vs ElectroTech Ltd. Plaintiff lawyer, please proceed with your opening statement."},
            {"speaker": "Plaintiff Lawyer", "content": "Thank you, Your Honor. My client, Mr. Sharma, purchased a high-end television from ElectroTech Ltd. that malfunctioned within just one week of purchase. The defendant refused to honor the warranty claiming 'physical damage' even though my client handled the product with utmost care. We will prove that ElectroTech's refusal to honor their warranty constitutes unfair trade practice and breach of contract."},
            {"speaker": "Judge", "content": "Thank you. Defendant lawyer, please present your opening statement."},
            {"speaker": "Defendant Lawyer", "content": defendant_opening},
            {"speaker": "Judge", "content": "We will now move to the examination phase. Plaintiff lawyer, you may call your first witness."},
            {"speaker": "Plaintiff Lawyer", "content": "I call Mr. Sharma to the witness stand."},
            {"speaker": "Judge", "content": "Mr. Sharma, please take the stand. Remember you are under oath."},
            {"speaker": "Witness (Mr. Sharma)", "content": "I understand, Your Honor."},
            {"speaker": "Plaintiff Lawyer", "content": "Question to Mr. Sharma: Please describe exactly what happened after you purchased the television."},
            {"speaker": "Witness (Mr. Sharma)", "content": "I purchased the 55-inch OLED TV from ElectroTech's flagship store on June 10th. Their technician came and installed it on the wall mount the same day. Everything worked perfectly for about five days. On the sixth day, the screen suddenly went blank while we were watching a movie. There was no physical impact or mishandling whatsoever."},
            {"speaker": "Plaintiff Lawyer", "content": "Question to Mr. Sharma: What did you do after the television stopped working?"},
            {"speaker": "Witness (Mr. Sharma)", "content": "I immediately called their customer service and reported the issue. They scheduled a technician visit for the next day. The technician came, looked at the TV for about 10 minutes, and then claimed there was 'physical damage' to the internal components and that it wouldn't be covered under warranty."},
            {"speaker": "Plaintiff Lawyer", "content": "I have no further questions for this witness at this time."},
            {"speaker": "Judge", "content": "Defendant lawyer, your witness for cross-examination."}
        ]
        
        for entry in fake_transcript:
            st.session_state.simulation.add_to_transcript(entry["speaker"], entry["content"])

sim: SimulationManager = st.session_state.simulation

# --- Main Simulation UI ---
phases = [
    'opening',
    'examination',
    'evidence',
    'objection',
    'closing',
    'judgment',
    'completed'
]
phase = st.session_state.current_phase

# Header with phase indicator
st.markdown(f"""
<div class="phase-transition">
    <h2>Current Phase: {phase.title()}</h2>
    <div style="background-color: #444; border-radius: 10px; padding: 5px;">
        <div style="display: flex; justify-content: space-between;">
            {"".join([f'<div class="{ "active" if p == phase else "" }" style="padding: 5px; border-radius: 5px; background-color: {"#4CAF50" if p == phase else "#444"}; flex: 1; margin: 0 2px; text-align: center;">{p.title()}</div>' for p in phases])}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Draw courtroom animation ---
role_for_animation = get_speaker_role(st.session_state.selected_role)
st.session_state.courtroom_anim.animate_phase(phase, role_for_animation if st.session_state.current_speaker == role_for_animation else None)
st.session_state.proceeding_anim.animate_phase(phase, st.session_state.selected_role)

# Transcript in expandable section
with st.expander("Court Transcript", expanded=True):
    transcript = sim.get_state().get('transcript', [])
    if transcript:
        for entry in transcript:
            # Ensure entry is a dictionary and has 'speaker' key
            if isinstance(entry, dict) and 'speaker' in entry:
                # Display all entries regardless of the user's role
                # Use a dark background for transcript entries for contrast
                st.markdown(f"""
                <div style="background:#181818;padding:10px;border-radius:6px;margin-bottom:6px;">
                    <span style="color:#e10600;font-weight:bold;">{entry['speaker']}:</span>
                    <span style="color:#fff;">{entry['content']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("The court transcript will appear here as the case proceeds.")

# --- Role-Playing & Phase Actions ---
role = st.session_state.selected_role
user_input = None

# Main court action area
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Your Actions")

# Helper function to generate fake responses
def generate_fake_responses(action_type, content):
    """Generate fake responses from the opposing side based on action type and content"""
    if action_type == "question":
        # Generate response to a question
        responses = [
            "Objection! This question is leading the witness.",
            "I must intervene here. This line of questioning is irrelevant to the facts of the case.",
            "Your Honor, I'd like to note that this question mischaracterizes the previous testimony.",
            "For the record, my client has already addressed this in his initial testimony.",
            "Let me remind the court that the witness has already stated that there was no mishandling of the product."
        ]
        return responses[hash(content) % len(responses)]
    
    elif action_type == "evidence":
        # Generate response to evidence presentation
        responses = [
            "Your Honor, I'd like to point out that this evidence was not properly disclosed during discovery.",
            "I must challenge the authenticity of this evidence. There's no proper chain of custody.",
            "This evidence is irrelevant to the matter at hand and should be stricken from the record.",
            "We strongly contest the interpretation of this evidence as presented by the defense.",
            "Your Honor, this evidence actually supports our claim of manufacturing defect."
        ]
        return responses[hash(content) % len(responses)]
    
    elif action_type == "statement":
        # Generate response to a statement
        responses = [
            "I must respectfully disagree with my colleague's characterization of the facts.",
            "The court should note that this statement contradicts the defendant's earlier position.",
            "This is a misrepresentation of the warranty terms as clearly stated in the contract.",
            "Your Honor, the defense is attempting to shift blame to the consumer without evidence.",
            "We maintain that ElectroTech's interpretation of their warranty deliberately disadvantages consumers."
        ]
        return responses[hash(content) % len(responses)]
    
    return "I must respectfully disagree with the defense's position."

if phase == 'opening':
    if role in ["Plaintiff Lawyer", "Defendant Lawyer"]:
        st.markdown("""
        <div style="padding: 10px; background-color: #000; border-radius: 5px; animation: fadeIn 1s; border: 1px solid #fff;">
            <h4 style="color: #e10600;">Opening Statements Phase</h4>
            <p style="color: #fff;">Present your opening statement to the court. Explain your client's position and what you intend to prove.</p>
        </div>
        """, unsafe_allow_html=True)
        user_input = st.text_area("Enter your opening statement:")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Record Statement"):
                with st.spinner("Recording..."):
                    st.session_state.tts_engine.speak("Please deliver your opening statement.")
                    user_input = st.session_state.stt_engine.process_microphone_input()
                    st.success(f"Recorded: {user_input}")
        with col2:
            if st.button("Submit Opening Statement", key="submit_opening"):
                if user_input:
                    # Set current speaker for animation
                    st.session_state.current_speaker = role_for_animation
                    # Add to transcript with animated effect
                    sim.add_to_transcript(role, user_input)
                    
                    # Animate the speech
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: #000; border-radius: 5px; border: 1px solid #e10600;">
                        <strong style="color: #e10600;">{role}:</strong> <span style="color: #fff;">{user_input[:50]}...</span>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)  # Short delay for animation effect
                    
                    st.session_state.current_phase = 'examination'
                    st.rerun()
                else:
                    st.warning("Please enter your statement before submitting.")
    elif role == "Judge":
        st.info("Wait for the lawyers to submit their opening statements.")
        # Judge can move the proceedings forward if needed
        if st.button("Proceed to Examination Phase"):
            st.session_state.current_phase = 'examination'
            st.rerun()
    elif role == "Witness":
        st.info("Witnesses are not active during opening statements. Please wait for your turn during the examination phase.")

elif phase == 'examination':
    if role in ["Plaintiff Lawyer", "Defendant Lawyer"]:
        st.markdown("""
        <div style="padding: 10px; background-color: #000; border-radius: 5px; animation: fadeIn 1s; border: 1px solid #fff;">
            <h4 style="color: #e10600;">Witness Examination Phase</h4>
            <p style="color: #fff;">You may now call and question witnesses to support your case.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive witness selection with photos
        witness_names = [w['name'] for w in case['witnesses']]
        st.subheader("Select a Witness")
        
        cols = st.columns(len(witness_names))
        for i, name in enumerate(witness_names):
            with cols[i]:
                st.markdown(f"""
                <div style="border:1px solid #fff; padding:10px; border-radius:5px; text-align:center; background:#000;">
                    <h4 style="color:#e10600;">👤</h4>
                    <p style="color:#fff;">{name}</p>
                </div>
                """, unsafe_allow_html=True)
        
        witness_choice = st.selectbox("Choose a witness to examine", witness_names)
        question = st.text_area("Enter your question for the witness:")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Record Question"):
                with st.spinner("Recording..."):
                    st.session_state.tts_engine.speak("Please ask your question.")
                    question = st.session_state.stt_engine.process_microphone_input()
                    st.success(f"Recorded: {question}")
        with col2:
            if st.button("Ask Question", key="ask_question"):
                if question and witness_choice:
                    # Set current speaker for animation
                    st.session_state.current_speaker = role_for_animation
                    # Add to transcript
                    sim.add_to_transcript(role, f"Question to {witness_choice}: {question}")
                    
                    # Use agent to generate witness response
                    witness_agent = WitnessAgent()
                    response = witness_agent.respond_to_question(witness_choice, question)
                    
                    # Update current speaker for animation
                    st.session_state.current_speaker = "witness"
                    # Add witness response to transcript
                    sim.add_to_transcript(f"Witness ({witness_choice})", response)
                    
                    # Add fake opposition response if user is defendant lawyer
                    if role == "Defendant Lawyer" and np.random.random() < 0.7:  # 70% chance to respond
                        time.sleep(0.5)  # Short delay
                        opposition_response = generate_fake_responses("question", question)
                        sim.add_to_transcript("Plaintiff Lawyer", opposition_response)
                    
                    st.rerun()
                else:
                    st.warning("Please select a witness and enter a question.")
        
        # Option to move to evidence phase
        if st.button("Conclude Examination Phase"):
            st.session_state.current_phase = 'evidence'
            st.rerun()
    
    elif role == "Judge":
        st.info("You are overseeing the witness examination. You may interrupt if necessary.")
        if st.button("Order Witness to Answer"):
            sim.add_to_transcript("Judge", "The witness is directed to answer the question.")
            st.rerun()
        if st.button("Move to Evidence Phase"):
            st.session_state.current_phase = 'evidence'
            st.rerun()
    
    elif role == "Witness":
        st.markdown("""
        <div style="padding: 10px; background-color: #000; border-radius: 5px; animation: fadeIn 1s; border: 1px solid #e10600;">
            <h4 style="color: #e10600;">You are on the Witness Stand</h4>
            <p style="color: #fff;">Answer questions truthfully when asked by the lawyers.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if there's a question waiting for this witness
        latest_entries = sim.get_state()['transcript'][-3:] if len(sim.get_state()['transcript']) >= 3 else sim.get_state()['transcript']
        for entry in latest_entries:
            if 'Question to' in entry['content'] and role == "Witness":
                st.markdown(f"""
                <div style="padding: 10px; background-color: #111; border-radius: 5px; border: 1px solid #fff;">
                    <strong style="color: #e10600;">Question:</strong> <span style="color: #fff;">{entry['content'].split(': ')[1]}</span>
                </div>
                """, unsafe_allow_html=True)
                
                answer = st.text_area("Your testimony:")
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("Record Testimony"):
                        with st.spinner("Recording..."):
                            st.session_state.tts_engine.speak("Please provide your testimony.")
                            answer = st.session_state.stt_engine.process_microphone_input()
                            st.success(f"Recorded: {answer}")
                with col2:
                    if st.button("Submit Testimony"):
                        if answer:
                            # Set current speaker for animation
                            st.session_state.current_speaker = "witness"
                            sim.add_to_transcript("Witness", answer)
                            st.rerun()
                        else:
                            st.warning("Please enter your testimony before submitting.")

elif phase == 'evidence':
    if role in ["Plaintiff Lawyer", "Defendant Lawyer"]:
        st.markdown("""
        <div style="padding: 10px; background-color: #000; border-radius: 5px; animation: fadeIn 1s; border: 1px solid #fff;">
            <h4 style="color: #e10600;">Evidence Presentation Phase</h4>
            <p style="color: #fff;">Present evidence to support your case.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Evidence selection with visual cards
        evidence_list = case.get('evidence', []) if case else []
        cols = st.columns(min(3, len(evidence_list)))
        for i, evidence in enumerate(evidence_list):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border:1px solid #fff; padding:10px; border-radius:5px; text-align:center; background:#000;">
                    <h4 style="color:#e10600;">📄</h4>
                    <p><strong style="color:#fff;">{evidence.get('title', 'Untitled')}</strong></p>
                    <p style="font-size:0.8em; color:#fff;">{evidence.get('type', 'Unknown Type')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        evidence_choice = st.selectbox("Select evidence to present", [ev['title'] for ev in evidence_list])
        explanation = st.text_area("Explain the significance of this evidence:")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Record Explanation"):
                with st.spinner("Recording..."):
                    st.session_state.tts_engine.speak("Please explain the significance of this evidence.")
                    explanation = st.session_state.stt_engine.process_microphone_input()
                    st.success(f"Recorded: {explanation}")
        with col2:
            if st.button("Present Evidence", key="present_evidence"):
                if explanation and evidence_choice:
                    # Set current speaker for animation
                    st.session_state.current_speaker = role_for_animation
                    # Find the selected evidence
                    selected_evidence = None
                    for ev in evidence_list:
                        if ev['title'] == evidence_choice:
                            selected_evidence = ev
                            break
                    
                    if selected_evidence:
                        # Animate evidence presentation
                        st.markdown(f"""
                        <div style="padding: 15px; background-color: #000; border-radius: 5px; 
                                animation: scaleIn 1s; border: 2px solid #e10600;">
                            <h4 style="color: #e10600;">Evidence Presented: {selected_evidence['title']}</h4>
                            <p><strong style="color: #fff;">Type:</strong> <span style="color: #fff;">{selected_evidence['type']}</span></p>
                            <p><strong style="color: #fff;">Description:</strong> <span style="color: #fff;">{selected_evidence['description']}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add to transcript
                        sim.add_to_transcript(role, f"Presenting evidence: {selected_evidence['title']} - {explanation}")
                        
                        # Add to presented evidence list
                        if selected_evidence not in st.session_state.evidence_presented:
                            st.session_state.evidence_presented.append(selected_evidence)
                        
                        # Add fake opposition response if user is defendant lawyer
                        if role == "Defendant Lawyer" and np.random.random() < 0.7:  # 70% chance to respond
                            time.sleep(1)  # Short delay for animation effect
                            opposition_response = generate_fake_responses("evidence", explanation)
                            sim.add_to_transcript("Plaintiff Lawyer", opposition_response)
                        
                        time.sleep(1)  # Short delay for animation effect
                        st.rerun()
                else:
                    st.warning("Please select evidence and provide an explanation.")
        
        # Option to move to objection or closing phase
        if st.button("Conclude Evidence Phase"):
            st.session_state.current_phase = 'closing'
            st.rerun()
    
    elif role == "Judge":
        st.info("You are overseeing the evidence presentation. You may comment on the admissibility of evidence.")
        if st.button("Question Evidence Relevance"):
            sim.add_to_transcript("Judge", "The court questions the relevance of this evidence. Please explain further.")
            st.rerun()
        if st.button("Move to Closing Arguments"):
            st.session_state.current_phase = 'closing'
            st.rerun()
    
    elif role == "Witness":
        st.info("Witnesses are not active during evidence presentation unless called upon to verify evidence.")

elif phase == 'objection':
    if role in ["Plaintiff Lawyer", "Defendant Lawyer"]:
        st.markdown("""
        <div style="padding: 10px; background-color: #000; border-radius: 5px; animation: pulse 1s infinite; border: 1px solid #e10600;">
            <h4 style="color: #e10600;">Objection Phase</h4>
            <p style="color: #fff;">You may raise objections to testimony or evidence.</p>
        </div>
        """, unsafe_allow_html=True)
        
        objection_reasons = [
            "Relevance",
            "Hearsay",
            "Leading the witness",
            "Speculation",
            "Lack of foundation",
            "Argumentative",
            "Asked and answered"
        ]
        
        objection_reason = st.selectbox("Select reason for objection", objection_reasons)
        objection_details = st.text_area("Explain your objection:")
        
        if st.button("Raise Objection", key="raise_objection"):
            if objection_details:
                # Dramatic animation for objection
                st.markdown("""
                <div style="text-align:center; animation: scaleIn 0.5s;">
                    <h2 style="color:#e10600; font-weight:bold; text-shadow: 0 0 10px #fff;">OBJECTION!</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Set current speaker for animation
                st.session_state.current_speaker = role_for_animation
                sim.add_to_transcript(role, f"Objection! {objection_reason}: {objection_details}")
                time.sleep(1)  # Short delay for animation effect
                st.rerun()
            else:
                st.warning("Please explain your objection before submitting.")
    
    elif role == "Judge":
        st.markdown("""
        <div style="padding: 10px; background-color: #000; border-radius: 5px; animation: fadeIn 1s; border: 1px solid #fff;">
            <h4 style="color: #e10600;">Ruling on Objection</h4>
            <p style="color: #fff;">You must rule on the objection raised.</p>
        </div>
        """, unsafe_allow_html=True)
        
        latest_entries = sim.get_state()['transcript'][-3:] if len(sim.get_state()['transcript']) >= 3 else sim.get_state()['transcript']
        objection_found = False
        
        for entry in latest_entries:
            if 'Objection!' in entry['content']:
                objection_found = True
                st.markdown(f"""
                <div style="padding: 10px; background-color: #111; border-radius: 5px; border: 1px solid #e10600;">
                    <strong style="color: #e10600;">{entry['speaker']}:</strong> <span style="color: #fff;">{entry['content']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Sustain Objection"):
                        # Set current speaker for animation
                        st.session_state.current_speaker = "judge"
                        sim.add_to_transcript("Judge", "Objection sustained.")
                        
                        # Animation for ruling
                        st.markdown("""
                        <div style="text-align: center; padding: 15px;">
                            <span style="font-size: 30px;">🔨</span>
                            <h3 style="color: #e10600;">Sustained</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        time.sleep(1)  # Short delay for animation effect
                        st.session_state.current_phase = 'evidence'
                        st.rerun()
                with col2:
                    if st.button("Overrule Objection"):
                        # Set current speaker for animation
                        st.session_state.current_speaker = "judge"
                        sim.add_to_transcript("Judge", "Objection overruled. Please continue.")
                        
                        # Animation for ruling
                        st.markdown("""
                        <div style="text-align: center; padding: 15px;">
                            <span style="font-size: 30px;">🔨</span>
                            <h3 style="color: #e10600;">Overruled</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        time.sleep(1)  # Short delay for animation effect
                        st.session_state.current_phase = 'evidence'
                        st.rerun()
        
        if not objection_found:
            st.info("No objections have been raised to rule on.")
            if st.button("Return to Evidence Phase"):
                st.session_state.current_phase = 'evidence'
                st.rerun()
    
    elif role == "Witness":
        st.info("Please wait while the objection is being handled by the court.")

elif phase == 'closing':
    if role in ["Plaintiff Lawyer", "Defendant Lawyer"]:
        st.markdown("""
        <div style="padding: 10px; background-color: #000; border-radius: 5px; animation: fadeIn 1s; border: 1px solid #fff;">
            <h4 style="color: #e10600;">Closing Arguments Phase</h4>
            <p style="color: #fff;">Present your final arguments summarizing your case.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show evidence summary
        if st.session_state.evidence_presented:
            st.subheader("Evidence Presented")
            for ev in st.session_state.evidence_presented:
                st.markdown(f"""
                <div style="padding: 5px; background-color: #111; border-radius: 5px; margin-bottom: 5px; border: 1px solid #fff;">
                    <strong style="color: #e10600;">{ev['title']}</strong> - <span style="color: #fff;">{ev['type']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        closing_argument = st.text_area("Enter your closing argument:")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Record Closing Argument"):
                with st.spinner("Recording..."):
                    st.session_state.tts_engine.speak("Please deliver your closing argument.")
                    closing_argument = st.session_state.stt_engine.process_microphone_input()
                    st.success(f"Recorded: {closing_argument}")
        with col2:
            if st.button("Submit Closing Argument", key="submit_closing"):
                if closing_argument:
                    # Set current speaker for animation
                    st.session_state.current_speaker = role_for_animation
                    sim.add_to_transcript(role, f"Closing Argument: {closing_argument}")
                    
                    # Animate the closing argument
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: #000; border-radius: 5px; border: 1px solid #e10600;">
                        <strong style="color: #e10600;">{role} Closing:</strong> <span style="color: #fff;">{closing_argument[:50]}...</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    time.sleep(1)  # Short delay for animation effect
                    
                    # Add fake opposition rebuttal if user is defendant lawyer and no closing from plaintiff yet
                    if role == "Defendant Lawyer":
                        plaintiff_closing = False
                        for entry in sim.get_state()['transcript']:
                            if entry['speaker'] == "Plaintiff Lawyer" and "Closing Argument:" in entry['content']:
                                plaintiff_closing = True
                                break
                        
                        if not plaintiff_closing:
                            time.sleep(1)  # Delay for realism
                            opposition_closing = "Thank you, Your Honor. In closing, I must emphasize that the evidence clearly shows ElectroTech's warranty policy is designed to evade responsibility. The testimony of our witnesses and technical experts confirms that the television suffered from a manufacturing defect, not user damage. We ask the court to hold ElectroTech accountable and award fair compensation to my client for both the defective product and the considerable distress caused by their unfair practices."
                            sim.add_to_transcript("Plaintiff Lawyer", f"Closing Argument: {opposition_closing}")
                    
                    # Check if both lawyers have submitted closing arguments
                    closing_count = 0
                    for entry in sim.get_state()['transcript']:
                        if 'Closing Argument:' in entry['content']:
                            closing_count += 1
                    
                    if closing_count >= 2:
                        st.session_state.current_phase = 'judgment'
                    
                    st.rerun()
                else:
                    st.warning("Please enter your closing argument before submitting.")
    
    elif role == "Judge":
        st.info("You are listening to the closing arguments. You will deliver judgment after both sides present.")
        if st.button("Move to Judgment Phase"):
            st.session_state.current_phase = 'judgment'
            st.rerun()
    
    elif role == "Witness":
        st.info("Witnesses are not active during closing arguments.")

elif phase == 'judgment':
    if role == "Judge":
        st.markdown("""
        <div style="padding: 10px; background-color: #000; border-radius: 5px; animation: glow 2s infinite; border: 1px solid #e10600;">
            <h4 style="color: #e10600;">Judgment Phase</h4>
            <p style="color: #fff;">Deliver your final verdict based on the evidence and arguments presented.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show case summary
        st.subheader("Case Summary")
        st.markdown(f"""
        <div style="padding: 10px; background-color: #000; border-radius: 5px; border: 1px solid #fff;">
            <strong style="color: #e10600;">Case:</strong> <span style="color: #fff;">{case['title']}</span><br>
            <strong style="color: #e10600;">Parties:</strong> <span style="color: #fff;">{case['parties']['plaintiff']} vs. {case['parties']['defendant']}</span><br>
            <strong style="color: #e10600;">Type:</strong> <span style="color: #fff;">{case['case_type']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        judgment_options = ["In favor of Plaintiff", "In favor of Defendant", "Partial judgment"]
        selected_judgment = st.selectbox("Select your verdict", judgment_options)
        
        judgment_text = st.text_area("Enter your detailed judgment:")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Record Judgment"):
                with st.spinner("Recording..."):
                    st.session_state.tts_engine.speak("Please deliver your judgment.")
                    judgment_text = st.session_state.stt_engine.process_microphone_input()
                    st.success(f"Recorded: {judgment_text}")
        with col2:
            if st.button("Pronounce Judgment", key="pronounce_judgment"):
                if judgment_text:
                    # Animation for judgment pronouncement
                    st.markdown("""
                    <div style="text-align: center; animation: fadeIn 1s;">
                        <span style="font-size: 30px;">🔨</span>
                        <h2 style="color: #e10600;">ORDER! ORDER!</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Set current speaker for animation
                    st.session_state.current_speaker = "judge"
                    sim.add_to_transcript("Judge", f"Final Judgment ({selected_judgment}): {judgment_text}")
                    
                    time.sleep(2)  # Longer delay for dramatic effect
                    st.session_state.current_phase = 'completed'
                    st.rerun()
                else:
                    st.warning("Please enter your judgment before pronouncing.")
    
    else:
        st.info("Please wait for the judge to deliver the final judgment.")
        
        # Show a pulsing "Awaiting Judgment" animation
        st.markdown("""
        <div style="text-align:center; margin: 30px 0; animation: pulse 1.5s infinite;">
            <h3 style="color: #e10600;">Awaiting Final Judgment</h3>
            <div style="font-size: 40px;">⚖️</div>
        </div>
        """, unsafe_allow_html=True)

elif phase == 'completed':
    st.markdown("""
    <div style="text-align:center; animation: fadeIn 2s;">
        <h2 style="color: #e10600;">Case Completed</h2>
        <div style="font-size: 50px; margin: 20px 0;">⚖️</div>
        <p style="font-size: 18px; color: #fff;">Justice has been served</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display final judgment
    final_judgment = None
    for entry in reversed(sim.get_state()['transcript']):
        if 'Final Judgment' in entry['content']:
            final_judgment = entry
            break
    
    if final_judgment:
        st.markdown(f"""
        <div style="padding: 20px; background-color: #000; border-radius: 10px; border: 2px solid #e10600; 
                  margin: 20px 0; animation: glow 3s infinite;">
            <h3 style="color: #e10600;">Final Verdict</h3>
            <p><strong style="color: #fff;">{final_judgment['speaker']}:</strong> <span style="color: #fff;">{final_judgment['content']}</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show confetti animation
    st.session_state.courtroom_anim.animate_confetti()
    
    # Option to start a new case
    if st.button("Start a New Case"):
        # Reset session state
        for key in ['selected_case_id', 'selected_role', 'simulation', 'current_phase', 
                    'transcript', 'evidence_presented', 'selected_witness', 'current_speaker']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- Bottom navigation buttons ---
st.markdown("<hr>", unsafe_allow_html=True)
cols = st.columns(3)

# Save and load transcript functionality
with cols[0]:
    if st.button("Save Transcript"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcript_{case['case_id']}_{timestamp}.json"
        
        # Save transcript data
        transcript_data = {
            "case_id": case["case_id"],
            "case_title": case["title"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_role": st.session_state.selected_role,
            "transcript": sim.get_state()['transcript']
        }
        
        # In a real app, this would save to a file or database
        st.json(transcript_data)
        st.success(f"Transcript saved as {filename}")

with cols[1]:
    if st.button("Help / Tutorial"):
        st.markdown("""
        ### Tutorial
        1. **Select your role**: Judge, lawyer, or witness
        2. **Navigate through phases**: Opening statements → Examination → Evidence → Objections → Closing → Judgment
        3. **Use the microphone**: Record your statements when available
        4. **View transcript**: Expand the transcript section to see the full court record
        
        ### Tips
        - Lawyers can present evidence, question witnesses, and raise objections
        - The judge controls the proceedings and delivers the final judgment
        - Witnesses provide testimony when questioned
        """)

with cols[2]:
    if st.button("Exit Simulation"):
        # Reset session state
        for key in ['selected_case_id', 'selected_role', 'simulation', 'current_phase', 
                    'transcript', 'evidence_presented', 'selected_witness', 'current_speaker']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- Footer ---
st.markdown("""
<div style="text-align:center; margin-top: 30px; padding: 10px; background-color: #000; border-radius: 5px; border-top: 1px solid #e10600;">
    <p style="color: #fff;">Indian Court Simulator - Educational Tool © 2024</p>
</div>
""", unsafe_allow_html=True)

# Add defender context information helper function
def get_defender_context_info(info_type):
    """Provides contextual information for the defendant lawyer"""
    context = {
        "case_summary": """
        <div style="padding: 15px; background-color: #000; border-radius: 5px; border: 1px solid #e10600; margin-bottom: 15px;">
            <h4 style="color: #e10600;">Case Summary - FOR DEFENSE EYES ONLY</h4>
            <p style="color: #fff;">ElectroTech Ltd. has maintained that Mr. Sharma's television was damaged due to improper handling, not a manufacturing defect. Our technician, Mr. Patel, examined the TV and found clear signs of impact damage to the internal components. The damage pattern is consistent with the TV having been struck or dropped, not with component failure.</p>
            <p style="color: #fff;">The warranty policy clearly excludes physical damage, and the plaintiff signed this agreement at purchase. Our sales records show that Mr. Sharma declined the extended accidental damage protection plan that would have covered this type of damage.</p>
        </div>
        """,
        
        "warranty_terms": """
        <div style="padding: 15px; background-color: #000; border-radius: 5px; border: 1px solid #e10600; margin-bottom: 15px;">
            <h4 style="color: #e10600;">Warranty Terms</h4>
            <p style="color: #fff;"><strong>Section 3.2:</strong> "This warranty does not cover damage resulting from accidents, misuse, abuse, improper handling or operation, power fluctuations, or attempted repair by unauthorized personnel."</p>
            <p style="color: #fff;"><strong>Section 5.1:</strong> "ElectroTech's liability is limited to the repair or replacement of the product at our option. We are not liable for incidental or consequential damages."</p>
            <p style="color: #fff;"><strong>Section 7.3:</strong> "All warranty claims are subject to inspection by ElectroTech's authorized technicians. Their determination regarding warranty coverage is final."</p>
        </div>
        """,
        
        "technician_report": """
        <div style="padding: 15px; background-color: #000; border-radius: 5px; border: 1px solid #e10600; margin-bottom: 15px;">
            <h4 style="color: #e10600;">Technician's Report</h4>
            <p style="color: #fff;"><strong>Technician:</strong> Raj Patel, Senior TV Specialist (7 years experience)</p>
            <p style="color: #fff;"><strong>Findings:</strong> "Upon examination of the 55-inch OLED television (Model ET-OLED55), I observed impact damage to the display panel's internal connection points. The fracture pattern is consistent with external force applied to the front of the television, not with electronic failure. The position of the damage suggests the television was struck by an object approximately 7-10 cm in diameter."</p>
            <p style="color: #fff;"><strong>Conclusion:</strong> "The damage observed is categorized as physical/impact damage and is not covered under the standard warranty as per Section 3.2 of the warranty terms."</p>
        </div>
        """,
        
        "cross_examination_strategy": """
        <div style="padding: 15px; background-color: #000; border-radius: 5px; border: 1px solid #e10600; margin-bottom: 15px;">
            <h4 style="color: #e10600;">Cross-Examination Strategy</h4>
            <p style="color: #fff;"><strong>For Mr. Sharma:</strong></p>
            <ul style="color: #fff;">
                <li>Question if anyone else had access to the television (children, visitors)</li>
                <li>Ask if he read the warranty terms before signing</li>
                <li>Inquire about the room layout and if objects could have fallen onto the TV</li>
                <li>Question why he declined the accidental damage protection plan</li>
            </ul>
            <p style="color: #fff;"><strong>For Technical Expert:</strong></p>
            <ul style="color: #fff;">
                <li>Establish the difference between manufacturing defects and impact damage</li>
                <li>Have them confirm that the damage pattern is inconsistent with internal component failure</li>
                <li>Ask about the frequency of customers claiming warranty for physical damage</li>
            </ul>
        </div>
        """,
        
        "opening_statement_full": """
        <div style="padding: 15px; background-color: #000; border-radius: 5px; border: 1px solid #e10600; margin-bottom: 15px;">
            <h4 style="color: #e10600;">Your Full Opening Statement</h4>
            <p style="color: #fff;">Your Honor, ElectroTech Ltd. has built its reputation on quality products and fair customer service policies. Our warranty terms are clear, transparent, and explained to all customers at the time of purchase.</p>
            <p style="color: #fff;">In this case, the plaintiff, Mr. Sharma, purchased a premium television that was properly installed and functioning correctly. Unfortunately, within a week, the television sustained physical damage. Our technician, Mr. Raj Patel, with over seven years of experience servicing our products, thoroughly examined the television and documented clear signs of impact damage - damage that is explicitly excluded from our warranty coverage.</p>
            <p style="color: #fff;">We will present evidence showing:</p>
            <ul style="color: #fff;">
                <li>The detailed technical report confirming impact damage, not manufacturing defect</li>
                <li>Photographic evidence of the damage pattern consistent with external force</li>
                <li>The warranty agreement signed by Mr. Sharma clearly excluding physical damage</li>
                <li>Records showing Mr. Sharma declined our accidental damage protection plan which would have covered this incident</li>
            </ul>
            <p style="color: #fff;">We empathize with Mr. Sharma's frustration, but ElectroTech cannot be held liable for damage that occurred after the product left our control. Our position is that we have acted in accordance with our clearly stated warranty policy, and this claim should be dismissed.</p>
            <p style="color: #fff;">Thank you, Your Honor.</p>
        </div>
        """
    }
    
    return context.get(info_type, "Information not available")

# --- Simulation Setup ---
if 'simulation' not in st.session_state:
    # Prepare case_data for simulation manager
    case_data = {
        "case_id": case["case_id"],
        "title": case["title"],
        "type": case["case_type"],
        "plaintiff": case["parties"]["plaintiff"],
        "defendant": case["parties"]["defendant"],
        "description": case["description"],
        "judge_data": {"name": "Justice Rao", "experience": "20 years", "specialization": "Civil Law"},
        "plaintiff_lawyer_data": {"name": "Adv. Mehta", "experience": "15 years", "specialization": "Contracts"},
        "defendant_lawyer_data": {"name": "Adv. Singh", "experience": "12 years", "specialization": "Contracts"},
        "witnesses": case["witnesses"],
        "evidence": case["evidence"]
    }
    st.session_state.simulation = create_simulation(case_data)
    st.session_state.simulation_state = 'not_started'
    st.session_state.transcript = []
    st.session_state.current_phase = 'opening'
    st.session_state.evidence_presented = []
    st.session_state.selected_witness = None
    st.session_state.current_speaker = None

    # Add fake transcript if case is first one and user is defendant lawyer
    if st.session_state.selected_case_id == "1" and st.session_state.selected_role == "Defendant Lawyer":
        # Define detailed opening statement for defendant lawyer
        defendant_opening = """Your Honor, ElectroTech Ltd. has built its reputation on quality products and fair customer service policies. Our warranty terms are clear, transparent, and explained to all customers at the time of purchase.

In this case, the plaintiff, Mr. Sharma, purchased a premium television that was properly installed and functioning correctly. Unfortunately, within a week, the television sustained physical damage. Our technician, Mr. Raj Patel, with over seven years of experience servicing our products, thoroughly examined the television and documented clear signs of impact damage - damage that is explicitly excluded from our warranty coverage.

We will present evidence showing the detailed technical report confirming impact damage, not manufacturing defect; photographic evidence of the damage pattern consistent with external force; the warranty agreement signed by Mr. Sharma clearly excluding physical damage; and records showing Mr. Sharma declined our accidental damage protection plan which would have covered this incident.

We empathize with Mr. Sharma's frustration, but ElectroTech cannot be held liable for damage that occurred after the product left our control. Our position is that we have acted in accordance with our clearly stated warranty policy, and this claim should be dismissed. Thank you, Your Honor."""
        
        fake_transcript = [
            {"speaker": "Judge", "content": "Court is now in session. We are here today for case number 1: Consumer Dispute - Mr. Sharma vs ElectroTech Ltd. Plaintiff lawyer, please proceed with your opening statement."},
            {"speaker": "Plaintiff Lawyer", "content": "Thank you, Your Honor. My client, Mr. Sharma, purchased a high-end television from ElectroTech Ltd. that malfunctioned within just one week of purchase. The defendant refused to honor the warranty claiming 'physical damage' even though my client handled the product with utmost care. We will prove that ElectroTech's refusal to honor their warranty constitutes unfair trade practice and breach of contract."},
            {"speaker": "Judge", "content": "Thank you. Defendant lawyer, please present your opening statement."},
            {"speaker": "Defendant Lawyer", "content": defendant_opening},
            {"speaker": "Judge", "content": "We will now move to the examination phase. Plaintiff lawyer, you may call your first witness."},
            {"speaker": "Plaintiff Lawyer", "content": "I call Mr. Sharma to the witness stand."},
            {"speaker": "Judge", "content": "Mr. Sharma, please take the stand. Remember you are under oath."},
            {"speaker": "Witness (Mr. Sharma)", "content": "I understand, Your Honor."},
            {"speaker": "Plaintiff Lawyer", "content": "Question to Mr. Sharma: Please describe exactly what happened after you purchased the television."},
            {"speaker": "Witness (Mr. Sharma)", "content": "I purchased the 55-inch OLED TV from ElectroTech's flagship store on June 10th. Their technician came and installed it on the wall mount the same day. Everything worked perfectly for about five days. On the sixth day, the screen suddenly went blank while we were watching a movie. There was no physical impact or mishandling whatsoever."},
            {"speaker": "Plaintiff Lawyer", "content": "Question to Mr. Sharma: What did you do after the television stopped working?"},
            {"speaker": "Witness (Mr. Sharma)", "content": "I immediately called their customer service and reported the issue. They scheduled a technician visit for the next day. The technician came, looked at the TV for about 10 minutes, and then claimed there was 'physical damage' to the internal components and that it wouldn't be covered under warranty."},
            {"speaker": "Plaintiff Lawyer", "content": "I have no further questions for this witness at this time."},
            {"speaker": "Judge", "content": "Defendant lawyer, your witness for cross-examination."}
        ]
        
        for entry in fake_transcript:
            st.session_state.simulation.add_to_transcript(entry["speaker"], entry["content"])

sim: SimulationManager = st.session_state.simulation

# --- Main Simulation UI ---
# ... [existing code] ...

# Add defendant lawyer information panel if user is defendant lawyer in first case
if st.session_state.selected_case_id == "1" and st.session_state.selected_role == "Defendant Lawyer":
    with st.sidebar:
        st.markdown("<h3 style='color: #e10600;'>Defense Attorney Notes</h3>", unsafe_allow_html=True)
        tabs = st.tabs(["Case Summary", "Warranty", "Tech Report", "Strategy", "Opening"])
        
        with tabs[0]:
            st.markdown(get_defender_context_info("case_summary"), unsafe_allow_html=True)
        
        with tabs[1]:
            st.markdown(get_defender_context_info("warranty_terms"), unsafe_allow_html=True)
        
        with tabs[2]:
            st.markdown(get_defender_context_info("technician_report"), unsafe_allow_html=True)
        
        with tabs[3]:
            st.markdown(get_defender_context_info("cross_examination_strategy"), unsafe_allow_html=True)
        
        with tabs[4]:
            st.markdown(get_defender_context_info("opening_statement_full"), unsafe_allow_html=True)