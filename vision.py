'''
from gtts import gTTS
import tempfile
from dotenv import load_dotenv
import os
import streamlit as st
from PIL import Image
import google.generativeai as genai
import pandas as pd
import requests

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# WHO Data Loader
@st.cache_data
def load_who_data():
    try:
        df = pd.read_csv("who_essential_medicines.csv")
        return df
    except Exception as e:
        st.error(f"WHO data load error: {e}")
        return pd.DataFrame()

def get_who_info(tablet_name, who_df):
    if who_df.empty:
        return "WHO dataset not loaded or missing."
    matches = who_df[who_df["Medicine Name"].str.contains(tablet_name, case=False, na=False)]
    if not matches.empty:
        match = matches.iloc[0]
        return f"""
**WHO Info**
- **Form**: {match.get('Form', 'N/A')}
- **Strength / Details**: {match.get('Strength / Details', 'N/A')}
- **Category**: {match.get('Category', 'N/A')}
"""
    return "No WHO data found."

# RxNorm API Fallback
def fetch_rxnorm_data(tablet_name):
    try:
        rxcui_res = requests.get(f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={tablet_name}")
        rxcui = rxcui_res.json().get("idGroup", {}).get("rxnormId", [None])[0]
        if rxcui:
            props = requests.get(f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/properties.json")
            p = props.json().get("properties", {})
            return f"""
**RxNorm Info**
- **Name**: {p.get("name", "N/A")}
- **RxCUI**: {p.get("rxcui", "N/A")}
- **TTY**: {p.get("tty", "N/A")}
"""
        return "No RxNorm data found."
    except Exception as e:
        return f"RxNorm Error: {e}"

# Gemini API Call
def get_gemini_response(input_text, image, user_note):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([input_text, *image])
        return response.text
    except Exception as e:
        return f"Error from Gemini API: {e}"

# Convert Uploaded Image for Gemini
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return [{"mime_type": uploaded_file.type, "data": bytes_data}]
    else:
        raise FileNotFoundError("No file uploaded")

# Text-to-Speech
def start_speech(text):
    tts = gTTS(text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        st.audio(fp.name, format="audio/mp3")

# Streamlit UI Config
st.set_page_config(page_title="Tablet Info Summarizer", layout="centered", page_icon="💊")

st.markdown(
    """
    <style>
        body {
            font-family: 'Poppins', sans-serif;
        }
        .header {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #ffd700;
        }
        .subheader {
            text-align: center;
            font-size: 1.5em;
            color: #00ffcc;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='header'>Tablet Info Summarizer</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>Upload a tablet image and get detailed information</div>", unsafe_allow_html=True)

# Session state
if "response_text" not in st.session_state:
    st.session_state.response_text = ""

# Inputs
user_input = st.text_input("Enter Additional Details (Optional):", help="Add any specific details or context.")
uploaded_file = st.file_uploader("Upload Tablet Image (JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"])
user_type = st.selectbox("Select User Type:", options=["Normal User", "Medical Specialist"])

# Load WHO Data
who_df = load_who_data()

# Main Button
if st.button("Analyze Tablet Info", use_container_width=True):
    if uploaded_file is not None:
        try:
            image_data = input_image_setup(uploaded_file)

            # Prompt based on user type
            if user_type == "Normal User":
                input_prompt = """
You are a helpful assistant providing clear and simple explanations about medicines.
Given an image of a tablet label, provide the following:
1. Tablet name
2. Uses (in everyday terms)
3. Common side effects
4. When to take it and any precautions
5. Warnings or interactions
Keep the language simple and easy for non-medical users to understand.
"""
            else:
                input_prompt = """
You are a medical expert summarizing detailed pharmaceutical data.
Given an image of a tablet label, provide:
1. Drug/Tablet name and composition
2. Pharmacological class, mechanism of action
3. Clinical indications, dosages, contraindications
4. Adverse reactions, interactions, precautions
5. Referencing current WHO/FDA standards if applicable
Use technical medical language suitable for healthcare professionals.
"""

            full_prompt = f"{input_prompt}\n\nTablet Details: {user_input}\n\nSummary:"
            gemini_summary = get_gemini_response(full_prompt, image_data, user_input)
            st.session_state.response_text = gemini_summary

            # WHO & RxNorm Info
            tablet_name = user_input.strip().split()[0] if user_input else "Paracetamol"
            who_info = get_who_info(tablet_name, who_df)
            rxnorm_info = fetch_rxnorm_data(tablet_name)

            st.markdown("<h3 style='color:#ffd700;'>Tablet Information Summary</h3>", unsafe_allow_html=True)
            st.success(gemini_summary)

            with st.expander("Additional Info (WHO & RxNorm)"):
                st.markdown(who_info)
                st.markdown(rxnorm_info)

        except Exception as e:
            st.error(f"Error processing the tablet info: {e}")
    else:
        st.warning("Please upload a tablet image to proceed.")

# Voice
if st.session_state.response_text:
    if st.button("Voice"):
        start_speech(st.session_state.response_text)
'''

from gtts import gTTS
import tempfile
from dotenv import load_dotenv
import os
import streamlit as st
from PIL import Image
import google.generativeai as genai
import pandas as pd
import requests

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# WHO Data Loader
@st.cache_data
def load_who_data():
    try:
        df = pd.read_csv("who_essential_medicines.csv")
        #st.success("WHO Data loaded successfully.")
        return df
    except Exception as e:
        st.error(f"WHO data load error: {e}")
        return pd.DataFrame()

def get_who_info(tablet_name, who_df):
    if who_df.empty:
        return "WHO dataset not loaded or missing."
    matches = who_df[who_df["Medicine Name"].str.contains(tablet_name, case=False, na=False)]
    if not matches.empty:
        match = matches.iloc[0]
        return f"""
**WHO Info**
- **Form**: {match.get('Form', 'N/A')}
- **Strength / Details**: {match.get('Strength / Details', 'N/A')}
- **Category**: {match.get('Category', 'N/A')}
"""
    return f"No WHO data found for {tablet_name}."

# RxNorm API Fallback
def fetch_rxnorm_data(tablet_name):
    try:
        rxcui_res = requests.get(f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={tablet_name}")
        if rxcui_res.status_code == 200:
            rxcui = rxcui_res.json().get("idGroup", {}).get("rxnormId", [None])[0]
            if rxcui:
                props = requests.get(f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/properties.json")
                if props.status_code == 200:
                    p = props.json().get("properties", {})
                    return f"""
**RxNorm Info**
- **Name**: {p.get("name", "N/A")}
- **RxCUI**: {p.get("rxcui", "N/A")}
- **TTY**: {p.get("tty", "N/A")}
"""
        return f"No RxNorm data found for {tablet_name}."
    except Exception as e:
        return f"RxNorm Error: {e}"

# Gemini API Call
def get_gemini_response(input_text, image, user_note):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([input_text, *image])
        return response.text
    except Exception as e:
        return f"Error from Gemini API: {e}"

# Convert Uploaded Image for Gemini
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return [{"mime_type": uploaded_file.type, "data": bytes_data}]
    else:
        raise FileNotFoundError("No file uploaded")

# Text-to-Speech
def start_speech(text):
    tts = gTTS(text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        st.audio(fp.name, format="audio/mp3")

# Streamlit UI Config
st.set_page_config(page_title="Tablet Info Summarizer", layout="centered", page_icon="💊")

st.markdown(
    """
    <style>
        body {
            font-family: 'Poppins', sans-serif;
        }
        .header {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #ffd700;
        }
        .subheader {
            text-align: center;
            font-size: 1.5em;
            color: #00ffcc;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='header'>Tablet Info Summarizer</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>Upload a tablet image and get detailed information</div>", unsafe_allow_html=True)

# Session state
if "response_text" not in st.session_state:
    st.session_state.response_text = ""

# Inputs
user_input = st.text_input("Enter Additional Details (Optional):", help="Add any specific details or context.")
uploaded_file = st.file_uploader("Upload Tablet Image (JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"])
user_type = st.selectbox("Select User Type:", options=["Normal User", "Medical Specialist"])

# Load WHO Data
who_df = load_who_data()

# Main Button
if st.button("Analyze Tablet Info", use_container_width=True):
    if uploaded_file is not None:
        try:
            image_data = input_image_setup(uploaded_file)

            # Prompt based on user type
            if user_type == "Normal User":
                input_prompt = """
You are a helpful assistant providing clear and simple explanations about medicines.
Given an image of a tablet label, provide the following:
1. Tablet name
2. Uses (in everyday terms)
3. Common side effects
4. When to take it and any precautions
5. Warnings or interactions
Keep the language simple and easy for non-medical users to understand.
"""
            else:
                input_prompt = """
You are a medical expert summarizing detailed pharmaceutical data.
Given an image of a tablet label, provide:
1. Drug/Tablet name and composition
2. Pharmacological class, mechanism of action
3. Clinical indications, dosages, contraindications
4. Adverse reactions, interactions, precautions
5. Referencing current WHO/FDA standards if applicable
Use technical medical language suitable for healthcare professionals.
"""

            full_prompt = f"{input_prompt}\n\nTablet Details: {user_input}\n\nSummary:"
            gemini_summary = get_gemini_response(full_prompt, image_data, user_input)
            st.session_state.response_text = gemini_summary

            

        except Exception as e:
            st.error(f"Error processing the tablet info: {e}")
    else:
        st.warning("Please upload a tablet image to proceed.")

# Voice
if st.session_state.response_text:
    if st.button("Voice"):
        start_speech(st.session_state.response_text)
