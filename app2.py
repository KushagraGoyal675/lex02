# app.py

import streamlit as st
import json
import os
import time
from datetime import datetime
import random

# Import all our core utils
from agents.plaintiff_agent import PlaintiffAgent
from agents.defendant_agent import DefendantAgent
from agents.judge_agent import JudgeAgent
from agents.witness_agent import WitnessAgent
from utils.simulation_manager import SimulationManager
from utils.tts import TTSEngine
from utils.stt import STTEngine
from utils.courtroom_animation import CourtroomAnimation
from utils.knowledge_base import load_laws
from utils.helper import load_cases, save_transcript

# Load laws
load_laws()

# Streamlit config
st.set_page_config(
    page_title="Lex Orion - Indian Courtroom Simulator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme
st.markdown("""
    <style>
        body { background-color: #0e0e0e; color: white; font-family: 'Georgia'; }
        .stButton>button { background-color: red; color: white; font-weight: bold; }
        .stSelectbox>div>div>div { color: black; }
        .stTextArea>div>textarea { background-color: #1e1e1e; color: white; }
        .stDownloadButton>button { background-color: darkred; color: white; font-weight: bold; }
        footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# Global session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "simulation_manager" not in st.session_state:
    st.session_state.simulation_manager = None
if "current_case" not in st.session_state:
    st.session_state.current_case = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "observer_mode" not in st.session_state:
    st.session_state.observer_mode = False
if "tts_engine" not in st.session_state:
    st.session_state.tts_engine = TTSEngine()
if "stt_engine" not in st.session_state:
    st.session_state.stt_engine = STTEngine()
if "courtroom_animation" not in st.session_state:
    st.session_state.courtroom_animation = CourtroomAnimation()
if "phase" not in st.session_state:
    st.session_state.phase = "opening"

# Sidebar navigation
st.sidebar.title("⚖️ Lex Orion")
navigation = st.sidebar.radio("Navigation", ["Home", "Start Trial", "Case Management", "Transcripts", "Agent Evaluation", "Logout"])

# Load case database
cases = load_cases()

# --- Home Page ---
if navigation == "Home":
    st.title("⚖️ Welcome to Lex Orion")
    st.markdown("""
    **Lex Orion** is a full courtroom simulator for Indian Civil Trials.  
    Practice realistic cases, object like a lawyer, and give judgments like a real judge!

    - 🔥 Realistic courtroom phases
    - 🤖 AI Agents for all parties
    - 🎤 Voice input & output (TTS + STT)
    - 🎥 Courtroom animations
    - 🎯 Observer Mode or Roleplay Mode
    """)

    if not st.session_state.logged_in:
        st.subheader("Login / Sign Up")
        option = st.selectbox("Choose Option", ["Login", "Sign Up"])

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):
            users_file = "data/users.json"
            if not os.path.exists(users_file):
                with open(users_file, "w") as f:
                    json.dump({}, f)

            with open(users_file, "r") as f:
                users = json.load(f)

            if option == "Login":
                if username in users and users[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome back, {username}!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid Credentials!")
            elif option == "Sign Up":
                if username in users:
                    st.error("Username already exists!")
                else:
                    users[username] = {"password": password, "transcripts": []}
                    with open(users_file, "w") as f:
                        json.dump(users, f)
                    st.success("Account Created! Please login now.")
                    st.experimental_rerun()
    else:
        st.success(f"You are logged in as {st.session_state.username}")
# --- Start Trial Page ---
if navigation == "Start Trial":
    if not st.session_state.logged_in:
        st.warning("Please login first to start a trial.")
        st.stop()

    st.title("🏛️ Start Courtroom Simulation")

    # Choose case
    case_titles = [f"{c['case_id']}: {c['title']}" for c in cases]
    selected_case = st.selectbox("Select a Case", case_titles)

    # Choose role
    roles = ["Observer (Full AI simulation)", "Judge", "Plaintiff Lawyer", "Defendant Lawyer", "Witness"]
    selected_role = st.selectbox("Select Your Role", roles)

    if st.button("Enter Courtroom"):
        case_id = selected_case.split(":")[0]
        case_data = next((c for c in cases if str(c["case_id"]) == case_id), None)
        if not case_data:
            st.error("Case not found!")
            st.stop()

        st.session_state.current_case = case_data
        st.session_state.user_role = selected_role
        st.session_state.observer_mode = selected_role == "Observer (Full AI simulation)"
        st.session_state.simulation_manager = SimulationManager(case_data)
        st.experimental_rerun()

# Actual Courtroom Simulation if loaded
if st.session_state.simulation_manager:
    sim: SimulationManager = st.session_state.simulation_manager
    case_data = st.session_state.current_case
    role = st.session_state.user_role
    phase = st.session_state.phase

    st.header(f"⚖️ {case_data['title']} — Court in Session")

    # Display courtroom animation
    st.session_state.courtroom_animation.animate_phase(phase, speaker=role)

    st.markdown("---")

    # Show case facts
    with st.expander("📜 Case Facts", expanded=False):
        st.write(case_data["facts"])

    # PHASE HANDLING
    from utils.phase_handler import handle_phase

    handle_phase(sim, case_data, role, phase, observer_mode=st.session_state.observer_mode)
# --- Manage Cases ---
if navigation == "Case Management":
    st.title("📚 Manage Cases")

    uploaded_file = st.file_uploader("Upload New Case File (JSON Format)", type=["json"])

    if uploaded_file:
        new_case = json.load(uploaded_file)
        cases.append(new_case)
        with open("data/cases.json", "w") as f:
            json.dump({"cases": cases}, f, indent=2)
        st.success("New case uploaded successfully!")
        st.experimental_rerun()

    st.write("---")
    st.write("### Existing Cases")
    for c in cases:
        st.write(f"**{c['case_id']}: {c['title']}**")

# --- Transcripts Page ---
if navigation == "Transcripts":
    st.title("📜 Past Transcripts")
    transcripts_dir = f"data/transcripts/{st.session_state.username}"
    os.makedirs(transcripts_dir, exist_ok=True)

    files = os.listdir(transcripts_dir)
    if files:
        selected_file = st.selectbox("Select Transcript", files)
        if selected_file:
            with open(os.path.join(transcripts_dir, selected_file)) as f:
                data = json.load(f)
            st.json(data)
            st.download_button(
                label="Download Transcript",
                data=json.dumps(data, indent=2),
                file_name=selected_file,
                mime="application/json"
            )
    else:
        st.info("No transcripts found yet.")

# --- Agent Evaluation Page ---
if navigation == "Agent Evaluation":
    st.title("🤖 Agent Evaluation & Results")
    if not st.session_state.simulation_manager:
        st.warning("Start a trial to evaluate agents.")
        st.stop()
    sim: SimulationManager = st.session_state.simulation_manager
    st.header("Agent Performance & Analysis")
    # Evaluate each agent
    agents = {
        "Judge": sim.judge,
        "Plaintiff Lawyer": sim.plaintiff_lawyer,
        "Defendant Lawyer": sim.defendant_lawyer,
    }
    # Add all witnesses
    for wid, witness in sim.witnesses.items():
        agents[f"Witness ({witness.config.get('name', wid)})"] = witness
    for name, agent in agents.items():
        st.subheader(f"{name}")
        with st.expander("Case Analysis", expanded=False):
            try:
                analysis = agent.analyze_case(sim.case_data)
                st.json(analysis)
            except Exception as e:
                st.error(f"Analysis not available: {e}")
        with st.expander("Prepared Arguments", expanded=False):
            try:
                arguments = agent.prepare_arguments(sim.case_data)
                st.write(arguments)
            except Exception as e:
                st.error(f"Arguments not available: {e}")
        with st.expander("Performance Metrics", expanded=False):
            try:
                metrics = agent.get_performance_metrics()
                st.json(metrics)
            except Exception as e:
                st.error(f"Metrics not available: {e}")

# --- Logout Option ---
if navigation == "Logout":
    st.session_state.clear()
    st.success("Logged out successfully!")
    time.sleep(1)
    st.experimental_rerun()
