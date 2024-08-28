import PyPDF2
from google.generativeai import GenerationConfig, GenerativeModel
import google.generativeai
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import PDFPageCountError
from PIL import Image
import re
import streamlit as st
import google


GOOGLE_API_KEY = "Your_Key"
google.generativeai.configure(api_key=GOOGLE_API_KEY)




def textExtraction(img):
    try:
        if img.type == "application/pdf":
            st.write("Processing PDF...")
            pdf_bytes = img.read()

            if not pdf_bytes:
                st.error("The PDF file is empty.")
                return ""
            try:
                images = convert_from_bytes(pdf_bytes)
                with st.expander("View your upload"):
                    st.image(images)
            except PDFPageCountError as e:
                st.error("Unable to get page count. The PDF might be empty or corrupted.")
                return ""
            except Exception as e:
                st.error(f"An error occurred while converting PDF to images: {e}")
                return ""
            gencon = GenerationConfig(temperature=0)
            text_results = []
            sysPrompt = "You are a handwritten text recognition expert. You will be given images of handwritten text. \
                Your job is provide an exact trascription of the text in the image/document. Return the output in plain text, no formatting.\
                    if the script has diagramatic representations, extract the information and label it separately using <DIAG>"
            model = GenerativeModel('gemini-1.5-pro-latest',generation_config=gencon, system_instruction=sysPrompt)
            for image in images:
                res = model.generate_content(image).text
                text_results.append(res)
            final_text = "\n\n".join(text_results)
        else:
            st.write("Processing Image...")
            image = Image.open(img)
            gencon = GenerationConfig(temperature=0)
            sysPrompt = "You are a handwritten text recognition expert. You can either be given a multi-paged PDF or images of handwritten text. Your job is to provide an exact transcription of the text in the image/document. Your output should separate all the answers using line spaces."
            model = GenerativeModel('gemini-1.5-pro-latest',generation_config=gencon, system_instruction=sysPrompt)
            final_text = model.generate_content(image).text

        return final_text
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return ""

# def textExtraction(img):
#     if img.type == "application/pdf":
#         print("this")
#         img = convert_from_bytes(img.read())
#     else:
#         print("this hsit")
#         img = Image.open(img)
#     sysPrompt = "You are a handwritten text recognition expert. You can either be given a multi paged pdf or images of handwritten text. Your job is provide an exact trascription of the text in the image/document. Your output should separate all the answers using line spaces."
#     model = genai.GenerativeModel('gemini-1.5-pro-latest', system_instruction=sysPrompt)
#     res = model.generate_content(img).text
#     return res

# def split_into_list(text):
#     pattern = r"(?i)\b[qa]\d+\s*[\).]?\b|[a-h]\s*\)|\b(?:Q|q|A|a)?\s*?(\d+)\s*[)]?"
#     questions = re.split(pattern, text)
#     pq = []
#     for i in range(1, len(questions)-1, 2):
#         #question_number = "Q" + str(questions[i]) + ")"
#         question_text = questions[i+1].strip()
#         pq.append(question_text)
#     return pq

# def split_into_list(text):
#     return text.split("%&$")

def split_into_list(transcript):


    pattern = r'(Q\d+\)|q\d+\)|A\d+\)|a\d+\)|A\)|a\)|\d+\)|\(\d+\)|\d+\.\))'
    
    # Use re.split() to split the transcript based on the pattern
    # The pattern is included in the split so it appears at the start of each split section
    answers = re.split(pattern, transcript)
    
    # The split results in a list where questions and answers are mixed. We combine them appropriately.
    answers = [answers[i] + answers[i + 1] for i in range(1, len(answers), 2)]
    
    return answers


def extract_text_from_pdf(pdf_path):
    
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    
    qa_dict = {}
    
    question_pattern = re.compile(r'(Q\s*\d+|Ques\s*\d+|Question\s*\d+):', re.IGNORECASE)
    answer_pattern = re.compile(r'(Ans\s*\d+|Answer\s*\d+|Answ er\s*\d+):', re.IGNORECASE)
    
    questions = re.split(question_pattern, text)
    
    for i in range(1, len(questions), 2):
        question_number = questions[i].strip()
        question_text = questions[i + 1].strip()
        
        answer_match = answer_pattern.search(question_text)
        if answer_match:
            answer_start = answer_match.start()
            answer_number = answer_match.group()
            
            question_only = question_text[:answer_start].strip().replace('\n', ' ')
            answer_only = question_text[answer_start + len(answer_number):].strip().replace('\n', ' ')
            qa_dict[question_only] = answer_only
    
    return qa_dict


def Evalref(ques,ans,subject):
    sd = st.progress(0)
    sysPrompt = f"Your are an expert in the subject of {subject}. You come from a long practicing background of experienced subject expert in your field.\
          You are tasked to evaluate a set of questions and their respective answers given by students. The input to you will be a question followed by its respective student answer. \
            Your task is to use your subject knowledege and evaluate the answers out of a total of 10 marks."
    gencon = GenerationConfig(temperature=0)
    model = GenerativeModel('gemini-1.5-pro', system_instruction=sysPrompt,  generation_config=gencon)
    prmt = "Your output should be in in the format: <score><SEP><suggestions>. Here <score> is just a integer number, like 5 or 7. The <score> SHOULD NOT be in a format like '7/10' or '5/10'. The <suggestions> are in plain text."
    grades = {}
    suggestions = {}
    tot = len(ans)

    for p,(i,j) in enumerate(zip(ques,ans)):
        sd.progress((100//tot)*(1+p))
        resil = model.generate_content([i,j,prmt]).text
        spl = resil.split("<SEP>")
        score = int(spl[0])
        sugg = str(spl[1])
        grades[i] = score
        suggestions[i] = sugg
    return grades, suggestions

def Evalkey(ques,key,ans):
    sd = st.progress(0)

    grades = {}
    suggestions = {}
    sysPrompt = "You are an external evaluator. You are tasked with evaluating the answers of student using only an answer key. The answer key will contain certain keywords, which you have to match in the stuents answer. If all the keywords in the answer key matches the student answer with correct semantic and contextual representation, the student should be awarded high score. Evaluation is out of 10. Your input will be quesitons, followed by the answer keys and finally followed by the student answers."
    gencon = GenerationConfig(temperature=0)
    model = GenerativeModel('gemini-1.5-pro', system_instruction=sysPrompt, generation_config=gencon)

    prmt = "Your output should be in in the format: <score><SEP><suggestions>. Here <score> is just a number like 5 and <suggestions> are in plain text."
    tot = len(ans)

    for p,(i,j,k) in enumerate(zip(ques,key,ans)):
        sd.progress((100//tot)*(1+p))
        resil = model.generate_content([i,j,k,prmt]).text
        spl = resil.split("<SEP>")
        score = int(spl[0])
        sugg = str(spl[1])
        grades[i] = score
        suggestions[i] = sugg
    return grades, suggestions

def checkDiag(ans):
    sysPrompt = "You are tasked to determine whether a given student's answer has any kind of diagrams or not. A diagram can be anything between a simple flowchart to a complex labelled diagram of a human heart."
    prmpt = "Does this image of a student's anwerscript have any kind of diagram in it. Just reply with a yes if it has a diagram and a no if it doesnt"
    model = GenerativeModel('gemini-1.5-pro-latest', system_instruction=sysPrompt)
    res = model.generate_content([ans,prmpt]).text
    if 'yes' in res.lower().strip():
        return True
    else:
        return False


def DiagEval(ques, key, ans):
    sysPrompt = "You are tasked to evaluate the student's diagram in a given image, based on the question and an answer key diagram. Your input will be the following: The question, student's answer, correct answer. You are expected to score (out of 10), by extracting the text and diagramatic information from the student's answer and the correct answer."
    prmpt = "Check the student's text and diagramatic answer based on the given key. Your output should be in the format: <score><SEP><suggestions>"
    model = GenerativeModel('gemini-1.5-pro-latest', system_instruction=sysPrompt)
    res = model.generate_content(["\n".join(ques), ans, key]).text
    return res

def cleaned_ans(ans):
    return [re.sub(r'Q\d+\)\s*|\n+', ' ', x).strip() for x in ans]

def Evalfinal(res1, res2):
    sysPrompt = ""
    model = GenerativeModel('gemini-1.5-flash', system_instruction=sysPrompt)
    res = model.generate_content([res1,res2]).text
    return res

