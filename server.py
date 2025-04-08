import socket
import threading
import json
import datetime
from database import Database

class Server:
    def __init__(self, host="0.0.0.0", port=5555):
        """Initialize server with host and port"""
        # Set up server properties
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.db = Database()
        self.running = False
        
    def start(self):
        """Start the server"""
        # Bind the server socket and start listening for connections
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"Server started on {self.host}:{self.port}")
        
        # Start accepting client connections
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()
        
        return True
    
    def stop(self):
        """Stop the server"""
        # Close the server socket and disconnect all clients
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        # Disconnect all clients
        for client in self.clients[:]:
            client["socket"].close()
        
        self.clients = []
        print("Server stopped")
        
    def accept_connections(self):
        """Accept incoming client connections"""
        # Listen for new client connections and handle them
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address}")
                
                # Start a thread to handle this client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def handle_client(self, client_socket, address):
        """Handle communication with a connected client"""
        # Authenticate the client and process their messages
        username = None
        
        try:
            # First message should be login credentials
            data = client_socket.recv(1024).decode('utf-8')
            login_data = json.loads(data)
            
            if login_data.get("type") == "login":
                username = login_data.get("username")
                password = login_data.get("password")
                
                # Verify credentials
                user = self.db.get_user(username)
                
                if user and self.verify_login(user, password):
                    # Login successful
                    response = {
                        "type": "login_response",
                        "success": True,
                        "role": user["role"]
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                    # Add to clients list
                    self.clients.append({
                        "socket": client_socket,
                        "username": username,
                        "role": user["role"]
                    })
                    
                    # Send recent message history
                    self.send_message_history(client_socket)
                    
                    # Broadcast that a new user joined
                    self.broadcast_message(username, f"{username} has joined the chat", system=True)
                    
                    # Handle messages from this client
                    self.handle_messages(client_socket, username)
                else:
                    # Login failed
                    response = {
                        "type": "login_response",
                        "success": False,
                        "message": "Invalid username or password"
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    client_socket.close()
            else:
                client_socket.close()
        
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            # Remove from clients list
            self.clients = [c for c in self.clients if c["socket"] != client_socket]
            
            if username:
                # Broadcast that user left
                self.broadcast_message(username, f"{username} has left the chat", system=True)
            
            if client_socket:
                client_socket.close()
    
    def verify_login(self, user, password):
        """Verify login credentials"""
        # Check the provided password against the stored hash
        from utils import verify_password
        return verify_password(user["password"], password)
    
    def handle_messages(self, client_socket, username):
        """Handle incoming messages from a client"""
        # Process and broadcast messages from the client
        while self.running:
            try:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                message_data = json.loads(data)
                
                if message_data.get("type") == "message":
                    content = message_data.get("content")
                    
                    # Broadcast the message to all clients
                    self.broadcast_message(username, content)
                    
            except Exception as e:
                print(f"Error receiving message from {username}: {e}")
                break
    
    def broadcast_message(self, username, content, system=False):
        """Broadcast a message to all connected clients"""
        # Send a message to all connected clients
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to database (unless it's a system message)
        if not system:
            self.db.save_message(username, content, timestamp)
        
        # Create message packet
        message_packet = {
            "type": "message",
            "username": "SYSTEM" if system else username,
            "timestamp": timestamp,
            "content": content,
            "system": system
        }
        
        packet_json = json.dumps(message_packet)
        
        # Send to all clients
        for client in self.clients[:]:
            try:
                client["socket"].send(packet_json.encode('utf-8'))
            except Exception:
                # If sending fails, this client is probably disconnected
                pass
    
    def send_message_history(self, client_socket):
        """Send message history to a newly connected client"""
        # Retrieve and send the last 100 messages to the client
        messages = self.db.get_messages(100)  # Get last 100 messages
        
        history_packet = {
            "type": "message_history",
            "messages": messages
        }
        
        try:
            client_socket.send(json.dumps(history_packet).encode('utf-8'))
        except Exception as e:
            print(f"Error sending message history: {e}")