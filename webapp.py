import streamlit as st
from groq import Groq
import base64

# Page Configuration
st.set_page_config(page_title="Honorgpt", page_icon="logo.jpg", layout="wide")

# Function to load and convert image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Try to load avatar, if fails use default
try:
    logo_base64 = get_base64_image("logo.jpg")
    ai_avatar = f"data:image/jpeg;base64,{logo_base64}"
except:
    ai_avatar = "🤖"

# CSS for Alignment and UI cleaning
st.markdown(f"""
    <style>
    /* Hide top menu items except Share */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    [data-testid="stStatusWidget"] {{display: none;}}
    [data-testid="stToolbar"] > div:not(:first-child) {{display: none !important;}}
    header[data-testid="stHeader"] {{background: transparent !important; visibility: visible !important;}}

    /* Message Alignment */
    .stChatMessage {{ background-color: transparent !important; }}
    
    /* User Message to Right */
    [data-testid="stChatMessage"]:has([data-testid="user-avatar"]) {{
        flex-direction: row-reverse !important;
        text-align: right !important;
    }}
    
    /* Assistant Message to Left */
    [data-testid="stChatMessage"]:has([data-testid="assistant-avatar"]) {{
        flex-direction: row !important;
    }}

    .centered-title {{
        text-align: center;
        padding: 20px;
        font-family: 'Segoe UI', sans-serif;
        color: white;
        font-size: 3rem;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("logo.jpg", width=150)
    st.title("Honorgpt Settings")
    st.write("Created by Tharindu Sandaruwan")
    st.markdown("<br>" * 5, unsafe_allow_html=True)
    if st.button("Log Out", use_container_width=True):
        st.toast("Logged out successfully!")

# Title
st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)

# Groq Client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {{"role": "system", "content": "You are Honorgpt, a fast AI created by Tharindu Sandaruwan."}}
    ]

# Display Chat History with Avatars
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant", avatar=ai_avatar):
            st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("What do you need to know?"):
    st.session_state.messages.append({{"role": "user", "content": prompt}})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ai_avatar):
        response_placeholder = st.empty()
        full_response = ""
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
        st.session_state.messages.append({{"role": "assistant", "content": full_response}})
