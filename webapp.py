import streamlit as st
from groq import Groq
import base64

# 1. Page Configuration
st.set_page_config(page_title="Honorgpt Login", page_icon="logo.jpg", layout="centered")

# --- සරල Password එක මෙතැනදී වෙනස් කරන්න ---
CORRECT_PASSWORD = "admin" 

# පසුව පාවිච්චි කිරීමට Session State එක හදමු
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ලොගින් පේජ් එක පෙන්වීම
def login_page():
    st.markdown("<h1 style='text-align: center;'>Honorgpt Login</h1>", unsafe_allow_html=True)
    st.image("logo.jpg", width=200, use_container_width=False)
    
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("වැරදි Password එකක්! නැවත උත්සාහ කරන්න.")

# ඇප් එකේ ප්‍රධාන කොටස (Login වුණාට පස්සේ පේන කොටස)
def main_app():
    # මෙතැනදී layout එක 'wide' වලට මාරු කරනවා Chat එකට පහසු වෙන්න
    st.markdown("""<style>[data-testid="stSidebarNav"] {display: none;}</style>""", unsafe_allow_html=True)
    
    # Avatar එක සඳහා ලෝගෝ එක Base64 වලට හැරවීම
    def get_base64_image(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return None

    img_data = get_base64_image("logo.jpg")
    ai_avatar = f"data:image/jpeg;base64,{img_data}" if img_data else "🤖"

    # UI එක පිරිසිදු කරන CSS
    st.markdown(f"""
        <style>
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        .stDeployButton {{ display:none; }}
        [data-testid="stToolbar"] > div:not(:first-child) {{ display: none !important; }}
        header[data-testid="stHeader"] {{ background: transparent !important; visibility: visible !important; }}
        .centered-title {{ text-align: center; padding: 10px; color: white; font-size: 2.5rem; font-weight: bold; }}
        </style>
        """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("logo.jpg", width=150)
        st.title("Honorgpt Settings")
        st.write("Created by Tharindu")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    st.markdown("<h1 class='centered-title'>Honorgpt</h1>", unsafe_allow_html=True)

    # AI Logic
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except:
        st.error("Secrets වල GROQ_API_KEY එක දාන්න!")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are Honorgpt, created by Tharindu Sandaruwan."}]

    for message in st.session_state.messages:
        if message["role"] != "system":
            avatar = ai_avatar if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=ai_avatar):
            response_placeholder = st.empty()
            full_response = ""
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True,
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# සත්‍යාපනය වී ඇත්දැයි පරීක්ෂා කිරීම
if not st.session_state.authenticated:
    login_page()
else:
    main_app()
