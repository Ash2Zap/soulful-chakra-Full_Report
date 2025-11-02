import streamlit as st
from fpdf import FPDF
import datetime
import re

# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------
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

# Chakra colors (for PDF bars)
CHAKRA_COLORS = {
    "Root (Muladhara)": (220, 38, 38),       # red
    "Sacral (Svadhisthana)": (249, 115, 22), # orange
    "Solar Plexus (Manipura)": (234, 179, 8),
    "Heart (Anahata)": (34, 197, 94),
    "Throat (Vishuddha)": (59, 130, 246),
    "Third Eye (Ajna)": (79, 70, 229),
    "Crown (Sahasrara)": (168, 85, 247),
}

# status → score
STATUS_SCORE = {
    "Balanced / Radiant": 100,
    "Slightly Weak": 75,
    "Blocked / Underactive": 40,
    "Overactive / Dominant": 55,
}

# --------------------------------------------------
# CLEANER (for PDF latin-1)
# --------------------------------------------------
def clean_txt(text: str) -> str:
    if not text:
        return ""
    text = text.replace("•", "- ")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("’", "'")
    text = text.replace("‘", "'")
    text = text.replace("“", '"')
    text = text.replace("”", '"')
    text = re.sub(r"[^\x00-\xFF]", "", text)
    return text

# --------------------------------------------------
# PREDEFINED chakra info
# --------------------------------------------------
PREDEFINED_INFO = {
    "Root (Muladhara)": {
        "Balanced / Radiant": {
            "notes": "Grounded, secure, body-energy stable.",
            "remedies": "Gratitude journaling, red color therapy, mindful walks.",
        },
        "Slightly Weak": {
            "notes": "Mild insecurity about money or home.",
            "remedies": "Walk barefoot, chant LAM, root Reiki.",
        },
        "Blocked / Underactive": {
            "notes": "Fear, instability, lower-body fatigue.",
            "remedies": "Money forgiveness, red visualization, Ho'oponopono for parents.",
        },
        "Overactive / Dominant": {
            "notes": "Control or anger bursts.",
            "remedies": "Slow breathwork, trust meditation, yin grounding.",
        },
    },
    "Sacral (Svadhisthana)": {
        "Balanced / Radiant": {
            "notes": "Creative, expressive, emotionally open.",
            "remedies": "Dance, water meditation, orange candle."
        },
        "Slightly Weak": {
            "notes": "Mild guilt or emotional swelling.",
            "remedies": "Ho'oponopono for past partners, sacral journaling."
        },
        "Blocked / Underactive": {
            "notes": "Suppressed emotion, intimacy blocks.",
            "remedies": "Womb healing, mirror work, sacral Reiki."
        },
        "Overactive / Dominant": {
            "notes": "Emotional dependency or drama loops.",
            "remedies": "Boundaries, solitude, self-love affirmations."
        },
    },
    "Solar Plexus (Manipura)": {
        "Balanced / Radiant": {
            "notes": "Confident, action-oriented, clear will.",
            "remedies": "Citrine work, power pose, gratitude."
        },
        "Slightly Weak": {
            "notes": "Procrastination, self doubt.",
            "remedies": "Breath of fire, success journaling."
        },
        "Blocked / Underactive": {
            "notes": "People pleasing, fear of visibility.",
            "remedies": "Solar breathing, visibility practice."
        },
        "Overactive / Dominant": {
            "notes": "Overwork, control or burnout.",
            "remedies": "Cooling breath, forgiveness, rest."
        },
    },
    "Heart (Anahata)": {
        "Balanced / Radiant": {
            "notes": "Loving, compassionate, grateful.",
            "remedies": "Green light meditation, kindness journaling."
        },
        "Slightly Weak": {
            "notes": "Occasional loneliness.",
            "remedies": "Self-hug, forgiveness letters, green color therapy."
        },
        "Blocked / Underactive": {
            "notes": "Grief, heartbreak or resentment.",
            "remedies": "Heart Reiki, rose quartz meditation, 108x Ho'oponopono."
        },
        "Overactive / Dominant": {
            "notes": "Overgiving, guilt after saying no.",
            "remedies": "Receiving practice, boundaries."
        },
    },
    "Throat (Vishuddha)": {
        "Balanced / Radiant": {
            "notes": "Clear and confident communication.",
            "remedies": "Blue light visualization, chanting."
        },
        "Slightly Weak": {
            "notes": "Hesitation to speak truth.",
            "remedies": "Mirror talk, 'My voice matters'."
        },
        "Blocked / Underactive": {
            "notes": "Unspoken truth, throat tightness.",
            "remedies": "Singing therapy, emotional expression."
        },
        "Overactive / Dominant": {
            "notes": "Talking too much or gossip.",
            "remedies": "Mindful silence, pause ritual."
        },
    },
    "Third Eye (Ajna)": {
        "Balanced / Radiant": {
            "notes": "Intuitive, clear, calm inner vision.",
            "remedies": "Meditation, visualization, dream journaling."
        },
        "Slightly Weak": {
            "notes": "Mild confusion.",
            "remedies": "Third eye breathing, screen detox."
        },
        "Blocked / Underactive": {
            "notes": "Overthinking, cannot see path.",
            "remedies": "Trust practice, candle gazing."
        },
        "Overactive / Dominant": {
            "notes": "Too many ideas, not grounded.",
            "remedies": "Grounding meditation, simple routines."
        },
    },
    "Crown (Sahasrara)": {
        "Balanced / Radiant": {
            "notes": "Connected to Divine, inner peace.",
            "remedies": "Silence, gratitude, service."
        },
        "Slightly Weak": {
            "notes": "Some disconnection from source.",
            "remedies": "White light meditation, crown breathing."
        },
        "Blocked / Underactive": {
            "notes": "Loss of purpose, spiritual fatigue.",
            "remedies": "Prayer, gratitude journal."
        },
        "Overactive / Dominant": {
            "notes": "Too much in upper chakras, ungrounded.",
            "remedies": "Earthing, grounding meals, body movement."
        },
    },
}

# --------------------------------------------------
# CRYSTALS (shortened to fit PDF)
# --------------------------------------------------
CRYSTAL_REMEDIES = {
    "Root (Muladhara)": {
        "Balanced / Radiant": "Red Jasper / Lava. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
        "Slightly Weak": "Black Tourmaline / Hematite. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
        "Blocked / Underactive": "Obsidian, 7 Chakra bracelet. Visit: https://myaurabliss.com/product/lava-rock-7-chakra-strand-bracelet/",
        "Overactive / Dominant": "Smoky Quartz to soften. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
    },
    "Sacral (Svadhisthana)": {
        "Balanced / Radiant": "Carnelian / Moonstone. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Slightly Weak": "Carnelian bracelet. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Blocked / Underactive": "Peach Moonstone + Rose Quartz. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Overactive / Dominant": "Moonstone, Amethyst. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
    },
    "Solar Plexus (Manipura)": {
        "Balanced / Radiant": "Citrine, Tiger eye. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
        "Slightly Weak": "Citrine tumble. Visit: https://myaurabliss.com/product/natural-citrine-bracelet/",
        "Blocked / Underactive": "Golden calcite, Tiger eye. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
        "Overactive / Dominant": "Yellow calcite + Lepidolite. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
    },
    "Heart (Anahata)": {
        "Balanced / Radiant": "Rose Quartz / Green Aventurine. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Slightly Weak": "Rose Quartz bracelet. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Blocked / Underactive": "Malachite, Rhodochrosite. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Overactive / Dominant": "Pink Opal, Amethyst. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
    },
    "Throat (Vishuddha)": {
        "Balanced / Radiant": "Blue Lace Agate, Aquamarine. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Slightly Weak": "Sodalite / Amazonite. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Blocked / Underactive": "Lapis pendant. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Overactive / Dominant": "Celestite, Blue calcite. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
    },
    "Third Eye (Ajna)": {
        "Balanced / Radiant": "Amethyst / Lapis. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Slightly Weak": "Fluorite, Labradorite. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Blocked / Underactive": "Chevron Amethyst. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Overactive / Dominant": "Obsidian + Amethyst. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
    },
    "Crown (Sahasrara)": {
        "Balanced / Radiant": "Clear Quartz, Selenite. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Slightly Weak": "Selenite bowl. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Blocked / Underactive": "Clear Quartz point. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Overactive / Dominant": "Smoky Quartz + Selenite. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
    },
}

# --------------------------------------------------
# PDF GENERATOR (5 pages, safe)
# --------------------------------------------------
def make_pdf(data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)

    chakras = data["chakras"]
    chakra_scores = {}
    blocked = 0
    for ch, info in chakras.items():
        score = STATUS_SCORE.get(info["status"], 60)
        chakra_scores[ch] = score
        if info["status"] == "Blocked / Underactive":
            blocked += 1
    blocked_pct = round((blocked / 7.0) * 100, 1)

    # PAGE 1 ------------------------------------------------
    pdf.add_page()
    pdf.set_fill_color(139, 92, 246)
    pdf.rect(0, 0, 210, 15, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.set_xy(10, 4)
    pdf.cell(0, 6, clean_txt("Soulful Academy"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, clean_txt("Chakra and Crystal Healing Report"), ln=True)

    pdf.ln(8)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt(f"Client: {data['client_name']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Gender: {data['gender']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Date: {data['date']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Healer: {data['coach_name']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Intent: {data['goal']}"), ln=True)

    pdf.ln(3)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, clean_txt("Overall Chakra Health"), ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, clean_txt(f"Blocked chakras: {blocked} of 7 ({blocked_pct}%)"), ln=True)

    y = pdf.get_y() + 2
    max_bar = 120
    for ch in CHAKRAS:
        score = chakra_scores[ch]
        bar_w = max_bar * (score / 100.0)
        r, g, b = CHAKRA_COLORS[ch]
        pdf.set_xy(15, y)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, clean_txt(ch), ln=0)
        pdf.set_fill_color(r, g, b)
        pdf.rect(75, y + 1, bar_w, 4, "F")
        pdf.set_xy(160, y)
        pdf.cell(0, 5, clean_txt(f"{score}%"), ln=1)
        y += 7

    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 5, clean_txt("Quick Reading"), ln=True)
    pdf.set_font("Arial", "", 9)
    if blocked == 0:
        pdf.multi_cell(0, 5, clean_txt("Energy is flowing in all seven chakras. Maintain current practice."))
    else:
        pdf.multi_cell(0, 5, clean_txt("Some chakras need attention. Heal the ones marked Blocked or Overactive first."))

    # PAGE 2 ------------------------------------------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Chakra Summary (Coach View)"), ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, clean_txt("This is a quick glance at what came up in the scan. Use Page 3 and 4 for deeper session notes."))

    for ch in CHAKRAS:
        info = chakras[ch]
        status = info["status"]
        crystal_line = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")
        # shorten links for PDF width
        if "Visit:" in crystal_line and len(crystal_line) > 120:
            before, after = crystal_line.split("Visit:", 1)
            crystal_line = before.strip() + " Visit: " + after.strip()[:75] + " ..."
        r, g, b = CHAKRA_COLORS[ch]
        pdf.ln(2)
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, clean_txt(ch), ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, clean_txt("Energy Status: " + status), ln=True)
        pdf.multi_cell(0, 5, clean_txt("Crystal Suggestion: " + crystal_line))

    # PAGE 3-4 ----------------------------------------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Detailed Chakra Guidance"), ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", "", 10)

    for ch in CHAKRAS:
        if pdf.get_y() > 250:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 6, clean_txt("Detailed Chakra Guidance (contd.)"), ln=True)
            pdf.ln(3)
            pdf.set_font("Arial", "", 10)

        info = chakras[ch]
        r, g, b = CHAKRA_COLORS[ch]
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, clean_txt(ch), ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, clean_txt("Status: " + info["status"]), ln=True)
        pdf.multi_cell(0, 5, clean_txt("Notes / Symptoms: " + info["notes"]))
        pdf.multi_cell(0, 5, clean_txt("Energy Remedies: " + info["remedies"]))
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, clean_txt("Crystal Remedies: " + info["crystals"]))
        pdf.ln(2)

    # PAGE 5 ------------------------------------------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Follow-up and Home Practice"), ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt(data["follow_up"]))
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Affirmations for Client"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt(data["affirmations"]))
    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, clean_txt("Crystal Support from MyAuraBliss"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt("Visit https://myaurabliss.com and choose the bracelet / crystal for the chakras that showed Blocked or Overactive."))
    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 4, clean_txt("Generated by Soulful Academy | What You Seek is Seeking You."))

    return pdf.output(dest="S").encode("latin-1", "ignore")

# --------------------------------------------------
# EMAIL (lazy import so it doesn't crash)
# --------------------------------------------------
def send_email_with_pdf(to_email: str, pdf_bytes: bytes, filename: str, client_name: str):
    try:
        import smtplib
        from email.message import EmailMessage
    except Exception:
        st.warning("Email library not available.")
        return

    try:
        email_user = st.secrets["email_user"]
        email_pass = st.secrets["email_pass"]
    except Exception:
        st.warning("Email not sent: please add email_user and email_pass in Streamlit secrets.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"Chakra and Crystal Report for {client_name}"
    msg["From"] = email_user
    msg["To"] = to_email
    msg.set_content("Your report is attached.")
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=filename)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_user, email_pass)
        smtp.send_message(msg)

    st.success("Report emailed successfully.")

# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
def main():
    st.set_page_config(page_title="Soulful Chakra Report", page_icon="🪬", layout="centered")

    st.title("Soulful Academy – Chakra + Crystal Scanning")
    st.caption("Rapid diagnostic report for your clients. Fill and download PDF.")

    c1, c2, c3 = st.columns(3)
    with c1:
        client_name = st.text_input("Client Name", "")
    with c2:
        coach_name = st.text_input("Coach / Healer", "Rekha Babulkar")
    with c3:
        date_val = st.text_input("Session Date", datetime.date.today().strftime("%d-%m-%Y"))

    gender = st.radio("Gender", ["Female", "Male", "Other"], horizontal=True)
    goal = st.text_input("Client Intent / Focus", "Relationship Healing / Money / Health")

    st.markdown("---")
    st.subheader("Chakra Observations")

    chakra_data = {}
    for ch in CHAKRAS:
        with st.expander(ch, expanded=(ch == "Root (Muladhara)")):
            status_key = f"{ch}_status"
            notes_key = f"{ch}_notes"
            remedies_key = f"{ch}_remedies"
            crystals_key = f"{ch}_crystals"
            prev_key = f"{ch}_prev"

            if status_key not in st.session_state:
                st.session_state[status_key] = STATUS_OPTIONS[0]
            if prev_key not in st.session_state:
                st.session_state[prev_key] = st.session_state[status_key]

            status = st.selectbox(f"Energy Status – {ch}", STATUS_OPTIONS, key=status_key)

            # auto-fill on change
            if st.session_state[prev_key] != status:
                st.session_state[notes_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("notes", "")
                st.session_state[remedies_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("remedies", "")
                st.session_state[crystals_key] = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")
                st.session_state[prev_key] = status

            if notes_key not in st.session_state:
                st.session_state[notes_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("notes", "")
            if remedies_key not in st.session_state:
                st.session_state[remedies_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("remedies", "")
            if crystals_key not in st.session_state:
                st.session_state[crystals_key] = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")

            notes = st.text_area(f"Notes / Symptoms – {ch}", st.session_state[notes_key], key=notes_key)
            remedies = st.text_area(f"Remedies – {ch}", st.session_state[remedies_key], key=remedies_key)
            crystals = st.text_area(f"Crystal Remedies – {ch}", st.session_state[crystals_key], key=crystals_key)

            chakra_data[ch] = {
                "status": status,
                "notes": notes,
                "remedies": remedies,
                "crystals": crystals,
            }

    st.markdown("---")
    st.subheader("Session Summary")
    follow_up = st.text_area("Follow-up Plan", "Follow-up in 7 days. Do chakra meditation, wear the suggested crystal from MyAuraBliss, do 108x Ho'oponopono on the key person/event.")
    affirmations = st.text_area("Affirmations", "I am safe. I receive. My power is safe. My heart is open. I speak my truth. I trust my guidance. I am connected to the Divine.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        make_pdf_btn = st.button("Create & Download PDF", use_container_width=True)
    with col2:
        email_to = st.text_input("Email report to", "")
        send_btn = st.button("Send PDF to Email", use_container_width=True)

    if make_pdf_btn or send_btn:
        if not client_name:
            st.error("Please enter Client Name.")
        else:
            payload = {
                "client_name": client_name,
                "gender": gender,
                "coach_name": coach_name,
                "date": date_val,
                "goal": goal,
                "chakras": chakra_data,
                "follow_up": follow_up,
                "affirmations": affirmations,
            }
            pdf_bytes = make_pdf(payload)

            if make_pdf_btn:
                st.success("PDF is ready. Download below.")
                st.download_button(
                    "Download Chakra Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"{client_name}_chakra_report.pdf",
                    mime="application/pdf"
                )

            if send_btn:
                if not email_to:
                    st.error("Enter an email to send.")
                else:
                    send_email_with_pdf(email_to, pdf_bytes, f"{client_name}_chakra_report.pdf", client_name)


# --------------------------------------------------
# RUN SAFELY
# --------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # show the error on the page instead of a blank screen
        st.error("App crashed. Here is the error:")
        st.exception(e)
