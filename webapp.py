import streamlit as st
from groq import Groq
from supabase import create_client
import base64

# 1. Page Configuration
st.set_page_config(
    page_title="Honorgpt",
    page_icon="logo.jpg"
)

# Supabase සම්බන්ධ කිරීම
@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = init_supabase()

# Session State
if "user_data" not in st.session_state:
    st.session_state.user_data = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_id" not in st.session_state:
    st.session_state.current_id = None


# =========================================================
# ADMIN LOGIN
# =========================================================

def handle_login():

    email = st.session_state.get("auth_email", "").strip()
    password = st.session_state.get("auth_pw", "")

    if not email or not password:
        st.error("Please enter Email and Password.")
        return

    # Admin credentials are stored in Streamlit Secrets
    admin_email = st.secrets["ADMIN_EMAIL"]
    admin_password = st.secrets["ADMIN_PASSWORD"]

    # Check Admin credentials first
    if email != admin_email or password != admin_password:
        st.error("❌ Access Denied. Admin account only.")
        return

    # Login to Supabase
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if res.user:
            st.session_state.user_data = res.user
            st.success("✅ Login successful!")
            st.rerun()

    except Exception as e:
        st.error("❌ Login failed. Check your Admin credentials.")


# =========================================================
# LOGO
# =========================================================

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None


img_data = get_base64_image("logo.jpg")

if img_data:
    ai_avatar = f"data:image/jpeg;base64,{img_data}"
else:
    ai_avatar = "🤖"


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    max-width: 800px;
    padding-top: 2rem;
    margin: auto;
}

.centered-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: bold;
    padding: 20px;
}

.stButton>button {
    width: 100%;
    border-radius: 12px;
    height: 50px;
    background-color: transparent;
    color: white;
    font-weight: bold;
    border: 2px solid #555;
}

.stButton>button:hover {
    border-color: #00a884;
    color: #00a884;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# AUTH PAGE
# =========================================================

def show_auth():

    st.markdown(
        "<h1 class='centered-title'>Honorgpt Access</h1>",
        unsafe_allow_html=True
    )

    st.info("🔐 Admin access only")

    st.text_input(
        "Admin Email",
        key="auth_email"
    )

    st.text_input(
        "Password",
        type="password",
        key="auth_pw"
    )

    st.write("")

    st.button(
        "LOGIN NOW",
        on_click=handle_login
    )


# =========================================================
# MAIN APP
# =========================================================

def show_app():

    with st.sidebar:

        st.image("logo.jpg", width=80)

        st.write(
            f"Admin: {st.session_state.user_data.email}"
        )

        if st.button("+ New Chat"):

            st.session_state.chat_history = []
            st.session_state.current_id = None

            st.rerun()

        st.markdown("---")

        # Load saved chats
        try:

            res = (
                supabase
                .table("chats")
                .select("id, title")
                .eq(
                    "user_id",
                    st.session_state.user_data.id
                )
                .order("id", desc=True)
                .execute()
            )

            for chat in res.data:

                if st.button(
                    f"💬 {chat['title']}",
                    key=f"c_{chat['id']}"
                ):

                    chat_data = (
                        supabase
                        .table("chats")
                        .select("*")
                        .eq("id", chat["id"])
                        .execute()
                    )

                    if chat_data.data:

                        st.session_state.chat_history = (
                            chat_data.data[0]["messages"]
                        )

                        st.session_state.current_id = chat["id"]

                        st.rerun()

        except Exception:
            pass

        st.markdown("---")

        if st.button("Logout"):

            supabase.auth.sign_out()

            st.session_state.user_data = None
            st.session_state.chat_history = []
            st.session_state.current_id = None

            st.rerun()


    # =====================================================
    # HONORGPT
    # =====================================================

    st.markdown(
        "<h1 class='centered-title'>Honorgpt</h1>",
        unsafe_allow_html=True
    )


    # Display previous messages
    for m in st.session_state.chat_history:

        if m["role"] != "system":

            with st.chat_message(
                m["role"],
                avatar=(
                    ai_avatar
                    if m["role"] == "assistant"
                    else None
                )
            ):

                st.markdown(m["content"])


    # =====================================================
    # CHAT
    # =====================================================

    if prompt := st.chat_input("Ask Honorgpt..."):

        if not st.session_state.chat_history:

            st.session_state.chat_history.append({
                "role": "system",
                "content": "You are Honorgpt."
            })


        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })


        with st.chat_message("user"):
            st.markdown(prompt)


        with st.chat_message(
            "assistant",
            avatar=ai_avatar
        ):

            full_res = ""

            placeholder = st.empty()

            client = Groq(
                api_key=st.secrets["GROQ_API_KEY"]
            )

            for chunk in client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                messages=st.session_state.chat_history,

                stream=True

            ):

                if chunk.choices[0].delta.content:

                    full_res += (
                        chunk.choices[0].delta.content
                    )

                    placeholder.markdown(
                        full_res + "▌"
                    )


            placeholder.markdown(full_res)


            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full_res
            })


            # =================================================
            # SAVE CHAT TO DATABASE
            # =================================================

            db_data = {

                "user_id":
                    st.session_state.user_data.id,

                "messages":
                    st.session_state.chat_history,

                "title":
                    prompt[:30]
            }


            if st.session_state.current_id:

                (
                    supabase
                    .table("chats")
                    .update(db_data)
                    .eq(
                        "id",
                        st.session_state.current_id
                    )
                    .execute()
                )

            else:

                db_res = (
                    supabase
                    .table("chats")
                    .insert(db_data)
                    .execute()
                )

                if db_res.data:

                    st.session_state.current_id = (
                        db_res.data[0]["id"]
                    )


# =========================================================
# MAIN EXECUTION
# =========================================================

if st.session_state.user_data is None:

    show_auth()

else:

    show_app()
