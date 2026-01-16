import streamlit as st
from groq import Groq
import base64
from streamlit_google_auth import Authenticate

# --- 1. PAGE CONFIG (Meka thama 1st line eka wenna ona) ---
st.set_page_config(page_title="HonorGPT", page_icon="🤖", layout="wide")

# --- 2. GOOGLE AUTHENTICATION SETUP ---
auth = Authenticate(
    cookie_name='honorgpt_cookie',
    cookie_key='honorgpt_secret_key',
    client_id=st.secrets["google_auth"]["client_id"],
    client_secret=st.secrets["google_auth"]["client_secret"],
    redirect_uri='https://siri-ai-tool-nci8jzgzzw95njjeur2bp9.streamlit.app/',
)

# Login status check kirima
auth.check_authenticator()

# User log wela naththan Login Screen eka pennanna
if not st.session_state.get('connected'):
    st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1>Welcome to HonorGPT 🤖</h1>
            <p>Please login with your Google account to continue.</p>
        </div>
    """, unsafe_allow_html=True)
    auth.login()
    st.stop()

# --- 3. AI TOOL INTERFACE (Log unama thama meka pennanne) ---

# Side bar eke Logout button eka
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6134/6134346.png", width=100)
    st.title("HonorGPT Settings")
    st.write(f"User: {st.session_state.get('user_info', {}).get('name')}")
    if st.button("Log Out"):
        auth.logout()
        st.rerun()

# Main Chat Interface
st.title("🤖 HonorGPT AI Assistant")

# --- METHANA INDAN OYAGE GROQ CHAT LOGIC EKA ---

# Groq Client setup (Secrets walin API Key eka gannawa)
# Mathaka athuwa 'GROQ_API_KEY' kiyala ekakuth Secrets walata danna
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "OYAGE_API_KEY_EKA_METHANATA"))

# Chat history eka initialize kirima
if "messages" not in st.session_state:
    st.session_state.messages = []

# Parana messages pennanna
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input ganna thana
if prompt := st.chat_input("Ask HonorGPT anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Response eka ganna thana
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Groq API eken response eka gannawa
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
