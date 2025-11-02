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
# PREDEFINED NOTES / REMEDIES (same as before)
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
# CRYSTAL REMEDIES (built to match your store style)
# You can rename to EXACT product names in myaurabliss.com
# ---------------------------------------------------------
CRYSTAL_REMEDIES = {
    "Root (Muladhara)": {
        "Balanced / Radiant": "Red Jasper Tumble • 7-Chakra Mala (Grounding) • Smoky Quartz – keep near feet. (myaurabliss.com root chakra collection) :contentReference[oaicite:1]{index=1}",
        "Slightly Weak": "Black Tourmaline Protection Stone • Hematite Bracelet • Red Jasper Angel for stability. :contentReference[oaicite:2]{index=2}",
        "Blocked / Underactive": "Red Jasper Wand on root • Black Obsidian near door • Grounding Kit (Root).",
        "Overactive / Dominant": "Smoky Quartz for excess fire • Hematite for balance • 7-Chakra Mala for harmonising."
    },
    "Sacral (Svadhisthana)": {
        "Balanced / Radiant": "Carnelian Palm Stone • Peach Moonstone • Orange Calcite (joy & creativity).",
        "Slightly Weak": "Carnelian Bracelet • Sunstone • Sacral Crystal Set (for emotional flow).",
        "Blocked / Underactive": "Peach Moonstone on womb • Carnelian tower • Rose Quartz to soothe guilt.",
        "Overactive / Dominant": "Moonstone for emotional balance • Pink Calcite • Amethyst to cool sacral."
    },
    "Solar Plexus (Manipura)": {
        "Balanced / Radiant": "Citrine Point • Tiger Eye Bracelet • 7 Chakra Mala (power activation).",
        "Slightly Weak": "Citrine tumble in pocket • Pyrite Money Stone • Yellow Aventurine.",
        "Blocked / Underactive": "Golden Calcite • Tiger Eye for confidence • Manifestation Citrine Kit.",
        "Overactive / Dominant": "Yellow Calcite (soften control) • Lepidolite for stress • Honey Calcite."
    },
    "Heart (Anahata)": {
        "Balanced / Radiant": "Rose Quartz Heart • Green Aventurine • Rhodonite for compassion. :contentReference[oaicite:3]{index=3}",
        "Slightly Weak": "Rose Quartz Bracelet • Prehnite with Epidote • Green Jade.",
        "Blocked / Underactive": "Rose Quartz Crystal Heart (self-love) • Rhodochrosite • Malachite for deep release.",
        "Overactive / Dominant": "Pink Opal • Mangano Calcite • Amethyst to calm overgiving."
    },
    "Throat (Vishuddha)": {
        "Balanced / Radiant": "Blue Lace Agate • Aquamarine • Angelite.",
        "Slightly Weak": "Sodalite • Amazonite • 7-Chakra Mala (speak truth).",
        "Blocked / Underactive": "Blue Apatite • Lapis Lazuli tower • Aquamarine pendant for expression.",
        "Overactive / Dominant": "Celestite • Angelite • Blue Calcite (to cool sharp speech)."
    },
    "Third Eye (Ajna)": {
        "Balanced / Radiant": "Amethyst Cluster • Lapis Lazuli • Iolite for intuition.",
        "Slightly Weak": "Amethyst Tumble • Fluorite Tower • Labradorite.",
        "Blocked / Underactive": "Indigo Gabbro • Chevron Amethyst • Sodalite for mental clarity.",
        "Overactive / Dominant": "Black Obsidian + Amethyst combo to ground visions."
    },
    "Crown (Sahasrara)": {
        "Balanced / Radiant": "Clear Quartz Generator • Selenite Wand • 7 Chakra Mala (higher connection).",
        "Slightly Weak": "Selenite Bowl • Amethyst Cluster • Angel Aura Quartz.",
        "Blocked / Underactive": "Clear Quartz Point on crown • Selenite charging plate • Lotus Crystal.",
        "Overactive / Dominant": "Smoky Quartz + Selenite combo • Hematite to ground."
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

    # header
    pdf.set_fill_color(139, 92, 246)
    pdf.rect(0, 0, 210, 18, "F")
    pdf.set_fill_color(236, 72, 153)
    pdf.rect(0, 18, 6, 275, "F")

    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=10, y=2, w=16)

    pdf.set_xy(30, 4)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 7, "Soulful Academy", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Professional Chakra + Crystal Report", ln=True)

    pdf.ln(15)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, f"Client Name: {data['client_name']}", ln=True)
    pdf.cell(0, 6, f"Gender: {data['gender']}", ln=True)
    pdf.cell(0, 6, f"Date: {data['date']}", ln=True)
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
        pdf.multi_cell(0, 5, f"Notes / Symptoms: {clean_txt(info['notes'])}")
        pdf.multi_cell(0, 5, f"Remedies: {clean_txt(info['remedies'])}")
        # crystals added
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, f"Crystal Remedies (myaurabliss.com): {clean_txt(info.get('crystals',''))}")

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
st.title("Soulful Academy Chakra + Crystal Scanning Template")

with st.form("chakra_form"):
    c1, c2 = st.columns(2)
    with c1:
        client_name = st.text_input("Client Name", "")
        coach_name = st.text_input("Coach / Healer Name", "Rekha Babulkar")
    with c2:
        date_val = st.text_input("Session Date", datetime.date.today().strftime("%d-%m-%Y"))
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        goal = st.text_input("Client Intent / Focus", "Relationship Healing")

    st.markdown("---")
    st.subheader("Chakra Observations (auto-fills Notes, Remedies, Crystals)")

    chakra_data = {}
    for ch in CHAKRAS:
        with st.expander(ch, expanded=(ch == "Root (Muladhara)")):
            status_key = f"status_{ch}"
            notes_key = f"notes_{ch}"
            remedies_key = f"rem_{ch}"
            crystals_key = f"crys_{ch}"

            status = st.selectbox(f"Energy Status – {ch}", STATUS_OPTIONS, key=status_key)

            # Dynamic auto-fill from PREDEFINED + CRYSTALS
            pre_notes = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("notes", "")
            pre_remedies = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("remedies", "")
            pre_crystals = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")

            # update session so that UI refresh still shows latest
            st.session_state[notes_key] = pre_notes
            st.session_state[remedies_key] = pre_remedies
            st.session_state[crystals_key] = pre_crystals

            notes = st.text_area(f"Notes / Symptoms – {ch}",
                                 value=st.session_state[notes_key],
                                 key=notes_key)

            remedies = st.text_area(f"Remedies – {ch}",
                                    value=st.session_state[remedies_key],
                                    key=remedies_key)

            crystals = st.text_area(f"Crystal Remedies – {ch}  (from myaurabliss.com)",
                                    value=st.session_state[crystals_key],
                                    key=crystals_key)

            chakra_data[ch] = {
                "status": status,
                "notes": notes,
                "remedies": remedies,
                "crystals": crystals,
            }

    st.markdown("---")
    st.subheader("Session Summary")
    follow_up = st.text_area("Follow-up Plan", "Follow-up in 7 days. Practice chakra meditation, wear recommended crystal, and do 108x Ho’oponopono on main person/event.")
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
            "gender": gender,
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
            label="Download Chakra + Crystal Report (PDF)",
            data=pdf_bytes,
            file_name=f"{client_name}_chakra_crystal_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
