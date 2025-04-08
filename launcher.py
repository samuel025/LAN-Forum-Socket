import tkinter as tk
from tkinter import ttk
import sys
import os

class Launcher:
    def __init__(self, root):
        """Initialize the launcher GUI"""
        self.root = root
        self.root.title("LAN Forum Launcher")
        self.root.geometry("400x300")
        
        # Center the window
        window_width = 400
        window_height = 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create a frame with some padding
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        ttk.Label(
            main_frame,
            text="LAN Forum Application",
            font=("Helvetica", 18)
        ).pack(pady=20)
        
        # Description
        ttk.Label(
            main_frame,
            text="Choose a mode to start the application:",
            font=("Helvetica", 12)
        ).pack(pady=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # Server button
        server_btn = ttk.Button(
            buttons_frame,
            text="Start as Server",
            command=self.start_server,
            padding=10
        )
        server_btn.pack(fill=tk.X, pady=5)
        
        # Client button
        client_btn = ttk.Button(
            buttons_frame,
            text="Start as Client",
            command=self.start_client,
            padding=10
        )
        client_btn.pack(fill=tk.X, pady=5)
        
        # Exit button
        exit_btn = ttk.Button(
            main_frame,
            text="Exit",
            command=root.destroy,
            padding=5
        )
        exit_btn.pack(side=tk.BOTTOM, pady=10)
    
    def start_server(self):
        """Start the application in server mode"""
        self.root.destroy()
        
        # Import server GUI
        from server_gui import ServerGUI
        
        # Create a new root window
        server_root = tk.Tk()
        server_app = ServerGUI(server_root)
        server_root.mainloop()
    
    def start_client(self):
        """Start the application in client mode"""
        self.root.destroy()
        
        # Import client GUI
        from client_gui import ClientGUI
        
        # Create a new root window
        client_root = tk.Tk()
        client_app = ClientGUI(client_root)
        client_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = Launcher(root)
    root.mainloop()