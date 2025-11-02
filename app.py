def make_pdf(data):
    download_logo()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)

    chakras = data["chakras"]

    # compute scores
    chakra_scores = {}
    blocked_count = 0
    for ch, info in chakras.items():
        status = info["status"]
        score = STATUS_SCORE.get(status, 60)
        chakra_scores[ch] = score
        if status == "Blocked / Underactive":
            blocked_count += 1

    blocked_pct = round((blocked_count / 7.0) * 100, 1)

    # ---------------- PAGE 1 (same as before) ----------------
    pdf.add_page()
    pdf.set_fill_color(139, 92, 246)
    pdf.rect(0, 0, 210, 18, "F")
    pdf.set_fill_color(236, 72, 153)
    pdf.rect(0, 18, 6, 275, "F")
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=10, y=2, w=16)
    pdf.set_xy(30, 4)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 7, clean_txt("Soulful Academy"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, clean_txt("Chakra and Crystal Healing Report"), ln=True)

    pdf.ln(12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt(f"Client Name: {data['client_name']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Gender: {data['gender']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Date: {data['date']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Coach: {data['coach_name']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Intent: {data['goal']}"), ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Overall Chakra Health"), ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, clean_txt(f"Blocked chakras: {blocked_count} of 7 ({blocked_pct}%)"), ln=True)

    # bar chart
    y = pdf.get_y() + 3
    max_bar_width = 120
    for ch in CHAKRAS:
        score = chakra_scores[ch]
        bar_w = max_bar_width * (score / 100.0)
        r, g, b = CHAKRA_COLORS[ch]
        pdf.set_xy(20, y)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, clean_txt(ch), ln=0)
        pdf.set_xy(80, y + 1)
        pdf.set_fill_color(r, g, b)
        pdf.rect(80, y + 1, bar_w, 4, "F")
        pdf.set_xy(165, y)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 5, clean_txt(f"{score}%"), ln=1)
        y += 7

    pdf.ln(3)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 5, clean_txt("Quick Reading"), ln=True)
    pdf.set_font("Arial", "", 9)
    if blocked_count == 0:
        pdf.multi_cell(0, 5, clean_txt("All chakras are open and flowing. Maintain current rituals."))
    else:
        pdf.multi_cell(0, 5, clean_txt("There are some energy blocks. Focus on the chakras marked as Blocked or Overactive. Use the remedies and crystals suggested."))

    # ---------------- PAGE 2 (new layout) ----------------
    pdf.add_page()
    pdf.set_fill_color(236, 72, 153)
    pdf.rect(0, 0, 210, 7, "F")
    pdf.ln(8)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Chakra Summary (Coach View)"), ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, clean_txt("Note: This is a quick snapshot for the healer. Detailed guidance is on the next pages."))

    for ch in CHAKRAS:
        info = chakras[ch]
        status = info["status"]
        crystal_line = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")
        # chop URL to avoid breaking layout
        if "Visit:" in crystal_line and len(crystal_line) > 120:
            before, after = crystal_line.split("Visit:", 1)
            after = after.strip()
            crystal_line = before.strip() + " Visit: " + after[:80] + " ..."
        r, g, b = CHAKRA_COLORS[ch]
        pdf.ln(2)
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, clean_txt(ch), ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, clean_txt(f"Energy Status: {status}"), ln=True)
        pdf.multi_cell(0, 5, clean_txt(f"Crystal Suggestion: {crystal_line}"))

    # ---------------- PAGES 3-4: detailed (same style) ----------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Detailed Chakra Guidance"), ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", "", 10)

    for ch in CHAKRAS:
        info = chakras[ch]
        if pdf.get_y() > 250:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 6, clean_txt("Detailed Chakra Guidance (contd.)"), ln=True)
            pdf.ln(3)
            pdf.set_font("Arial", "", 10)
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

    # ---------------- PAGE 5: follow up ----------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Follow-up and Home Practice"), ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt(data["follow_up"]))
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Affirmations"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt(data["affirmations"]))
    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, clean_txt("Crystal Support From MyAuraBliss"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt("Visit https://myaurabliss.com and pick the bracelets or crystal sets for the chakras that showed Blocked or Overactive."))
    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 4, clean_txt("Generated by Soulful Academy | What You Seek is Seeking You."))

    return pdf.output(dest="S").encode("latin-1", "ignore")
