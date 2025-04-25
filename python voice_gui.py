import whisper
import pyttsx3
import sounddevice as sd
from scipy.io.wavfile import write
import tkinter as tk
from tkinter import messagebox
import threading
import time
import webbrowser
import os

# مكتبات التحكم بالصوت النظامي
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# إعداد الصوت
engine = pyttsx3.init()
engine.setProperty('rate', 150)
volume = engine.getProperty('volume')

# تحميل نموذج Whisper
model = whisper.load_model("base")

# تسجيل الصوت
is_recording = False
def record_audio(filename="temp.wav", duration=5, fs=44100):
    global is_recording
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, audio)

def start_recording():
    global is_recording
    is_recording = True
    status_text.set("🎙️ Recording...")
    threading.Thread(target=listen).start()

def stop_recording():
    global is_recording
    is_recording = False
    status_text.set("✅ Recording stopped")

# تحويل الصوت إلى نص
def recognize_speech(filename="temp.wav"):
    result = model.transcribe(filename , language="en")
    return result["text"]

# التحدث
def speak(text):
    engine.say(text)
    engine.runAndWait()

# تنفيذ الأوامر
def handle_response(text):
    user_text.set(text)
    text = text.lower()
    reply = "Sorry, I didn't understand that."

    if "hello" in text:
        reply = "Hello! my name is azrs. How can I help you?"
    elif "your name" in text:
        reply = "I am azrs, your assistant."
    elif "time" in text:
        now = time.strftime("%I:%M %p")
        reply = f"The time is {now}"
    elif "date" in text:
        today = time.strftime("%A, %B %d, %Y")
        reply = f"Today's date is {today}"
    elif "stop" in text:
        reply = "Goodbye!"
        speak(reply)
        root.destroy()
        return
    elif "lower volume" in text:
        set_system_volume(-0.1)
        reply = "System volume lowered."
    elif "raise volume" in text:
        set_system_volume(0.1)
        reply = "System volume raised."
    elif "google" in text:
        webbrowser.open("https://www.google.com")
        reply = "Opening Google..."
    elif "youtube" in text:
        webbrowser.open("https://www.youtube.com")
        reply = "Opening YouTube..."

    assistant_text.set(reply)
    speak(reply)

# تغيير صوت النظام
def set_system_volume(change):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
    current_volume = volume_interface.GetMasterVolumeLevelScalar()
    new_volume = max(0.0, min(1.0, current_volume + change))
    volume_interface.SetMasterVolumeLevelScalar(new_volume, None)

# عملية الاستماع
def listen():
    record_audio()
    try:
        text = recognize_speech()
        handle_response(text)
    except Exception as e:
        assistant_text.set("⚠️ Couldn't hear you.")
        speak("Sorry, I couldn't hear you.")

# واجهة المستخدم
root = tk.Tk()
root.title("🎧 Voice Assistant")
root.geometry("500x400")
root.configure(bg="#1e1e2e")

tk.Label(root, text="🗣️ You said:", font=("Arial", 14), fg="white", bg="#1e1e2e").pack(pady=5)
user_text = tk.StringVar()
tk.Label(root, textvariable=user_text, font=("Arial", 14), fg="#89dceb", bg="#1e1e2e").pack()

tk.Label(root, text="🤖 Assistant says:", font=("Arial", 14), fg="white", bg="#1e1e2e").pack(pady=5)
assistant_text = tk.StringVar()
tk.Label(root, textvariable=assistant_text, font=("Arial", 14), fg="#f9e2af", bg="#1e1e2e").pack()

status_text = tk.StringVar(value="⏹️ Not recording")
tk.Label(root, textvariable=status_text, font=("Arial", 12), fg="#cba6f7", bg="#1e1e2e").pack(pady=10)

tk.Button(root, text="▶️ Start Recording", command=start_recording, font=("Arial", 12), bg="#74c7ec").pack(pady=5)
tk.Button(root, text="⏹️ Stop Recording", command=stop_recording, font=("Arial", 12), bg="#f38ba8").pack(pady=5)
tk.Button(root, text="❌ Exit", command=root.destroy, font=("Arial", 12), bg="#f38ba8").pack(pady=10)

root.mainloop()
