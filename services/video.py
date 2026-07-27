import os
import re
import tempfile
import subprocess

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import yt_dlp
from groq import Groq

YOUTUBE_ID_RE = re.compile(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|shorts/|embed/))([\w-]{11})")
MODELO_WHISPER = "whisper-large-v3-turbo"


def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no está configurada.")
    return Groq(api_key=api_key)


def _youtube_video_id(url):
    match = YOUTUBE_ID_RE.search(url)
    return match.group(1) if match else None


def _transcripcion_youtube_captions(video_id):
    transcript_list = YouTubeTranscriptApi().list(video_id)
    try:
        transcript = transcript_list.find_transcript(["es", "es-419", "en"])
    except NoTranscriptFound:
        transcript = next(iter(transcript_list))
    datos = transcript.fetch()
    return " ".join(seg.text.strip() for seg in datos if seg.text.strip())


def _descargar_audio(url, carpeta):
    salida = os.path.join(carpeta, "audio.%(ext)s")
    opciones = {
        "format": "bestaudio/best",
        "outtmpl": salida,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opciones) as ydl:
        ydl.download([url])
    return os.path.join(carpeta, "audio.mp3")


def _transcribir_con_groq(ruta_audio):
    client = get_groq_client()
    with open(ruta_audio, "rb") as f:
        resultado = client.audio.transcriptions.create(
            file=(os.path.basename(ruta_audio), f.read()),
            model=MODELO_WHISPER,
            response_format="text",
        )
    return str(resultado).strip()


def extraer_guion_url(url):
    """Extrae el guion completo de un video a partir de un link de YouTube, TikTok o Instagram."""
    video_id = _youtube_video_id(url)
    if video_id:
        try:
            return _transcripcion_youtube_captions(video_id), "captions"
        except (TranscriptsDisabled, NoTranscriptFound):
            pass
    with tempfile.TemporaryDirectory() as carpeta:
        ruta_audio = _descargar_audio(url, carpeta)
        return _transcribir_con_groq(ruta_audio), "whisper"


def extraer_guion_archivo(uploaded_file):
    """Extrae el guion completo a partir de un archivo de video/audio ya descargado."""
    sufijo = os.path.splitext(uploaded_file.name)[1] or ".mp4"
    with tempfile.TemporaryDirectory() as carpeta:
        ruta_original = os.path.join(carpeta, f"original{sufijo}")
        with open(ruta_original, "wb") as f:
            f.write(uploaded_file.getbuffer())
        ruta_audio = os.path.join(carpeta, "audio.mp3")
        subprocess.run(
            ["ffmpeg", "-y", "-i", ruta_original, "-vn", "-acodec", "libmp3lame", "-ar", "16000", "-ac", "1", ruta_audio],
            check=True, capture_output=True,
        )
        return _transcribir_con_groq(ruta_audio)
