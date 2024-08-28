import streamlit as st
import os
from PIL import Image
import PyPDF2
#from pdf2image import convert_from_path
from chains import *

from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table, select, Boolean
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String, unique=True, nullable=False),
    Column('password', String, nullable=False),
    Column('role', String, nullable=False)  
)

metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def register_user(username, password, role):
    existing_user = session.execute(select(users_table).where(users_table.c.username == username)).fetchone()
    if existing_user:
        st.warning("Username already exists")
    else:
        session.execute(users_table.insert().values(username=username, password=password, role=role))
        session.commit()
        st.success(f"Successfully registered as a {role}")

def authenticate_user(username, password, role):
    user = session.execute(select(users_table).where(users_table.c.username == username).where(users_table.c.password == password).where(users_table.c.role == role)).fetchone()
    return user is not None

# Function to handle login and registration
def login_page():
    st.caption("**Be** *the* 8055")
    action = st.radio("Action", ["Login", "Register"])
    st.markdown(
    """
    <div style="background-color: blue; color: white; padding: 20px;">
      This is a container styled using HTML.
    </div>
    """,unsafe_allow_html=True
)
    cot = st.container()
    with cot:
        
        st.title("Welcome")
        st.write("Please login with the designated credentials for your role")

        role = st.selectbox("Select your role", ["Student", "Evaluator"])
        

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):
            if action == "Register":
                register_user(username, password, role)
            else:
                if authenticate_user(username, password, role):
                    st.session_state["user"] = {"role": role, "username": username}
                    st.success("Login successful")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
    cot.markdown("""
    <div style="background-color: red; border: 1px solid black; padding: 10px;">
      This is a container with custom styles defined using Markdown.
    </div>
                 """, unsafe_allow_html=True)
# Sidebar navigation
def sidebar():
    st.sidebar.title("Navigation")
    if "user" not in st.session_state:
        st.sidebar.write("Please log in to continue")
        return
    role = st.session_state["user"]["role"]
    st.sidebar.write(f"Logged in as: {role}")

    if role == "Student":
        page = st.sidebar.radio("Go to", ["About", "Student", "Score", "Future Scope", "Logout"])
    elif role == "Evaluator":
        page = st.sidebar.radio("Go to", ["About", "Evaluator", "Score", "Future Scope", "Logout"])
    else:
        page = st.sidebar.radio("Go to", ["About", "Future Scope", "Logout"])

    if page == "Logout":
        del st.session_state["user"]
        st.experimental_rerun()

    return page

# About page
def about_page():
    st.title("About")
    st.write("""
    This project is focused on automating the evaluation of answer sheets using multi-agent LLMs. 
    The system is designed to help educators and students alike by providing quick and accurate assessments.
    """)

# Student page (visible only to students)
def student_page():
    st.title("Student Page")
    st.write("Upload your answer sheet below:")

    uploaded_file = st.file_uploader("Upload your answersheet (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file:
   
        
        st.image(uploaded_file, caption="Uploaded PDF as Images", use_column_width=True)
        text = textExtraction(uploaded_file)
        

        with st.expander("View Transcript"):
            st.write(text)

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text



# Evaluator page (visible only to evaluators)
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

# Future Scope page
def future_scope_page():
    st.title("Future Scope")
    st.write("""
    - Integration with more sophisticated models for even better accuracy.
    - Incorporating more features such as peer review and collaborative evaluation.
    - Exploring ways to reduce biases in automated evaluations.
    """)

# Main application logic
def main():
    if "user" not in st.session_state:
        login_page()
    else:
        page = sidebar()

        if page == "About":
            about_page()
        elif page == "Student":
            student_page()
        elif page == "Evaluator":
            evaluator_page()
        elif page == "Score":
            score_page()
        elif page == "Future Scope":
            future_scope_page()

if __name__ == "__main__":
    main()
