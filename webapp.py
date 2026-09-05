import streamlit as st
from groq import Groq

# ==============================
# PAGE CONFIGURATION
# ==============================
st.set_page_config(
    page_title="Honorgpt",
    page_icon="logo.jpg",
    layout="centered"
)

# ==============================
# SESSION STATE
# ==============================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==============================
# CSS
# ==============================
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
    border-radius: 12px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# ==============================
# GROQ CLIENT
# ==============================
def get_groq_client():
    return Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )


# ==============================
# FREE FIRE OPTIMIZER
# ==============================
def free_fire_optimizer():

    st.markdown("## 🎮 Free Fire Device Optimizer")

    st.write(
        "ඔයාගේ phone model එක සහ RAM එක අනුව "
        "Free Fire සඳහා suitable settings recommend කරමු."
    )

    col1, col2 = st.columns(2)

    with col1:
        phone = st.text_input(
            "📱 Phone Model",
            placeholder="Ex: Honor X5b"
        )

    with col2:
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
        "💡 Resolution හෝ Refresh Rate වගේ technical details ඕන නැහැ."
    )

    st.write("")

    if st.button(
        "🚀 OPTIMIZE MY DEVICE",
        use_container_width=True
    ):

        if not phone.strip():
            st.warning("📱 Please enter your phone model.")
            return

        prompt = f"""
You are a responsible Free Fire Device Optimizer.

User device:
Phone Model: {phone}
RAM: {ram}
Game: {game}

Create a realistic and useful gaming optimization guide.

IMPORTANT RULES:

- Do NOT ask for screen resolution.
- Do NOT ask for refresh rate.
- Do NOT require technical specifications.
- If a specification is unknown, do not pretend it is known.
- Base recommendations mainly on phone model and RAM.
- Sensitivity values are recommendations, not guaranteed perfect values.
- Never promise automatic headshots.
- Never promise zero recoil.
- Never promise zero lag.

Give the result with these sections:

1. 📱 Device Performance
Classify the device as:
Low / Entry / Mid / High

Explain briefly.

2. 🎯 Free Fire Sensitivity

Give recommended values for:

- General
- Red Dot
- 2X Scope
- 4X Scope
- Sniper Scope
- Free Look

Use the current Free Fire sensitivity scale appropriately.

3. 🖱️ DPI

Give a reasonable DPI range.

Explain that DPI depends on touch preference and device display.

4. 🎨 Graphics & FPS

Recommend:

- Graphics
- High FPS
- Auto Scale

5. ⚙️ Android Developer Options

Only recommend useful and reasonably safe settings.

For every setting provide:

- Setting name
- Recommended value
- Short explanation

Do NOT recommend risky or unnecessary developer settings.

6. 🚀 Performance Optimization

Include:

- Background apps
- Battery
- Storage
- Heating
- RAM usage

7. 🌐 Network / Ping

Give simple tips for reducing connection-related lag.

8. 🎮 Gameplay Tip

Give a short tip explaining how the user can fine-tune sensitivity after testing.

Make the answer easy to read on a mobile phone.
"""

        with st.spinner("🔍 Analyzing device..."):

            try:

                client = get_groq_client()

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a responsible mobile gaming "
                                "optimization assistant."
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

                st.success("✅ Optimization Complete!")

                st.markdown(result)

            except Exception as e:

                st.error(
                    f"❌ Optimizer failed: {e}"
                )


# ==============================
# HONORGPT CHAT
# ==============================
def honorgpt_chat():

    st.markdown("## 🤖 Honorgpt")

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.chat_history = []

        st.rerun()

    # Show previous messages
    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):

            st.markdown(
                message["content"]
            )

    # Chat input
    prompt = st.chat_input(
        "Ask Honorgpt..."
    )

    if prompt:

        # Save user message
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": prompt
            }
        )

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

You can communicate in Sinhala and English.

Give clear, useful and honest answers.

Do not make up information.
"""
                    }
                ]

                messages.extend(
                    st.session_state.chat_history
                )

                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    stream=True
                )

                for chunk in stream:

                    if chunk.choices[0].delta.content:

                        full_response += (
                            chunk.choices[0].delta.content
                        )

                        placeholder.markdown(
                            full_response + "▌"
                        )

                placeholder.markdown(
                    full_response
                )

                # Save AI response
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": full_response
                    }
                )

            except Exception as e:

                st.error(
                    f"❌ AI connection failed: {e}"
                )


# ==============================
# LOGO
# ==============================
try:

    st.image(
        "logo.jpg",
        width=100
    )

except Exception:

    pass


# ==============================
# HEADER
# ==============================
st.markdown(
    "<h1 class='centered-title'>Honorgpt</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='subtitle'>AI Assistant • Free Fire Device Optimizer</p>",
    unsafe_allow_html=True
)


# ==============================
# TABS
# ==============================
tab1, tab2 = st.tabs(
    [
        "🤖 Honorgpt",
        "🎮 Free Fire Optimizer"
    ]
)


# Honorgpt
with tab1:

    honorgpt_chat()


# Free Fire Optimizer
with tab2:

    free_fire_optimizer()
