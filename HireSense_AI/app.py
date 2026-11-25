import streamlit as st
from utils import extract_resume_text, analyze_match, generate_advice

st.set_page_config(page_title="HireSense AI", page_icon="🎯", layout="wide")
st.title("🎯 HireSense AI")
st.caption("AI Resume & Job Matching Agent — understand your fit, find skill gaps, improve your resume.")

with st.sidebar:
    st.header("About")
    st.write("Upload a resume and paste a job description to get a match score, matched skills, missing skills, and actionable recommendations.")
    st.info("For best results, use a text-based PDF or DOCX resume.")

resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
job_description = st.text_area("Paste the job description", height=260, placeholder="Paste responsibilities, requirements, and qualifications here...")
analyze = st.button("Analyze Match", type="primary", use_container_width=True)

if analyze:
    if not resume_file or not job_description.strip():
        st.error("Please upload a resume and paste a job description.")
        st.stop()
    try:
        resume_text = extract_resume_text(resume_file)
        if not resume_text.strip():
            st.error("Could not extract text. Try a text-based PDF or DOCX.")
            st.stop()
        result = analyze_match(resume_text, job_description)
        st.subheader("Match report")
        c1, c2, c3 = st.columns(3)
        c1.metric("Overall match", f"{result['score']}%")
        c2.metric("Matched skills", len(result["matched"]))
        c3.metric("Missing skills", len(result["missing"]))
        st.progress(result["score"] / 100)
        left, right = st.columns(2)
        with left:
            st.markdown("#### ✅ Matched skills")
            st.write(", ".join(result["matched"]) if result["matched"] else "No known skills matched.")
        with right:
            st.markdown("#### 📌 Skills to develop")
            st.write(", ".join(result["missing"]) if result["missing"] else "No missing skills from the detected list.")
        st.markdown("#### 🧠 AI career advice")
        st.write(generate_advice(resume_text, job_description, result))
        st.markdown("#### 🔎 Keyword overlap")
        st.write(f"Text similarity: **{result['similarity']}%**")
        st.caption("This score is an estimate, not a guaranteed ATS score or hiring decision.")
    except Exception as e:
        st.error(f"Analysis failed: {e}")
