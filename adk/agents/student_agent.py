from google.generativeai import GenerativeModel
from adk.skills.student_skill import get_student_profile

class StudentAgent:

    def __init__(self):
        self.model = GenerativeModel("gemini-1.5-flash")

    def run(self, user_id: str):
        """Runs the skill to fetch student data."""
        return get_student_profile(user_id)
