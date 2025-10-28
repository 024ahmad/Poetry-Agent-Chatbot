from agents import Agent, Runner, trace
from dotenv import load_dotenv
from connection import config
import asyncio
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os

load_dotenv()

# 🎭 Sub-agents
lyric_agent = Agent(
    name="Lyric Poetry Agent",
    instructions="""
    You are a lyric poetry agent. Write short, emotional poems that express personal feelings like love, longing, loneliness, or joy. Focus on mood, not story. Use soft, expressive, and vivid language.
    """
)

narrative_agent = Agent(
    name="Narrative Poetry Agent",
    instructions="""
    You are a narrative poetry agent. Create poems that tell complete stories with characters, setting, and plot. Use a storytelling tone, and maintain poetic rhythm and flow.
    """
)

dramatic_agent = Agent(
    name="Dramatic Poetry Agent",
    instructions="""
    You are a dramatic poetry agent. Write dialogue-driven poems where characters express emotions and conflicts. Style it like a scene from a play, with intensity and expression.
    """
)

# 🤖 Parent agent
poet_parent_agent = Agent(
    name="Poetry Parent Agent",
    instructions="""
    You are a poetry coordinator agent. Your role is to understand the user's input and decide whether it needs a lyric, narrative, or dramatic poem. 
    Use handoffs to delegate the task to the appropriate sub-agent based on the user's tone, emotion, or storytelling need.

    If the user's request is short (e.g., just a few words like "sad poetry", "love", "betrayal"), **do not ask questions**. 
    Instead, intelligently infer the intent:
    - If it involves emotions or moods, hand off to the Lyric Poetry Agent.
    - If it mentions characters, events, or storytelling, hand off to the Narrative Poetry Agent.
    - If it sounds like a scene or dialogue, hand off to the Dramatic Poetry Agent.

    Avoid asking clarifying questions unless the request is completely unrelated to poetry.
    Always return a poem matching the user's style or tone.
    """,
    handoffs=[lyric_agent, narrative_agent, dramatic_agent]
)

# 🔄 Async runner function
async def run_poetry_agent(user_input):
    with trace("Poetry Agent"):
        result = await Runner.run(
            poet_parent_agent,
            user_input,
            run_config=config
        )
        return result

# 🎤 Voice Recognition Function
def speech_to_text():
    """Convert voice to text"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        st.info("🎤 **Listening...** Please start speaking now")
        recognizer.adjust_for_ambient_noise(source)
        
        try:
            audio = recognizer.listen(source, timeout=10)
            st.success("✅ **Voice captured!** Processing your request...")
            
            text = recognizer.recognize_google(audio, language='en-US')
            return text
            
        except sr.WaitTimeoutError:
            st.error("⏰ **Timeout!** Please try again")
            return None
        except sr.UnknownValueError:
            st.error("❌ **Speech not recognized.** Please try again")
            return None
        except Exception as e:
            st.error(f"❌ **Error:** {e}")
            return None

# 🔊 Text-to-Speech Function
def text_to_speech(text, language='en'):
    """Convert text to voice"""
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
            
    except Exception as e:
        st.error(f"**Voice generation error:** {e}")
        return None

# 🌐 Streamlit UI with Voice Features
st.set_page_config(
    page_title="AI Poetry Generator Pro", 
    layout="centered",
    page_icon="🎭"
)

# 🎨 Professional CSS Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3.5em;
        text-align: center;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2em;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .sub-header {
        text-align: center;
        font-size: 1.4em;
        color: #6c757d;
        margin-bottom: 2.5em;
        font-weight: 300;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .section-header {
        font-size: 1.6em;
        font-weight: 600;
        color: #495057;
        margin-bottom: 1em;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 0.5em;
    }
    .voice-btn {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.8em 2em !important;
        border-radius: 12px !important;
        font-size: 1.1em !important;
        transition: all 0.3s ease !important;
    }
    .voice-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3) !important;
    }
    .generate-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.8em 2em !important;
        border-radius: 12px !important;
        font-size: 1.1em !important;
        transition: all 0.3s ease !important;
    }
    .generate-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3) !important;
    }
    .reset-btn {
        background: linear-gradient(135deg, #6c757d 0%, #495057 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.8em 1.5em !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    .reset-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(108, 117, 125, 0.3) !important;
    }
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e9ecef;
        font-size: 1.1em;
        padding: 1em;
        transition: border 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        border-radius: 12px;
        padding: 1.5em;
        margin: 1em 0;
    }
    .poem-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1.5em;
        margin: 1em 0;
        font-style: italic;
        line-height: 1.6;
    }
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.5em;
        margin: 1em 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)

# 📝 Professional UI Layout
st.markdown('<div class="main-header">AI Poetry Generator Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Create Beautiful Poetry with Voice & Text • Powered by AI Agents</div>', unsafe_allow_html=True)

# Initialize Session State
if 'voice_text' not in st.session_state:
    st.session_state.voice_text = ""
if 'final_input' not in st.session_state:
    st.session_state.final_input = ""
if 'poetry_generated' not in st.session_state:
    st.session_state.poetry_generated = False
if 'poetry_result' not in st.session_state:
    st.session_state.poetry_result = None

# 🎤 Voice Input Section
st.markdown('<div class="section-header">🎤 Voice Input</div>', unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🎤 **Start Voice Recording**", key="voice_input", use_container_width=True):
            voice_text = speech_to_text()
            if voice_text:
                st.session_state.voice_text = voice_text
                st.session_state.final_input = voice_text
                st.success(f"**Voice Input Received:** {voice_text}")
    
    with col2:
        if st.button("🗑️ **Clear Input**", key="clear_voice", use_container_width=True):
            st.session_state.voice_text = ""
            st.session_state.final_input = ""
            st.rerun()

# 📝 Text Input Section
st.markdown('<div class="section-header">📝 Text Input</div>', unsafe_allow_html=True)

user_input = st.text_area(
    "**Enter your poetry theme or topic:**", 
    height=120, 
    placeholder="Example: Write a dramatic poem about betrayal, love, or nature...",
    value=st.session_state.final_input,
    key="text_input"
)

if user_input != st.session_state.final_input:
    st.session_state.final_input = user_input

# ⚙️ Generation Section
st.markdown('<div class="section-header">⚡ Generate Poetry</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    generate_clicked = st.button("🚀 **Generate Poetry**", key="generate", use_container_width=True)

with col2:
    enable_voice = st.checkbox("🔊 **Enable Voice Output**", value=True)

with col3:
    if st.button("🔄 **Reset All**", key="reset"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# 🎭 Poetry Generation Logic
if generate_clicked and st.session_state.final_input.strip():
    with st.spinner("🪄 **AI is crafting your unique poem...**"):
        try:
            poetry_result = asyncio.run(run_poetry_agent(st.session_state.final_input))
            st.session_state.poetry_result = poetry_result
            st.session_state.poetry_generated = True
            
            # Success Display
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.success("🎉 **Your Poem is Ready!**")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Poem Display
            st.markdown("### 📜 **Generated Poem**")
            st.markdown(f'<div class="poem-box">{poetry_result.final_output}</div>', unsafe_allow_html=True)
            st.markdown(f"**🤖 Generated by:** `{poetry_result.last_agent.name}`")
            
            # Voice Output
            if enable_voice and poetry_result.final_output:
                st.markdown("### 🔊 **Audio Version**")
                with st.spinner("🎵 **Generating audio version...**"):
                    audio_file = text_to_speech(poetry_result.final_output)
                    
                    if audio_file:
                        audio_bytes = open(audio_file, 'rb').read()
                        st.audio(audio_bytes, format='audio/mp3')
                        os.unlink(audio_file)
                        st.success("🔊 **Audio ready! Click play to listen**")
                        
        except Exception as e:
            st.error(f"❌ **Generation Error:** {e}")

elif generate_clicked and not st.session_state.final_input.strip():
    st.warning("⚠️ **Please enter a topic or theme first**")

# Display Previous Poem
if st.session_state.poetry_generated and st.session_state.poetry_result:
    st.markdown("---")
    st.markdown("### 📖 **Previous Poem**")
    st.markdown(f'<div class="poem-box">{st.session_state.poetry_result.final_output}</div>', unsafe_allow_html=True)

# 📚 Instructions Section
with st.expander("📖 **How to Use This Application**", expanded=False):
    st.markdown("""
    ### **Quick Start Guide**
    
    #### **Option 1: Voice Input (Recommended)**
    1. Click **'Start Voice Recording'**
    2. Speak your poetry theme clearly
    3. Wait for voice recognition
    4. Click **'Generate Poetry'**
    
    #### **Option 2: Text Input**
    1. Type your poetry theme in the text area
    2. Click **'Generate Poetry'**
    
    #### **Features:**
    - **Voice Output**: Listen to your poem (enable checkbox)
    - **Multiple Styles**: AI chooses between lyric, narrative, or dramatic poetry
    - **Professional Quality**: Industry-standard AI agents
    
    #### **Example Inputs:**
    - "A romantic poem about sunset"
    - "Dramatic poem about hero's journey" 
    - "Emotional poem about lost love"
    - "Nature poem about mountains"
    
    #### **Tips for Best Results:**
    - Speak clearly in quiet environment
    - Be specific with your theme
    - Use descriptive words for better poetry
    """)

# 🎯 Feature Highlights
st.markdown("---")
st.markdown("### 🚀 **Advanced Features**")

feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🎭 **Multi-Style AI**")
        st.markdown("Automatically selects between lyric, narrative, and dramatic poetry styles based on your input.")
        st.markdown('</div>', unsafe_allow_html=True)

with feature_col2:
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🎤 **Voice First**")
        st.markdown("Speak your ideas naturally. Advanced speech recognition converts voice to text instantly.")
        st.markdown('</div>', unsafe_allow_html=True)

with feature_col3:
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🔊 **Audio Output**")
        st.markdown("Listen to your generated poems with high-quality text-to-speech technology.")
        st.markdown('</div>', unsafe_allow_html=True)