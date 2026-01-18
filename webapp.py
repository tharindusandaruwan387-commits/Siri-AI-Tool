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

# CSS
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
        # පළමු මැසේජ් එකෙන් කොටසක් මාතෘකාව ලෙස ගමු
        title_text = "New Chat"
        if len(st.session_state.messages) > 1:
            title_text = st.session_state.messages[1]["content"][:30]
            
        data = {
            "user_id": st.session_state.user.id,
            "messages": st.session_state.messages,
            "title": title_text
        }
        
        try:
            if st.session_state.current_chat_id:
                supabase.table("chats").update(data).eq("id", st.session_state.current_chat_id).execute()
            else:
                res = supabase.table("chats").insert(data).execute()
                if res.data:
                    st.session_state.current_chat_id = res.data[0]["id"]
        except Exception as e:
            pass # සේව් කිරීමේදී දෝෂයක් ආවොත් චැට් එකට බාධා නොකරයි

def load_chat(chat_id):
    res = supabase.table("chats").select("*").eq("id", chat_id).execute()
    if res.data:
        st.session_state.messages = res.data[0]["messages"]
        st.session_state.current_chat_id = chat_id

# --- AUTH PAGE ---
def auth_page():
    st.markdown("<h1 class='centered-title'>Honorgpt Access</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        e = st.text_input("Email", key="l_email")
        p = st.text_input("Password", type="password", key="l_pw")
        if st.button("Login Now", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                if res.user:
                    st.session_state.user = res.user
                    # JavaScript refresh එකකින් තොරව rerun කිරීම
                    st.rerun()
            except:
                st.error("Login වැරදියි! නැවත උත්සාහ කරන්න.")

    with tab2:
        ne = st.text_input("Email", key="s_email")
        np = st.text_input("Password", type="password", key="s_pw")
        if st.button("Create Account", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": ne, "password": np})
                st.success("Account එක හැදුනා! දැන් Login ටැබ් එකට ගිහින් ලොග් වෙන්න.")
            except:
                st.error("Signup Failed!")

# --- MAIN APP ---
def main_app():
    # SIDEBAR
    with st.sidebar:
        st.image("logo.jpg", width=80)
        st.write(f"Logged as: {st.session_state.user.email}")
        
        if st.button("+ New Chat"):
            st.session_state.messages = [{"role": "system", "content": "You are Honorgpt."}]
            st.session_state.current_chat_id = None
            st.rerun()
        
        st.markdown("---")
        st.subheader("Recent Chats")
        try:
            history = supabase.table("chats").select("id, title").eq("user_id", st.session_state.user.id).order("id", desc=True).execute()
            for chat in history.data:
                if st.button(f"💬 {chat['title']}", key=f"chat_{chat['id']}"):
                    load_chat(chat['id'])
                    st.rerun()
        except:
            st.write("No chats found.")
        
        st.markdown("---")
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

    # MAIN CHAT AREA
    st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)
    
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except:
        st.error("GROQ_API_KEY අඩුවක් තියෙනවා!")
        st.stop()

    if not st.session_state.messages:
        st.session_state.messages = [{"role": "system", "content": "You are Honorgpt."}]

    for m in st.session_state.messages:
        if m["role"] != "system":
            avatar = ai_avatar if m["role"] == "assistant" else None
            with st.chat_message(m["role"], avatar=avatar):
                st.markdown(m["content"])

    if prompt := st.chat_input("Ask Honorgpt..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=ai_avatar):
            res_box = st.empty()
            full_res = ""
            for chunk in client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages, stream=True):
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            save_chat_to_db()

if st.session_state.user is None:
    auth_page()
else:
    main_app()
