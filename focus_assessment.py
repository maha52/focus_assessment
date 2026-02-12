import streamlit as st
import random
import time
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Focus Assessment | Sishya School",
    layout="centered"
)

# ---------------- PDF GENERATOR ----------------
def generate_pdf(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "Sishya School, Hosur")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 80, "Focus Assessment Report (SEL)")

    y = height - 140
    c.setFont("Helvetica", 11)

    for k, v in data.items():
        c.drawString(80, y, f"{k}: {v}")
        y -= 25

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ---------------- HEADER ----------------
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=90)
with col2:
    st.markdown("## **Sishya School, Hosur**")
    st.markdown("### 🧠 Focus Assessment – Social Emotional Learning")

st.divider()

# ---------------- STUDENT DETAILS ----------------
if "started" not in st.session_state:
    with st.form("student_form"):
        st.subheader("👤 Student Information")
        name = st.text_input("Student Name")
        clas = st.text_input("Class / Section")
        start_btn = st.form_submit_button("Start Assessment")

    if start_btn:
        st.session_state.student_name = name
        st.session_state.student_class = clas
        st.session_state.started = True
    else:
        st.stop()

# ---------------- CONSTANTS ----------------
STIMULI = ["A", "B", "C", "D", "E", "X", "Y", "Z"]
TOTAL_TRIALS = 20

# ---------------- SESSION STATE INIT ----------------
if "trial" not in st.session_state:
    st.session_state.trial = 1
    st.session_state.phase = "target"
    st.session_state.target = random.choice(STIMULI)
    st.session_state.stimulus = ""
    st.session_state.hits = 0
    st.session_state.misses = 0
    st.session_state.false_clicks = 0
    st.session_state.reaction_times = []
    st.session_state.start_time = 0

if "class_results" not in st.session_state:
    st.session_state.class_results = []

# ---------------- TRIAL DISPLAY ----------------
st.subheader(f"Trial {st.session_state.trial} / {TOTAL_TRIALS}")

# ---------------- TARGET PHASE ----------------
if st.session_state.phase == "target":
    st.markdown(
        f"""
        <h3 style='text-align:center;'>Remember this target</h3>
        <h1 style='text-align:center;font-size:90px;color:green;'>
        {st.session_state.target}
        </h1>
        """,
        unsafe_allow_html=True
    )

    if st.button("Next ▶️"):
        st.session_state.stimulus = random.choice(STIMULI)
        st.session_state.start_time = time.time()
        st.session_state.phase = "stimulus"
        st.rerun()

# ---------------- STIMULUS PHASE ----------------
elif st.session_state.phase == "stimulus":
    st.markdown(
        f"""
        <h3 style='text-align:center;'>Focus on the letter</h3>
        <h1 style='text-align:center;font-size:90px;'>
        {st.session_state.stimulus}
        </h1>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎯 TARGET"):
            reaction = time.time() - st.session_state.start_time
            if st.session_state.stimulus == st.session_state.target:
                st.session_state.hits += 1
                st.session_state.reaction_times.append(reaction)
            else:
                st.session_state.false_clicks += 1
            st.session_state.phase = "next"
            st.rerun()

    with col2:
        if st.button("Skip ⏭️"):
            if st.session_state.stimulus == st.session_state.target:
                st.session_state.misses += 1
            st.session_state.phase = "next"
            st.rerun()

# ---------------- NEXT TRIAL ----------------
elif st.session_state.phase == "next":
    st.session_state.trial += 1
    if st.session_state.trial > TOTAL_TRIALS:
        st.session_state.phase = "result"
    else:
        st.session_state.target = random.choice(STIMULI)
        st.session_state.phase = "target"
    st.rerun()

# ---------------- RESULT ----------------
elif st.session_state.phase == "result":
    avg_rt = (
        sum(st.session_state.reaction_times) / len(st.session_state.reaction_times)
        if st.session_state.reaction_times else 0
    )

    accuracy = round((st.session_state.hits / TOTAL_TRIALS) * 100, 1)

    if accuracy >= 80 and st.session_state.false_clicks <= 2:
        focus_level = "High"
        remark = "Excellent focus and strong self-regulation skills."
    elif accuracy >= 60:
        focus_level = "Moderate"
        remark = "Good focus. Can further improve sustained attention."
    else:
        focus_level = "Developing"
        remark = "Needs support in maintaining focus and impulse control."

    st.session_state.class_results.append({
        "Name": st.session_state.student_name,
        "Class": st.session_state.student_class,
        "Accuracy (%)": accuracy,
        "Reaction Time (sec)": round(avg_rt, 2),
        "Focus Level": focus_level
    })

    st.success("Assessment Completed")

    st.markdown("## 📄 Focus Assessment Report")
    st.write(f"**Student Name:** {st.session_state.student_name}")
    st.write(f"**Class:** {st.session_state.student_class}")
    st.write(f"**Focus Accuracy:** {accuracy}%")
    st.write(f"**Average Reaction Time:** {avg_rt:.2f} sec")
    st.write(f"**Focus Level:** {focus_level}")
    st.info(f"🧠 SEL Remark: {remark}")

    pdf_data = {
        "Student Name": st.session_state.student_name,
        "Class": st.session_state.student_class,
        "Focus Accuracy (%)": accuracy,
        "Average Reaction Time (sec)": round(avg_rt, 2),
        "Focus Level": focus_level,
        "SEL Remark": remark
    }

    pdf = generate_pdf(pdf_data)

    st.download_button(
        "📥 Download PDF Report",
        pdf,
        file_name=f"{st.session_state.student_name}_Focus_Report.pdf",
        mime="application/pdf"
    )

    if st.button("🔄 New Student"):
        st.session_state.clear()
        st.rerun()

# ---------------- CLASS DASHBOARD ----------------
st.divider()
st.header("📊 Class-wise Focus Dashboard")

if st.session_state.class_results:
    st.dataframe(st.session_state.class_results, use_container_width=True)

    avg_focus = sum(d["Accuracy (%)"] for d in st.session_state.class_results) / len(st.session_state.class_results)
    avg_rt_class = sum(d["Reaction Time (sec)"] for d in st.session_state.class_results) / len(st.session_state.class_results)

    st.metric("📈 Average Class Focus (%)", round(avg_focus, 1))
    st.metric("⏱ Average Reaction Time (sec)", round(avg_rt_class, 2))
else:
    st.info("No class data recorded yet.")
