# AI-Powered IELTS Grading System (LangGraph)
> An intelligent system that automates the IELTS essay grading process and pedagogical feedback generation using AI Agents and human-in-the-loop workflows.
> Watch demo [_here_](https://langgraph-nu.vercel.app/).
![Banking Bot Demo](./img/LangGraph_Demo.gif)
## Table of Contents
* [General Information](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Frontend Overview](#frontend-overview)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Contact](#contact)

## General Information
- This project solves the problem of heavy manual workloads for IELTS instructors by using AI Agents to grade essays based on official rubrics and generate professional feedback.

- The purpose is to demonstrate a Multi-Agent system capable of extracting student information, performing deep academic analysis, and drafting administrative documents.

- It provides a seamless bridge between autonomous AI grading and human oversight, ensuring every piece of feedback is reviewed before being sent to students.

## Technologies Used
- **Backend**: Python 3.10+, FastAPI, LangGraph, LangChain, CrewAI, Llama 3.3 (Groq).
- **Frontend**: React.js, CSS, Axios.
- **Database**: PostgreSQL (with pgvector support).
- **Infrastructure**: Docker, Docker Compose.
- **Automation**: n8n (Webhook,GoogleDrive & Email integration).
  
## Features
- **Multi-Agent Orchestration**: Utilizes CrewAI agents for specialized grading tasks.
  - **Data Extraction Specialist**: Extracts the student's name from both the file content and the filename.

  - **Academic Grader**: Evaluates and scores the essay based on the four official IELTS criteria: Task Response (TR), Coherence and Cohesion (CC), Lexical Resource (LR), and Grammatical Range and Accuracy (GRA).

  - **Pedagogical Feedback Writer**: Acts as an IELTS expert with 15 years of experience to draft high-quality, constructive feedback.

  - **Email Specialist**: Converts the feedback into a professional HTML format for email delivery.

State Management with LangGraph: LangGraph is utilized to manage the GradingState, ensuring a seamless and reliable transition between the grading (analysis) and writing (composition) phases of the workflow.

- **Deep Academic Analysis**: Evaluates essays across four criteria (TR, CC, LR, GRA) with specific error listing and band score calculation.

- **Human-in-the-loop**: Features a "Review & Edit" modal where teachers can manually modify AI-generated email drafts before final approval.

- **End-to-End Automation**: Integrates with Google Drive for submission ingestion and automated email services for feedback delivery.

## Frontend Overview
The system features a React-based management interface designed for academic administrators:

### 1. Submission Dashboard
- **Purpose**: Provides a centralized view of all student submissions, their AI scores, and current processing status.
- **Main Tasks**: Monitor incoming essays, view submission dates, and track which items are pending review.

### 2. Admin Dashboard
- **Purpose**: Acts as the "Human-in-the-loop" editor.
- **Main Tasks**: Teachers can view the original PDF essay, edit the AI-generated HTML feedback, and click Approve to trigger the final email delivery.

## Setup
### Backend
1. Navigate to the root folder.
2. Install dependencies: `pip install -r requirements.txt`.
3. Change the name of `.env_sample` file to `.env`, and use your own Groq API: `GROQ_API_KEY=your_groq_api_key`.
4. Run: `python server.py`

### Frontend
1. Navigate to the `/frontend` folder.
2. Install dependencies: `npm install`
3. Run: `npm start`

### Local Setup
1. Clone the repository: git clone <repo-url>
2. Create a .env file in the root: GROQ_API_KEY=your_key_here and DATABASE_URL=your_postgres_url.
3. Start the entire stack using Docker: `docker-compose up --build`

## Usage
- **Student**: Uploads an essay to a watched Google Drive folder.

- **AI Workflow**: n8n triggers the FastAPI backend -> LangGraph coordinates CrewAI agents to grade and draft feedback -> Results are saved to DB.

- **Teacher**: Logs into Dashboard -> Reviews AI score -> Edits email draft -> Clicks Approve.

- **Automation**: n8n receives the approval and sends the final edited email to the student.
  
## Project Status
Project is: **Complete** - Fully functional with LangGraph state management, CrewAI coordination, and a React human-in-the-loop dashboard.

## Room for Improvement
- Add a "Re-grade" feature to allow AI to re-evaluate based on specific teacher instructions.

- Support for more file formats (DOCX, Images with OCR).

- Real-time notifications for teachers when a new submission is graded by AI.

## Contact
Created by [@thanhcongluong](https://github.com/ThanhCongLuong) - feel free to contact me!
