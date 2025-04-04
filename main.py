import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

class StickShapeDetector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stick Shape Detector")
        self.root.configure(bg='#e0e0e0')
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        
        # Display parameters
        self.cell_size = 50  # Pixels per grid unit (visual scaling)
        self.max_size = 10   # Max number of sticks (each 1 unit long, even counts only)
        self.show_optimized = False
        
        # Cost parameters (constants)
        self.red_cost_per_stick = 2.50  # Cost per red stick (1 unit long)
        self.blue_cost_per_stick = 3.00 # Cost per blue stick (1 unit long)
        self.budget = 30.00             # Total budget in dollars
        
        # Setup GUI
        self.setup_gui()
        
        # Stick tracking
        self.red_sticks = 0
        self.blue_sticks = 0
        
        self.update()
        self.root.mainloop()