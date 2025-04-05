import os 
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber

#load environment variables
load_dotenv()

#configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#extract text from pdf
def extract_text_from_pdf(pdf_path):
    text=""
    try:
        #direct text extraction
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text=page.extract_text()
                if page_text:
                    text+=page_text
        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Direct text extraction failed: {e}")
        
    #fallback to ocr for image based pdfs
    print("Falling back to OCR for image-based PDF.")
    try:
        images=convert_from_path(pdf_path)
        for image in images:
            page_text=pytesseract.image_to_string(image)
            text+=page_text+"\n"
    except Exception as e:
        print(f"OCR failed: {e}")

    return text.strip()


def analyse_resume(resume_text,job_description=None):
    if not resume_text:
        return {"error": "Resume text is required for analysis."}
    
    model=genai.GenerativeModel("gemini-1.5-flash")

    base_prompt=f""" 
    lore ipsom

    Resume:
    {resume_text}
    """

    if job_description:
        base_prompt+=f"""
        Additonally, compare this resume to the following job description.

        Job Description:
        {job_description}

        Highlight the Strengths, Weaknesses, Skills, Recommendations for Improvement, Skills to Improve, Suggested Courses, Overall Assessment 
        """
    
    response=model.generate_content(base_prompt)

    analysis=response.text.strip()
    return analysis


#streamlit app
st.set_page_config(page_title="Resume Analyser", layout="wide")
st.title("Resume Analyser")
st.write("Analyse your resume and match it with your job description")

col1,col2=st.columns(2)
with col1:
    uploaded_file=st.file_uploader("Upload your resume(PDF)",type=["pdf"])
with col2:
    job_description=st.text_area("Enter yout job description:",placeholder="Paste the job decription here.")

if uploaded_file is not None:
    st.success("Resume uploaded succesfully")
else:
    st.warning("Please upload a resume in PDF format.")

st. markdown("<div style='padding-top:10px;'></div>",unsafe_allow_html=True)

if uploaded_file:
    #save uploaded file locally for processing
    with open("uploaded_resume.pdf","wb") as f:
        f.write(uploaded_file.getbuffer())
    #extract text from pdf
    resume_text=extract_text_from_pdf("uploaded_resume.pdf")

    if st.button("Analyse Resume"):
        with st.spinner("Analaysing Resume..."):
            try:
                #analyse resume
                analysis=analyse_resume(resume_text,job_description)
                st.success("Analysis completed.")
                st.write(analysis)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

#footer
st.markdown("....")
st.markdown("""<p style='text-align:center;'>Powered by <b> Streamlit</b> and <b>Google Gemini AI</b></p>""",unsafe_allow_html=True)
