import streamlit as st # type: ignore
from huggingface_hub import InferenceClient
import base64

st.set_page_config(page_title="Honorgpt", page_icon="logo.jpg", layout="wide")

st.markdown("""
    <style>
    .centered-title {
        text-align: center;
        padding: 10px;
        font-family: 'Segoe UI', sans-serif;
        color: white;
    }
    .round-image {
        border-radius: 50%;
        overflow: hidden;
        width: 100px;
        height: 100px;
        object-fit: cover;
        border: 3px solid #FF4B4B;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

with st.sidebar:
    st.image("logo.jpg", width=150)
    st.title("Honorgpt Settings")
    st.write("Created by Tharindu Sandaruwan")
    
    st.markdown("<br>" * 10, unsafe_allow_html=True)
    if st.button("Settings", use_container_width=True):
        st.toast("Settings coming soon!")

img_base64 = get_image_base64("logo.jpg")
st.markdown(f"""
    <div style="text-align: center;">
        <img src="data:image/jpeg;base64,{img_base64}" class="round-image">
        <h1 class='centered-title'>Honorgpt</h1>
    </div>
    """, unsafe_allow_html=True)

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
                st.error("Too many requests. Please try again in 1 minute.")
            else:
                st.error(f"Error: {e}")
