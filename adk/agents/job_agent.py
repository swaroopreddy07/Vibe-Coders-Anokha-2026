from adk.skills.extract_job_skill import extract_job_requirements

class JobAgent:

    def run(self, url: str):
        """Runs the job extraction skill."""
        return extract_job_requirements(url)
