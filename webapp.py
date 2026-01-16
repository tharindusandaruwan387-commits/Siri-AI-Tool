import streamlit as st # type: ignore
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Siri AI - My First AI Tool",
page_icon="🗿")
st.title("🗿 Siri AI Personal Assistant")
st.markdown("How can I help you?")

client = InferenceClient(api_key=st.secrets["HF_TOKEN"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you need to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat_completion(
            model="meta-llama/Llama-3.2-3B-Instruct", #
            messages=st.session_state.messages,
            max_tokens=500,
        )
        answer = response.choices[0].message.content
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})


        st.rerun()
