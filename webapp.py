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
    font-weight: 700;
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
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# =========================
# GROQ CLIENT
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

    # Show chat history
    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask Honorgpt...")

    if not prompt:
        return

    # User message
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # AI message
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

If you do not know something, say that you are not sure.
Do not invent facts.
"""
                }
            ]

            messages.extend(
                st.session_state.chat_history
            )

            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
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

            placeholder.markdown(full_response)

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
        "Phone model, RAM සහ game එක අනුව "
        "gaming settings recommend කරමු."
    )

    # Phone
    phone = st.text_input(
        "📱 Phone Model",
        placeholder="Example: Honor X5b"
    )

    # RAM
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

    # Game
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

        optimizer_prompt = f"""
You are Honorgpt's Free Fire Device Optimizer.

User device:

Phone Model: {phone}
RAM: {ram}
Game: {game}

Create a realistic gaming optimization guide.

IMPORTANT:

1. Do not ask for screen resolution.
2. Do not ask for refresh rate.
3. Do not require technical specifications.
4. Do not invent unknown phone specifications.
5. Recommendations should mainly depend on phone model and RAM.
6. Sensitivity values are starting recommendations only.
7. Never promise automatic headshots.
8. Never promise zero recoil.
9. Never promise zero lag.
10. Keep the answer easy to understand on a phone.

Give these sections:

📱 1. DEVICE PERFORMANCE

Classify the device:

Low / Entry / Mid / High

Give a short explanation.

🎯 2. FREE FIRE SENSITIVITY

Give recommended values for:

General
Red Dot
2X Scope
4X Scope
Sniper Scope
Free Look

Use the current Free Fire sensitivity scale appropriately.

🖱️ 3. DPI

Give a reasonable DPI range.

Explain that DPI depends on touch preference and device.

🎨 4. GRAPHICS & FPS

Recommend:

Graphics
High FPS
Auto Scale

⚙️ 5. ANDROID DEVELOPER OPTIONS

Only recommend useful and reasonably safe settings.

For each setting provide:

Setting name
Recommended value
Short explanation

Do not recommend risky or unnecessary developer settings.

🚀 6. PERFORMANCE OPTIMIZATION

Explain:

Background apps
Battery
Storage
Heating
RAM usage

🌐 7. NETWORK / PING

Give simple tips for connection-related lag.

🎮 8. GAMEPLAY TUNING

Give a short tip for testing and adjusting sensitivity.

Make the final answer clean and mobile-friendly.
"""

        with st.spinner("🔍 Analyzing your device..."):

            try:

                client = get_groq_client()

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
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
                            "content": optimizer_prompt
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
# HEADER / LOGO
# =========================
try:
    st.image("logo.jpg", width=100)
except Exception:
    pass

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
