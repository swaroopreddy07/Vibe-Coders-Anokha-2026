# main.py
from adk.agents.job_agent import JobAgent
from adk.agents.student_agent import StudentAgent

job_agent = JobAgent()
student_agent = StudentAgent()

# Put any real job URL here that you want to test.
# Try a site that usually allows scraping (RemoteOK, WeWorkRemotely, company pages)
job_url = "https://www.linkedin.com/jobs/view/4058486764/"  # change if needed

print("JOB AGENT TEST:")
job_result = job_agent.run(job_url)
if job_result.get("error"):
    print("Job extraction failed:", job_result.get("detail"))
else:
    print("Source:", job_result.get("source"))
    print("Snippet (first 400 chars):\n", job_result.get("snippet")[:400])
    print("\nResponsibilities:", job_result.get("responsibilities"))
    print("Qualifications:", job_result.get("qualifications"))
    print("Skills:", job_result.get("skills"))

print("\nSTUDENT AGENT TEST:")
student = student_agent.run("sanjana01")
print(student)
