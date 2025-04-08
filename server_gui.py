import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import socket
from utils import validate_username, validate_password
from database import Database
from server import Server

class ServerGUI:
    def __init__(self, root):
        """Initialize the server GUI"""
        self.root = root
        self.root.title("Forum Server")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.db = Database()
        self.server = None
        
        # Create frames
        self.create_login_frame()
        self.create_main_frame()
        
        # Show login frame first
        self.show_login_frame()
    
    def create_login_frame(self):
        """Create the admin login frame"""
        self.login_frame = ttk.Frame(self.root, padding=20)
        
        # Login title
        ttk.Label(self.login_frame, text="Admin Login", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Username
        ttk.Label(self.login_frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar(value="admin")
        ttk.Entry(self.login_frame, textvariable=self.username_var).grid(row=1, column=1, sticky="ew", pady=5)
        
        # Password
        ttk.Label(self.login_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(self.login_frame, textvariable=self.password_var, show="*").grid(row=2, column=1, sticky="ew", pady=5)
        
        # Login button
        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=3, column=0, columnspan=2, pady=20)
    
    def create_main_frame(self):
        """Create the main server admin frame"""
        self.main_frame = ttk.Frame(self.root, padding=20)
        
        # Create tabs
        self.tabs = ttk.Notebook(self.main_frame)
        self.tabs.pack(fill=tk.BOTH, expand=True)
        
        # Register users tab
        self.register_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.register_tab, text="Register Users")
        
        # Server control tab
        self.server_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.server_tab, text="Server Control")
        
        # Set up register form
        self.setup_register_form()
        
        # Set up server control
        self.setup_server_control()
        
    def setup_register_form(self):
        """Setup the user registration form"""
        # Title
        ttk.Label(self.register_tab, text="Register New User", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # Username
        ttk.Label(self.register_tab, text="Username:").grid(row=1, column=0, sticky="w", pady=5)
        self.new_username_var = tk.StringVar()
        ttk.Entry(self.register_tab, textvariable=self.new_username_var).grid(row=1, column=1, sticky="ew", pady=5)
        
        # Password
        ttk.Label(self.register_tab, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.new_password_var = tk.StringVar()
        ttk.Entry(self.register_tab, textvariable=self.new_password_var, show="*").grid(row=2, column=1, sticky="ew", pady=5)
        
        # Role
        ttk.Label(self.register_tab, text="Role:").grid(row=3, column=0, sticky="w", pady=5)
        self.role_var = tk.StringVar(value="user")
        role_combo = ttk.Combobox(self.register_tab, textvariable=self.role_var, values=["user", "admin"], state="readonly")
        role_combo.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Register button
        ttk.Button(self.register_tab, text="Register User", command=self.register_user).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Users list
        ttk.Label(self.register_tab, text="Registered Users:", font=("Helvetica", 12)).grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
        
        # Create a treeview for users
        self.users_tree = ttk.Treeview(self.register_tab, columns=("username", "role"), show="headings")
        self.users_tree.heading("username", text="Username")
        self.users_tree.heading("role", text="Role")
        self.users_tree.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=5)
        
        # Add scroll bar to tree view
        scrollbar = ttk.Scrollbar(self.register_tab, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=6, column=2, sticky="ns")
        
        # Configure grid weights
        self.register_tab.grid_columnconfigure(1, weight=1)
        self.register_tab.grid_rowconfigure(6, weight=1)
    
    def setup_server_control(self):
        """Setup server control interface"""
        # Server status
        ttk.Label(self.server_tab, text="Server Status:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.status_var = tk.StringVar(value="Not Running")
        ttk.Label(self.server_tab, textvariable=self.status_var, font=("Helvetica", 12, "bold")).grid(row=0, column=1, sticky="w", pady=5)
        
        # Start/Stop button
        self.server_button_var = tk.StringVar(value="Start Server")
        self.server_button = ttk.Button(
            self.server_tab, 
            textvariable=self.server_button_var, 
            command=self.toggle_server
        )
        self.server_button.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Server log
        ttk.Label(self.server_tab, text="Server Log:", font=("Helvetica", 12)).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        self.log_text = scrolledtext.ScrolledText(self.server_tab, height=15, wrap=tk.WORD)
        self.log_text.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Connected clients
        ttk.Label(self.server_tab, text="Connected Clients:", font=("Helvetica", 12)).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
        
        self.clients_tree = ttk.Treeview(self.server_tab, columns=("username", "role"), show="headings")
        self.clients_tree.heading("username", text="Username")
        self.clients_tree.heading("role", text="Role")
        self.clients_tree.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=5)
        
        # Configure grid weights
        self.server_tab.grid_columnconfigure(1, weight=1)
        self.server_tab.grid_rowconfigure(3, weight=1)
        self.server_tab.grid_rowconfigure(5, weight=1)
        
        # Redirect standard output to log
        import sys
        self.original_stdout = sys.stdout
        sys.stdout = self
    
    def write(self, text):
        """Redirect stdout to the log text widget"""
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, text)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    def flush(self):
        """Required for stdout redirection"""
        pass
    
    def show_login_frame(self):
        """Show the login frame"""
        self.main_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_main_frame(self):
        """Show the main admin frame"""
        self.login_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.load_users()
    
    def login(self):
        """Verify admin login"""
        username = self.username_var.get()
        password = self.password_var.get()
        
        user = self.db.get_user(username)
        
        if user and user["role"] == "admin":
            from utils import verify_password
            if verify_password(user["password"], password):
                self.show_main_frame()
                return
        
        messagebox.showerror("Login Failed", "Invalid admin credentials!")
    
    def register_user(self):
        """Register a new user"""
        username = self.new_username_var.get()
        password = self.new_password_var.get()
        role = self.role_var.get()
        
        # Validate input
        if not validate_username(username):
            messagebox.showerror("Error", "Invalid username! Must be 3-20 characters, alphanumeric and underscores only.")
            return
        
        if not validate_password(password):
            messagebox.showerror("Error", "Invalid password! Must be at least 8 characters.")
            return
        
        # Add user to database
        if self.db.add_user(username, password, role):
            messagebox.showinfo("Success", f"User '{username}' registered successfully!")
            
            # Clear form
            self.new_username_var.set("")
            self.new_password_var.set("")
            self.role_var.set("user")
            
            # Refresh users list
            self.load_users()
        else:
            messagebox.showerror("Error", f"Username '{username}' already exists!")
    
    def load_users(self):
        """Load users from database into the tree view"""
        # Clear current items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Connect to database
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Get users
        cursor.execute("SELECT username, role FROM users ORDER BY username")
        users = cursor.fetchall()
        
        # Add to tree
        for user in users:
            self.users_tree.insert("", tk.END, values=(user["username"], user["role"]))
        
        conn.close()
    
    def toggle_server(self):
        """Start or stop the server"""
        if self.server and self.server.running:
            # Stop server
            self.server.stop()
            self.server = None
            self.status_var.set("Not Running")
            self.server_button_var.set("Start Server")
            
            # Clear clients tree
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
        else:
            # Start server
            self.server = Server()
            if self.server.start():
                self.status_var.set("Running")
                self.server_button_var.set("Stop Server")
                
                # Start a thread to update clients list
                update_thread = threading.Thread(target=self.update_clients_list)
                update_thread.daemon = True
                update_thread.start()
    
    def update_clients_list(self):
        """Update the connected clients list periodically"""
        import time
        while self.server and self.server.running:
            # Clear current items
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            
            # Add current clients
            for client in self.server.clients:
                self.clients_tree.insert("", tk.END, values=(client["username"], client["role"]))
            
            time.sleep(2)  # Update every 2 seconds
    
    def on_close(self):
        """Handle window close event"""
        if self.server and self.server.running:
            if messagebox.askyesno("Exit", "Server is running. Stop server and exit?"):
                self.server.stop()
                self.root.destroy()
        else:
            self.root.destroy()
        
        # Restore original stdout
        import sys
        sys.stdout = self.original_stdout