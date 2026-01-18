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

# Session State පරීක්ෂාව - මෙතනින් තමයි ලොග් වෙලාද නැද්ද කියලා තීරණය කරන්නේ
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_id" not in st.session_state:
    st.session_state.current_id = None

# ලෝගෝ එක Base64 වලට හැරවීම
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

img_data = get_base64_image("logo.jpg")
ai_avatar = f"data:image/jpeg;base64,{img_data}" if img_data else "🤖"

# CSS
st.markdown("""
    <style>
    .stApp { max-width: 1000px; margin: 0 auto; }
    .centered-title { text-align: center; font-size: 2.5rem; font-weight: bold; padding: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 50px; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- ලොගින් පේජ් එක ---
def show_login():
    st.markdown("<h1 class='centered-title'>Honorgpt Login</h1>", unsafe_allow_html=True)
    
    # Frame එකක් නැතිව කෙලින්ම Input පෙන්වමු
    email = st.text_input("Email Address", placeholder="example@gmail.com")
    password = st.text_input("Password", type="password", placeholder="Enter password")
    
    if st.button("LOGIN NOW"):
        if email and password:
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state.user_data = res.user
                    st.success("සාර්ථකයි! ලොග් වෙනවා...")
                    st.rerun() # කෙලින්ම ඇතුළට අරන් යයි
            except Exception as e:
                st.error("Email හෝ Password වැරදියි!")
        else:
            st.warning("කරුණාකර විස්තර පුරවන්න.")
    
    st.markdown("---")
    st.write("ඔයාට Account එකක් නැද්ද? Supabase Dashboard එකෙන් User කෙනෙක් එකතු කරන්න.")

# --- ප්‍රධාන ඇප් එක ---
def show_app():
    # Sidebar එකේ පරණ චැට්
    with st.sidebar:
        st.image("logo.jpg", width=80)
        st.write(f"Logged as: {st.session_state.user_data.email}")
        
        if st.button("+ Start New Chat"):
            st.session_state.chat_history = []
            st.session_state.current_id = None
            st.rerun()
            
        st.markdown("---")
        st.subheader("Previous Chats")
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
    
    # Chat display
    for m in st.session_state.chat_history:
        if m["role"] != "system":
            with st.chat_message(m["role"], avatar=ai_avatar if m["role"] == "assistant" else None):
                st.markdown(m["content"])

    # Chat input
    if prompt := st.chat_input("Ask Honorgpt anything..."):
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
            
            # Database එකට සේව් කිරීම
            chat_title = prompt[:30]
            db_data = {"user_id": st.session_state.user_data.id, "messages": st.session_state.chat_history, "title": chat_title}
            if st.session_state.current_id:
                supabase.table("chats").update(db_data).eq("id", st.session_state.current_id).execute()
            else:
                res = supabase.table("chats").insert(db_data).execute()
                if res.data: st.session_state.current_id = res.data[0]["id"]

# තර්කනය (Logic)
if st.session_state.user_data is None:
    show_login()
else:
    show_app()
