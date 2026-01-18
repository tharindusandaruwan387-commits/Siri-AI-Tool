import streamlit as st
from groq import Groq
from supabase import create_client
import base64

# 1. Page Configuration
st.set_page_config(page_title="Honorgpt", page_icon="logo.jpg")

# Supabase සම්බන්ධ කිරීම
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# Session State පරීක්ෂාව
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_id" not in st.session_state:
    st.session_state.current_id = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# ලෝගෝ එක Base64 වලට හැරවීම
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

img_data = get_base64_image("logo.jpg")
ai_avatar = f"data:image/jpeg;base64,{img_data}" if img_data else "🤖"

# CSS - පිරිසිදු මැදට පෙනෙන පෙනුම
st.markdown("""
    <style>
    .block-container { max-width: 800px; padding-top: 2rem; margin: auto; }
    .centered-title { text-align: center; font-size: 2.5rem; font-weight: bold; padding: 20px; }
    .stButton>button { width: 100%; border-radius: 12px; height: 50px; background-color: #00a884; color: white; font-weight: bold; border: none; }
    .auth-link { text-align: center; cursor: pointer; color: #00a884; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTH PAGE (Login & Sign Up) ---
def show_auth():
    if st.session_state.auth_mode == "login":
        st.markdown("<h1 class='centered-title'>Honorgpt Login</h1>", unsafe_allow_html=True)
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        
        if st.button("LOGIN"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state.user_data = res.user
                    st.rerun()
            except:
                st.error("Invalid Email or Password!")
        
        if st.button("Sign Up", key="go_to_signup"):
            st.session_state.auth_mode = "signup"
            st.rerun()

    else:
        st.markdown("<h1 class='centered-title'>Create Account</h1>", unsafe_allow_html=True)
        new_email = st.text_input("Email Address", key="signup_email")
        new_password = st.text_input("Password (min 6 chars)", type="password", key="signup_pw")
        
        if st.button("SIGN UP"):
            try:
                supabase.auth.sign_up({"email": new_email, "password": new_password})
                st.success("Account created! Please login.")
                st.session_state.auth_mode = "login"
                st.rerun()
            except:
                st.error("Signup failed! Try a different email.")
        
        if st.button("Already have an account? Login", key="go_to_login"):
            st.session_state.auth_mode = "login"
            st.rerun()

# --- MAIN APP ---
def show_app():
    with st.sidebar:
        st.image("logo.jpg", width=80)
        st.write(f"User: {st.session_state.user_data.email}")
        if st.button("+ New Chat"):
            st.session_state.chat_history = []
            st.session_state.current_id = None
            st.rerun()
        st.markdown("---")
        st.subheader("History")
        try:
            res = supabase.table("chats").select("id, title").eq("user_id", st.session_state.user_data.id).order("id", desc=True).execute()
            for chat in res.data:
                if st.button(f"💬 {chat['title']}", key=f"c_{chat['id']}"):
                    chat_data = supabase.table("chats").select("*").eq("id", chat['id']).execute()
                    st.session_state.chat_history = chat_data.data[0]["messages"]
                    st.session_state.current_id = chat['id']
                    st.rerun()
        except: pass
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user_data = None
            st.rerun()

    st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)
    for m in st.session_state.chat_history:
        if m["role"] != "system":
            with st.chat_message(m["role"], avatar=ai_avatar if m["role"] == "assistant" else None):
                st.markdown(m["content"])

    if prompt := st.chat_input("Ask Honorgpt..."):
        if not st.session_state.chat_history:
            st.session_state.chat_history.append({"role": "system", "content": "You are Honorgpt."})
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant", avatar=ai_avatar):
            full_res = ""
            placeholder = st.empty()
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            for chunk in client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.chat_history, stream=True):
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})
            db_data = {"user_id": st.session_state.user_data.id, "messages": st.session_state.chat_history, "title": prompt[:30]}
            if st.session_state.current_id:
                supabase.table("chats").update(db_data).eq("id", st.session_state.current_id).execute()
            else:
                db_res = supabase.table("chats").insert(db_data).execute()
                if db_res.data: st.session_state.current_id = db_res.data[0]["id"]

# Main Logic
if st.session_state.user_data is None:
    show_auth()
else:
    show_app()

