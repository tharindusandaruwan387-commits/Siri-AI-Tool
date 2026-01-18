import streamlit as st
from groq import Groq
from supabase import create_client
import base64

# 1. Page Configuration
st.set_page_config(page_title="Honorgpt", page_icon="logo.jpg", layout="wide")

# Supabase සම්බන්ධ කිරීම
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# ලෝගෝ එක Base64 වලට හැරවීම
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

img_data = get_base64_image("logo.jpg")
ai_avatar = f"data:image/jpeg;base64,{img_data}" if img_data else "🤖"

# CSS
st.markdown(f"""
    <style>
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    .stDeployButton {{ display:none; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    .centered-title {{ text-align: center; padding: 10px; font-size: 2.5rem; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Authentication පරීක්ෂාව
if "user" not in st.session_state:
    st.session_state.user = None

# --- AUTH PAGE ---
def auth_page():
    st.markdown("<h1 class='centered-title'>Honorgpt Access</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login Now", use_container_width=True)
            if submit:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.success("සාර්ථකයි! කරුණාකර නැවත 'Login Now' ක්ලික් කරන්න හෝ පිටුව Refresh කරන්න.")
                    st.rerun()
                except Exception as e:
                    st.error("Login වැරදියි. නැවත උත්සාහ කරන්න.")

    with tab2:
        with st.form("signup_form"):
            n_email = st.text_input("Email")
            n_password = st.text_input("Password", type="password")
            n_submit = st.form_submit_button("Create Account", use_container_width=True)
            if n_submit:
                try:
                    supabase.auth.sign_up({"email": n_email, "password": n_password})
                    st.success("Account එක හැදුනා! දැන් Login ටැබ් එකට ගිහින් ලොග් වෙන්න.")
                except: st.error("Signup Error!")

# --- MAIN APP ---
def main_app():
    with st.sidebar:
        st.image("logo.jpg", width=100)
        st.write(f"Account: {st.session_state.user.email}")
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

    st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are Honorgpt."}]

    for message in st.session_state.messages:
        if message["role"] != "system":
            avatar = ai_avatar if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar=ai_avatar):
            full_res = ""
            placeholder = st.empty()
            completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages, stream=True)
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

if st.session_state.user is None:
    auth_page()
else:
    main_app()
