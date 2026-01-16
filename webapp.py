import streamlit as st # type: ignore
from huggingface_hub import InferenceClient
import base64

st.set_page_config(page_title="Honorgpt", page_icon="logo.jpg", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    [data-testid="stToolbar"] > div:not(:first-child) {
        display: none !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }

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

client = InferenceClient(api_key=st.secrets["HF_TOKEN"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Honorgpt, created by Tharindu Sandaruwan."}
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
        response_text = ""
        message_placeholder = st.empty() 
        try:
            stream = client.chat_completion(
                model="meta-llama/Llama-3.2-3B-Instruct",
                messages=st.session_state.messages,
                max_tokens=500,
                stream=True 
            )
            for chunk in stream:
                if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                    token = chunk.choices[0].delta.content
                    response_text += token
                    message_placeholder.markdown(response_text + "▌")
            message_placeholder.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            if "429" in str(e):
                st.error("Model is busy. Please try again in a minute.")
            else:
                st.error(f"Error: {e}")
