import sys
import threading
import queue
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import messagebox

# Voice visualization parameters
DURATION = 0.1  # seconds per frame
FS = 16000      # sampling rate

class VoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Recognition System")
        self.text_var = tk.StringVar()
        self.text_var.set("Say something...")

        # Language selection
        self.language_var = tk.StringVar(value="en-IN")
        languages = {
            "English": "en-IN",
            "Hindi": "hi-IN",
            "Tamil": "ta-IN",
            "Telugu": "te-IN"
        }
        self.language_menu = tk.OptionMenu(root, self.language_var, *languages.keys())
        self.language_menu.config(font=("Arial", 16))
        self.language_menu.pack(pady=10)

        self.languages = languages

        # Increase window and font size
        self.root.geometry("900x500")
        self.label = tk.Label(root, textvariable=self.text_var, font=("Arial", 40), wraplength=860, justify="center")
        self.label.pack(pady=40, fill="x")

        self.canvas = tk.Canvas(root, width=860, height=200, bg="black")
        self.canvas.pack(pady=20)

        self.status_var = tk.StringVar()
        self.status_var.set("Status: Ready")
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Arial", 16), fg="blue")
        self.status_label.pack(pady=5)

        self.running = True
        self.listening = False  # Add this flag
        self.audio_queue = queue.Queue()
        self.recognizer = sr.Recognizer()

        # Try to initialize microphone
        try:
            self.mic = sr.Microphone()
        except Exception as e:
            messagebox.showerror("Microphone Error", f"Could not access microphone:\n{e}")
            root.destroy()
            return

        # Start Listening button
        self.start_btn = tk.Button(root, text="Start Listening", command=self.start_listening, font=("Arial", 16))
        self.start_btn.pack(pady=10)

        self.close_btn = tk.Button(root, text="Close", command=self.close, font=("Arial", 16))
        self.close_btn.pack(pady=10)

        # Start only the visualization thread initially
        self.visual_thread = threading.Thread(target=self.visualize_audio, daemon=True)
        self.visual_thread.start()

    def start_listening(self):
        if not self.listening:
            self.listening = True
            self.start_btn.config(state="disabled")
            self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
            self.listen_thread.start()

    def listen_loop(self):
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source)
                while self.running:
                    try:
                        self.root.after(0, self.status_var.set, "Status: Listening...")
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=4)
                        self.audio_queue.put(audio.get_raw_data())
                        self.root.after(0, self.status_var.set, "Status: Recognizing...")
                        try:
                            # Get selected language code
                            lang_key = self.language_var.get()
                            lang_code = self.languages.get(lang_key, "en-IN")
                            text = self.recognizer.recognize_google(audio, language=lang_code)
                            text = text.strip()
                            if text.lower() == "close":
                                self.root.after(0, self.close)
                                break
                            else:
                                self.root.after(0, self.text_var.set, f"You said: {text}")
                                self.root.after(0, self.status_var.set, "Status: Ready")
                        except sr.UnknownValueError:
                            self.root.after(0, self.text_var.set, "Could not understand")
                            self.root.after(0, self.status_var.set, "Status: Ready")
                        except sr.RequestError as e:
                            self.root.after(0, self.text_var.set, f"API Error: {e}")
                            self.root.after(0, self.status_var.set, "Status: API Error")
                    except sr.WaitTimeoutError:
                        self.root.after(0, self.status_var.set, "Status: Waiting for speech...")
                        continue
                    except Exception as e:
                        self.root.after(0, self.text_var.set, f"Error: {e}")
                        self.root.after(0, self.status_var.set, "Status: Error")
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Critical Error", f"Error in listen loop:\n{e}")
            self.root.after(0, self.close)
        finally:
            self.listening = False
            self.root.after(0, self.start_btn.config, {"state": "normal"})

    def visualize_audio(self):
        while self.running:
            try:
                data = self.audio_queue.get(timeout=1)
                audio_np = np.frombuffer(data, dtype=np.int16)
                self.draw_waveform(audio_np)
            except queue.Empty:
                continue
            except Exception as e:
                self.root.after(0, self.status_var.set, f"Status: Visualization error: {e}")

    def draw_waveform(self, audio_np):
        self.canvas.delete("all")
        if len(audio_np) == 0:
            return
        w = 860
        h = 200
        step = max(1, len(audio_np) // w)
        points = []
        for x in range(w):
            idx = x * step
            if idx < len(audio_np):
                y = int((audio_np[idx] / 32768) * (h // 2)) + (h // 2)
                points.append((x, y))
        for i in range(1, len(points)):
            self.canvas.create_line(points[i-1][0], points[i-1][1], points[i][0], points[i][1], fill="lime")
        self.root.update_idletasks()

    def close(self):
        self.running = False
        self.close_btn.config(state="disabled")
        self.root.after(200, self.root.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = VoiceApp(root)
        root.protocol("WM_DELETE_WINDOW", app.close)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", str(e))
        sys.exit(1)