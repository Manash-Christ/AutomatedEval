import streamlit as st
from utils.database import SessionLocal, ReportDetails, StudentDetails
from utils.ocr import split_into_list

def view_student_scores():
    st.header("Your Scores and Reports")
    db = SessionLocal()
    reports = db.query(ReportDetails).filter(ReportDetails.student_id == st.session_state['profile'].student_id).all()
    if reports:
        for report in reports:
            st.subheader(f"Course ID: {report.course_id}")
            if report.score == 0:
                st.info("Evaluation Pending")
            else:
                st.markdown(f"**Score:** {report.score}")
                with st.expander("View Report"):
                    st.write(report.report)
    else:
        st.info("No reports available.")
    db.close()

def view_all_scores():
    st.header("All Students' Scores and Reports")
    db = SessionLocal()
    reports = db.query(ReportDetails).all()
    if reports:
        for report in reports:
            student = db.query(StudentDetails).filter(StudentDetails.student_id == report.student_id).first()
            st.subheader(f"{student.first_name} {student.last_name} - {student.register_number}")
            st.markdown(f"**Course ID:** {report.course_id}")
            if report.score == 0:
                st.info("Evaluation Pending")
            else:
                st.markdown(f"**Score:** {report.score}")
                with st.expander("View Report"):
                    st.write(report.report)
    else:
        st.info("No reports available.")
    db.close()

import streamlit as st
from utils.database import SessionLocal, ReportDetails, StudentDetails, EvaluatorDetails
import pandas as pd

def get_student_reports(student_id):
    db = SessionLocal()
    reports = db.query(ReportDetails).filter(ReportDetails.student_id == student_id).all()
    db.close()
    return reports

def get_all_student_reports():
    db = SessionLocal()
    reports = db.query(ReportDetails).all()
    db.close()
    return reports

def display_score_report(report):
    st.markdown(f"### **Course ID: {report.course_id}**")
    st.markdown(f"#### **Evaluator ID: {report.evaluator_id}**")
    st.markdown(f"**Final Score:** `{report.score}`")
    st.markdown("### **Detailed Evaluation**")
    ques = report.questions.split(",")
    ans = split_into_list(report.transcript)
    for i,j in zip(ques,ans):
        st.markdown(f"""
                    -**Ques:** {i}
                    -**Ans:** {j}
""")
    st.info("Provide additional feedback or suggestions here if needed.")

def student_scores_tab():
    st.header("Your Scores and Evaluation Reports")
    student_id = st.session_state['profile'].student_id
    reports = get_student_reports(student_id)
    
    if reports:
        for report in reports:
            with st.expander(f"Course: {report.course_id} - Score: {report.score}"):
                display_score_report(report)
    else:
        st.info("No evaluation reports available yet.")

def evaluator_scores_tab():
    st.header("All Students' Scores and Evaluation Reports")
    reports = get_all_student_reports()
    
    if reports:
        # Group reports by course and student
        grouped_reports = {}
        for report in reports:
            student = f"Student ID: {report.student_id}"
            course = report.course_id
            if course not in grouped_reports:
                grouped_reports[course] = {}
            if student not in grouped_reports[course]:
                grouped_reports[course][student] = []
            grouped_reports[course][student].append(report)
        
        for course, students in grouped_reports.items():
            st.subheader(f"Course ID: {course}")
            for student, reports in students.items():
                with st.expander(student):
                    for report in reports:
                        display_score_report(report)
    else:
        st.info("No evaluation reports available yet.")

def scores_tab():
    role = st.session_state['user'].role
    if role == "Student":
        student_scores_tab()
    elif role == "Evaluator":
        evaluator_scores_tab()

# Call this function in the main app when the Scores tab is selected

