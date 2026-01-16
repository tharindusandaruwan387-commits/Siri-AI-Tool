import streamlit as st
from groq import Groq # type: ignore
import base64
from streamlit_google_auth import Authenticate

# --- 1. GOOGLE AUTHENTICATION SETUP ---
auth = Authenticate(
    secret_credentials_path='google_credentials.json',
    cookie_name='honorgpt_cookie',
    cookie_key='honorgpt_secret_key',
    redirect_uri='https://siri-ai-tool-nci8jzgzzw95njjeur2bp9.streamlit.app/',
)

auth.check_authenticator()

# User log wela naththan login pennanna
if not st.session_state.get('connected'):
    st.markdown("<h1 style='text-align: center;'>Welcome to Honorgpt</h1>", unsafe_allow_html=True)
    st.write("Please login with your Gmail to continue.")
    auth.login('Login with Google', 'main')
    st.stop() # Login wenakan pahala code eka run wenne na

# --- LOGGED IN USERS TA WITARAK PAHALA TIKA PENWA ---

# 2. Page Configuration
st.set_page_config(page_title="Honorgpt", page_icon="logo.jpg", layout="wide")

# Function to convert image to base64 for avatars
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load your logo as avatar
logo_base64 = get_base64_image("logo.jpg")
ai_avatar = f"data:image/jpeg;base64,{logo_base64}"

# CSS for WhatsApp style chat and UI cleaning
st.markdown(f"""
<style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .centered-title {{
        text-align: center;
        padding: 20px;
        font-family: 'Segoe UI', sans-serif;
        color: white;
        font-size: 3rem;
        font-weight: bold;
    }}
    /* WhatsApp style chat bubbles placeholder - Oya kalin dapu CSS tika methana thiyenna ona */
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("logo.jpg", width=150)
    st.title("Honorgpt Settings")
    st.write(f"Logged in as: {st.session_state['name']}")
    auth.logout('Logout', 'sidebar') # Logout button eka side bar ekata damma

# Main Title
st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)

# AI Logic
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Honorgpt, a fast AI assistant created by Tharindu Sandaruwan."}
    ]

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant", avatar=ai_avatar):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What do you need to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ai_avatar):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True,
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error: {e}")
