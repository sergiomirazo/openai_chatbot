import tkinter as tk
import openai
openai.api_key = "YOUR_VERY_OWN_API_KEY" #Replace with your openai API key

def query(text):
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo-0301',  # Replace with your favorite engine model
        messages=[
        {"role": "system", "content": "Act like Nicole, a 25 years old woman expert in digital marketing and web development"},
        {"role": "user", "content": f"{text}"},
    ],
    )
    response_text = response.choices[0].message.content
    print(response_text)
    return response_text

def send_message():
    message = entry_message.get()
    post_user_message(message)
    entry_message.delete(0, tk.END)

def post_user_message(message):
    user_message = tk.Label(chat_frame, text=message, bg='#87f5a8', wraplength=250, anchor='e')
    user_message.pack(pady=5, padx=10, anchor='e')
    post_chatbot_message(message)

def post_chatbot_message(message):
    response = query(message)
    chatbot_message = tk.Label(chat_frame, text=response, bg='#b5f7f6', wraplength=250, anchor='w')
    chatbot_message.pack(pady=5, padx=10, anchor='w')

# Home window
window = tk.Tk()
window.title("Chatbot")
window.geometry("400x600")

# Chat frame
chat_frame = tk.Frame(window, bg='#01000f')
chat_frame.pack(fill=tk.BOTH, expand=True)

# Scrollbar
scrollbar = tk.Scrollbar(chat_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Entry bar
entry_frame = tk.Frame(window, bg='#f2f2f7')
entry_frame.pack(fill=tk.X, padx=10, pady=5)

entry_message = tk.Entry(entry_frame, bg='#01000f', fg='#b5f7f6', width=50)
entry_message.pack(side=tk.LEFT, padx=5, pady=5)

send_button = tk.Button(entry_frame, text="Send", command=send_message, bg='#2c8f54', fg='#b5f7f6', relief=tk.FLAT)
send_button.pack(side=tk.RIGHT, padx=5)

# Quick start
post_chatbot_message("Hi there!")

window.mainloop()
