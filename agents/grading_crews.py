from crewai import Agent, Task, Crew
from pydantic import BaseModel
from langchain_groq import ChatGroq
import os
class StudentInfo(BaseModel):
    clean_name: str
    
groq_api_key = os.getenv("GROQ_API_KEY")
MY_LLM = ChatGroq(model='groq/llama-3.3-70b-versatile', temperature=0,api_key=groq_api_key)

data_extractor_agent = Agent(
    role='Data Extraction Specialist',
    goal="Extract the student's name. Prioritize extracting student name from the file name (but remove the .pdf extension and any extra characters)",
    backstory='Data extraction specialist.',
    llm=MY_LLM,
    verbose=True
)

academic_grader_agent = Agent(
    role='Academic Grader',
    goal='Grade the assignments accurately.',
    backstory='Professional instructors.',
    llm=MY_LLM,
    verbose=True
)

feedback_writer_agent = Agent(
    role='Pedagogical Feedback Writer',
    goal='Write pedagogical feedback',
    backstory='You are an IELTS examiner with 15 years of experience. You are known for providing highly critical yet accurate feedback on Lexical Resource and Grammatical Range for candidates. You always point out specific errors and provide improvement strategies to enhance band scores.',
    llm=MY_LLM,
    verbose=True
)

email_composer_agent = Agent(
    role='Email Specialist',
    goal='Compose the resulting email',
    backstory='Specializes in drafting administrative documents.',
    verbose=True,
    llm=MY_LLM,
    allow_delegation=False
)


def run_grading_crew(file_content, rubric_content, file_name): 
    ex_task = Task(
        description=f"Based on the content: {file_content} and file name: {file_name}, find the student's name.", 
        agent=data_extractor_agent, 
        output_pydantic=StudentInfo,
        expected_output="The student's proper name, with suffixes such as .pdf, _Resume, or parentheses removed."
    )
    
    gr_task = Task(
        description=(
            f"Grade this essay: {file_content} using this Rubric: {rubric_content}\n"
            "MANDATORY WORKFLOW:\n"
            "1. List all specific grammar and vocabulary errors.\n"
            "2. Evaluate each criterion (TR, CC, LR, GRA) with evidence from the text.\n"
            "3. Calculate the average score.\n"
            "4. Cross-check with the Rubric to finalize the band score."
        ), 
    agent=academic_grader_agent,
    expected_output="The table should include a breakdown of errors, detailed scores for the four criteria, and the final score (from 4.0 to 9.0). Finally, record the score using the following format: FINAL_SCORE: [number]"
)
    
    crew = Crew(
        agents=[data_extractor_agent, academic_grader_agent], 
        tasks=[ex_task, gr_task]
    )
    return crew.kickoff()

def run_communication_crew(total_score, student_name, file_content, grading_details):
    fb_task = Task(
    description=(
        f"Write a concise IELTS feedback for {student_name}'s essay.\n"
        f"OFFICIAL RESULTS: Total Score is {total_score}. Detailed breakdown: {grading_details}\n"
        "Requirements:\n"
        "- Use Bullet Points for each Bold criteria with Bold Detailed Scores: {grading_details}.\n"
        "- Ensure the breakdown matches the Total Score provided.\n"
        "- Max 2 sentences per criterion.\n"
        "- Call Student by name or use 'you'. use 'I' to refer to the examiner.\n"
        "- Add 'Ben Luong' as a signature after best regards"
    ),
    agent=feedback_writer_agent, 
    expected_output="A concise review using Bullet Points matching the official score."
    )

    em_task = Task(
    description=(
        f"Draft an HTML email for {student_name}.\n"
        "Instructions: Wrap the feedback provided by the Pedagogical Feedback Writer into a professional HTML structure.\n"
        f"MANDATORY: Use the Total Score {total_score} and the specific breakdown provided in the previous step.\n"
        "Structure: Greeting with Bold name -> Bold Total Score -> Bold Detailed Scores -> Concise Feedback -> Closing.\n"
        "Constraints: Use only HTML tags (<p>, <ul>, <li>, <b>). No Markdown (**)."
    ), 
    agent=email_composer_agent, 
    expected_output="The final HTML email code."
    )
    crew = Crew(agents=[feedback_writer_agent, email_composer_agent], tasks=[fb_task, em_task])
    result =  crew.kickoff()
    return result.raw