import streamlit as st
from fpdf import FPDF
import datetime
import os
import requests
import re

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Soulful Academy – Chakra Report",
    page_icon="🪬",
    layout="centered"
)

# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------
LOGO_URL = "https://ik.imagekit.io/86edsgbur/Untitled%20design%20(73)%20(3)%20(1).jpg?updatedAt=1759258123716"
LOGO_FILE = "soulful_logo.jpg"

CHAKRAS = [
    "Root (Muladhara)",
    "Sacral (Svadhisthana)",
    "Solar Plexus (Manipura)",
    "Heart (Anahata)",
    "Throat (Vishuddha)",
    "Third Eye (Ajna)",
    "Crown (Sahasrara)",
]

STATUS_OPTIONS = [
    "Balanced / Radiant",
    "Slightly Weak",
    "Blocked / Underactive",
    "Overactive / Dominant",
]

# ---------------------------------------------------------
# PREDEFINED NOTES AND REMEDIES
# ---------------------------------------------------------
PREDEFINED_INFO = {
    "Root (Muladhara)": {
        "Balanced / Radiant": {
            "notes": "Grounded, stable, calm, connected to body and finances aligned.",
            "remedies": "Maintain with gratitude journaling, red crystal grounding meditation, mindful walks."
        },
        "Slightly Weak": {
            "notes": "Mild insecurity about money, overthinking about safety, or shifting base frequently.",
            "remedies": "Walk barefoot daily, chant ‘LAM’, root Reiki healing and safety affirmations."
        },
        "Blocked / Underactive": {
            "notes": "Chronic fear, financial instability, or low body energy (legs/back).",
            "remedies": "Red color therapy, money forgiveness ritual, Ho’oponopono for parents."
        },
        "Overactive / Dominant": {
            "notes": "Control tendencies, anger, or attachment to material comfort.",
            "remedies": "Trust meditations, grounding breathwork, slow paced yoga."
        },
    },
    "Sacral (Svadhisthana)": {
        "Balanced / Radiant": {
            "notes": "Creative, emotionally expressive, open to intimacy and pleasure.",
            "remedies": "Dance therapy, water visualization, orange candle meditation."
        },
        "Slightly Weak": {
            "notes": "Occasional guilt or emotional imbalance in relationships.",
            "remedies": "Ho’oponopono for past partners, sacral journaling, forgiveness rituals."
        },
        "Blocked / Underactive": {
            "notes": "Suppressed emotions, relationship blocks, sexual disconnection.",
            "remedies": "Womb healing, mirror work, sacral Reiki cleansing."
        },
        "Overactive / Dominant": {
            "notes": "Emotional dependency, codependency, or overattachment to people.",
            "remedies": "Healthy boundaries practice, creative solitude, self-love affirmations."
        },
    },
    "Solar Plexus (Manipura)": {
        "Balanced / Radiant": {
            "notes": "Confident, decisive, taking action with self-trust and focus.",
            "remedies": "Yellow crystal (Citrine), power pose practice, gratitude before tasks."
        },
        "Slightly Weak": {
            "notes": "Mild procrastination, low motivation or fear of failure.",
            "remedies": "Breath of fire, journaling success stories, affirm ‘My power is safe’."
        },
        "Blocked / Underactive": {
            "notes": "Self-doubt, indecision, people pleasing, weak boundaries.",
            "remedies": "Solar breathing, visibility mirror practice, Ho’oponopono for authority figures."
        },
        "Overactive / Dominant": {
            "notes": "Overwork, aggression, excessive control or burnout.",
            "remedies": "Solar cooling breath, forgiveness practice, balanced nutrition."
        },
    },
    "Heart (Anahata)": {
        "Balanced / Radiant": {
            "notes": "Loving, compassionate, peaceful and grateful.",
            "remedies": "Heart gratitude meditation, green light visualization, kindness journaling."
        },
        "Slightly Weak": {
            "notes": "Occasional loneliness or fear of vulnerability.",
            "remedies": "Daily self-hug, forgiveness letters, green color therapy."
        },
        "Blocked / Underactive": {
            "notes": "Grief, heartbreak, resentment or rejection wound.",
            "remedies": "Heart Reiki healing, rose quartz meditation, 108x Ho’oponopono."
        },
        "Overactive / Dominant": {
            "notes": "Overgiving, martyr patterns, or guilt after helping others.",
            "remedies": "Practice receiving compliments, balanced care, loving boundaries."
        },
    },
    "Throat (Vishuddha)": {
        "Balanced / Radiant": {
            "notes": "Clear communication, confident expression, authentic sharing.",
            "remedies": "Blue color visualization, chanting, and creative writing."
        },
        "Slightly Weak": {
            "notes": "Occasional hesitation or mild self-censorship.",
            "remedies": "Mirror talk, journaling emotions, affirm ‘My voice matters’."
        },
        "Blocked / Underactive": {
            "notes": "Fear of judgment, throat tightness, unspoken truth.",
            "remedies": "Singing therapy, public speaking, releasing withheld emotions."
        },
        "Overactive / Dominant": {
            "notes": "Speaking impulsively, dominance in communication, or gossiping.",
            "remedies": "Mindful silence, blue stone therapy, communication pause ritual."
        },
    },
    "Third Eye (Ajna)": {
        "Balanced / Radiant": {
            "notes": "Intuitive, focused, seeing clearly with insight and calm.",
            "remedies": "Meditation, visualization, journaling dreams."
        },
        "Slightly Weak": {
            "notes": "Mild confusion or scattered thoughts.",
            "remedies": "Third eye breathing, lavender oil, reduce screen time."
        },
        "Blocked / Underactive": {
            "notes": "Overthinking, self-doubt, or mental fatigue.",
            "remedies": "Trust practice, candle gazing, Ho’oponopono for clarity."
        },
        "Overactive / Dominant": {
            "notes": "Too many ideas, mental exhaustion, lack of grounding.",
            "remedies": "Grounding meditation, simple routines, eye relaxation."
        },
    },
    "Crown (Sahasrara)": {
        "Balanced / Radiant": {
            "notes": "Spiritually connected, peaceful, open to divine guidance.",
            "remedies": "Silence meditation, gratitude, service-based actions."
        },
        "Slightly Weak": {
            "notes": "Occasional disconnection or doubt in spiritual trust.",
            "remedies": "Crown breathing, mantra ‘I am one with the divine’, white light meditation."
        },
        "Blocked / Underactive": {
            "notes": "Loss of purpose, cynicism, spiritual fatigue.",
            "remedies": "Prayer, journaling gratitude, grounding spiritual rituals."
        },
        "Overactive / Dominant": {
            "notes": "Too much in higher realms, lack of grounding or routine.",
            "remedies": "Earthing practices, grounding meals, reconnect with physical activities."
        },
    },
}

# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------
def clean_txt(text):
    return re.sub(r"[^\x00-\x7F]", "", text or "")

def download_logo():
    if not os.path.exists(LOGO_FILE):
        try:
            r = requests.get(LOGO_URL, timeout=10)
            if r.status_code == 200:
                with open(LOGO_FILE, "wb") as f:
                    f.write(r.content)
        except:
            pass

# ---------------------------------------------------------
# PDF CREATOR
# ---------------------------------------------------------
def make_pdf(data):
    download_logo()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)

    # header bar
    pdf.set_fill_color(139, 92, 246)
    pdf.rect(0, 0, 210, 18, "F")
    pdf.set_fill_color(236, 72, 153)
    pdf.rect(0, 18, 6, 275, "F")

    # logo
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=10, y=2, w=16)

    pdf.set_xy(30, 4)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 7, "Soulful Academy", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Professional Chakra Scan Report", ln=True)

    pdf.ln(15)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, f"Client Name: {data['client_name']}", ln=True)
    pdf.cell(0, 6, f"Session Date: {data['date']}", ln=True)
    pdf.cell(0, 6, f"Coach: {data['coach_name']}", ln=True)
    pdf.cell(0, 6, f"Intent: {data['goal']}", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Chakra Analysis", ln=True)
    pdf.set_font("Arial", "", 10)
    for ch, info in data["chakras"].items():
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, ch, ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, f"Status: {info['status']}", ln=True)
        pdf.multi_cell(0, 5, f"Notes: {clean_txt(info['notes'])}")
        pdf.multi_cell(0, 5, f"Remedies: {clean_txt(info['remedies'])}")

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Follow-up Plan", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, data["follow_up"])

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Affirmations", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, data["affirmations"])

    pdf.ln(3)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 4, "Generated by Soulful Academy | What You Seek is Seeking You.")
    return pdf.output(dest="S").encode("latin-1", "ignore")

# ---------------------------------------------------------
# FORM UI
# ---------------------------------------------------------
st.image(LOGO_URL, width=160)
st.title("Chakra Scanning Template (Coach Mode)")

with st.form("chakra_form"):
    c1, c2 = st.columns(2)
    with c1:
        client_name = st.text_input("Client Name", "")
        coach_name = st.text_input("Coach / Healer Name", "Rekha Babulkar")
    with c2:
        date_val = st.text_input("Session Date", datetime.date.today().strftime("%d-%m-%Y"))
        goal = st.text_input("Client Intent / Focus", "Relationship Healing")

    st.markdown("---")
    st.subheader("Chakra Observations")

    chakra_data = {}
    for ch in CHAKRAS:
        with st.expander(ch, expanded=(ch == "Root (Muladhara)")):
            status = st.selectbox(f"Energy Status – {ch}", STATUS_OPTIONS, key=f"status_{ch}")
            pre_notes = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("notes", "")
            pre_remedies = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("remedies", "")
            notes = st.text_area(f"Notes / Symptoms – {ch}", value=pre_notes, key=f"notes_{ch}")
            remedies = st.text_area(f"Remedies – {ch}", value=pre_remedies, key=f"rem_{ch}")
            chakra_data[ch] = {"status": status, "notes": notes, "remedies": remedies}

    st.markdown("---")
    st.subheader("Session Summary")
    follow_up = st.text_area("Follow-up Plan", "Follow-up in 7 days. Practice chakra meditation and affirmations.")
    affirmations = st.text_area("Affirmations", 
                                "I am safe. I allow emotions. My power is safe. My heart is open. "
                                "I express my truth. I trust my guidance. I am connected to the Divine.")

    submitted = st.form_submit_button("Create PDF Report", use_container_width=True)

if submitted:
    if not client_name:
        st.error("Please enter client name before generating report.")
    else:
        payload = {
            "client_name": client_name,
            "coach_name": coach_name,
            "date": date_val,
            "goal": goal,
            "chakras": chakra_data,
            "follow_up": follow_up,
            "affirmations": affirmations
        }
        pdf_bytes = make_pdf(payload)
        st.success("Report created successfully. Download below.")
        st.download_button(
            label="Download Chakra Report (PDF)",
            data=pdf_bytes,
            file_name=f"{client_name}_chakra_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
