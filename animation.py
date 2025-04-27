# animation.py
# Animation utilities for Indian Court Simulator

import streamlit as st
import time
import random

class CourtroomAnimation:
    def __init__(self):
        self.animation_phases = {
            'opening': ('⚖️', 'Court in Session'),
            'examination': ('👨‍⚖️👨‍💼👩‍💼🧑‍💼', 'Witness Examination'),
            'evidence': ('📄📁', 'Evidence Presentation'),
            'objection': ('✋❗', 'Objection Raised'),
            'closing': ('🔚', 'Closing Arguments'),
            'completed': ('✅', 'Court Adjourned')
        }
        self.colors = [
            '#f8f9fa', '#e9ecef', '#dee2e6', '#ced4da', '#adb5bd',
            '#6c757d', '#495057', '#343a40', '#212529'
        ]

    def animate_phase(self, phase: str, duration: float = 1.5):
        """
        Animate the transition for a given phase with colored background.
        """
        if phase in self.animation_phases:
            icon, label = self.animation_phases[phase]
            color = random.choice(self.colors)
            st.markdown(f"""
                <div style='text-align:center;font-size:48px;transition:all 0.5s;background:{color};padding:20px;border-radius:16px;'>
                    {icon}<br><b>{label}</b>
                </div>""", unsafe_allow_html=True)
            time.sleep(duration)

    def animate_transcript_entry(self, speaker: str, content: str, delay: float = 0.5):
        """
        Animate a transcript entry with a typewriter effect.
        """
        st.write(f"**{speaker}:** ", unsafe_allow_html=True)
        displayed = ""
        for char in content:
            displayed += char
            st.markdown(f"<span style='font-size:20px;'>{displayed}</span>", unsafe_allow_html=True)
            time.sleep(0.03)
        time.sleep(delay)

    def animate_case_progress(self, current: int, total: int):
        """
        Show a progress bar for the case phases.
        """
        progress = st.progress(current / total)
        time.sleep(0.5)
        progress.empty()

    def animate_confetti(self):
        """
        Show a confetti animation at the end of the simulation.
        """
        st.balloons()

class CourtroomProceedingAnimation:
    """
    Defines and animates a full courtroom proceeding with phase transitions and transcript effects.
    """
    def __init__(self):
        self.phases = [
            'opening',
            'examination',
            'evidence',
            'objection',
            'closing',
            'completed'
        ]
        self.anim = CourtroomAnimation()

    def animate_full_proceeding(self, transcript: list):
        """
        Animate the full courtroom proceeding with all phases and transcript entries.
        transcript: List of dicts with keys 'phase', 'speaker', 'content'.
        """
        current_phase = None
        total_phases = len(self.phases)
        for idx, entry in enumerate(transcript):
            phase = entry.get('phase', None)
            if phase and phase != current_phase:
                current_phase = phase
                self.anim.animate_phase(phase)
                self.anim.animate_case_progress(self.phases.index(phase)+1, total_phases)
            self.anim.animate_transcript_entry(entry['speaker'], entry['content'])
        self.anim.animate_confetti()

# Usage example (to be used in app.py or other UI):
# anim = CourtroomAnimation()
# anim.animate_phase('opening')
# anim.animate_transcript_entry('Judge', 'Court is now in session.')
# anim.animate_case_progress(2, 6)
# anim.animate_confetti()
