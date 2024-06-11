import socket
import threading
import sqlite3

# Database setup
conn = sqlite3.connect('chat_users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()

def register_user(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    if result and result[0] == password:
        return True
    return False

clients = []

def handle_client(client_socket, client_address):
    print(f"New connection from {client_address}")
    username = client_socket.recv(1024).decode('utf-8')
    
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"{username}: {message}")
            for client in clients:
                if client != client_socket:
                    client.send(f"{username}: {message}".encode('utf-8'))
        except:
            break

    print(f"Connection closed: {username}")
    clients.remove(client_socket)
    client_socket.close()

def server_program():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))
    server.listen(5)
    print("Server listening on port 5555")

    while True:
        client_socket, client_address = server.accept()
        clients.append(client_socket)
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()

if __name__ == "__main__":
    server_program()
