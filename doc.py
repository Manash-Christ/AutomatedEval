
# PYTHON FILE TO READ IMAGE/PDF FOR BOTH ANSWER SHEET AND ANSWER KEY
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import re

from chains import textExtraction
ques =""" 
Question 1: Explain the basic architecture of a large language model (LLM) and its primary components.
Question 2: Discuss the challenges associated with training large language models
"""
file = st.file_uploader(label="Upload Answersheet images")
if file:
    st.image(file)
    text = textExtraction(file)
    st.write("Extracted Text: \n")
    st.write(text)
    sentences = re.split(r'(?<!\w\.\s)(?!\w\.)(?<!\w\.\s\w\.)\.', text)
    st.write(sentences)
    paragraphs = re.split(r"\n\n", text)

    


