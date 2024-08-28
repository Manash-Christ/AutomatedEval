import streamlit as st
from utils.database import SessionLocal, ReportDetails, StudentDetails, EvaluatorDetails
from utils.ocr import *

COURSE = {
    'MAI471': "Large Language Models",
    'MAI431': "Internet of Things",
    'MAI432': "Multi Agent Systems"
}

def fetch_course_data(course_id):
    db = SessionLocal()
    
    # Total submissions for the course
    total_submissions = db.query(ReportDetails).filter_by(course_id=course_id.strip()).count()
    
    # Total evaluated submissions for the course (assuming score 0 means not evaluated)
    total_evaluated = db.query(ReportDetails).filter(ReportDetails.course_id == course_id.strip(), ReportDetails.score > 0).count()
    
    # Calculate new submissions
    new_submissions = total_submissions - total_evaluated
    
    db.close()
    return total_submissions, total_evaluated, new_submissions

def evaluator_dashboard():
    st.header("Evaluate Answer Sheets")

    db = SessionLocal()

    course_ids = st.session_state['profile'].course_ids
    if not course_ids:
        st.error("No courses assigned. Please contact the administrator.")
        return

    course_list = course_ids.split(",")  
    for course_id in course_list:
        st.subheader(f"{course_id.strip()}: {COURSE[course_id.strip()]}")

        # Fetch course data
        total_submissions, total_evaluated, new_submissions = fetch_course_data(course_id)
        
        # Display course summary
        if total_submissions == 0:
            st.info("No submissions for this course.")
        else:
            st.write(f"Total Submissions: {total_submissions}")
            st.write(f"Total Evaluated: {total_evaluated}")
            
            if new_submissions > 0:
                st.warning(f"New answer script(s) arrived: {new_submissions}")

        st.write("Upload the Answer Key for this course:")
        answer_key_file = st.file_uploader(f"Upload Answer Key for {course_id.strip()}", type=["pdf", "txt"], key=f"{course_id.strip()}_key")
        
        if answer_key_file:
            qa = extract_text_from_pdf(answer_key_file)
            st.success("Answer key processed successfully.")
        else:
            st.warning("Please upload an answer key to continue.")
            continue

        reports = db.query(ReportDetails).filter(
            ReportDetails.course_id == course_id.strip(),
            ReportDetails.score == 0  # Only show reports that haven't been evaluated yet
        ).all()

        if reports:
            for report in reports:
                # Fetch the student details
                student = db.query(StudentDetails).filter(StudentDetails.student_id == report.student_id).first()

                with st.expander(f"Student: {student.first_name} {student.last_name} (Register Number: {student.register_number})"):
                    st.write("**Transcript:**")
                    student_answers = split_into_list(report.transcript)
                    st.write(student_answers)
                    st.write(qa)
                    for k,j in zip(qa.keys(), student_answers):
                        with st.container():
                            st.markdown(f"""
**Question:**  
{k}

**Student Answer:**  
{j}

""")

                cor_id = report.course_id
                subject = COURSE[cor_id]
                ques = list(qa.keys())
                key = list(qa.values())
                ans = student_answers
                
                if st.button("Evaluate", key=f"{report.report_id}_evaluate", use_container_width=True):
                    with st.spinner(f"Evaluating {student.first_name}'s answers..."):
                        ext_scores, ext_suggestions = Evalkey(ques, key, ans)
                        int_scores, int_suggestions = Evalref(ques, ans, subject)
                        exS = sum([int(i) for i in ext_scores.values()])
                        inS = sum([int(i) for i in int_scores.values()])
                        st.success("Evaluation completed successfully.")

                        # Store the evaluation results in session state
                        st.session_state[f"{report.report_id}_ext_scores"] = ext_scores
                        st.session_state[f"{report.report_id}_int_scores"] = int_scores
                        st.session_state[f"{report.report_id}_exS"] = exS
                        st.session_state[f"{report.report_id}_inS"] = inS
                        st.session_state[f"{report.report_id}_ext_report"] = ""
                        st.session_state[f"{report.report_id}_int_report"] = ""

                        for i, (q, scr, sug) in enumerate(zip(list(ext_scores.keys()), list(ext_scores.values()), list(ext_suggestions.values()))):
                            pip = f"Q{i+1}: **Question:** {q}\n\n**Score:** {scr}\n\n**Suggestion:** {sug}"
                            st.session_state[f"{report.report_id}_ext_report"] += "\n" + pip + "\n"

                        for i, (q, scr, sug) in enumerate(zip(list(int_scores.keys()), list(int_scores.values()), list(int_suggestions.values()))):
                            pop = f"Q{i+1}: **Question:** {q}\n\n**Score:** {scr}\n\n**Suggestion:** {sug}"
                            st.session_state[f"{report.report_id}_int_report"] += "\n" + pop + "\n"

                # Check if evaluation has been completed and display results
                if f"{report.report_id}_ext_scores" in st.session_state:

                    # Display evaluations side-by-side
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**External Knowledge Evaluation:**")
                        st.write(st.session_state[f"{report.report_id}_ext_report"])

                    with col2:
                        st.write("**Internal Answer Key Evaluation:**")
                        st.write(st.session_state[f"{report.report_id}_int_report"])

                    # Display the total scores and average
                    exS = st.session_state[f"{report.report_id}_exS"]
                    inS = st.session_state[f"{report.report_id}_inS"]

                    st.markdown(f"""
                        **External total score:** {exS}  
                        **Internal total score:** {inS}  
                        **Average:** {(exS + inS) / 2}
                    """)

                    # Slider to weigh both scores
                    weight_ext = st.slider("Weight for External Knowledge Evaluation", 0, 100, 50, key=f"{report.report_id}_ext_weight")
                    weight_int = 100 - float(weight_ext)

                    # Dynamically calculate and display the final score based on slider value
                    final_score = (exS * weight_ext + inS * weight_int) / 100
                    st.write(f"**Weighted Score:** {final_score:.2f}")

                    # Button to save the final score
                    if st.button("Save Score", key=f"{report.report_id}_save_score"):
                        evaluator_id = st.session_state['profile'].evaluator_id
                        report.score = final_score
                        report.evaluator_id = evaluator_id
                        report.questions = ",".join(ques)
                        report.report = f"**FINAL REPORT**\n\n**INTERNAL REPORT**\n{st.session_state[f'{report.report_id}_int_report']}\n\n**EXTERNAL REPORT**\n{st.session_state[f'{report.report_id}_ext_report']}\n\nWeightage = {weight_ext}\nFinal Score: {final_score:.2f}"
                        db.commit()
                        st.success("Score saved successfully.")
        else:
            st.write("No pending answer sheets for this course.")
    
    db.close()

