import streamlit as st
from utils.database import SessionLocal, ReportDetails, StudentDetails

from utils.ocr import textExtraction, split_into_list
from pdf2image import convert_from_bytes
from PIL import Image

COURSE = {
    'MAI471':"Large Language Models",
    'MAI431':"Internet of Things",
    'MAI432':"Multi Agent Systems"
}
session = SessionLocal()



def check_existing_upload(student_id, course_id):
    # Check if the student has already uploaded an answer script for this course
    return session.query(ReportDetails).filter_by(student_id=student_id, course_id=course_id).first()

def delete_existing_upload(report):
    # Delete the existing record
    session.delete(report)
    session.commit()

def student_dashboard():
    st.header("Upload Answer Sheet")

    course_ids = st.session_state['profile'].course_ids
    #st.write(course_ids[0])
    if not course_ids:
        st.error("No courses available. Please contact the administrator.")
        return
    student_id = st.session_state['profile'].student_id 


    course_list = course_ids.split(",") 
    
    course_name = [COURSE[k] for k in course_list]
    selected_course = st.selectbox("Select a Course", course_name)
    kn = {v:k for k,v in COURSE.items()}
    # st.write(student_id);st.write(kn[selected_course])
    # st.write(session.query(ReportDetails).filter_by(student_id=student_id, course_id=kn[selected_course]).first())

    existing_report = check_existing_upload(student_id, kn[selected_course])
    if existing_report:
        st.warning("You have already uploaded an answer script for this course.")
        with st.expander("View your uploaded transcript"):
            st.text(existing_report.transcript)
        if st.button("Delete Previous Upload"):
            delete_existing_upload(existing_report)
            st.success("Previous upload deleted. You can now upload a new answer script.")
            st.rerun()
        else:
            st.info("Please delete your previous upload to upload a new answer script.")

    else:

        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg"])

    # if uploaded_file:
    #     st.subheader("Uploaded image")
    #     if uploaded_file.type == 'application/pdf':
    #         with st.expander("Your uploaded image"):
    #             st.write("this is pdf")
    #             st.image(convert_from_bytes(uploaded_file.read()))
    #     else:
    #         st.write("this is image")
    #         st.image(uploaded_file)
        

        if 'transcript' not in st.session_state:
            st.session_state['transcript'] = None

        if uploaded_file is not None and selected_course:
            if st.session_state['transcript'] is None:
                with st.spinner("Processing..."):
                    transcript = textExtraction(uploaded_file)
                    answers = split_into_list(transcript)
                    st.success("File uploaded and processed successfully!")
                    st.session_state['transcript'] = transcript
                    st.session_state['answers'] = answers

            # Display the transcript if it has been processed
            if st.session_state['transcript'] is not None:
                with st.expander("View Transcript"):
                    for i, j in enumerate(st.session_state['answers']):
                        st.text(f"**ANS {i+1}** --> {j}")

                if st.button("Send for evaluation", use_container_width=True):
                    with st.spinner("Sending report..."):
                        db = SessionLocal()
                        new_report = ReportDetails(
                            student_id=st.session_state['profile'].student_id,
                            course_id=kn[selected_course],
                            transcript=st.session_state['transcript'],  
                            score=0, 
                            report="Evaluation Pending"
                        )
                        db.add(new_report)
                        db.commit()
                        db.close()
                        st.info("Your answer sheet has been submitted for evaluation. Check back later for results.")
        else:
            st.info("Please upload your answer sheet in PDF or Image format.")

    st.caption("*ADD TEXT ABOUT SOMETHING*")
