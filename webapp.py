import streamlit as st
from groq import Groq

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Honorgpt",
    page_icon="🤖",
    layout="centered"
)


# =========================================
# SESSION STATE
# =========================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================================
# DEVICE DATABASE
# =========================================
# Sensitivity values are fixed starting
# presets. AI does NOT generate these values.

DEVICE_DATABASE = {

    "honor x5b": {

        "2 GB": {
            "general": 180,
            "red_dot": 175,
            "2x": 165,
            "4x": 155,
            "sniper": 90,
            "free_look": 130,
            "dpi": "420-460"
        },

        "3 GB": {
            "general": 185,
            "red_dot": 180,
            "2x": 170,
            "4x": 160,
            "sniper": 95,
            "free_look": 135,
            "dpi": "430-470"
        },

        "4 GB": {
            "general": 190,
            "red_dot": 185,
            "2x": 175,
            "4x": 165,
            "sniper": 100,
            "free_look": 140,
            "dpi": "440-480"
        },

        "6 GB": {
            "general": 195,
            "red_dot": 190,
            "2x": 180,
            "4x": 170,
            "sniper": 105,
            "free_look": 145,
            "dpi": "450-490"
        },

        "8 GB": {
            "general": 195,
            "red_dot": 190,
            "2x": 180,
            "4x": 170,
            "sniper": 110,
            "free_look": 150,
            "dpi": "450-500"
        }
    },


    "redmi 12": {

        "4 GB": {
            "general": 185,
            "red_dot": 180,
            "2x": 170,
            "4x": 160,
            "sniper": 100,
            "free_look": 140,
            "dpi": "430-480"
        },

        "6 GB": {
            "general": 190,
            "red_dot": 185,
            "2x": 175,
            "4x": 165,
            "sniper": 105,
            "free_look": 145,
            "dpi": "440-490"
        },

        "8 GB": {
            "general": 195,
            "red_dot": 190,
            "2x": 180,
            "4x": 170,
            "sniper": 110,
            "free_look": 150,
            "dpi": "450-500"
        }
    },


    "redmi 13c": {

        "4 GB": {
            "general": 185,
            "red_dot": 180,
            "2x": 170,
            "4x": 160,
            "sniper": 95,
            "free_look": 140,
            "dpi": "430-480"
        },

        "6 GB": {
            "general": 190,
            "red_dot": 185,
            "2x": 175,
            "4x": 165,
            "sniper": 100,
            "free_look": 145,
            "dpi": "440-490"
        },

        "8 GB": {
            "general": 195,
            "red_dot": 190,
            "2x": 180,
            "4x": 170,
            "sniper": 105,
            "free_look": 150,
            "dpi": "450-500"
        }
    },


    "samsung galaxy a05": {

        "4 GB": {
            "general": 180,
            "red_dot": 175,
            "2x": 165,
            "4x": 155,
            "sniper": 95,
            "free_look": 135,
            "dpi": "420-470"
        },

        "6 GB": {
            "general": 190,
            "red_dot": 185,
            "2x": 175,
            "4x": 165,
            "sniper": 100,
            "free_look": 145,
            "dpi": "440-490"
        }
    },


    "samsung galaxy a15": {

        "4 GB": {
            "general": 185,
            "red_dot": 180,
            "2x": 170,
            "4x": 160,
            "sniper": 100,
            "free_look": 140,
            "dpi": "430-480"
        },

        "6 GB": {
            "general": 190,
            "red_dot": 185,
            "2x": 175,
            "4x": 165,
            "sniper": 105,
            "free_look": 145,
            "dpi": "440-490"
        },

        "8 GB": {
            "general": 195,
            "red_dot": 190,
            "2x": 180,
            "4x": 170,
            "sniper": 110,
            "free_look": 150,
            "dpi": "450-500"
        }
    }
}


# =========================================
# RAM FALLBACK DATABASE
# =========================================

RAM_DATABASE = {

    "2 GB": {
        "general": 175,
        "red_dot": 170,
        "2x": 160,
        "4x": 150,
        "sniper": 85,
        "free_look": 125,
        "dpi": "400-450"
    },

    "3 GB": {
        "general": 180,
        "red_dot": 175,
        "2x": 165,
        "4x": 155,
        "sniper": 90,
        "free_look": 130,
        "dpi": "420-460"
    },

    "4 GB": {
        "general": 185,
        "red_dot": 180,
        "2x": 170,
        "4x": 160,
        "sniper": 95,
        "free_look": 135,
        "dpi": "430-480"
    },

    "6 GB": {
        "general": 190,
        "red_dot": 185,
        "2x": 175,
        "4x": 165,
        "sniper": 100,
        "free_look": 140,
        "dpi": "440-490"
    },

    "8 GB": {
        "general": 195,
        "red_dot": 190,
        "2x": 180,
        "4x": 170,
        "sniper": 105,
        "free_look": 145,
        "dpi": "450-500"
    },

    "12 GB": {
        "general": 195,
        "red_dot": 190,
        "2x": 180,
        "4x": 170,
        "sniper": 110,
        "free_look": 150,
        "dpi": "450-500"
    },

    "16 GB": {
        "general": 200,
        "red_dot": 195,
        "2x": 185,
        "4x": 175,
        "sniper": 115,
        "free_look": 155,
        "dpi": "460-520"
    }
}


# =========================================
# GROQ
# =========================================

def get_groq_client():

    return Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )


# =========================================
# FIND DEVICE
# =========================================

def get_device_settings(phone, ram):

    phone_key = phone.strip().lower()

    if phone_key in DEVICE_DATABASE:

        phone_data = DEVICE_DATABASE[phone_key]

        if ram in phone_data:

            return phone_data[ram], True

    return RAM_DATABASE[ram], False


# =========================================
# HONORGPT
# =========================================

def honorgpt_chat():

    # Title + small clear button
    col1, col2 = st.columns([8, 1])

    with col1:

        st.markdown(
            "## 🤖 Honorgpt"
        )

    with col2:

        if st.button(
            "🗑️",
            help="Clear chat"
        ):

            st.session_state.chat_history = []

            st.rerun()


    # Chat messages
    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # IMPORTANT:
    # Streamlit keeps chat input at the bottom.
    prompt = st.chat_input(
        "Message Honorgpt..."
    )


    if not prompt:

        return


    # User message
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    with st.chat_message("user"):

        st.markdown(prompt)


    # AI response
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


                content = (
                    chunk.choices[0]
                    .delta
                    .content
                )


                if content:

                    full_response += content

                    placeholder.markdown(
                        full_response + "▌"
                    )


            placeholder.markdown(
                full_response
            )


            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )


        except Exception as e:

            st.error(
                f"❌ AI Error: {e}"
            )


# =========================================
# FREE FIRE OPTIMIZER
# =========================================

def free_fire_optimizer():

    st.markdown(
        "## 🎮 Free Fire Device Optimizer"
    )

    st.write(
        "Phone Model + RAM + Game select කරලා "
        "device preset එක ලබාගන්න."
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
        "Resolution, Refresh Rate හෝ Android version "
        "අවශ්‍ය නැහැ."
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


        settings, exact = get_device_settings(
            phone,
            ram
        )


        # =====================================
        # RESULT
        # =====================================

        st.success(
            "✅ Optimization Complete!"
        )


        st.markdown(
            "### 📱 Device Information"
        )


        st.write(
            f"**Phone:** {phone.strip()}"
        )

        st.write(
            f"**RAM:** {ram}"
        )

        st.write(
            f"**Game:** {game}"
        )


        if exact:

            st.info(
                "🎯 Exact device preset found."
            )

        else:

            st.info(
                "ℹ️ Phone preset not found. "
                "RAM-based preset used."
            )


        # =====================================
        # SENSITIVITY
        # =====================================

        st.markdown(
            "### 🎯 Recommended Sensitivity"
        )


        st.markdown(
            f"""
| Setting | Value |
|---|---:|
| General | **{settings["general"]}** |
| Red Dot | **{settings["red_dot"]}** |
| 2X Scope | **{settings["2x"]}** |
| 4X Scope | **{settings["4x"]}** |
| Sniper Scope | **{settings["sniper"]}** |
| Free Look | **{settings["free_look"]}** |
"""
        )


        st.caption(
            "🎯 These numbers come directly from the "
            "device database. They are starting presets, "
            "not guaranteed perfect values."
        )


        # =====================================
        # DPI
        # =====================================

        st.markdown(
            "### 🖱️ DPI"
        )


        st.write(
            f"**Recommended starting range:** "
            f"{settings['dpi']}"
        )


        st.caption(
            "DPI එක වෙනස් කිරීම optional. Touch feeling "
            "අනුව fine-tune කරන්න."
        )


        # =====================================
        # GRAPHICS
        # =====================================

        st.markdown(
            "### 🎨 Graphics & FPS"
        )


        if ram in [
            "2 GB",
            "3 GB",
            "4 GB"
        ]:

            st.write(
                "**Graphics:** Smooth / Low"
            )

            st.write(
                "**High FPS:** ON if stable"
            )

            st.write(
                "**Auto Scale:** OFF"
            )

        else:

            st.write(
                "**Graphics:** Smooth / Standard"
            )

            st.write(
                "**High FPS:** ON"
            )

            st.write(
                "**Auto Scale:** OFF"
            )


        # =====================================
        # PERFORMANCE
        # =====================================

        st.markdown(
            "### 🚀 Performance"
        )


        st.write(
            "• Game එක open කිරීමට කලින් "
            "unnecessary background apps close කරන්න."
        )

        st.write(
            "• Phone එක වැඩිපුර උණු වුණොත් break එකක් ගන්න."
        )

        st.write(
            "• Storage එකේ free space තියාගන්න."
        )

        st.write(
            "• Gaming වෙලාවේ Battery Saver off කරලා බලන්න."
        )

        st.write(
            "• Background downloads / updates නවත්වන්න."
        )


        # =====================================
        # DEVELOPER OPTIONS
        # =====================================

        st.markdown(
            "### ⚙️ Developer Options"
        )


        st.write(
            "**Window animation scale:** 0.5x"
        )

        st.write(
            "**Transition animation scale:** 0.5x"
        )

        st.write(
            "**Animator duration scale:** 0.5x"
        )


        st.caption(
            "මේවා UI animations වේගවත් කරන optional settings."
        )


        # =====================================
        # NETWORK
        # =====================================

        st.markdown(
            "### 🌐 Network / Ping"
        )


        st.write(
            "• Stable Wi-Fi හෝ strong mobile signal use කරන්න."
        )

        st.write(
            "• Background downloads නවත්වන්න."
        )

        st.write(
            "• Unnecessary VPN use නොකරන්න."
        )

        st.write(
            "• High ping එක sensitivity settings "
            "වලින් fix කරන්න බැහැ."
        )


        # =====================================
        # GAMEPLAY
        # =====================================

        st.markdown(
            "### 🎮 Gameplay Tip"
        )


        st.write(
            "මේ sensitivity values starting point එකක් "
            "විදිහට use කරන්න."
        )

        st.write(
            "Aim එක target එක පහුකරනවා නම් "
            "General/Red Dot ටිකක් අඩු කරන්න."
        )

        st.write(
            "Aim එක slow නම් General/Red Dot ටිකක් වැඩි කරන්න."
        )


# =========================================
# LOGO
# =========================================

try:

    st.image(
        "logo.jpg",
        width=100
    )

except Exception:

    pass


# =========================================
# HEADER
# =========================================

st.markdown(
    "<h1 class='centered-title'>Honorgpt</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='subtitle'>AI Assistant • Free Fire Device Optimizer</p>",
    unsafe_allow_html=True
)


# =========================================
# TABS
# =========================================

tab1, tab2 = st.tabs(
    [
        "🤖 Honorgpt",
        "🎮 Free Fire Optimizer"
    ]
)


with tab1:

    honorgpt_chat()


with tab2:

    free_fire_optimizer()
