import streamlit as st
from groq import Groq
from supabase import create_client
import base64

# 1. Page Configuration
st.set_page_config(page_title="Honorgpt", page_icon="logo.jpg", layout="wide")

# Supabase සම්බන්ධ කිරීම
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Secrets Error! Please check SUPABASE_URL and SUPABASE_KEY.")
    st.stop()

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
    [data-testid="stToolbar"] > div:not(:first-child) {{ display: none !important; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stChatMessage"]:has([data-testid="user-avatar"]) {{
        flex-direction: row-reverse !important;
        text-align: right !important;
    }}
    .centered-title {{ text-align: center; padding: 10px; font-size: 2.5rem; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Session State එක පරීක්ෂා කිරීම
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- LOGIN / SIGNUP PAGE ---
def auth_page():
    st.markdown("<h1 class='centered-title'>Honorgpt Access</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email", key="login_email_input")
        password = st.text_input("Password", type="password", key="login_pw_input")
        if st.button("Login Now", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = res.user.email
                    st.rerun() # කෙලින්ම පිටුව අලුත් කරනවා
            except Exception as e:
                st.error(f"Login වැරදියි: {e}")

    with tab2:
        n_email = st.text_input("Email", key="signup_email_input")
        n_password = st.text_input("Password", type="password", key="signup_pw_input")
        if st.button("Create Account", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": n_email, "password": n_password})
                st.success("Account එක හැදුනා! දැන් Login ටැබ් එකට ගිහින් ලොග් වෙන්න.")
            except Exception as e:
                st.error(f"Signup Error: {e}")

# --- MAIN CHAT APP ---
def main_app():
    # Sidebar
    with st.sidebar:
        st.image("logo.jpg", width=100)
        st.write(f"Account: {st.session_state.user_email}")
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user_authenticated = False
            st.session_state.user_email = ""
            st.rerun()

    st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)

    # Groq AI එක සම්බන්ධ කිරීම
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except:
        st.error("GROQ_API_KEY එක Secrets වලට දාන්න!")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are Honorgpt, created by Tharindu Sandaruwan."}]

    # Chat පෙන්වීම
    for message in st.session_state.messages:
        if message["role"] != "system":
            avatar = ai_avatar if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask Honorgpt anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=ai_avatar):
            full_res = ""
            placeholder = st.empty()
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages,
                    stream=True
                )
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        placeholder.markdown(full_res + "▌")
                placeholder.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e:
                st.error(f"AI Error: {e}")

# පිටු අතර මාරු වීම (Control Logic)
if not st.session_state.user_authenticated:
    auth_page()
else:
    main_app()
