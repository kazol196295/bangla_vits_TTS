import streamlit as st
import requests
import base64

st.set_page_config(
    page_title="Bangla TTS", 
    page_icon="🇧🇩",
    layout="centered"
)

st.title("🇧🇩 Bangla Text-to-Speech")
st.caption("Powered by VITS | Backend runs on Kaggle GPU")

# Backend URL from secrets or manual input
default_url = st.secrets.get("KAGGLE_URL", "")
api_url = st.sidebar.text_input(
    "🔗 Kaggle Backend URL",
    value=default_url,
    placeholder="https://xxxx.ngrok-free.app",
    help="Paste the Ngrok URL from your running Kaggle notebook"
)

st.sidebar.divider()
st.sidebar.markdown("""
**How to use:**
1. Run the Kaggle notebook
2. Copy the Ngrok URL
3. Paste it here
4. Enter Bengali text & generate
""")

if not api_url:
    st.info("👈 Enter your Kaggle Ngrok URL in the sidebar to get started")
    st.stop()

# Test connection
if st.sidebar.button("🔄 Test Connection"):
    try:
        r = requests.get(f"{api_url}/health", timeout=5)
        if r.json().get("model_loaded"):
            st.sidebar.success("✅ Connected & Ready")
        else:
            st.sidebar.warning("⏳ Model still loading...")
    except Exception as e:
        st.sidebar.error(f"❌ Error: {e}")

# Main UI
text = st.text_area(
    "📝 Enter Bengali Text:", 
    value="আমি বাংলায় কথা বলতে পারি।", 
    height=150
)

if st.button("🔊 Generate Speech", type="primary", use_container_width=True):
    if not text.strip():
        st.warning("Please enter some text")
        st.stop()
    
    with st.spinner("🎙️ Generating audio on Kaggle GPU..."):
        try:
            response = requests.post(
                f"{api_url}/generate",
                json={"text": text, "model_choice": "current"},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                audio_bytes = base64.b64decode(data["audio_base64"])
                
                st.audio(audio_bytes, format="audio/wav")
                st.download_button(
                    label="⬇️ Download WAV",
                    data=audio_bytes,
                    file_name="bangla_tts.wav",
                    mime="audio/wav"
                )
                st.success("✅ Generated successfully!")
            else:
                st.error(f"Backend error: {response.text}")
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timeout. The text might be too long or Kaggle is busy.")
        except Exception as e:
            st.error(f"Failed: {str(e)}")

st.divider()
st.caption("[Model: kazol196295/bangla-vits-female-1.2](https://huggingface.co/kazol196295/bangla-vits-female-1.2)")