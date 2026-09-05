import streamlit as st
from groq import Groq

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Honorgpt",
    page_icon="🤖",
    layout="centered"
)

# =========================
# SESSION STATE
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================
# CSS
# =========================
st.markdown("""
<style>
.block-container {
    max-width: 850px;
    padding-top: 1.5rem;
    margin: auto;
}

.centered-title {
    text-align: center;
    font-size: 2.7rem;
    font-weight: bold;
    padding: 5px;
}

.subtitle {
    text-align: center;
    color: #999;
    margin-bottom: 25px;
}

.stButton > button {
    width: 100%;
    border-radius: 12px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# =========================
# GROQ
# =========================
def get_groq_client():
    return Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )


# =========================
# HONORGPT
# =========================
def honorgpt_chat():

    st.markdown("## 🤖 Honorgpt")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask Honorgpt...")

    if prompt:

        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            placeholder = st.empty()
            full_response = ""

            try:

                client = get_groq_client()

                messages = [
                    {
                        "role": "system",
                        "content": """
You are Honorgpt.

You are a helpful AI assistant.

You can communicate naturally in Sinhala and English.

Give clear, useful and honest answers.

Do not invent information.
"""
                    }
                ]

                messages.extend(
                    st.session_state.chat_history
                )

                stream = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=messages,
                    temperature=0.3,
                    stream=True
                )

                for chunk in stream:

                    if not chunk.choices:
                        continue

                    content = chunk.choices[0].delta.content

                    if content:

                        full_response += content

                        placeholder.markdown(
                            full_response + "▌"
                        )

                placeholder.markdown(
                    full_response
                )

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_response
                })

            except Exception as e:

                st.error(
                    f"❌ AI Error: {e}"
                )


# =========================
# FREE FIRE OPTIMIZER
# =========================
def free_fire_optimizer():

    st.markdown("## 🎮 Free Fire Device Optimizer")

    st.write(
        "ඔයාගේ phone model එක සහ RAM එක අනුව "
        "Free Fire settings recommend කරමු."
    )

    phone = st.text_input(
        "📱 Phone Model",
        placeholder="Example: Honor X5b"
    )

    ram = st.selectbox(
        "🧠 RAM",
        [
            "2 GB",
            "3 GB",
            "4 GB",
            "6 GB",
            "8 GB",
            "12 GB",
            "16 GB"
        ]
    )

    game = st.selectbox(
        "🎮 Game",
        [
            "Free Fire",
            "Free Fire MAX"
        ]
    )

    st.caption(
        "💡 Resolution, Refresh Rate හෝ Android version "
        "දැනගන්න අවශ්‍ය නැහැ."
    )

    if st.button(
        "🚀 OPTIMIZE MY DEVICE",
        use_container_width=True
    ):

        if not phone.strip():

            st.warning(
                "📱 Please enter your phone model."
            )

            return

        prompt = f"""
You are Honorgpt's Free Fire Device Optimizer.

Device:

Phone Model: {phone}
RAM: {ram}
Game: {game}

Create a realistic and useful optimization guide.

IMPORTANT:

- Do not ask for screen resolution.
- Do not ask for refresh rate.
- Do not require technical specifications.
- Do not invent unknown specifications.
- Base recommendations mainly on phone model and RAM.
- Sensitivity values are starting recommendations.
- Never promise automatic headshots.
- Never promise zero recoil.
- Never promise zero lag.

Give these sections:

1. 📱 DEVICE PERFORMANCE

Classify the device as:

Low / Entry / Mid / High

Explain briefly.

2. 🎯 FREE FIRE SENSITIVITY

Give values for:

General
Red Dot
2X Scope
4X Scope
Sniper Scope
Free Look

3. 🖱️ DPI

Give a reasonable DPI range.

Explain that DPI depends on touch preference and device.

4. 🎨 GRAPHICS & FPS

Recommend:

Graphics
High FPS
Auto Scale

5. ⚙️ ANDROID DEVELOPER OPTIONS

Only recommend useful and reasonably safe settings.

For each setting give:

Setting name
Recommended value
Short explanation

Do not recommend risky or unnecessary settings.

6. 🚀 PERFORMANCE OPTIMIZATION

Include:

Background apps
Battery
Storage
Heating
RAM usage

7. 🌐 NETWORK / PING

Give simple tips for connection-related lag.

8. 🎮 GAMEPLAY TUNING

Give a short tip for testing and adjusting sensitivity.

Make the answer clean and easy to read on a mobile phone.
"""

        with st.spinner("🔍 Analyzing device..."):

            try:

                client = get_groq_client()

                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a responsible "
                                "mobile gaming optimization assistant."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3
                )

                result = response.choices[0].message.content

                st.success(
                    "✅ Optimization Complete!"
                )

                st.markdown(result)

            except Exception as e:

                st.error(
                    f"❌ Optimizer Error: {e}"
                )


# =========================
# LOGO
# =========================
try:
    st.image("logo.jpg", width=100)
except Exception:
    pass


# =========================
# HEADER
# =========================
st.markdown(
    "<h1 class='centered-title'>Honorgpt</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='subtitle'>AI Assistant • Free Fire Optimizer</p>",
    unsafe_allow_html=True
)


# =========================
# TABS
# =========================
tab1, tab2 = st.tabs([
    "🤖 Honorgpt",
    "🎮 Free Fire Optimizer"
])

with tab1:
    honorgpt_chat()

with tab2:
    free_fire_optimizer()
