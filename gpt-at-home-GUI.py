import tkinter as tk
import customtkinter as ctk
import requests
import json
import threading
import datetime
import os
from gtts import gTTS
from playsound import playsound
from tkinter import filedialog, messagebox

# Local LLM server URL and port
server_url = 'http://192.168.1.187:9003/v1/chat/completions'

# Parameters
temperature = 0.7
max_tokens = 150
top_p = 1.0
frequency_penalty = 0.0
presence_penalty = 0.0

# User Profile
class UserProfile:
    def __init__(self, name, avatar):
        self.name = name
        self.avatar = avatar

# Dummy user profile (replace with actual implementation)
current_user = UserProfile(name="User", avatar="default_avatar.png")

# Conversation history
conversation_history = []

# Functions
def make_inference_request():
    global conversation_history
    # Request payload
    payload = {
        "messages": conversation_history,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        "stream": True
    }

    try:
        with requests.post(server_url, json=payload, headers={"Content-Type": "application/json"}, stream=True) as response:
            if response.status_code == 200:
                response_text = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            line_str = line_str[len('data: '):]

                        if line_str == '[DONE]':
                            break

                        try:
                            response_json = json.loads(line_str)
                            if 'choices' in response_json:
                                for choice in response_json['choices']:
                                    delta_content = choice.get('delta', {}).get('content', '')
                                    response_text += delta_content
                        except json.JSONDecodeError:
                            update_chat_window(f"Non-JSON response: {line_str}\n", sender="error")

                if response_text:
                    update_chat_window(response_text, sender="assistant")
                    speak(response_text)
            else:
                update_chat_window(f"Request failed with status code: {response.status_code}\n", sender="error")
                update_chat_window(f"Response: {response.text}\n", sender="error")
    except Exception as e:
        update_chat_window(f"An error occurred: {e}\n", sender="error")
    finally:
        loading_label.pack_forget()

def update_chat_window(message, sender="user"):
    chat_window.configure(state=ctk.NORMAL)
    if sender == "user":
        chat_window.insert(ctk.END, f"{current_user.name}: {message}\n", "user")
        conversation_history.append({"role": "user", "content": message})
    elif sender == "assistant":
        chat_window.insert(ctk.END, f"GPT: {message}\n", "assistant")
        conversation_history.append({"role": "assistant", "content": message})
    elif sender == "error":
        chat_window.insert(ctk.END, f"Error: {message}\n", "error")
    chat_window.configure(state=ctk.DISABLED)
    chat_window.yview(ctk.END)

def on_send(event=None):
    user_input = user_entry.get()
    if user_input.strip():
        update_chat_window(user_input, sender="user")
        loading_label.pack(pady=5)
        threading.Thread(target=make_inference_request).start()
        user_entry.delete(0, ctk.END)

def clear_chat():
    chat_window.configure(state=ctk.NORMAL)
    chat_window.delete(1.0, ctk.END)
    chat_window.configure(state=ctk.DISABLED)
    conversation_history.clear()

def update_settings():
    global temperature, max_tokens, top_p, frequency_penalty, presence_penalty
    try:
        temperature = float(temp_entry.get())
        max_tokens = int(tokens_entry.get())
        top_p = float(top_p_entry.get())
        frequency_penalty = float(freq_penalty_entry.get())
        presence_penalty = float(pres_penalty_entry.get())
        messagebox.showinfo("Settings Updated", "Settings have been updated successfully!")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numerical values for the settings.")

def save_chat():
    chat_text = chat_window.get(1.0, ctk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(chat_text)
        messagebox.showinfo("Chat Saved", "Chat history saved successfully!")

def speak(text):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        tts = gTTS(text=text, lang='en')
        
        voice_log_dir = "voice_logs"
        if not os.path.exists(voice_log_dir):
            os.makedirs(voice_log_dir)
        
        file_path = os.path.join(voice_log_dir, f"voice_log_{timestamp}.mp3")
        tts.save(file_path)
        
        playsound(file_path)
        
        # Optionally, log the file path to a text file for future reference
        with open(os.path.join(voice_log_dir, "voice_log_index.txt"), "a") as index_file:
            index_file.write(f"{timestamp}: {file_path}\n")
        
    except Exception as e:
        update_chat_window(f"Text-to-Speech Error: {e}\n", sender="error")

def toggle_theme():
    current_mode = ctk.get_appearance_mode()
    new_mode = "light" if current_mode == "dark" else "dark"
    ctk.set_appearance_mode(new_mode)

def play_voice_log():
    log_dir = "voice_logs"
    if not os.path.exists(log_dir):
        messagebox.showerror("Error", "No voice logs found.")
        return
    
    file_path = filedialog.askopenfilename(initialdir=log_dir, title="Select a Voice Log", filetypes=[("MP3 Files", "*.mp3")])
    if file_path:
        playsound(file_path)

# GUI setup
ctk.set_appearance_mode("dark")  # Keep it dark mode for a modern look
ctk.set_default_color_theme("dark-blue")  # This theme is darker and more sophisticated

# Color Customization
BG_COLOR = "#1f1f1f"  # Dark grey background
TEXT_COLOR = "#e0e0e0"  # Light grey text
BUTTON_COLOR = "#4a4a4a"  # Darker button
BUTTON_HOVER_COLOR = "#5a5a5a"  # Slightly lighter on hover

root = ctk.CTk()
root.title("Local LLM Chat")
root.geometry("800x700")
root.configure(bg=BG_COLOR)

# Chat frame
chat_frame = ctk.CTkFrame(root, fg_color=BG_COLOR)
chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

chat_window = ctk.CTkTextbox(chat_frame, wrap=ctk.WORD, state=ctk.DISABLED, width=580, height=400, text_color=TEXT_COLOR, bg_color=BG_COLOR)
chat_window.tag_config("user", foreground="#1e90ff")  # Dodger blue for user
chat_window.tag_config("assistant", foreground="#32cd32")  # Lime green for assistant
chat_window.tag_config("error", foreground="#ff4500")  # Orange red for errors
chat_window.pack(padx=10, pady=10, fill="both", expand=True)

# User entry frame
user_entry_frame = ctk.CTkFrame(root, fg_color=BG_COLOR)
user_entry_frame.pack(pady=5, padx=10, fill="x")

user_entry = ctk.CTkEntry(user_entry_frame, width=450, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
user_entry.grid(row=0, column=0, padx=10, pady=5)
user_entry.bind("<Return>", on_send)

send_button = ctk.CTkButton(user_entry_frame, text="Send", command=on_send, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
send_button.grid(row=0, column=1, padx=5, pady=5)

clear_button = ctk.CTkButton(user_entry_frame, text="Clear Chat", command=clear_chat, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
clear_button.grid(row=0, column=2, padx=5, pady=5)

save_button = ctk.CTkButton(user_entry_frame, text="Save Chat", command=save_chat, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
save_button.grid(row=0, column=3, padx=5, pady=5)

loading_label = ctk.CTkLabel(root, text="Loading...", text_color="gray", fg_color=BG_COLOR)

# Settings frame
settings_frame = ctk.CTkFrame(root, fg_color=BG_COLOR)
settings_frame.pack(pady=10, padx=10, fill="both", expand=True)

settings_label = ctk.CTkLabel(settings_frame, text="Settings", text_color=TEXT_COLOR, fg_color=BG_COLOR)
settings_label.grid(row=0, column=0, columnspan=2, pady=5)

temp_label = ctk.CTkLabel(settings_frame, text="Temperature:", text_color=TEXT_COLOR, fg_color=BG_COLOR)
temp_label.grid(row=1, column=0, pady=5, padx=5, sticky="w")

temp_entry = ctk.CTkEntry(settings_frame, width=50, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
temp_entry.grid(row=1, column=1, pady=5, padx=5, sticky="w")
temp_entry.insert(0, str(temperature))

tokens_label = ctk.CTkLabel(settings_frame, text="Max Tokens:", text_color=TEXT_COLOR, fg_color=BG_COLOR)
tokens_label.grid(row=2, column=0, pady=5, padx=5, sticky="w")

tokens_entry = ctk.CTkEntry(settings_frame, width=50, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
tokens_entry.grid(row=2, column=1, pady=5, padx=5, sticky="w")
tokens_entry.insert(0, str(max_tokens))

top_p_label = ctk.CTkLabel(settings_frame, text="Top P:", text_color=TEXT_COLOR, fg_color=BG_COLOR)
top_p_label.grid(row=3, column=0, pady=5, padx=5, sticky="w")

top_p_entry = ctk.CTkEntry(settings_frame, width=50, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
top_p_entry.grid(row=3, column=1, pady=5, padx=5, sticky="w")
top_p_entry.insert(0, str(top_p))

freq_penalty_label = ctk.CTkLabel(settings_frame, text="Frequency Penalty:", text_color=TEXT_COLOR, fg_color=BG_COLOR)
freq_penalty_label.grid(row=4, column=0, pady=5, padx=5, sticky="w")

freq_penalty_entry = ctk.CTkEntry(settings_frame, width=50, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
freq_penalty_entry.grid(row=4, column=1, pady=5, padx=5, sticky="w")
freq_penalty_entry.insert(0, str(frequency_penalty))

pres_penalty_label = ctk.CTkLabel(settings_frame, text="Presence Penalty:", text_color=TEXT_COLOR, fg_color=BG_COLOR)
pres_penalty_label.grid(row=5, column=0, pady=5, padx=5, sticky="w")

pres_penalty_entry = ctk.CTkEntry(settings_frame, width=50, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
pres_penalty_entry.grid(row=5, column=1, pady=5, padx=5, sticky="w")
pres_penalty_entry.insert(0, str(presence_penalty))

update_button = ctk.CTkButton(settings_frame, text="Update Settings", command=update_settings, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
update_button.grid(row=6, column=0, columnspan=2, pady=10)

theme_button = ctk.CTkButton(root, text="Toggle Theme", command=toggle_theme, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
theme_button.pack(pady=5)

voice_log_button = ctk.CTkButton(root, text="Play Voice Log", command=play_voice_log, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
voice_log_button.pack(pady=5)

# Start the GUI loop
root.mainloop()
import tkinter as tk
import customtkinter as ctk
import requests
import json
import threading
import datetime
import os
from gtts import gTTS
from playsound import playsound
from tkinter import filedialog, messagebox

# Local LLM server URL and port
server_url = 'http://192.168.1.187:9003/v1/chat/completions'

# Parameters
temperature = 0.7
max_tokens = 150
top_p = 1.0
frequency_penalty = 0.0
presence_penalty = 0.0

# User Profile
class UserProfile:
    def __init__(self, name, avatar):
        self.name = name
        self.avatar = avatar

# Dummy user profile (replace with actual implementation)
current_user = UserProfile(name="User", avatar="default_avatar.png")

# Conversation history
conversation_history = []

# Functions
def make_inference_request():
    global conversation_history
    # Request payload
    payload = {
        "messages": conversation_history,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        "stream": True
    }

    try:
        with requests.post(server_url, json=payload, headers={"Content-Type": "application/json"}, stream=True) as response:
            if response.status_code == 200:
                response_text = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            line_str = line_str[len('data: '):]

                        if line_str == '[DONE]':
                            break

                        try:
                            response_json = json.loads(line_str)
                            if 'choices' in response_json:
                                for choice in response_json['choices']:
                                    delta_content = choice.get('delta', {}).get('content', '')
                                    response_text += delta_content
                        except json.JSONDecodeError:
                            update_chat_window(f"Non-JSON response: {line_str}\n", sender="error")

                if response_text:
                    update_chat_window(response_text, sender="assistant")
                    speak(response_text)
            else:
                update_chat_window(f"Request failed with status code: {response.status_code}\n", sender="error")
                update_chat_window(f"Response: {response.text}\n", sender="error")
    except Exception as e:
        update_chat_window(f"An error occurred: {e}\n", sender="error")
    finally:
        loading_label.pack_forget()

def update_chat_window(message, sender="user"):
    chat_window.configure(state=ctk.NORMAL)
    if sender == "user":
        chat_window.insert(ctk.END, f"{current_user.name}: {message}\n", "user")
        conversation_history.append({"role": "user", "content": message})
    elif sender == "assistant":
        chat_window.insert(ctk.END, f"GPT: {message}\n", "assistant")
        conversation_history.append({"role": "assistant", "content": message})
    elif sender == "error":
        chat_window.insert(ctk.END, f"Error: {message}\n", "error")
    chat_window.configure(state=ctk.DISABLED)
    chat_window.yview(ctk.END)

def on_send(event=None):
    user_input = user_entry.get()
    if user_input.strip():
        update_chat_window(user_input, sender="user")
        loading_label.pack(pady=5)
        threading.Thread(target=make_inference_request).start()
        user_entry.delete(0, ctk.END)

def clear_chat():
    chat_window.configure(state=ctk.NORMAL)
    chat_window.delete(1.0, ctk.END)
    chat_window.configure(state=ctk.DISABLED)
    conversation_history.clear()

def update_settings():
    global temperature, max_tokens, top_p, frequency_penalty, presence_penalty
    try:
        temperature = float(temp_entry.get())
        max_tokens = int(tokens_entry.get())
        top_p = float(top_p_entry.get())
        frequency_penalty = float(freq_penalty_entry.get())
        presence_penalty = float(pres_penalty_entry.get())
        messagebox.showinfo("Settings Updated", "Settings have been updated successfully!")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numerical values for the settings.")

def save_chat():
    chat_text = chat_window.get(1.0, ctk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(chat_text)
        messagebox.showinfo("Chat Saved", "Chat history saved successfully!")

def speak(text):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        tts = gTTS(text=text, lang='en')
        
        voice_log_dir = "voice_logs"
        if not os.path.exists(voice_log_dir):
            os.makedirs(voice_log_dir)
        
        file_path = os.path.join(voice_log_dir, f"voice_log_{timestamp}.mp3")
        tts.save(file_path)
        
        playsound(file_path)
        
        # Optionally, log the file path to a text file for future reference
        with open(os.path.join(voice_log_dir, "voice_log_index.txt"), "a") as index_file:
            index_file.write(f"{timestamp}: {file_path}\n")
        
    except Exception as e:
        update_chat_window(f"Text-to-Speech Error: {e}\n", sender="error")

def toggle_theme():
    current_mode = ctk.get_appearance_mode()
    new_mode = "light" if current_mode == "dark" else "dark"
    ctk.set_appearance_mode(new_mode)

def play_voice_log():
    log_dir = "voice_logs"
    if not os.path.exists(log_dir):
        messagebox.showerror("Error", "No voice logs found.")
        return
    
    file_path = filedialog.askopenfilename(initialdir=log_dir, title="Select a Voice Log", filetypes=[("MP3 Files", "*.mp3")])
    if file_path:
        playsound(file_path)

# GUI setup
ctk.set_appearance_mode("dark")  # Keep it dark mode for a modern look
ctk.set_default_color_theme("dark-blue")  # This theme is darker and more sophisticated

# Color Customization
BG_COLOR = "#1f1f1f"  # Dark grey background
TEXT_COLOR = "#e0e0e0"  # Light grey text
BUTTON_COLOR = "#4a4a4a"  # Darker button
BUTTON_HOVER_COLOR = "#5a5a5a"  # Slightly lighter on hover

root = ctk.CTk()
root.title("Local LLM Chat")
root.geometry("800x700")
root.configure(bg=BG_COLOR)

# Chat frame
chat_frame = ctk.CTkFrame(root, fg_color=BG_COLOR)
chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

chat_window = ctk.CTkTextbox(chat_frame, wrap=ctk.WORD, state=ctk.DISABLED, width=580, height=400, text_color=TEXT_COLOR, bg_color=BG_COLOR)
chat_window.tag_config("user", foreground="#1e90ff")  # Dodger blue for user
chat_window.tag_config("assistant", foreground="#32cd32")  # Lime green for assistant
chat_window.tag_config("error", foreground="#ff4500")  # Orange red for errors
chat_window.pack(padx=10, pady=10, fill="both", expand=True)

# User entry frame
user_entry_frame = ctk.CTkFrame(root, fg_color=BG_COLOR)
user_entry_frame.pack(pady=5, padx=10, fill="x")

user_entry = ctk.CTkEntry(user_entry_frame, width=450, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
user_entry.grid(row=0, column=0, padx=10, pady=5)
user_entry.bind("<Return>", on_send)

send_button = ctk.CTkButton(user_entry_frame, text="Send", command=on_send, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
send_button.grid(row=0, column=1, padx=5, pady=5)

clear_button = ctk.CTkButton(user_entry_frame, text="Clear Chat", command=clear_chat, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
clear_button.grid(row=0, column=2, padx=5, pady=5)

save_button = ctk.CTkButton(user_entry_frame, text="Save Chat", command=save_chat, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
save_button.grid(row=0, column=3, padx=5, pady=5)

loading_label = ctk.CTkLabel(root, text="Loading...", text_color="gray", fg_color=BG_COLOR)

# Settings frame
settings_frame = ctk.CTkFrame(root, fg_color=BG_COLOR)
settings_frame.pack(pady=10, padx=10, fill="both", expand=True)

settings_label = ctk.CTkLabel(settings_frame, text="Settings", text_color=TEXT_COLOR, fg_color=BG_COLOR)
settings_label.grid(row=0, column=0, columnspan=2, pady=5)

temp_label = ctk.CTkLabel(settings_frame, text="Temperature:", text_color=TEXT_COLOR, fg_color=BG_COLOR)
temp_label.grid(row=1, column=0, pady=5, padx=5, sticky="w")

temp_entry = ctk.CTkEntry(settings_frame, width=50, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
temp_entry.grid(row=1, column=1, pady=5, padx=5, sticky="w")
temp_entry.insert(0, str(temperature))

tokens_label = ctk.CTkLabel(settings_frame, text="Max Tokens:", text_color=TEXT_COLOR, fg_color=BG_COLOR)
tokens_label.grid(row=2, column=0, pady=5, padx=5, sticky="w")

tokens_entry = ctk.CTkEntry(settings_frame, width=50, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
tokens_entry.grid(row=2, column=1, pady=5, padx=5, sticky="w")
tokens_entry.insert(0, str(max_tokens))

top_p_label = ctk.CTkLabel(settings_frame, text="Top P:", text_color=TEXT_COLOR, fg_color=BG_COLOR)
top_p_label.grid(row=3, column=0, pady=5, padx=5, sticky="w")

top_p_entry = ctk.CTkEntry(settings_frame, width=50, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
top_p_entry.grid(row=3, column=1, pady=5, padx=5, sticky="w")
top_p_entry.insert(0, str(top_p))

freq_penalty_label = ctk.CTkLabel(settings_frame, text="Frequency Penalty:", text_color=TEXT_COLOR, fg_color=BG_COLOR)
freq_penalty_label.grid(row=4, column=0, pady=5, padx=5, sticky="w")

freq_penalty_entry = ctk.CTkEntry(settings_frame, width=50, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
freq_penalty_entry.grid(row=4, column=1, pady=5, padx=5, sticky="w")
freq_penalty_entry.insert(0, str(frequency_penalty))

pres_penalty_label = ctk.CTkLabel(settings_frame, text="Presence Penalty:", text_color=TEXT_COLOR, fg_color=BG_COLOR)
pres_penalty_label.grid(row=5, column=0, pady=5, padx=5, sticky="w")

pres_penalty_entry = ctk.CTkEntry(settings_frame, width=50, text_color=TEXT_COLOR, bg_color=BUTTON_COLOR)
pres_penalty_entry.grid(row=5, column=1, pady=5, padx=5, sticky="w")
pres_penalty_entry.insert(0, str(presence_penalty))

update_button = ctk.CTkButton(settings_frame, text="Update Settings", command=update_settings, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
update_button.grid(row=6, column=0, columnspan=2, pady=10)

theme_button = ctk.CTkButton(root, text="Toggle Theme", command=toggle_theme, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
theme_button.pack(pady=5)

voice_log_button = ctk.CTkButton(root, text="Play Voice Log", command=play_voice_log, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
voice_log_button.pack(pady=5)

# Start the GUI loop
root.mainloop()
