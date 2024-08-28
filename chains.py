import PyPDF2
import google.generativeai as genai
from pdf2image import convert_from_path
from PIL import Image
import re


GOOGLE_API_KEY = "AIzaSyCr04_iyPZP6Dx2dB5JpUAqd3A1sJa9U0A"
genai.configure(api_key=GOOGLE_API_KEY)


def textExtraction(img):
    if type(img) == str:
        if img.endswith(".pdf"):
            img = convert_from_path("Document.pdf", dpi=300)
        #else:
    img = Image.open(img)
    sysPrompt = "You are a handwritten text recognition expert. You can either be given a multi paged pdf or images of handwritten text. Your job is provide an exact trascription of the text in the image/document."
    model = genai.GenerativeModel('gemini-1.5-pro-latest', system_instruction=sysPrompt)
    res = model.generate_content(img).text
    return res

def split_into_questions(text):
    pattern = r'(?i)\b(?:Q|Question|A|Answer|Ans|Ques)?\s*?(\d+)\s*[)]?'
    questions = re.split(pattern, text)
    processed_questions = []
    for i in range(1, len(questions)-1, 2):
        question_number = "Q" + questions[i] + ")"
        question_text = questions[i+1].strip()
        processed_questions.append(question_number + " " + question_text)
    return processed_questions

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
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
    
    return qa_dict, text

def Evalref(ques,ans,subject):
    sysPrompt = f"Your are an expert in the subject of {subject}. You come from a long practicing background of experienced subject expert in your field.\
          You are tasked to evaluate a set of questions and their respective answers given by students. The input to you will be a question followed by its respective student answer. \
            Your task is to use your subject knowledege and evaluate the answers out of a total of 10 marks.\
                  Your output should be in plain text and in the format <evaluation score>%SEP%<suggestions>"
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=sysPrompt)
    res = model.generate_content([ques,ans]).text
    return res

def Evalkey(ques,key,ans):
    sysPrompt = "You are an external evaluator. You are tasked with evaluating the answers of student using only an answer key. The answer key will contain certain keywords, which you have to match in the stuents answer. If all the keywords in the answer key matches the student answer with correct semantic and contextual representation, the student should be awarded high score. Evaluation is out of 10. Your input will be quesitons, followed by the answer keys and finally followed by the student answers. Your output should be in the format <evaluation score> %SEP% <suggestions>"
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=sysPrompt)
    res = model.generate_content([ques,key,ans]).text
    return res

def cleaned_ans(ans):
    return [re.sub(r'Q\d+\)\s*|\n+', ' ', x).strip() for x in ans]

def Evalfinal(res1, res2):
    sysPrompt = ""
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=sysPrompt)
    res = model.generate_content([res1,res2]).text
    return res

