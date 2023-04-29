import tkinter as tk
import openai #you must install openai library

root= tk.Tk()
BG_ = '#218850' #Enter your favorite color for background, in hex format here
FG_ = '#E6E1FF' #Enter your favorite color for foreground, in hex format here

window = tk.Canvas(root, width=500, height=1000, relief='raised', bg=BG_)
window.pack(fill='x')

label1 = tk.Label(root, text='Make your query:')
label1.config(font=('helvetica', 22, 'bold'), bg=BG_, fg=FG_)
window.create_window(250, 125, window=label1)

label3 = tk.Label(root, text=' ', font=('helvetica', 14), bg=BG_, fg='blue')
window.create_window(250, 350, window=label3)
    
label4 = tk.Label(root, text=' ', font=('helvetica', 12, 'bold'), bg=BG_, )
window.create_window(250, 380, window=label4)

entry1 = tk.Entry(root)
entry1.config(font=('helvetica', 14), bg=FG_, fg='blue')
window.create_window(250, 240, window=entry1)

openai.api_key = "YOUR VERY OWN API KEY FROM OPENAI HERE"

def query():
    global label3
    global label4
    label3.destroy()
    label4.destroy()
    prompt = entry1.get()
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=2000,
        top_p=1.0,
        n=1)
    response_text = response["choices"][0]["text"]
    print(len(response_text))
    print(response_text)
    label3 = tk.Label(root, text=prompt,
                      font=('helvetica', 14), bg=BG_, fg='blue')
    window.create_window(250, 350, window=label3)
    
    label4 = tk.Label(root, text=response_text, wraplength=360,
                      anchor="n", bg=BG_, fg=FG_, font=('helvetica', 12))
    window.create_window(250, 700, window=label4)
    
button1 = tk.Button(text='Enter',
                    command=query, bg='blue',
                    fg=FG_, font=('helvetica', 12, 'bold'))
window.create_window(250, 300, window=button1)

root.mainloop()
