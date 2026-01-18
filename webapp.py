import streamlit as st
from groq import Groq
from supabase import create_client
import base64

# 1. Page Configuration
st.set_page_config(page_title="Honorgpt", page_icon="logo.jpg", layout="wide")

# Supabase සම්බන්ධ කිරීම
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# Session State එක මුලින්ම පරීක්ෂා කිරීම
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

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
    .centered-title {{ text-align: center; font-size: 2.5rem; font-weight: bold; padding: 10px; }}
    .stButton>button {{ width: 100%; border-radius: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE FUNCTIONS ---
def save_chat_to_db():
    if st.session_state.user and st.session_state.messages:
        title = st.session_state.messages[1]["content"][:30] if len(st.session_state.messages) > 1 else "New Chat"
        data = {"user_id": st.session_state.user.id, "messages": st.session_state.messages, "title": title}
        if st.session_state.current_chat_id:
            supabase.table("chats").update(data).eq("id", st.session_state.current_chat_id).execute()
        else:
            res = supabase.table("chats").insert(data).execute()
            if res.data: st.session_state.current_chat_id = res.data[0]["id"]

# --- AUTH PAGE ---
def auth_page():
    st.markdown("<h1 class='centered-title'>Honorgpt Access</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Log In"):
            try:
                # කෙලින්ම Auth එක පරීක්ෂා කිරීම
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state.user = res.user
                    st.success("සාර්ථකයි! ඇතුළු වෙනවා...")
                    st.rerun() # මෙතනදී කෙලින්ම Main App එකට යයි
            except:
                st.error("Login වැරදියි! නැවත උත්සාහ කරන්න.")

    with tab2:
        n_email = st.text_input("New Email")
        n_password = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            try:
                supabase.auth.sign_up({"email": n_email, "password": n_password})
                st.info("Account එක හැදුනා! දැන් Login වෙන්න.")
            except: st.error("Signup Failed!")

# --- MAIN APP ---
def main_app():
    with st.sidebar:
        st.image("logo.jpg", width=80)
        st.write(f"User: {st.session_state.user.email}")
        if st.button("+ New Chat"):
            st.session_state.messages = []
            st.session_state.current_chat_id = None
            st.rerun()
        
        st.markdown("---")
        # පරණ චැට් පෙන්වීම
        history = supabase.table("chats").select("id, title").eq("user_id", st.session_state.user.id).order("id", desc=True).execute()
        for chat in history.data:
            if st.button(f"💬 {chat['title']}", key=f"c_{chat['id']}"):
                res = supabase.table("chats").select("*").eq("id", chat['id']).execute()
                st.session_state.messages = res.data[0]["messages"]
                st.session_state.current_chat_id = chat['id']
                st.rerun()

        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

    st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    # මැසේජ් පෙන්වීම
    for m in st.session_state.messages:
        if m["role"] != "system":
            with st.chat_message(m["role"], avatar=ai_avatar if m["role"] == "assistant" else None):
                st.markdown(m["content"])

    if prompt := st.chat_input("Ask something..."):
        if not st.session_state.messages:
            st.session_state.messages.append({"role": "system", "content": "You are Honorgpt."})
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar=ai_avatar):
            full_res = ""
            placeholder = st.empty()
            for chunk in client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages, stream=True):
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            save_chat_to_db()

# වැඩසටහන ආරම්භය
if st.session_state.user is None:
    auth_page()
else:
    main_app()
