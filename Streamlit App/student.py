import streamlit as st

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