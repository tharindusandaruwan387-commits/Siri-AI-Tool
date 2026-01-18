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

# ලෝගෝ එක Base64 වලට හැරවීම
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

img_data = get_base64_image("logo.jpg")
ai_avatar = f"data:image/jpeg;base64,{img_data}" if img_data else "🤖"

# CSS - WhatsApp Style & Sidebar Styling
st.markdown(f"""
    <style>
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    .stDeployButton {{ display:none; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stChatMessage"]:has([data-testid="user-avatar"]) {{
        flex-direction: row-reverse !important;
        text-align: right !important;
    }}
    .centered-title {{ text-align: center; padding: 10px; font-size: 2.5rem; font-weight: bold; }}
    .stButton>button {{ width: 100%; border-radius: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# Session State මුලික සැකසුම්
if "user" not in st.session_state: st.session_state.user = None
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None
if "messages" not in st.session_state: st.session_state.messages = []

# --- DATABASE FUNCTIONS ---
def save_chat_to_db():
    if st.session_state.user and st.session_state.messages:
        chat_title = st.session_state.messages[1]["content"][:30] if len(st.session_state.messages) > 1 else "New Chat"
        data = {
            "user_id": st.session_state.user.id,
            "messages": st.session_state.messages,
            "title": chat_title
        }
        if st.session_state.current_chat_id:
            supabase.table("chats").update(data).eq("id", st.session_state.current_chat_id).execute()
        else:
            res = supabase.table("chats").insert(data).execute()
            if res.data: st.session_state.current_chat_id = res.data[0]["id"]

def load_chat(chat_id):
    res = supabase.table("chats").select("*").eq("id", chat_id).execute()
    if res.data:
        st.session_state.messages = res.data[0]["messages"]
        st.session_state.current_chat_id = chat_id

# --- AUTH PAGE ---
def auth_page():
    st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        with st.form("login"):
            e = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login Now"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                    st.session_state.user = res.user
                    st.rerun()
                except: st.error("Login Failed!")
    with tab2:
        with st.form("signup"):
            ne = st.text_input("Email")
            np = st.text_input("Password", type="password")
            if st.form_submit_button("Create Account"):
                try:
                    supabase.auth.sign_up({"email": ne, "password": np})
                    st.success("Account Created! Now Login.")
                except: st.error("Signup Failed!")

# --- MAIN APP ---
def main_app():
    # SIDEBAR - CHAT HISTORY
    with st.sidebar:
        st.image("logo.jpg", width=80)
        st.write(f"Logged as: {st.session_state.user.email}")
        
        if st.button("+ New Chat"):
            st.session_state.messages = [{"role": "system", "content": "You are Honorgpt."}]
            st.session_state.current_chat_id = None
            st.rerun()
        
        st.markdown("---")
        st.subheader("Recent Chats")
        history = supabase.table("chats").select("id, title").eq("user_id", st.session_state.user.id).order("id", desc=True).execute()
        for chat in history.data:
            if st.button(f"💬 {chat['title']}", key=str(chat['id'])):
                load_chat(chat['id'])
                st.rerun()
        
        st.markdown("---")
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

    # MAIN CHAT AREA
    st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    if not st.session_state.messages:
        st.session_state.messages = [{"role": "system", "content": "You are Honorgpt."}]

    for m in st.session_state.messages:
        if m["role"] != "system":
            with st.chat_message(m["role"], avatar=ai_avatar if m["role"] == "assistant" else None):
                st.markdown(m["content"])

    if prompt := st.chat_input("Ask Honorgpt..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar=ai_avatar):
            res_box = st.empty()
            full_res = ""
            for chunk in client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages, stream=True):
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            save_chat_to_db() # මෙතනදී තමයි Database එකට සේව් වෙන්නේ

if st.session_state.user is None: auth_page()
else: main_app()

