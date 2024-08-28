import streamlit as st
from PIL import Image
from chains import *

def main():
    st.title("Automated Answer Sheet Evaluation System")


    sides = [
        "About"
    ]
    
    uploaded_answer = st.file_uploader("Upload Answer Sheets (PDF)",accept_multiple_files=True)
    uploaded_key = st.file_uploader("Upload Reference Answer Key (PDF)", type="pdf")




if __name__ == "__main__":
    main()
