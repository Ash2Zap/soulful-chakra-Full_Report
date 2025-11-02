import streamlit as st
from fpdf import FPDF
import datetime
import os
import requests
import re
import smtplib
from email.message import EmailMessage
from io import BytesIO

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Soulful Academy – Chakra + Crystal Report",
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
# LINKS to your store (we browsed the site to take these)  🌸
# Root & Heart & Crown & Third Eye are 100% from the site
# Others follow the same URL pattern on myaurabliss.com
# Source: myaurabliss.com product-category chakra pages
# :contentReference[oaicite:0]{index=0}
# ---------------------------------------------------------
CHAKRA_LINKS = {
    "Root (Muladhara)": "https://myaurabliss.com/product-category/chakra/root-chakra/",
    "Sacral (Svadhisthana)": "https://myaurabliss.com/product-category/chakra/sacral-chakra/",
    "Solar Plexus (Manipura)": "https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
    "Heart (Anahata)": "https://myaurabliss.com/product-category/chakra/heart-chakra/",
    "Throat (Vishuddha)": "https://myaurabliss.com/product-category/chakra/throat-chakra/",
    "Third Eye (Ajna)": "https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
    "Crown (Sahasrara)": "https://myaurabliss.com/product-category/chakra/crown-chakra/",
}

# ---------------------------------------------------------
# PREDEFINED NOTES / REMEDIES
# ---------------------------------------------------------
PREDEFINED_INFO = {
    "Root (Muladhara)": {
        "Balanced / Radiant": {
            "notes": "Grounded, stable, calm, connected to body and finances aligned.",
            "remedies": "Gratitude journaling, red crystal grounding meditation, mindful walks."
        },
        "Slightly Weak": {
            "notes": "Mild insecurity about money, overthinking about safety, shifting base often.",
            "remedies": "Walk barefoot, chant LAM, Root Reiki healing, safety affirmations."
        },
        "Blocked / Underactive": {
            "notes": "Chronic fear, financial instability, or low energy in legs/lower back.",
            "remedies": "Red color therapy, money forgiveness ritual, Ho’oponopono for parents."
        },
        "Overactive / Dominant": {
            "notes": "Control tendencies, anger bursts, attachment to material comfort.",
            "remedies": "Trust meditations, slow breathwork, grounding yin yoga."
        },
    },
    "Sacral (Svadhisthana)": {
        "Balanced / Radiant": {
            "notes": "Creative, emotionally expressive, open to intimacy and pleasure.",
            "remedies": "Dance therapy, water visualization, orange candle meditation."
        },
        "Slightly Weak": {
            "notes": "Mild guilt or emotional up/down in relationships.",
            "remedies": "Ho’oponopono for past partners, sacral journaling, forgiveness rituals."
        },
        "Blocked / Underactive": {
            "notes": "Suppressed emotions, relationship blocks, disconnection from sensuality.",
            "remedies": "Womb healing, mirror work, sacral Reiki cleansing."
        },
        "Overactive / Dominant": {
            "notes": "Emotional dependency, drama loops, or overattachment to people.",
            "remedies": "Healthy boundaries, creative solitude, self-love affirmations."
        },
    },
    "Solar Plexus (Manipura)": {
        "Balanced / Radiant": {
            "notes": "Confident, decisive, action-oriented, leadership energy present.",
            "remedies": "Citrine work, power pose, gratitude before tasks."
        },
        "Slightly Weak": {
            "notes": "Procrastination, self-doubt or low motivation.",
            "remedies": "Breath of fire, success journaling, ‘My power is safe’ affirmations."
        },
        "Blocked / Underactive": {
            "notes": "People pleasing, indecision, fear of visibility.",
            "remedies": "Solar breathing, visibility mirror practice, Ho’oponopono for authority."
        },
        "Overactive / Dominant": {
            "notes": "Overwork, aggression, excessive control or burnout.",
            "remedies": "Cooling breath, forgiveness practice, balanced diet/rest."
        },
    },
    "Heart (Anahata)": {
        "Balanced / Radiant": {
            "notes": "Loving, compassionate, peaceful and grateful.",
            "remedies": "Green light visualization, kindness journaling, heart gratitude meditation."
        },
        "Slightly Weak": {
            "notes": "Occasional loneliness or fear of vulnerability.",
            "remedies": "Daily self-hug, forgiveness letters, green color therapy."
        },
        "Blocked / Underactive": {
            "notes": "Grief, heartbreak, resentment, rejection/love wound.",
            "remedies": "Heart Reiki healing, rose quartz meditation, 108x Ho’oponopono."
        },
        "Overactive / Dominant": {
            "notes": "Overgiving, martyr patterns, guilty after saying no.",
            "remedies": "Receiving practice, boundaries, ‘I deserve to receive’ affirmations."
        },
    },
    "Throat (Vishuddha)": {
        "Balanced / Radiant": {
            "notes": "Clear communication, confident expression, authentic sharing.",
            "remedies": "Blue light visualization, chanting, journaling emotions."
        },
        "Slightly Weak": {
            "notes": "Hesitation to speak, fear of judgment in small doses.",
            "remedies": "Mirror talk, ‘My voice matters’, short reels/talks daily."
        },
        "Blocked / Underactive": {
            "notes": "Unspoken truth, throat tightness, holding back feelings.",
            "remedies": "Singing therapy, public speaking, release withheld emotions."
        },
        "Overactive / Dominant": {
            "notes": "Talking too much, dominating discussions, or gossip.",
            "remedies": "Mindful silence, blue stones, communication pause ritual."
        },
    },
    "Third Eye (Ajna)": {
        "Balanced / Radiant": {
            "notes": "Intuitive, clear-seeing, calm mind.",
            "remedies": "Meditation, visualization, dream journaling."
        },
        "Slightly Weak": {
            "notes": "Mild confusion or scattered thoughts.",
            "remedies": "Third eye breathing, lavender oil, screen-time detox."
        },
        "Blocked / Underactive": {
            "notes": "Overthinking, self-doubt, feeling ‘I can’t see my path’.",
            "remedies": "Trust practice, candle gazing, Ho’oponopono for clarity."
        },
        "Overactive / Dominant": {
            "notes": "Too many ideas, mental exhaustion, not grounded.",
            "remedies": "Grounding meditation, simple routines, eye relaxation."
        },
    },
    "Crown (Sahasrara)": {
        "Balanced / Radiant": {
            "notes": "Spiritually connected, peaceful, intuitive downloads.",
            "remedies": "Silence meditation, gratitude, seva/service."
        },
        "Slightly Weak": {
            "notes": "Sometimes disconnected or doubting divine timing.",
            "remedies": "Crown breathing, ‘I am one with the Divine’, white light meditation."
        },
        "Blocked / Underactive": {
            "notes": "Loss of purpose, spiritual fatigue, dryness in prayer.",
            "remedies": "Prayer, gratitude journaling, grounding spiritual rituals."
        },
        "Overactive / Dominant": {
            "notes": "Too much in upper chakras, not in body, not in routine.",
            "remedies": "Earthing, grounding meals, physical exercise + selenite cleanse."
        },
    },
}

# ---------------------------------------------------------
# CRYSTAL REMEDIES + LINKS
# pulled / derived from myaurabliss.com categories
# ---------------------------------------------------------
CRYSTAL_REMEDIES = {
    "Root (Muladhara)": {
        "Balanced / Radiant": "Red Jasper / Lava Rock / Sulemani Hakik bracelet. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
        "Slightly Weak": "Black Tourmaline, Hematite, Grounding combo. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
        "Blocked / Underactive": "Obsidian, Red Jasper wand, 7 Chakra Strand. Visit: https://myaurabliss.com/product/lava-rock-7-chakra-strand-bracelet/",
        "Overactive / Dominant": "Smoky Quartz + Hematite to balance fire. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
    },
    "Sacral (Svadhisthana)": {
        "Balanced / Radiant": "Carnelian / Peach Moonstone / Orange calcite set. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Slightly Weak": "Carnelian bracelet + Sunstone. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Blocked / Underactive": "Peach Moonstone on womb + Rose Quartz. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Overactive / Dominant": "Moonstone + Amethyst to cool emotions. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
    },
    "Solar Plexus (Manipura)": {
        "Balanced / Radiant": "Citrine / Tiger Eye / 7 Chakra bracelet. Visit: https://myaurabliss.com/product/natural-citrine-bracelet/",
        "Slightly Weak": "Citrine tumble + Pyrite money stone. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
        "Blocked / Underactive": "Golden calcite, Tiger eye, manifestation kit. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
        "Overactive / Dominant": "Yellow calcite + Lepidolite to soften control. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
    },
    "Heart (Anahata)": {
        "Balanced / Radiant": "Rose Quartz Heart, Green Aventurine, Rhodonite. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Slightly Weak": "Rose Quartz bracelet, Prehnite, Green jade. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Blocked / Underactive": "Malachite, Rhodochrosite, Rose Quartz love kit. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Overactive / Dominant": "Pink Opal, Mangano calcite, Amethyst to calm. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
    },
    "Throat (Vishuddha)": {
        "Balanced / Radiant": "Blue Lace Agate / Aquamarine / Angelite. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Slightly Weak": "Sodalite + Amazonite. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Blocked / Underactive": "Lapis Lazuli tower + Aquamarine pendant. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Overactive / Dominant": "Celestite / Blue calcite (cooling). Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
    },
    "Third Eye (Ajna)": {
        "Balanced / Radiant": "Amethyst cluster / Lapis Lazuli. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Slightly Weak": "Fluorite tower, Labradorite. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Blocked / Underactive": "Chevron Amethyst, Sodalite, Indigo gabbro. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Overactive / Dominant": "Black Obsidian + Amethyst to ground. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
    },
    "Crown (Sahasrara)": {
        "Balanced / Radiant": "Clear Quartz, Selenite wand, 7 Chakra mala. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Slightly Weak": "Selenite bowl, Angel aura quartz. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Blocked / Underactive": "Clear Quartz point on crown. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Overactive / Dominant": "Smoky Quartz + Selenite to balance. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
    },
}

# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------
def clean_txt(text: str) -> str:
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
# EMAIL SENDER (dummy – fill secrets to make it live)
# ---------------------------------------------------------
def send_email_with_pdf(to_email: str, subject: str, body: str, pdf_bytes: bytes, filename: str):
    """
    To make this work on Streamlit Cloud:
    - add to .streamlit/secrets.toml:
      email_user="your@gmail.com"
      email_pass="your-app-password"
    - then this will send from that account.
    """
    try:
        email_user = st.secrets["email_user"]
        email_pass = st.secrets["email_pass"]
    except Exception:
        st.warning("Email not sent: add email_user and email_pass in Streamlit secrets.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_user
    msg["To"] = to_email
    msg.set_content(body)

    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=filename)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_user, email_pass)
        smtp.send_message(msg)

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
    pdf.cell(0, 6, "Chakra + Crystal Healing Report", ln=True)

    # client details
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

    for ch, info in data["chakras"].items():
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, ch, ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, f"Status: {info['status']}", ln=True)
        pdf.multi_cell(0, 5, f"Notes / Symptoms: {clean_txt(info['notes'])}")
        pdf.multi_cell(0, 5, f"Healing Remedies: {clean_txt(info['remedies'])}")
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, f"Crystal Remedies: {clean_txt(info['crystals'])}")

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
# UI (REACTIVE – no form, so dropdown updates fields immediately)
# ---------------------------------------------------------
st.image(LOGO_URL, width=160)
st.title("Soulful Academy Chakra + Crystal Scanning Template")

# client info
c1, c2, c3 = st.columns(3)
with c1:
    client_name = st.text_input("Client Name", "")
with c2:
    coach_name = st.text_input("Coach / Healer", "Rekha Babulkar")
with c3:
    date_val = st.text_input("Session Date", datetime.date.today().strftime("%d-%m-%Y"))

gender = st.radio("Gender", ["Female", "Male", "Other"], horizontal=True)
goal = st.text_input("Client Intent / Focus", "Relationship Healing")

st.markdown("---")
st.subheader("Chakra Observations")

chakra_data = {}

for ch in CHAKRAS:
    with st.expander(ch, expanded=(ch == "Root (Muladhara)")):

        status_key = f"{ch}_status"
        notes_key = f"{ch}_notes"
        remedies_key = f"{ch}_remedies"
        crystals_key = f"{ch}_crystals"
        prev_status_key = f"{ch}_prev_status"

        # init
        if status_key not in st.session_state:
            st.session_state[status_key] = STATUS_OPTIONS[0]
        if prev_status_key not in st.session_state:
            st.session_state[prev_status_key] = st.session_state[status_key]

        # status selector
        status = st.selectbox(f"Energy Status – {ch}", STATUS_OPTIONS, key=status_key)

        # if status changed, refresh notes/remedies/crystals
        if st.session_state[prev_status_key] != status:
            st.session_state[notes_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("notes", "")
            st.session_state[remedies_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("remedies", "")
            st.session_state[crystals_key] = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")
            st.session_state[prev_status_key] = status

        # ensure keys exist
        if notes_key not in st.session_state:
            st.session_state[notes_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("notes", "")
        if remedies_key not in st.session_state:
            st.session_state[remedies_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("remedies", "")
        if crystals_key not in st.session_state:
            st.session_state[crystals_key] = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")

        notes = st.text_area(f"Notes / Symptoms – {ch}", value=st.session_state[notes_key], key=notes_key)
        remedies = st.text_area(f"Remedies – {ch}", value=st.session_state[remedies_key], key=remedies_key)
        crystals = st.text_area(f"Crystal Remedies – {ch}", value=st.session_state[crystals_key], key=crystals_key)

        # quick link to shop
        link = CHAKRA_LINKS.get(ch)
        if link:
            st.markdown(f"[Visit {ch} products on MyAuraBliss]({link})")

        chakra_data[ch] = {
            "status": status,
            "notes": notes,
            "remedies": remedies,
            "crystals": crystals,
        }

st.markdown("---")
st.subheader("Session Summary")
follow_up = st.text_area("Follow-up Plan", "Follow-up in 7 days. Practice chakra meditation, wear the suggested crystal bracelet from MyAuraBliss, and do 108x Ho’oponopono.")
affirmations = st.text_area("Affirmations",
                            "I am safe. I allow emotions. My power is safe. My heart is open. "
                            "I express my truth. I trust my guidance. I am connected to the Divine.")

st.markdown("---")
st.subheader("Download / Email")

col_a, col_b = st.columns(2)
with col_a:
    generate_pdf = st.button("💜 Create & Download PDF", use_container_width=True)
with col_b:
    email_to = st.text_input("Send report to email", "")
    send_email_btn = st.button("📩 Send PDF to email", use_container_width=True)

if generate_pdf or send_email_btn:
    if not client_name:
        st.error("Please enter client name.")
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

        if generate_pdf:
            st.success("PDF ready. Download below 👇")
            st.download_button(
                label="Download Chakra + Crystal Report (PDF)",
                data=pdf_bytes,
                file_name=f"{client_name}_chakra_crystal_report.pdf",
                mime="application/pdf"
            )

        if send_email_btn:
            if not email_to:
                st.error("Enter an email to send.")
            else:
                send_email_with_pdf(
                    to_email=email_to,
                    subject=f"Chakra + Crystal Report for {client_name}",
                    body="Your Soulful Academy report is attached. Love, Rekha 💜",
                    pdf_bytes=pdf_bytes,
                    filename=f"{client_name}_chakra_crystal_report.pdf"
                )
                st.success("If email credentials are set in secrets, the report has been sent ✅")
