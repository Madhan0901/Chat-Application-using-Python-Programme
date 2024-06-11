import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

class AuthClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Login")
        
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        
        tk.Label(root, text="Username:").pack(pady=5)
        tk.Entry(root, textvariable=self.username).pack(pady=5)
        tk.Label(root, text="Password:").pack(pady=5)
        tk.Entry(root, textvariable=self.password, show='*').pack(pady=5)
        
        tk.Button(root, text="Login", command=self.login).pack(pady=10)
        tk.Button(root, text="Register", command=self.register).pack(pady=5)
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 5555))
    
    def login(self):
        username = self.username.get()
        password = self.password.get()
        self.client_socket.send(f"LOGIN:{username}:{password}".encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        if response == "OK":
            self.root.destroy()
            self.open_chat_window(username)
        else:
            messagebox.showerror("Error", "Invalid credentials")
    
    def register(self):
        username = self.username.get()
        password = self.password.get()
        self.client_socket.send(f"REGISTER:{username}:{password}".encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        if response == "OK":
            messagebox.showinfo("Success", "Registration successful")
        else:
            messagebox.showerror("Error", "Username already exists")

    def open_chat_window(self, username):
        chat_root = tk.Tk()
        ChatClient(chat_root, self.client_socket, username)
        chat_root.mainloop()

class ChatClient:
    def __init__(self, root, client_socket, username):
        self.root = root
        self.root.title("Chat Application")
        
        self.client_socket = client_socket
        self.username = username
        
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.chat_area.pack(padx=20, pady=10)
        self.chat_area.config(state=tk.DISABLED)
        
        self.msg_entry = tk.Entry(self.root)
        self.msg_entry.pack(padx=20, pady=10)
        self.msg_entry.bind("<Return>", self.send_message)
        
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def send_message(self, event):
        message = self.msg_entry.get()
        self.msg_entry.delete(0, tk.END)
        if message:
            self.client_socket.send(f"{self.username}: {message}".encode('utf-8'))
    
    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.chat_area.config(state=tk.NORMAL)
                    self.chat_area.insert(tk.END, message + "\n")
                    self.chat_area.yview(tk.END)
                    self.chat_area.config(state=tk.DISABLED)
                else:
                    break
            except:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthClient(root)
    root.mainloop()
