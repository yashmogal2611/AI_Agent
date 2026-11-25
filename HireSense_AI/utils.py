import io
import re
from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS = [
    "python", "java", "c++", "sql", "javascript", "typescript", "pandas", "numpy",
    "scikit-learn", "machine learning", "deep learning", "natural language processing",
    "nlp", "computer vision", "generative ai", "llm", "langchain", "pytorch",
    "tensorflow", "power bi", "tableau", "excel", "data visualization", "statistics",
    "data analysis", "data science", "rest api", "flask", "fastapi", "streamlit",
    "git", "docker", "aws", "azure", "communication", "problem solving",
    "data structures", "algorithms", "html", "css", "mongodb", "mysql", "postgresql"
]

def extract_resume_text(uploaded_file):
    name = uploaded_file.name.lower()
    raw = uploaded_file.getvalue()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Unsupported file type")

def detect_skills(text):
    normalized = text.lower()
    found = []
    for skill in SKILLS:
        # Match whole phrases while allowing punctuation around the skill.
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.append(skill)
    return sorted(set(found))

def analyze_match(resume_text, job_description):
    resume_skills = set(detect_skills(resume_text))
    job_skills = set(detect_skills(job_description))
    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)
    skill_score = (len(matched) / len(job_skills) * 100) if job_skills else 0

    try:
        matrix = TfidfVectorizer(stop_words="english").fit_transform([resume_text, job_description])
        similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100
    except ValueError:
        similarity = 0

    # Skill coverage has greater weight than general text similarity.
    overall = (0.75 * skill_score) + (0.25 * similarity)
    return {
        "score": round(overall),
        "matched": matched,
        "missing": missing,
        "similarity": round(similarity)
    }

def generate_advice(resume_text, job_description, result):
    if result["missing"]:
        missing = ", ".join(result["missing"][:8])
        return (
            f"Prioritize these job-description skills that were not detected in your resume: {missing}. "
            "If you genuinely have these skills, add them in the relevant skills or project sections and "
            "demonstrate them with specific examples. Otherwise, learn them through a small project. "
            "Tailor your project bullets to show measurable outcomes and the tools used."
        )
    return (
        "Your resume contains the detected skills from this job description. "
        "Strengthen your application by aligning project descriptions with the role, adding measurable "
        "results, and making your experience easy to scan. Review the job requirements manually too."
    )
