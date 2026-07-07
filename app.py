import streamlit as st
import google.genai as genai
import re
from youtube_transcript_api import YouTubeTranscriptApi

st.set_page_config(page_title="AI YouTube Summarizer", page_icon="📺", layout="centered")
st.title("📺 Smart YouTube Video Summarizer")
st.write("Paste a YouTube link below to generate an AI summary of the video transcript.")

with st.sidebar:
    st.header("🔑 Configuration")
    api_key = st.secrets.get("GEMINI_API_KEY", "")

def extract_video_id(url):
    pattern = r"(?:v=|\/shorts\/|\/embed\/|\/v\/|youtu\.be\/|\/watch\?v=)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

video_url = st.text_input("YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Generate AI Summary", type="primary"):
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar first!")
    elif not video_url:
        st.warning("Please provide a valid YouTube link.")
    else:
        video_id = extract_video_id(video_url)
        
        if not video_id:
            st.error("Could not parse YouTube Video ID. Check the link syntax.")
        else:
            with st.spinner("Fetching transcript from video..."):
                try:
                    # FIX: Using instantiation and the updated .fetch() method
                    api_instance = YouTubeTranscriptApi()
                    transcript_list = api_instance.fetch(video_id)
                    full_transcript = " ".join([item.text for item in transcript_list])
                except Exception as e:
                    st.error(f"Failed to fetch transcript: {e}")
                    full_transcript = None

            if full_transcript:
                with st.spinner("Gemini AI is analyzing and summarizing..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"Provide a concise summary of the following transcript. Break it down into 'Key Takeaways' and a short 'Detailed Summary':\n\n{full_transcript}"
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                        )
                        st.success("✨ Summary Generated Successfully!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"AI Generation Failed: {e}")
