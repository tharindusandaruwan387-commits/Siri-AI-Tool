import streamlit as st # type: ignore
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Siri AI", page_icon="🤖")

with st.sidebar:
    st.title("🤖 Siri AI Settings")
    st.write("Created by Tharindu Sandaruwan")
    st.info("Llama 3.2 Powered Personal Assistant")

st.title("🤖 Siri AI Personal Assistant")

client = InferenceClient(api_key=st.secrets["HF_TOKEN"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "You are Siri AI, a personal assistant created by Tharindu Sandaruwan. Always introduce yourself as Siri AI. If anyone asks who created or developed you, you must proudly say that you were created by Tharindu Sandaruwan. Keep your answers helpful and friendly."
        }
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
            st.error(f"Error: {e}")
