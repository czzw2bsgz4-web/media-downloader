import streamlit as st
import yt_dlp
import os
import tempfile
import re

st.set_page_config(page_title="Media Downloader", page_icon="film", layout="centered")

st.markdown("<h1 style='text-align:center'>Media Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888'>YouTube / IG / TikTok / X / Facebook / Bilibili + 1000 more</p>", unsafe_allow_html=True)
st.divider()

url = st.text_input("Paste video URL", placeholder="https://...")

col1, col2 = st.columns(2)
with col1:
    mode = st.radio("Mode", ["Video (MP4)", "Audio only (MP3)", "Video + Subtitles"])
with col2:
    quality = st.radio("Quality", ["Best", "1080p", "720p", "480p"])

if st.button("Download", type="primary", use_container_width=True):
    if not url or not url.strip():
        st.error("Please paste a URL")
    else:
        url = url.strip()
        if not re.match(r"https?://", url):
            url = "https://" + url

        tmp_dir = tempfile.mkdtemp()
        output_template = os.path.join(tmp_dir, "%(title).70s.%(ext)s")

        base_opts = {
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "max_filesize": 500 * 1024 * 1024,
        }

        if mode == "Video (MP4)":
            res_map = {"Best": "", "1080p": "1080", "720p": "720", "480p": "480"}
            res = res_map.get(quality, "")
            if res:
                fmt = f"bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best"
            else:
                fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            base_opts.update({"format": fmt, "merge_output_format": "mp4"})
        elif mode == "Audio only (MP3)":
            base_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
        elif mode == "Video + Subtitles":
            base_opts.update({
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["zh-Hant", "zh-Hans", "zh", "en", "ja"],
                "embedsubtitles": True,
            })

        with st.spinner("Downloading..."):
            try:
                with yt_dlp.YoutubeDL(base_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    if mode == "Audio only (MP3)":
                        filename = os.path.splitext(filename)[0] + ".mp3"

                    if not os.path.exists(filename):
                        for f in os.listdir(tmp_dir):
                            filename = os.path.join(tmp_dir, f)
                            break

                    if os.path.exists(filename):
                        title = info.get("title", "Done")
                        st.success("Done: " + title)
                        with open(filename, "rb") as f:
                            st.download_button(
                                label="Save file",
                                data=f,
                                file_name=os.path.basename(filename),
                                use_container_width=True,
                            )
                    else:
                        st.error("File not found")
            except yt_dlp.utils.DownloadError as e:
                msg = str(e)
                if "Private video" in msg or "Sign in" in msg:
                    st.error("Private video or login required")
                elif "not a valid URL" in msg or "Unsupported URL" in msg:
                    st.error("Unsupported URL format")
                else:
                    st.error("Download failed: " + msg[:200])
            except Exception as e:
                st.error("Error: " + str(e)[:200])

with st.expander("Supported platforms"):
    st.markdown("""
    - **YouTube** - youtube.com, youtu.be
    - **Instagram** - instagram.com/p/, /reel/
    - **TikTok** - tiktok.com
    - **Twitter/X** - twitter.com, x.com
    - **Facebook** - facebook.com/watch
    - **Bilibili** - bilibili.com
    - **Twitch** - twitch.tv
    - **Reddit** - reddit.com
    - **Vimeo** - vimeo.com
    - **SoundCloud** - soundcloud.com
    - ...and 1000+ more sites!
    """)
