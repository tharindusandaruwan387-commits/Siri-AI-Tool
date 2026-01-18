import streamlit as st
from groq import Groq
from supabase import create_client
import base64

# 1. Page Configuration - layout="wide" අයින් කර ඇති නිසා ස්වයංක්‍රීයව මැදට පෙන්වයි
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

# ලෝගෝ එක Base64 වලට හැරවීම
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

img_data = get_base64_image("logo.jpg")
ai_avatar = f"data:image/jpeg;base64,{img_data}" if img_data else "🤖"

# CSS - මැදට පෙනීම (Centered) සහ අතුරුමුහුණතේ ලස්සන සඳහා
st.markdown("""
    <style>
    /* ඇප් එකේ අන්තර්ගතය මැදට පෙන්වීමට */
    .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        margin: auto;
    }
    .centered-title { text-align: center; font-size: 2.5rem; font-weight: bold; padding: 20px; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 12px; height: 50px; background-color: #00a884; color: white; font-weight: bold; border: none; }
    div[data-testid="stTextInput"] > div > div > input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ලොගින් පේජ් එක ---
def show_login():
    st.markdown("<h1 class='centered-title'>Honorgpt Login</h1>", unsafe_allow_html=True)
    
    email = st.text_input("Email Address", placeholder="Enter your email")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("LOGIN NOW"):
        if email and password:
            try:
                # ලොගින් වීම පරීක්ෂා කිරීම
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state.user_data = res.user
                    st.success("සාර්ථකයි! ඇතුළු වෙනවා...")
                    st.rerun() # එක පාරින්ම චැට් එකට යයි
            except Exception:
                st.error("Email හෝ Password වැරදියි!")
        else:
            st.warning("කරුණාකර සියලු විස්තර පුරවන්න.")

# --- ප්‍රධාන ඇප් එක ---
def show_app():
    # Sidebar සැකසුම
    with st.sidebar:
        st.image("logo.jpg", width=80)
        st.write(f"User: {st.session_state.user_data.email}")
        
        if st.button("+ New Chat"):
            st.session_state.chat_history = []
            st.session_state.current_id = None
            st.rerun()
            
        st.markdown("---")
        st.subheader("Recent Chats")
        try:
            # පරණ චැට් ලිස්ට් එක Database එකෙන් ලබා ගැනීම
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
    
    # පරණ මැසේජ් පෙන්වීම
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
            # AI පිළිතුර ලබා ගැනීම
            for chunk in client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.chat_history, stream=True):
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})
            
            # Database එකට චැට් එක සේව් කිරීම
            chat_title = prompt[:30]
            db_data = {"user_id": st.session_state.user_data.id, "messages": st.session_state.chat_history, "title": chat_title}
            if st.session_state.current_id:
                supabase.table("chats").update(db_data).eq("id", st.session_state.current_id).execute()
            else:
                db_res = supabase.table("chats").insert(db_data).execute()
                if db_res.data: st.session_state.current_id = db_res.data[0]["id"]

# Main Logic
if st.session_state.user_data is None:
    show_login()
else:
    show_app()
