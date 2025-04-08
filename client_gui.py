import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from client import Client
import datetime

class ClientGUI:
    def __init__(self, root):
        """Initialize the client GUI"""
        self.root = root
        self.root.title("Forum Client")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.client = Client()
        
        # Create frames
        self.create_login_frame()
        self.create_chat_frame()
        
        # Show login frame first
        self.show_login_frame()
    
    def create_login_frame(self):
        """Create the login frame"""
        self.login_frame = ttk.Frame(self.root, padding=20)
        
        # Login title
        ttk.Label(self.login_frame, text="Login", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Server info
        ttk.Label(self.login_frame, text="Server IP:").grid(row=1, column=0, sticky="w", pady=5)
        self.server_ip_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(self.login_frame, textvariable=self.server_ip_var).grid(row=1, column=1, sticky="ew", pady=5)
        
        ttk.Label(self.login_frame, text="Server Port:").grid(row=2, column=0, sticky="w", pady=5)
        self.server_port_var = tk.StringVar(value="5555")
        ttk.Entry(self.login_frame, textvariable=self.server_port_var).grid(row=2, column=1, sticky="ew", pady=5)
        
        # Username
        ttk.Label(self.login_frame, text="Username:").grid(row=3, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(self.login_frame, textvariable=self.username_var).grid(row=3, column=1, sticky="ew", pady=5)
        
        # Password
        ttk.Label(self.login_frame, text="Password:").grid(row=4, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(self.login_frame, textvariable=self.password_var, show="*").grid(row=4, column=1, sticky="ew", pady=5)
        
        # Login button
        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=5, column=0, columnspan=2, pady=20)
        
        # Status message
        self.status_var = tk.StringVar()
        ttk.Label(self.login_frame, textvariable=self.status_var, foreground="red").grid(row=6, column=0, columnspan=2, pady=5)
        
        # Configure grid weights
        self.login_frame.grid_columnconfigure(1, weight=1)
    
    def create_chat_frame(self):
        """Create the chat frame"""
        self.chat_frame = ttk.Frame(self.root, padding=10)
        
        # Chat header
        self.header_frame = ttk.Frame(self.chat_frame)
        self.header_frame.pack(fill=tk.X, pady=5)
        
        # User info
        self.user_info_var = tk.StringVar()
        ttk.Label(self.header_frame, textvariable=self.user_info_var, font=("Helvetica", 12)).pack(side=tk.LEFT)
        
        # Logout button
        ttk.Button(self.header_frame, text="Logout", command=self.logout).pack(side=tk.RIGHT)
        
        # Messages area
        self.messages_frame = ttk.Frame(self.chat_frame)
        self.messages_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.messages_text = scrolledtext.ScrolledText(self.messages_frame, wrap=tk.WORD)
        self.messages_text.pack(fill=tk.BOTH, expand=True)
        self.messages_text.config(state=tk.DISABLED)
        
        # Message input area
        self.input_frame = ttk.Frame(self.chat_frame)
        self.input_frame.pack(fill=tk.X, pady=5)
        
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(self.input_frame, textvariable=self.message_var)
        self.message_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.message_entry.bind("<Return>", self.send_message)
        
        ttk.Button(self.input_frame, text="Send", command=self.send_message).pack(side=tk.RIGHT, padx=5)
    
    def show_login_frame(self):
        """Show the login frame"""
        self.chat_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_chat_frame(self):
        """Show the chat frame"""
        self.login_frame.pack_forget()
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        self.message_entry.focus()
    
    def login(self):
        """Attempt to login to the server"""
        username = self.username_var.get()
        password = self.password_var.get()
        server_ip = self.server_ip_var.get()
        
        try:
            server_port = int(self.server_port_var.get())
        except ValueError:
            self.status_var.set("Invalid port number")
            return
        
        # Validate input
        if not username or not password:
            self.status_var.set("Please enter username and password")
            return
        
        # Update client connection details
        self.client = Client(server_ip, server_port)
        
        # Set callbacks
        self.client.set_message_callback(self.on_message_received)
        self.client.set_connect_callback(self.on_connected)
        self.client.set_disconnect_callback(self.on_disconnected)
        
        # Attempt login
        self.status_var.set("Connecting...")
        success, message = self.client.login(username, password)
        
        if success:
            self.show_chat_frame()
        else:
            self.status_var.set(message)
    
    def logout(self):
        """Logout from the server"""
        if self.client:
            self.client.disconnect()
        
        self.show_login_frame()
        self.status_var.set("")
        self.clear_messages()
    
    def on_connected(self, username, role):
        """Callback when connected to server"""
        self.user_info_var.set(f"Logged in as: {username} ({role})")
        self.root.title(f"Forum Client - {username}")
    
    def on_disconnected(self):
        """Callback when disconnected from server"""
        messagebox.showinfo("Disconnected", "You have been disconnected from the server.")
        self.show_login_frame()
    
    def on_message_received(self, username, content, timestamp, system=False):
        """Handle received message"""
        self.messages_text.config(state=tk.NORMAL)
        
        # Format timestamp
        try:
            # Parse the datetime string
            dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            # Format it in a more readable way
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = timestamp
        
        # Add the message with formatting
        if system:
            self.messages_text.insert(tk.END, f"[{time_str}] ", "time")
            self.messages_text.insert(tk.END, f"{content}\n", "system")
        else:
            self.messages_text.insert(tk.END, f"[{time_str}] ", "time")
            self.messages_text.insert(tk.END, f"{username}: ", "username")
            self.messages_text.insert(tk.END, f"{content}\n", "message")
        
        # Configure tags
        self.messages_text.tag_configure("time", foreground="gray")
        self.messages_text.tag_configure("username", foreground="blue", font=("Helvetica", 10, "bold"))
        self.messages_text.tag_configure("message", foreground="black")
        self.messages_text.tag_configure("system", foreground="green", font=("Helvetica", 10, "italic"))
        
        # Scroll to bottom
        self.messages_text.see(tk.END)
        self.messages_text.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Send a message to the server"""
        content = self.message_var.get().strip()
        if content:
            if self.client.send_message(content):
                self.message_var.set("")  # Clear input field
            else:
                messagebox.showerror("Error", "Failed to send message. You may be disconnected.")
        return "break"  # Prevent default behavior for Enter key
    
    def clear_messages(self):
        """Clear the messages area"""
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete(1.0, tk.END)
        self.messages_text.config(state=tk.DISABLED)
    
    def on_close(self):
        """Handle window close event"""
        if self.client and self.client.connected:
            if messagebox.askyesno("Exit", "Disconnect and exit?"):
                self.client.disconnect()
                self.root.destroy()
        else:
            self.root.destroy()