from google.generativeai import configure, GenerativeModel
import json
from adk.tools.db_tool import get_student_data

# (No LLM needed for this skill — we just prepare the student profile response)

def get_student_profile(user_id: str) -> dict:
    """Skill: returns student information fetched from DB."""
    student = get_student_data(user_id)

    if "error" in student:
        return {"error": "Student not found"}

    # The skill returns clean structured JSON
    return {
        "student_profile": {
            "name": student.get("name"),
            "email": student.get("email"),
            "education": student.get("education"),
            "projects": student.get("projects"),
            "skills": student.get("skills"),
            "experience": student.get("experience")
        }
    }
