import streamlit as st
from utils.auth import authenticate_user, register_evaluator, register_student, get_user_profile
from utils.database import create_tables, SessionLocal, ReportDetails
import hashlib



global COURSE
COURSE = {
    'MAI471':"Large Language Models",
    'MAI431':"Internet of Things",
    'MAI432':"Multi Agent Systems"
}
# Initialize database tables
create_tables()

st.set_page_config(page_title="Automated Answer Sheet Evaluation", page_icon="📄", layout="wide")

# Hide default Streamlit menu and footer
hide_streamlit_style = """
    <style>
    
    [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.html(hide_streamlit_style,)#) unsafe_allow_html=True)

# Session state management
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False
    st.session_state['user'] = None
    st.session_state['profile'] = None

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def login():
    st.title("Welcome to Automated Answer Sheet Evaluation System")
    menu = ["Login/Register", "About", "Future Scope"]
    choice = st.sidebar.selectbox("Start Here", menu)

    if choice == "Login/Register":
        r1, r2 = st.tabs(['Login', 'Register'])
        
        with r1:
            st.subheader("Login Section")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type='password', key="login_password")
            if st.button("Login", key="login_button"):
                hashed_pswd = hash_password(password)
                user = authenticate_user(username, hashed_pswd)
                if user:
                    profile = get_user_profile(user)
                    st.session_state['authentication_status'] = True
                    st.session_state['user'] = user
                    st.session_state['profile'] = profile
                    st.success(f"Logged in as {user.role}")
                    st.rerun()
                else:
                    st.error("Invalid Username/Password")

        with r2:
            st.subheader("Create New Account")
            role = st.selectbox("Select Role", ["Student", "Evaluator"], key="register_role")
            first_name = st.text_input("First Name", key="register_first_name")
            last_name = st.text_input("Last Name", key="register_last_name")
            username = st.text_input("Username", key="register_username")
            password = st.text_input("Password", type='password', key="register_password")
            confirm_password = st.text_input("Confirm Password", type='password', key="register_confirm_password")

            if role == "Student":
                register_number = st.text_input("Register Number", key="register_register_number")
                course_ids = st.multiselect("Course(s) Enrolled", list(COURSE.keys()), key="register_course_ids_student")

                if st.button("Register", key="register_student_button"):
                    if password == confirm_password:
                        hashed_pswd = hash_password(password)
                        success, message = register_student(username, hashed_pswd, first_name, last_name, register_number, ",".join(course_ids))
                        if success:
                            st.success(message)
                            st.info("Go to Login Menu to login")
                        else:
                            st.error(message)
                    else:
                        st.error("Passwords do not match")

            elif role == "Evaluator":
                course_ids = st.multiselect("Course(s) Teaching", list(COURSE.keys()), key="register_course_ids_evaluator")

                if st.button("Register", key="register_evaluator_button"):
                    if password == confirm_password:
                        hashed_pswd = hash_password(password)
                        success, message = register_evaluator(username, hashed_pswd, first_name, last_name, ",".join(course_ids))
                        if success:
                            st.success(message)
                            st.info("Go to Login Menu to login")
                        else:
                            st.error(message)
                    else:
                        st.error("Passwords do not match")

    elif choice == "About":
        st.subheader("About")
        st.markdown("""
       # 📝 About the Automatic Answer Script Evaluation System

Welcome to the **Automatic Answer Script Evaluation System**, a state-of-the-art multi-agent platform designed to revolutionize the way educational assessments are conducted. This project leverages cutting-edge artificial intelligence to evaluate student answer scripts with precision, speed, and objectivity, completely eliminating the need for human intervention.

## 🌟 Key Features

### 1. Multi-Agent System
Our system is powered by a network of specialized agents, each responsible for a critical aspect of the evaluation process:
- **Agent 1**: Transcribes handwritten or typed answer scripts into text strings using advanced OCR technology.
- **Agent 2**: Evaluates answers by comparing them against an official answer key, ensuring accuracy in marking.
- **Agent 3**: Uses external knowledge bases to assess the answers, providing a broader context for evaluation.
- **Agent 4**: Analyzes and evaluates diagrams included in the answers, ensuring they meet the required standards.
- **Agent 5**: Aggregates the scores from all agents to calculate the final marks, delivering a comprehensive and fair assessment.

### 2. Seamless Integration
Our system seamlessly integrates with educational databases, ensuring that student records, answer keys, and evaluation results are efficiently managed and stored. The entire process is designed to be user-friendly, with an intuitive interface that makes it easy for evaluators to monitor and manage assessments.

### 3. Objective and Consistent Evaluation
By automating the evaluation process, our system eliminates the potential for human bias and error. Each answer is judged purely on its content, and the final marks reflect a fair and objective assessment. This consistency is crucial in maintaining academic integrity.

### 4. Comprehensive Feedback
Students receive detailed feedback on their submissions, with suggestions for improvement based on both internal knowledge (from the answer key) and external knowledge (contextual information). This feedback is valuable for students to understand their mistakes and learn how to improve.

### 5. Diagrammatic Evaluation
Unique to our system is the ability to evaluate diagrams within the answer scripts. Diagrams are an essential component of many subjects, and our system ensures they are given the attention they deserve during evaluation.

## 🚀 How It Works

1. **Upload**: Instructors or administrators upload the student answer scripts and the corresponding answer keys to the system.
2. **Evaluation**: The system's agents process the scripts, evaluating each answer against the answer key and external knowledge bases. Diagrams are also extracted and evaluated.
3. **Results**: Final scores are calculated, and a detailed report is generated. This report includes scores, feedback, and suggestions for improvement.
4. **Review**: Administrators can review the evaluation results and make adjustments if necessary before publishing the final grades.

## 🔍 Why Choose Our System?

- **Efficiency**: Drastically reduces the time required for evaluations, allowing instructors to focus on teaching.
- **Accuracy**: Leverages AI to ensure that evaluations are accurate, consistent, and free from human error.
- **Scalability**: Capable of handling large volumes of answer scripts, making it suitable for institutions of all sizes.
- **Fairness**: Ensures that every student is evaluated on the same criteria, promoting fairness in grading.

## 🌐 Join the Future of Education

The Automatic Answer Script Evaluation System is more than just a tool—it's a leap forward in the way we assess knowledge and skills. By harnessing the power of AI, we're setting new standards for educational evaluation, paving the way for a more efficient, accurate, and fair future.

---

Thank you for choosing our system. We are committed to delivering the best in educational technology and look forward to helping you achieve your academic goals.

### Contact Us
For more information or to get in touch with our team, please visit our [contact page](#).


        """)

    elif choice == "Future Scope":
        st.subheader("Future Scope")
        st.write("""
# 🔮 Future Scope and Possible Advancements

The **Automatic Answer Script Evaluation System** is a pioneering step towards revolutionizing the educational assessment process. While the current system is highly advanced, there is always room for growth and improvement. The future scope of this project envisions a range of exciting possibilities and technological advancements that can further enhance the efficiency, accuracy, and capabilities of the system.

## 🌱 Future Scope

### 1. **Adaptive Learning Integration**
   - **Personalized Feedback**: Incorporating adaptive learning technologies to provide more personalized feedback based on each student's learning style and performance. This could include tailored study materials and recommendations for improvement.
   - **Continuous Improvement**: The system could track student progress over time, adjusting its evaluation criteria based on individual learning curves, thus offering a more personalized assessment.

### 2. **Enhanced Diagram Evaluation**
   - **3D Diagram Evaluation**: As technology advances, the system could be upgraded to evaluate 3D diagrams and models, which are becoming increasingly common in fields like engineering and medicine.
   - **AI-Powered Drawing Recognition**: Implementing more sophisticated AI models that can better recognize and evaluate hand-drawn diagrams, even in less-than-ideal conditions (e.g., faint lines, poor handwriting).

### 3. **Multi-Language Support**
   - **Global Reach**: Expanding the system's capabilities to support multiple languages, making it accessible to educational institutions worldwide. This would involve integrating multilingual OCR and evaluation models.
   - **Cultural Context Awareness**: Enhancing the external knowledge evaluation to be context-aware, taking into account cultural and regional differences in education systems.

### 4. **Real-Time Collaboration**
   - **Instructor Collaboration**: Introducing features that allow multiple instructors to collaborate on the evaluation process in real-time, sharing insights, and making collective decisions on grading.
   - **Peer Evaluation**: Allowing students to engage in peer evaluations, where their assessments are guided and moderated by the system, promoting collaborative learning.

### 5. **Integration with Learning Management Systems (LMS)**
   - **Seamless Integration**: Developing APIs and plugins to integrate the system with popular Learning Management Systems (LMS) like Moodle, Blackboard, and Canvas, enabling direct access to student assessments and grades.
   - **Automated Grading**: Automating the entire grading process within the LMS, from assignment submission to final grade posting, reducing the administrative burden on educators.

### 6. **Advanced AI Models**
   - **Contextual Understanding**: Implementing more advanced AI models that not only evaluate answers but also understand the context and nuances of complex, open-ended questions.
   - **Explainable AI**: Developing AI models that can explain their grading decisions in detail, helping instructors and students understand the reasoning behind each score.

## 🚀 Possible Advancements

### 1. **Blockchain for Academic Integrity**
   - **Immutable Records**: Utilizing blockchain technology to ensure the integrity of the evaluation process by creating immutable records of grades and feedback, which can be securely shared with students and institutions.
   - **Credential Verification**: Implementing a blockchain-based system for verifying academic credentials and assessment histories, making it easier to share and authenticate student achievements.

### 2. **AI-Driven Content Creation**
   - **Dynamic Question Generation**: Using AI to generate custom exam questions tailored to the curriculum and learning outcomes, reducing the workload on educators.
   - **Automated Answer Key Generation**: Developing AI tools that can create answer keys based on the content of lectures, textbooks, and other instructional materials.

### 3. **Emotional Intelligence in Evaluation**
   - **Sentiment Analysis**: Integrating sentiment analysis to evaluate the tone and emotional content of student answers, particularly in subjects like literature and social sciences, where emotional expression is key.
   - **Emotional Feedback**: Providing feedback that takes into account the student's emotional state, encouraging positive reinforcement and constructive criticism.

### 4. **Augmented Reality (AR) and Virtual Reality (VR)**
   - **Interactive Assessments**: Creating immersive AR/VR environments where students can perform practical tasks and experiments that are evaluated in real-time by the system.
   - **Virtual Classrooms**: Extending the system to virtual classrooms where evaluations are conducted in a fully interactive, immersive environment, bridging the gap between traditional and online education.

### 5. **Cross-Disciplinary Evaluations**
   - **Holistic Assessments**: Developing the capability to evaluate interdisciplinary projects that span multiple subjects, providing a more holistic view of a student's knowledge and skills.
   - **Collaborative Projects**: Facilitating the evaluation of group projects and collaborative efforts, where multiple students contribute to a single submission, with individual contributions tracked and assessed.

## 🚧 Challenges and Considerations

While these advancements offer exciting possibilities, they also come with challenges, including:
- **Ethical AI**: Ensuring that AI models are fair, unbiased, and transparent in their evaluations.
- **Data Privacy**: Protecting student data and maintaining confidentiality in an increasingly connected digital landscape.
- **Technical Complexity**: Balancing the need for advanced features with the system's usability and reliability.

## 🌐 The Road Ahead

The **Automatic Answer Script Evaluation System** is poised to evolve continuously, incorporating the latest technological advancements to meet the ever-changing needs of educational institutions. As we move forward, our focus remains on delivering a system that is not only efficient and accurate but also fair, ethical, and supportive of student growth.

Join us on this journey towards the future of education, where technology empowers both educators and students to achieve their fullest potential.

---

Thank you for your interest in the future of our project. We are committed to driving innovation in educational technology and look forward to the exciting developments ahead.

### Stay Updated
For the latest news and updates on our advancements, please visit our [news page](#) or follow us on [social media](#).

        """)




def logout():
    st.session_state['authentication_status'] = False
    st.session_state['user'] = None
    st.session_state['profile'] = None
    st.success("You have been logged out.")
    st.rerun()

def fetch_student_scores(student_id):
    session = SessionLocal()

    try:
        results = (
            session.query(ReportDetails.course_id, ReportDetails.score)
            .filter(ReportDetails.student_id == student_id)
            .filter(ReportDetails.score > 0) 
            .all()
        )

        course_scores = {course_id: score for course_id, score in results}
        return course_scores

    finally:
        session.close()

if st.session_state['authentication_status']:
    role = st.session_state['user'].role
    if role == "Student":
        studid = st.session_state['profile'].student_id
        st.sidebar.title(f"Welcome, {st.session_state['profile'].first_name}")
        selection = st.sidebar.selectbox("Navigation", ["Home", "Upload Answer Sheet", "View Scores"])
        if selection == "Home":
            cr = list(st.session_state['profile'].course_ids.split(","))
            crr = [COURSE[k] for k in cr]
            course_scores = fetch_student_scores(studid)
            st.header(f"Student Portal")
            st.write(f"**Name:** `{st.session_state['profile'].first_name} {st.session_state['profile'].last_name}`")
            st.write(f"**Register Number:** `{st.session_state['profile'].register_number}`")
            st.write(f"**Courses Enrolled:** `{', '.join(crr)}`")
            with st.expander("At a Glance", icon = '📊'):
                st.markdown("#### Your Performance at a Glance")
                
                if len(cr) > 1:
                    for i in cr:
                        st.write(f"**Course ID:** `{i}`")
                        st.write(f"**Course:** `{COURSE[i]}`")
                        if i in course_scores:
                            st.write(f"**Score:** `{course_scores[i]}`")
                        else:
                            st.write("**Score:** `Not evaluated yet`")
                else:
                    st.write(f"**Course ID:** `{cr[0]}`")
                    st.write(f"**Course:** `{COURSE[cr[0]]}`")
                    if cr[0] in course_scores:
                        st.write(f"**Score:** `{course_scores[cr[0]]}`")
                    else:
                        st.write("**Score:** Not evaluated yet")

            st.markdown("""
                            ### 📋 Evaluation Process Guidelines

Welcome to the Student Portal! Below is a step-by-step guide to help you navigate the process of submitting your answer scripts for evaluation and checking your scores. Follow these steps to ensure a smooth and successful evaluation experience.

#### 1. Select the Course to Upload Answers For
- Begin by selecting the course for which you want to upload your answers.
- Navigate to the **Upload Answer Script** section in your dashboard.
- Choose the relevant course from the list of courses you're enrolled in.

#### 2. Upload Your Answer Script
- Once you have selected the course, you will be prompted to upload your answer script.
- Ensure that your answer script is in the correct format (e.g., PDF or image).
- Click on the **Upload** button to upload your answer script.
- Wait for the upload to complete. You will see a preview of your uploaded file.

#### 3. Check if the Transcript is Correct and Send for Evaluation
- After uploading, the system will automatically transcribe your answer script into text.
- Carefully review the transcribed text to ensure it accurately reflects your answers.
- If there are any discrepancies, you can correct them before proceeding.
- Once you're satisfied with the transcript, click on the **Submit for Evaluation** button.
- Your answer script will now be sent for evaluation by the system.

#### 4. Wait for Evaluation to be Completed
- The evaluation process may take some time, depending on the complexity of your answers.
- You can check the status of your evaluation in the **Evaluation Status** section.
- Please be patient and wait for the system to complete the evaluation.

#### 5. Check Scores in the Scores Tab
- Once the evaluation is complete, you will receive a notification.
- Navigate to the **Scores** tab to view your evaluation results.
- Your score for each course will be displayed, along with detailed feedback and suggestions for improvement.
- If you have any questions or concerns about your scores, you can contact your evaluator for further clarification.

---

By following these guidelines, you can ensure that your answer scripts are accurately evaluated, and you receive the feedback needed to excel in your courses. Good luck!

""")

            
        elif selection == "Upload Answer Sheet":
            st.caption("ADD SOME TEXT")
            from pages.Student import student_dashboard
            student_dashboard()
        elif selection == "View Scores":
            from pages.Scores import view_student_scores, scores_tab
            view_student_scores()
            scores_tab()
        
    elif role == "Evaluator":
        st.sidebar.title(f"Welcome, {st.session_state['profile'].first_name}")
        selection = st.sidebar.selectbox("Navigation", ["Home", "Evaluate Answer Sheets", "View All Scores"])
        if selection == "Home":
            st.write(f"**Name:** {st.session_state['profile'].first_name} {st.session_state['profile'].last_name}")
            #st.write(f"**Register Number:** {st.session_state['profile'].register_number}")
            st.write(f"**Course IDs:** {st.session_state['profile'].course_ids}")
        elif selection == "Evaluate Answer Sheets":
            st.write("---")
            from pages.Evaluator import evaluator_dashboard
            evaluator_dashboard()
        elif selection == "View All Scores":
            from pages.Scores import view_all_scores
            view_all_scores()
    st.sidebar.button("Logout", on_click=logout)
else:
    login()
