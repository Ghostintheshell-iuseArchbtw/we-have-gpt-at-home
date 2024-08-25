import tkinter as tk
import customtkinter as ctk
from tkinter import scrolledtext
import speech_recognition as sr
import os
from gtts import gTTS
from playsound import playsound

# Initialize the main window
root = ctk.CTk()
root.title("Chat Application")
root.geometry("600x600")

# Define colors
BG_COLOR = "#333333"  # Dark gray background
TEXT_COLOR = "#FFFFFF"  # White text
BUTTON_COLOR = "#444444"  # Slightly lighter gray for buttons
BUTTON_HOVER_COLOR = "#555555"  # Even lighter gray for button hover

# Set up the main text area
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12))
chat_box.pack(pady=10, padx=10, fill="both", expand=True)

# Function to handle sending messages
def on_send():
    message = user_input.get()
    if message.strip():
        chat_box.insert(tk.END, f"You: {message}\n")
        user_input.delete(0, tk.END)
        # Here you can add code to handle the message (e.g., send it to an AI model)
    else:
        chat_box.insert(tk.END, "Message cannot be empty.\n")

# Function to clear the chat
def clear_chat():
    chat_box.delete(1.0, tk.END)

# Function to save the chat
def save_chat():
    with open("chat_log.txt", "w") as file:
        file.write(chat_box.get(1.0, tk.END))
    chat_box.insert(tk.END, "Chat saved to chat_log.txt\n")

# Function to handle speech-to-text
def record_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        chat_box.insert(tk.END, "Listening...\n")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            user_input.delete(0, tk.END)
            user_input.insert(0, text)
            chat_box.insert(tk.END, f"You (spoken): {text}\n")
        except sr.UnknownValueError:
            chat_box.insert(tk.END, "Could not understand audio.\n")
        except sr.RequestError:
            chat_box.insert(tk.END, "Error with the speech recognition service.\n")
        except Exception as e:
            chat_box.insert(tk.END, f"Error: {str(e)}\n")

# Function to play the voice log
def play_voice_log():
    message = chat_box.get(1.0, tk.END).strip()
    if message:
        tts = gTTS(text=message, lang="en")
        tts.save("voice_log.mp3")
        playsound("voice_log.mp3")
    else:
        chat_box.insert(tk.END, "No chat log to play.\n")

# Function to update settings
def update_settings():
    chat_box.insert(tk.END, "Settings updated.\n")

# Function to toggle between light and dark themes
def toggle_theme():
    chat_box.insert(tk.END, "Theme toggled (not implemented).\n")

# Input frame
input_frame = ctk.CTkFrame(root, fg_color=BG_COLOR)
input_frame.pack(pady=10, padx=10, fill="x")

user_input = ctk.CTkEntry(input_frame, width=450, fg_color=BUTTON_COLOR, text_color=TEXT_COLOR)
user_input.grid(row=0, column=0, padx=10, pady=5)

send_button = ctk.CTkButton(input_frame, text="Send", command=on_send, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
send_button.grid(row=0, column=1, padx=10, pady=5)

# Additional controls
control_frame = ctk.CTkFrame(root, fg_color=BG_COLOR)
control_frame.pack(pady=10, padx=10, fill="x")

clear_button = ctk.CTkButton(control_frame, text="Clear Chat", command=clear_chat, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
clear_button.grid(row=0, column=0, padx=10, pady=5)

save_button = ctk.CTkButton(control_frame, text="Save Chat", command=save_chat, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
save_button.grid(row=0, column=1, padx=10, pady=5)

toggle_theme_button = ctk.CTkButton(control_frame, text="Toggle Theme", command=toggle_theme, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
toggle_theme_button.grid(row=0, column=2, padx=10, pady=5)

play_log_button = ctk.CTkButton(control_frame, text="Play Voice Log", command=play_voice_log, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
play_log_button.grid(row=0, column=3, padx=10, pady=5)

speech_button = ctk.CTkButton(control_frame, text="Speak", command=record_speech, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
speech_button.grid(row=0, column=4, padx=10, pady=5)

# Start the Tkinter main loop
root.mainloop()
