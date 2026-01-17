import streamlit as st
from groq import Groq
import base64

# 1. Page Configuration
st.set_page_config(page_title="Honorgpt", page_icon="logo.jpg", layout="wide")

# Avatar එක සඳහා ලෝගෝ එක Base64 වලට හැරවීම
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

img_data = get_base64_image("logo.jpg")
ai_avatar = f"data:image/jpeg;base64,{img_data}" if img_data else "🤖"

# CSS - Syntax Error එක මඟහැරීමට {{ }} භාවිතා කර ඇත
st.markdown(f"""
    <style>
    /* අනවශ්‍ය දේවල් ඉවත් කිරීම */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    .stDeployButton {{ display:none; }}
    [data-testid="stStatusWidget"] {{ display: none !important; }}
    [data-testid="stToolbar"] > div:not(:first-child) {{ display: none !important; }}
    header[data-testid="stHeader"] {{ background: transparent !important; visibility: visible !important; }}

    /* WhatsApp Style Chat Bubbles */
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
        st.toast("Logging out...")

# Title
st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)

# AI Logic
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Secrets Error: Please check if GROQ_API_KEY is saved correctly. Details: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {{"role": "system", "content": "You are Honorgpt, a fast AI created by Tharindu Sandaruwan."}}
    ]

# Chat History පෙන්වීම
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
            st.session_state.messages.append({{"role": "assistant", "content": full_response}})
        except Exception as e:
            st.error(f"Groq API Error: {e}")
