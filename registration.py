import streamlit as st
import os
from PyPDF2 import PdfReader
from pyairtable import Table
import datetime
import re

PERSONAL_ACCESS_TOKEN = st.secrets["PERSONAL_ACCESS_TOKEN"]
BASE_ID = st.secrets["BASE_ID"]
TABLE_NAME = st.secrets["TABLE_NAME"]  # Replace with your table name

# set environment variable for GROQ API key

airtable = Table(PERSONAL_ACCESS_TOKEN, BASE_ID, TABLE_NAME)

# Create title for WHU MBA Streamlit App
st.title("Registration LinkedIn Profile Accelerating Entrepreneurship with Generative AI")

text = ""

# Helper function to validate email format
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Helper function to validate name (at least 2 words)
def is_valid_name(name):
    return len(name.strip().split()) >= 2

# Display initial input form for user details and PDF upload
with st.form("registration_form"):
    name = st.text_input("Please enter your first name and last name *", placeholder="e.g., John Doe")
    email = st.text_input("Please enter your email address *", placeholder="e.g., john.doe@example.com")
    
    # user needs to indicate with yes or no if they are a student
    uploaded_file = st.file_uploader("Please upload a PDF of your LinkedIn profile *", 
                                   help="You can find this PDF by going to your LinkedIn profile page, click on Resources, and click on Save PDF. By uploading the file, you agree that we use and store your LinkedIn profile for the purpose of matchig for the generative AI course", 
                                   type="pdf")
    
    st.markdown("*Required fields")
    submit_form = st.form_submit_button("Submit")

# If the form is submitted
if submit_form:
    # Collect all validation errors
    errors = []
    
    # Validate name
    if not name or not name.strip():
        errors.append("Please enter your name.")
    elif not is_valid_name(name):
        errors.append("Please enter both your first name and last name.")
    
    # Validate email
    if not email or not email.strip():
        errors.append("Please enter your email address.")
    elif not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    
    
    # Validate PDF upload
    if uploaded_file is None:
        errors.append("Please upload your LinkedIn profile PDF.")
    
    # Display errors if any
    if errors:
        for error in errors:
            st.error(error)
    else:
        # All validations passed, process the form
        try:
            # Read the pdf file
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Additional validation: check if PDF contains text
            if not text.strip():
                st.error("The uploaded PDF appears to be empty or contains no readable text. Please upload a valid LinkedIn profile PDF.")
            else:
                st.session_state.profile = text
                
                record = {"Name": name.strip(), "Email": email.strip().lower(), "LinkedIn Profile": st.session_state.profile, "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                airtable.create(record)
                st.success("**Registration successful.**")
                
        except Exception as e:
            st.error(f"An error occurred while processing your PDF: {str(e)}. Please try uploading the file again.")



