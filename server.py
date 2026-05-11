import os
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from main import app as langgraph_app
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
server = FastAPI(title="AI Grading System API")

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL").strip()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Student(Base):
    __tablename__ = "students"
    student_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True)

load_dotenv()


class GradingRequest(BaseModel):
    file_id: str
    file_content: str
    rubric_content: str
    student_name: Optional[str] = "Student"
    student_email: str


def run_grading_process(data: GradingRequest):
    db = SessionLocal()
    try:
        initial_state = {
            "file_id": data.file_id,
            "file_content": data.file_content,
            "file_name": data.student_name,
            "rubric_content": data.rubric_content,
            "student_name": "Extracting student name...", 
            "teacher_approved": False,
        }
        config = {"configurable": {"thread_id": data.file_id}}
        final_state = langgraph_app.invoke(initial_state, config)
        
        extracted_name = final_state.get("student_name", data.student_name)

        student = db.query(Student).filter(Student.email == data.student_email).first()
        if not student:
            student = Student(full_name=extracted_name, email=data.student_email)
            db.add(student)
            db.commit()
            db.refresh(student)
        
        current_student_id = student.student_id

        payload = {
            "student_id": current_student_id,
            "file_id": data.file_id,
            "file_name": data.student_name, 
            "student_name": extracted_name,
            "essay_content": data.file_content,
            "ai_score": final_state.get("total_score"),
            "ai_feedback": final_state.get("email_draft"),
            "status": "pending_review",
        }

        n8n_save_db_url = 'http://n8n:5678/webhook/save-to-db'
        requests.post(n8n_save_db_url, json=payload)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

@server.post("/start-grading")
async def start_grading(request: GradingRequest):
    run_grading_process(request) 
    return {"status": "done"}

@server.get("/submissions")
async def get_submissions():
    db = SessionLocal()
    try:
        query = text("""
            SELECT s.*, st.full_name as student_real_name, st.email 
            FROM submissions s
            JOIN students st ON s.student_id = st.student_id
            ORDER BY s.created_at DESC
        """)
        
        results = db.execute(query).mappings().all()
        return list(results)
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return []
    finally:
        db.close()

class ApproveRequest(BaseModel):
    final_email_content: str

@server.post("/approve/{student_id}")
async def approve_submission(student_id: int, data: ApproveRequest, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        stmt = text("""
            UPDATE submissions 
            SET status = 'approved', ai_feedback = :final_content 
            WHERE student_id = :id
        """)
        db.execute(stmt, {"final_content": data.final_email_content, "id": student_id})
        db.commit()

        query = text("""
            SELECT s.*, st.email, st.full_name
            FROM submissions s
            JOIN students st ON s.student_id = st.student_id
            WHERE s.student_id = :id
        """)
        row = db.execute(query, {"id": student_id}).mappings().first()
        
        if row:
            payload = {key: (val.isoformat() if hasattr(val, 'isoformat') else val) for key, val in row.items()}
            n8n_email_url = "http://AI_automation_v2:5678/webhook/send-email"
            background_tasks.add_task(requests.post, n8n_email_url, json=payload)
            
            return {"status": "success", "message": "Email sent with your manual edits!"}
            
    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 500
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server, host="0.0.0.0", port=8000)