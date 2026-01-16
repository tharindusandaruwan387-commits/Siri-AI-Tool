import streamlit as st
from groq import Groq

st.set_page_config(page_title="Honorgpt", page_icon="logo.jpg", layout="wide")

st.markdown("""
    <style>
    /* Hide unwanted elements but keep sidebar toggle visible */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stStatusWidget"] {display: none;}
    
    /* Show Share button but hide other toolbar icons */
    [data-testid="stToolbar"] > div:not(:first-child) {
        display: none !important;
    }
    
    /* Ensure Sidebar Hamburger icon is visible and white */
    header[data-testid="stHeader"] {
        background: transparent !important;
        visibility: visible !important;
    }
    
    /* Title styling */
    .centered-title {
        text-align: center;
        padding: 20px;
        font-family: 'Segoe UI', sans-serif;
        color: white;
        font-size: 3rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.image("logo.jpg", width=150)
    st.title("Honorgpt Settings")
    st.write("Created by Tharindu Sandaruwan")
    st.markdown("<br>" * 10, unsafe_allow_html=True)
    if st.button("Settings", use_container_width=True):
        st.toast("Settings coming soon!")

st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Honorgpt, a fast AI assistant created by Tharindu Sandaruwan."}
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("What do you need to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
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
