import streamlit as st
import google.genai as genai
import re
from youtube_transcript_api import YouTubeTranscriptApi

st.set_page_config(page_title="AI YouTube Summarizer", page_icon="📺", layout="centered")
st.title("📺 Smart YouTube Video Summarizer")
st.write("Generate an AI summary of a YouTube video using its link or transcript text.")

# Revert to clean, manual sidebar entry to bypass all cloud vault errors
with st.sidebar:
    st.header("🔑 Configuration")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.markdown("[Get a free key here](https://google.com)")

tab1, tab2 = st.tabs(["🔗 Summarize via Link", "📝 Paste Transcript Directly"])

with tab1:
    video_url = st.text_input("YouTube Video URL:", placeholder="https://youtube.com...", key="link_input")
    if st.button("Generate Summary from Link", type="primary"):
        if not api_key:
            st.warning("Please enter your Gemini API key in the sidebar first!")
        elif not video_url:
            st.warning("Please provide a valid YouTube link.")
        else:
            pattern = r"(?:v=|\/shorts\/|\/embed\/|\/v\/|youtu\.be\/|\/watch\?v=)([a-zA-Z0-9_-]{11})"
            match = re.search(pattern, video_url)
            video_id = match.group(1) if match else None
            
            if not video_id:
                st.error("Could not parse YouTube Video ID.")
            else:
                with st.spinner("Attempting to fetch transcript from YouTube..."):
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                        full_transcript = " ".join([item.text for item in transcript_list])
                    except Exception as e:
                        st.error("⚠️ YouTube cloud server IP block detected. Please use the 'Paste Transcript Directly' tab above to complete your summary!")
                        full_transcript = None

                if full_transcript:
                    with st.spinner("Gemini AI is analyzing..."):
                        try:
                            client = genai.Client(api_key=api_key)
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=f"Provide a concise summary broken into 'Key Takeaways':\n\n{full_transcript}"
                            )
                            st.success("✨ Summary Generated Successfully!")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"AI Generation Failed: {e}")

with tab2:
    st.write("If the link method is blocked by YouTube's cloud restrictions, paste any video text transcript here to get an instant AI summary.")
    manual_transcript = st.text_area("Paste Transcript Text Here:", height=250, placeholder="Paste transcript sentences here...")
    
    if st.button("Generate Summary from Text", type="primary", key="text_button"):
        if not api_key:
            st.warning("Please enter your Gemini API key in the sidebar first!")
        elif not manual_transcript.strip():
            st.warning("Please paste some text first.")
        else:
            with st.spinner("Gemini AI is analyzing your text..."):
                try:
                    # Initialize client with manual string
                    client = genai.Client(api_key=str(api_key).strip())
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"Provide a concise summary broken into 'Key Takeaways' and a 'Detailed Summary' for this text:\n\n{manual_transcript}"
                    )
                    st.success("✨ Summary Generated Successfully!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI Generation Failed: {e}")
