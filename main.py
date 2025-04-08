#!/usr/bin/env python3
import tkinter as tk

if __name__ == "__main__":
    # Import the Launcher class
    from  launcher import Launcher

    
    # Create the root window
    root = tk.Tk()
    
    # Create the launcher application
    app = Launcher(root)
    
    # Start the main event loop
    root.mainloop()