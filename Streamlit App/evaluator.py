import streamlit as st

def evaluator_page():
    st.title("Evaluator Page")

    st.write("View the list of uploaded answer sheets below:")

    # Mocking a list of uploaded files for demonstration
    uploaded_files = ["student1.pdf", "student2.png"]
    st.write(uploaded_files)

    selected_file = st.selectbox("Select a file to view", uploaded_files)

    if st.button("Evaluate"):
        # Mock evaluation process
        st.success(f"Evaluation of {selected_file} completed successfully")

# Score page (visible to both students and evaluators)
def score_page():
    st.title("Score Page")

    if st.session_state["user"]["role"] == "Student":
        st.write(f"Score and report for {st.session_state['user']['username']}")

        # Mocking a report and score
        st.write("Score: 85/100")
        st.write("Mistakes and suggestions:")
        st.write("- Mistake 1: Incorrect answer to Q2")
        st.write("- Suggestion: Review the topic on sensors")

    elif st.session_state["user"]["role"] == "Evaluator":
        st.write("View scores and reports for all students")

        # Mocking a list of students and their scores
        student_scores = {"student1": 85, "student2": 90}
        for student, score in student_scores.items():
            st.write(f"{student}: {score}/100")