import socket
import threading
import json

class Client:
    def __init__(self, host="127.0.0.1", port=5555):
        """Initialize client with host and port"""
        self.host = host
        self.port = port
        self.client_socket = None
        self.connected = False
        self.username = None
        self.role = None
        self.message_callback = None
        self.on_connect_callback = None
        self.on_disconnect_callback = None
    
    def connect(self):
        """Connect to the server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        self.connected = False
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        
        if self.on_disconnect_callback:
            self.on_disconnect_callback()
    
    def login(self, username, password):
        """Attempt to log in to the server"""
        if not self.connect():
            return False, "Could not connect to server"
        
        # Send login credentials
        login_data = {
            "type": "login",
            "username": username,
            "password": password
        }
        
        try:
            self.client_socket.send(json.dumps(login_data).encode('utf-8'))
            
            # Wait for response
            response_data = self.client_socket.recv(1024).decode('utf-8')
            response = json.loads(response_data)
            
            if response.get("success"):
                self.connected = True
                self.username = username
                self.role = response.get("role")
                
                # Start listening for messages
                receive_thread = threading.Thread(target=self.receive_messages)
                receive_thread.daemon = True
                receive_thread.start()
                
                if self.on_connect_callback:
                    self.on_connect_callback(self.username, self.role)
                
                return True, "Login successful"
            else:
                self.client_socket.close()
                return False, response.get("message", "Login failed")
        
        except Exception as e:
            self.client_socket.close()
            return False, f"Error during login: {e}"
    
    def receive_messages(self):
        """Continuously receive messages from the server"""
        while self.connected:
            try:
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                message_data = json.loads(data)
                
                # Process different message types
                if message_data.get("type") == "message":
                    if self.message_callback:
                        self.message_callback(
                            message_data.get("username"),
                            message_data.get("content"),
                            message_data.get("timestamp"),
                            message_data.get("system", False)
                        )
                
                elif message_data.get("type") == "message_history":
                    messages = message_data.get("messages", [])
                    for msg in messages:
                        if self.message_callback:
                            self.message_callback(
                                msg.get("username"),
                                msg.get("content"),
                                msg.get("timestamp"),
                                False
                            )
            
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        
        # If we exit the loop, connection is lost
        self.disconnect()
    
    def send_message(self, content):
        """Send a message to the server"""
        if not self.connected:
            return False
        
        message_data = {
            "type": "message",
            "content": content
        }
        
        try:
            self.client_socket.send(json.dumps(message_data).encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect()
            return False
    
    def set_message_callback(self, callback):
        """Set callback for received messages"""
        self.message_callback = callback
    
    def set_connect_callback(self, callback):
        """Set callback for successful connection"""
        self.on_connect_callback = callback
    
    def set_disconnect_callback(self, callback):
        """Set callback for disconnection"""
        self.on_disconnect_callback = callback