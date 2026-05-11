import os
from langgraph.graph import StateGraph, END
from state.workflow_state import GradingState
from agents.grading_crews import run_grading_crew, run_communication_crew
from dotenv import load_dotenv
import re
load_dotenv()

def call_grading_dept(state: GradingState):
    result = run_grading_crew(state['file_content'], state['rubric_content'], state['file_name'])
    try:
        student_info = result.tasks_output[0].pydantic
        clean_name = student_info.clean_name if student_info else "Student"
    except:
        clean_name = "Student"

    ai_output = str(result.raw)
    score_match = re.search(r"FINAL_SCORE:\s*(\d+\.?\d*)", ai_output)
    if score_match:
        final_score = float(score_match.group(1))
    else:
        all_numbers = re.findall(r"(\d+\.?\d*)", ai_output)
        final_score = float(all_numbers[-1]) if all_numbers else 0.0
    
    
    return {
        "student_name": clean_name,
        "total_score": final_score, 
    }

def call_writing_dept(state: GradingState):
    result = run_communication_crew(
        total_score=state['total_score'], 
        student_name=state['student_name'],
        file_content=state['file_content'],
        grading_details=state.get('teacher_comments', 'No comments yet')
    )
    return {"email_draft": str(result)}

workflow = StateGraph(GradingState)
workflow.add_node("grading", call_grading_dept)
workflow.add_node("writing", call_writing_dept)

workflow.set_entry_point("grading")
workflow.add_edge("grading", "writing")
workflow.add_edge("writing", END)

def decide_next(state: GradingState):
    return "approved" if state.get("teacher_approved", False) else "rejected"

app = workflow.compile()
