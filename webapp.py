import streamlit as st
from groq import Groq
from supabase import create_client
import base64

# Page Config
st.set_page_config(page_title="Honorgpt Login", page_icon="logo.jpg")

# Supabase සම්බන්ධ කිරීම
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("Please add Supabase URL and Key to Secrets!")
    st.stop()

if "user" not in st.session_state:
    st.session_state.user = None

# Login/Signup Page
def auth_page():
    st.markdown("<h1 style='text-align: center;'>Honorgpt Access</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.rerun()
            except:
                st.error("Login වැරදියි! Email හෝ Password චෙක් කරන්න.")

    with tab2:
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_pw")
        if st.button("Create Account"):
            try:
                supabase.auth.sign_up({"email": new_email, "password": new_password})
                st.success("Account එක හැදුනා! දැන් Login වෙන්න.")
            except:
                st.error("Signup වීමේදී දෝෂයක් ඇතිවිය.")

# Main AI Chat App
def main_app():
    with st.sidebar:
        st.write(f"Logged in as: {st.session_state.user.email}")
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()
    
    st.title("Honorgpt AI")
    # මෙතනට ඔයාගේ කලින් තිබ්බ AI Chat code එක දාන්න පුළුවන්...
    st.info("සාර්ථකව ලොග් වුණා! දැන් ඔබට චැට් කළ හැක.")

# පාලනය (Control)
if st.session_state.user is None:
    auth_page()
else:
    main_app()
