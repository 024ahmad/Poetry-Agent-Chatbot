from agents import Agent, Runner, trace
from dotenv import load_dotenv
from connection import config
import asyncio
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
import re
from audio_recorder_streamlit import audio_recorder

load_dotenv()

# ============================================
#      LANGUAGE DETECTION
# ============================================

LANG_MAP = {
    "urdu": "ur",
    "hindi": "hi",
    "arabic": "ar",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "turkish": "tr",
    "chinese": "zh-cn",
    "japanese": "ja",
    "korean": "ko",
    "english": "en"
}

def detect_language(user_text: str):
    text = (user_text or "").lower()
    for key in LANG_MAP.keys():
        if key in text:
            return LANG_MAP[key]
    return "en"   # default English


# ============================================
#                AGENTS
# ============================================

lyric_agent = Agent(
    name="Lyric Poetry Agent",
    instructions="""
    You write ORIGINAL lyric poems about emotions.
    Never repeat the user's text.
    """
)

narrative_agent = Agent(
    name="Narrative Poetry Agent",
    instructions="""
    You write ORIGINAL story-based narrative poetry.
    Never repeat the user's text.
    """
)

dramatic_agent = Agent(
    name="Dramatic Poetry Agent",
    instructions="""
    You write ORIGINAL dramatic/dialogue-style poetry.
    Never repeat the user's text.
    """
)

poet_parent_agent = Agent(
    name="Poetry Parent Agent",
    instructions="""
    Select correct agent:
    - Emotion → Lyric  
    - Story → Narrative  
    - Dialogue → Dramatic

    If the user asks for the result in a specific language — for example, ‘love story in Urdu’ — then generate the love story/poetry in that same requested language.

    ALWAYS generate a FRESH poem.
    NEVER repeat user's words.
    At END add: __AGENT__:Lyric / Narrative / Dramatic
    """,
    handoffs=[lyric_agent, narrative_agent, dramatic_agent]
)


# ============================================
#          POETRY RUNNER
# ============================================

async def run_poetry_agent(user_input):

    user_input = (user_input or "").strip()

    wrapper = (
        "Write an ORIGINAL poem based on this topic.\n"
        "Do NOT repeat the user's text.\n"
        "Write 6–18 beautiful poetic lines.\n"
        "At the end append: __AGENT__:<AgentName>\n\n"
        f"USER TOPIC: {user_input}\n\n"
        "Now write the poem:"
    )

    with trace("Poetry Agent"):
        return await Runner.run(poet_parent_agent, wrapper, run_config=config)


# ============================================
#        SPEECH → TEXT
# ============================================

def speech_to_text_from_bytes(wav_bytes):
    recognizer = sr.Recognizer()
    try:
        audio_file = io.BytesIO(wav_bytes)
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        return recognizer.recognize_google(audio, language="en-US")
    except Exception as e:
        st.error(f"Speech-To-Text Error: {e}")
        return None


# ============================================
#        TEXT → MP3 AUDIO
# ============================================

def text_to_speech(text, lang_code="en"):
    try:
        tts = gTTS(text=text, lang=lang_code)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Audio Error: {e}")
        return None


# ============================================
#              UI + CSS
# ============================================

st.set_page_config(page_title="AI Poetry Generator Pro", page_icon="🎭", layout="centered")

st.markdown("""
<style>

.main-header {
    font-size: 3.5em;
    text-align: center;
    font-weight: 800;
    background: linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-header {
    text-align: center;
    font-size: 1.2em;
    color: #6c757d;
    margin-bottom: 2em;
}

.section-header {
    font-size: 1.6em;
    font-weight: 600;
    margin-bottom: 0.8em;
    border-bottom: 2px solid #e9ecef;
    padding-bottom: 0.4em;
}

.poem-box {
    background: #f8f9fa;
    border-left: 4px solid #667eea;
    padding: 1.5em;
    border-radius: 8px;
    font-style: italic;
    line-height: 1.6;
    margin-top: 1em;
}

/* ✅ NEW PREMIUM GENERATE BUTTON */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #6a5af9, #8854d0);
    color: white;
    border: none;
    padding: 0.9em 2.2em;
    font-size: 1.1em;
    font-weight: bold;
    border-radius: 12px;
    transition: 0.3s ease-in-out;
    box-shadow: 0px 4px 12px rgba(120, 80, 220, 0.4);
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #7d6bff, #9b63ff);
    transform: scale(1.07);
    box-shadow: 0px 6px 16px rgba(120, 80, 220, 0.7);
    cursor: pointer;
}

</style>
""", unsafe_allow_html=True)


# ============================================
#            SESSION STATE
# ============================================

if "final_input" not in st.session_state:
    st.session_state.final_input = ""

if "poetry_result" not in st.session_state:
    st.session_state.poetry_result = None

if "text_input_key" not in st.session_state:
    st.session_state.text_input_key = ""


# ============================================
#              HEADER
# ============================================

st.markdown("<div class='main-header'>AI Poetry Generator Pro</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Create Beautiful Poetry with Voice & Text • Powered by AI Agents</div>", unsafe_allow_html=True)


# ============================================
#            VOICE INPUT
# ============================================

st.markdown("<div class='section-header'>🎤 Voice Input</div>", unsafe_allow_html=True)

wav_audio = audio_recorder(text="Click to Record", icon_size="3x")

if wav_audio:
    st.success("✅ Voice Recorded!")
    text = speech_to_text_from_bytes(wav_audio)

    if text:
        st.success(f"🎙 Recognized Text: **{text}**")
        st.session_state.final_input = text
        st.session_state.text_input_key = text


# ✅ CLEAR BUTTON
if st.button("🗑️ Clear Voice Input"):
    st.session_state.final_input = ""
    st.session_state.text_input_key = ""
    st.session_state.poetry_result = None
    st.rerun()


# ============================================
#              TEXT INPUT
# ============================================

st.markdown("<div class='section-header'>📝 Text Input</div>", unsafe_allow_html=True)

user_input = st.text_area(
    "Enter topic:",
    value=st.session_state.text_input_key,
    key="text_input_key",
    height=120,
    placeholder="Example: love poetry, urdu me dosti ki poetry, arabic poem..."
)

st.session_state.final_input = user_input


# ============================================
#           GENERATE POETRY
# ============================================

st.markdown("<div class='section-header'>⚡ Generate Poetry</div>", unsafe_allow_html=True)

col1, col2 = st.columns([2,2])

with col1:
    generate_clicked = st.button("🚀 Generate Poetry")

with col2:
    enable_voice = st.checkbox("🔊 Voice Output", value=True)


if generate_clicked:

    topic = st.session_state.final_input.strip()

    if not topic:
        st.warning("⚠ Please enter a topic first.")

    else:
        # ✅ detect language
        lang_code = detect_language(topic)

        with st.spinner("✨ Crafting your poem..."):
            try:
                poetry_result = asyncio.run(run_poetry_agent(topic))
                st.session_state.poetry_result = poetry_result

                poem_text = poetry_result.final_output or ""

                # ✅ extract agent name
                agent_name = "Unknown"
                m = re.search(r"__AGENT__\s*:\s*([A-Za-z]+)", poem_text)
                if m:
                    agent_name = m.group(1)
                    poem_text = re.sub(r"__AGENT__\s*:\s*[A-Za-z]+", "", poem_text).strip()

                st.markdown(f"<div class='poem-box'>{poem_text}</div>", unsafe_allow_html=True)
                st.write(f"🤖 Generated by: `{agent_name}`")

                # ✅ audio output (correct language)
                if enable_voice:
                    audio_buf = text_to_speech(poem_text, lang_code)
                    if audio_buf:
                        st.audio(audio_buf, format="audio/mp3")
                        st.download_button("📥 Download MP3", audio_buf.getvalue(), "poem.mp3", "audio/mp3")

            except Exception as e:
                st.error(f"Error: {e}")


# ============================================
#           PREVIOUS POEM
# ============================================

if st.session_state.poetry_result:
    st.markdown("---")
    st.markdown("### 📖 Previous Poem")
    st.markdown(
        f"<div class='poem-box'>{st.session_state.poetry_result.final_output}</div>",
        unsafe_allow_html=True
    )
