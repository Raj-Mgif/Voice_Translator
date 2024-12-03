import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
from playsound import playsound

# Dictionary of language codes (for recognition and translation)
LANGUAGES = {
    'English': 'en',
    'Hindi': 'hi',
    'Bengali': 'bn',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Marathi': 'mr',
    'Gujarati': 'gu',
    'Punjabi': 'pa',
    'Malayalam': 'ml',
    'Kannada': 'kn',
    'Urdu': 'ur',
}

# Function to recognize speech in the selected input language asynchronously
def recognize_speech_in_background(input_lang_code, callback):
    recognizer = sr.Recognizer()

    def callback_wrapper(recognizer, audio):
        try:
            text = recognizer.recognize_google(audio, language=input_lang_code)
            callback(text)
        except sr.UnknownValueError:
            callback(None)
        except sr.RequestError:
            messagebox.showerror("Error", "Google Speech Recognition service is unavailable.")
            callback(None)

    return recognizer.listen_in_background(sr.Microphone(), callback_wrapper)

# Function to translate text from source language to target language
def translate_text(text, source_lang, target_lang):
    try:
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return translated
    except Exception as e:
        messagebox.showerror("Translation Error", f"Error occurred during translation: {str(e)}")
        return None

# Function to convert text to speech
def text_to_speech(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts_file = "translated_audio.mp3"
        tts.save(tts_file)
        playsound(tts_file)
        os.remove(tts_file)
    except Exception as e:
        messagebox.showerror("Error", f"Could not play audio: {str(e)}")

# Sender block class
class SenderBlock:
    def __init__(self, root, receiver_block):
        self.root = root
        self.receiver_block = receiver_block

        self.frame = tk.Frame(root)
        self.frame.grid(row=0, column=0, padx=10, pady=10)

        # Input language selection
        self.input_lang_label = tk.Label(self.frame, text="Input Language:")
        self.input_lang_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        self.input_lang_combo = ttk.Combobox(self.frame, values=list(LANGUAGES.keys()))
        self.input_lang_combo.grid(row=0, column=1, padx=10, pady=5)
        self.input_lang_combo.current(0)  # Default to the first language

        # Output language selection
        self.output_lang_label = tk.Label(self.frame, text="Output Language:")
        self.output_lang_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

        self.output_lang_combo = ttk.Combobox(self.frame, values=list(LANGUAGES.keys()))
        self.output_lang_combo.grid(row=1, column=1, padx=10, pady=5)
        self.output_lang_combo.current(1)  # Default to the second language (Hindi)

        # Buttons on the left
        self.start_button = tk.Button(self.frame, text="Start Session", command=self.start_session)
        self.start_button.grid(row=2, column=0, padx=10, pady=5, sticky='w')

        self.pause_button = tk.Button(self.frame, text="Pause", command=self.pause_session, state=tk.DISABLED)
        self.pause_button.grid(row=3, column=0, padx=10, pady=5, sticky='w')

        self.resume_button = tk.Button(self.frame, text="Resume", command=self.resume_session, state=tk.DISABLED)
        self.resume_button.grid(row=4, column=0, padx=10, pady=5, sticky='w')

        # Text boxes on the right
        self.recognized_text_label = tk.Label(self.frame, text="Recognized Speech:")
        self.recognized_text_label.grid(row=0, column=2, padx=10, pady=5)

        self.recognized_text = tk.Text(self.frame, height=5, width=40)
        self.recognized_text.grid(row=1, column=2, rowspan=2, padx=10, pady=5)

        self.translated_text_label = tk.Label(self.frame, text="Translated Text:")
        self.translated_text_label.grid(row=3, column=2, padx=10, pady=5)

        self.translated_text = tk.Text(self.frame, height=5, width=40)
        self.translated_text.grid(row=4, column=2, rowspan=2, padx=10, pady=5)

        self.listener = None

    def start_session(self):
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

        input_lang_code = LANGUAGES[self.input_lang_combo.get()]
        output_lang_code = LANGUAGES[self.output_lang_combo.get()]

        # Update receiver block with opposite languages
        self.receiver_block.update_languages(input_lang_code, output_lang_code)

        self.listener = recognize_speech_in_background(input_lang_code, self.handle_recognized_speech)

    def pause_session(self):
        if self.listener:
            self.listener(wait_for_stop=False)
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)

    def resume_session(self):
        input_lang_code = LANGUAGES[self.input_lang_combo.get()]
        self.listener = recognize_speech_in_background(input_lang_code, self.handle_recognized_speech)
        self.resume_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)

    def clear_text(self):
        self.recognized_text.delete(1.0, tk.END)
        self.translated_text.delete(1.0, tk.END)

    def handle_recognized_speech(self, recognized_text):
        if recognized_text:
            self.recognized_text.insert(tk.END, recognized_text + "\n")
            input_lang_code = LANGUAGES[self.input_lang_combo.get()]
            output_lang_code = LANGUAGES[self.output_lang_combo.get()]
            translated = translate_text(recognized_text, input_lang_code, output_lang_code)
            if translated:
                self.translated_text.insert(tk.END, translated + "\n")
                text_to_speech(translated, output_lang_code)

# Receiver block class
class ReceiverBlock:
    def __init__(self, root):
        self.frame = tk.Frame(root)
        self.frame.grid(row=0, column=1, padx=10, pady=10)

        # Input language selection
        self.input_lang_label = tk.Label(self.frame, text="Input Language:")
        self.input_lang_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        self.input_lang_combo = ttk.Combobox(self.frame, values=list(LANGUAGES.keys()))
        self.input_lang_combo.grid(row=0, column=1, padx=10, pady=5)
        self.input_lang_combo.current(1)  # Default to Hindi

        # Output language selection
        self.output_lang_label = tk.Label(self.frame, text="Output Language:")
        self.output_lang_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

        self.output_lang_combo = ttk.Combobox(self.frame, values=list(LANGUAGES.keys()))
        self.output_lang_combo.grid(row=1, column=1, padx=10, pady=5)
        self.output_lang_combo.current(0)  # Default to English

        # Text boxes and buttons
        self.input_text_label = tk.Label(self.frame, text="Input Text:")
        self.input_text_label.grid(row=0, column=2, padx=10, pady=5)

        self.input_text = tk.Text(self.frame, height=5, width=40)
        self.input_text.grid(row=1, column=2, rowspan=2, padx=10, pady=5)

        self.translated_text_label = tk.Label(self.frame, text="Translated Text:")
        self.translated_text_label.grid(row=3, column=2, padx=10, pady=5)

        self.translated_text = tk.Text(self.frame, height=5, width=40, state=tk.DISABLED)
        self.translated_text.grid(row=4, column=2, rowspan=2, padx=10, pady=5)

        self.translate_button = tk.Button(self.frame, text="Translate", command=self.translate_text)
        self.translate_button.grid(row=2, column=0, padx=10, pady=5, sticky='w')

        self.speak_button = tk.Button(self.frame, text="Play Translated Text", command=self.speak_translated_text)
        self.speak_button.grid(row=3, column=0, padx=10, pady=5, sticky='w')

    def update_languages(self, sender_input_lang, sender_output_lang):
        self.input_lang_combo.set(sender_output_lang)  # Set opposite for receiver input
        self.output_lang_combo.set(sender_input_lang)  # Set opposite for receiver output

    def translate_text(self):
        input_text = self.input_text.get(1.0, tk.END).strip()
        if input_text:
            input_lang_code = LANGUAGES[self.input_lang_combo.get()]
            output_lang_code = LANGUAGES[self.output_lang_combo.get()]
            translated = translate_text(input_text, input_lang_code, output_lang_code)
            if translated:
                self.translated_text.config(state=tk.NORMAL)
                self.translated_text.delete(1.0, tk.END)
                self.translated_text.insert(tk.END, translated)
                self.translated_text.config(state=tk.DISABLED)

    def speak_translated_text(self):
        translated = self.translated_text.get(1.0, tk.END).strip()
        if translated:
            output_lang_code = LANGUAGES[self.output_lang_combo.get()]
            text_to_speech(translated, output_lang_code)

    def clear_text(self):
        self.input_text.delete(1.0, tk.END)
        self.translated_text.config(state=tk.NORMAL)
        self.translated_text.delete(1.0, tk.END)
        self.translated_text.config(state=tk.DISABLED)

# Main Application class
class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Translator")
        self.root.geometry("900x500")

        self.receiver_block = ReceiverBlock(root)
        self.sender_block = SenderBlock(root, self.receiver_block)

        # Add a common "End Session" button in the middle
        self.end_session_button = tk.Button(root, text="End Session", command=self.end_session, bg="red", fg="white")
        self.end_session_button.grid(row=1, column=0, columnspan=2, pady=10)

    def end_session(self):
        # Clear text in both sender and receiver blocks
        self.sender_block.clear_text()
        self.receiver_block.clear_text()
        messagebox.showinfo("Session Ended", "The session has been successfully ended and all text has been cleared.")

# Running the application
if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
