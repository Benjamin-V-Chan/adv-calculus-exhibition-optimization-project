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
        

    def setup_gui(self):
        self.main_frame = tk.Frame(self.root, bg='#e0e0e0')
        self.main_frame.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame, bg='#e0e0e0')
        self.left_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        self.canvas_frame = tk.LabelFrame(self.left_frame, text="Rectangle Display", 
                                        bg='white', font=('Arial', 12, 'bold'), 
                                        relief=tk.GROOVE, bd=2)
        self.canvas_frame.pack(pady=5)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=self.max_size*self.cell_size, 
                              height=self.max_size*self.cell_size, bg='white')
        self.canvas.pack(pady=5)
        
        self.opt_btn = tk.Button(self.canvas_frame, text="Show Optimized Area", 
                               command=self.toggle_optimized, bg='#2196F3', fg='white',
                               font=('Arial', 10, 'bold'), relief=tk.RAISED, bd=3)
        self.opt_btn.pack(pady=5)
        
        self.constants_frame = tk.LabelFrame(self.left_frame, text="Constants", 
                                           bg='#f5f5f5', font=('Arial', 12, 'bold'),
                                           relief=tk.GROOVE, bd=2)
        self.constants_frame.pack(pady=5, fill=tk.X)
        
        self.const_budget = tk.Label(self.constants_frame, 
                                   text=f"Budget: ${self.budget:.2f}", 
                                   bg='#f5f5f5', font=('Arial', 10), anchor='w')
        self.const_budget.pack(fill=tk.X, padx=5, pady=1)
        
        self.const_red_cost = tk.Label(self.constants_frame, 
                                     text=f"Red Stick Cost: ${self.red_cost_per_stick:.2f} (1 unit)", 
                                     bg='#f5f5f5', font=('Arial', 10), fg='#d32f2f', anchor='w')
        self.const_red_cost.pack(fill=tk.X, padx=5, pady=1)
        
        self.const_blue_cost = tk.Label(self.constants_frame, 
                                      text=f"Blue Stick Cost: ${self.blue_cost_per_stick:.2f} (1 unit)", 
                                      bg='#f5f5f5', font=('Arial', 10), fg='#1976d2', anchor='w')
        self.const_blue_cost.pack(fill=tk.X, padx=5, pady=1)
        
        self.const_max_size = tk.Label(self.constants_frame, 
                                     text=f"Max Sticks: {self.max_size} (even only)", 
                                     bg='#f5f5f5', font=('Arial', 10), anchor='w')
        self.const_max_size.pack(fill=tk.X, padx=5, pady=1)
        
        self.right_frame = tk.Frame(self.main_frame, bg='#e0e0e0')
        self.right_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)
        
        self.camera_frame = tk.LabelFrame(self.right_frame, text="Camera Feed", 
                                        bg='white', font=('Arial', 12, 'bold'),
                                        relief=tk.GROOVE, bd=2)
        self.camera_frame.pack(pady=5, fill=tk.X)
        
        self.camera_label = tk.Label(self.camera_frame, bg='white')
        self.camera_label.pack(pady=5)
        
        self.info_frame = tk.LabelFrame(self.right_frame, text="Analysis Dashboard", 
                                      bg='#f5f5f5', font=('Arial', 14, 'bold'),
                                      relief=tk.GROOVE, bd=2)
        self.info_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        self.red_count = tk.Label(self.info_frame, text="Red Sticks: 0", bg='#f5f5f5',
                                font=('Arial', 12), fg='#d32f2f', anchor='w')
        self.red_count.pack(fill=tk.X, padx=10, pady=2)
        
        self.red_cost = tk.Label(self.info_frame, text="Red Cost: $0.00", bg='#f5f5f5',
                               font=('Arial', 12), fg='#d32f2f', anchor='w')
        self.red_cost.pack(fill=tk.X, padx=10, pady=2)
        
        self.blue_count = tk.Label(self.info_frame, text="Blue Sticks: 0", bg='#f5f5f5',
                                 font=('Arial', 12), fg='#1976d2', anchor='w')
        self.blue_count.pack(fill=tk.X, padx=10, pady=2)
        
        self.blue_cost = tk.Label(self.info_frame, text="Blue Cost: $0.00", bg='#f5f5f5',
                                font=('Arial', 12), fg='#1976d2', anchor='w')
        self.blue_cost.pack(fill=tk.X, padx=10, pady=2)
        
        self.area_label = tk.Label(self.info_frame, text="Area: 0 units²", bg='#f5f5f5',
                                 font=('Arial', 12), anchor='w')
        self.area_label.pack(fill=tk.X, padx=10, pady=2)
        
        self.total_cost = tk.Label(self.info_frame, text="Total Cost: $0.00", bg='#f5f5f5',
                                 font=('Arial', 12, 'bold'), fg='#388e3c', anchor='w')
        self.total_cost.pack(fill=tk.X, padx=10, pady=2)
        
        self.opt_red_count = tk.Label(self.info_frame, text="", bg='#f5f5f5',
                                    font=('Arial', 12, 'italic'), fg='#d32f2f', anchor='w')
        self.opt_red_count.pack(fill=tk.X, padx=10, pady=2)
        
        self.opt_red_cost = tk.Label(self.info_frame, text="", bg='#f5f5f5',
                                   font=('Arial', 12, 'italic'), fg='#d32f2f', anchor='w')
        self.opt_red_cost.pack(fill=tk.X, padx=10, pady=2)
        
        self.opt_blue_count = tk.Label(self.info_frame, text="", bg='#f5f5f5',
                                     font=('Arial', 12, 'italic'), fg='#1976d2', anchor='w')
        self.opt_blue_count.pack(fill=tk.X, padx=10, pady=2)
        
        self.opt_blue_cost = tk.Label(self.info_frame, text="", bg='#f5f5f5',
                                    font=('Arial', 12, 'italic'), fg='#1976d2', anchor='w')
        self.opt_blue_cost.pack(fill=tk.X, padx=10, pady=2)
        
        self.opt_area = tk.Label(self.info_frame, text="", bg='#f5f5f5',
                               font=('Arial', 12, 'italic'), anchor='w')
        self.opt_area.pack(fill=tk.X, padx=10, pady=2)
        
        self.opt_total_cost = tk.Label(self.info_frame, text="", bg='#f5f5f5',
                                     font=('Arial', 12, 'bold', 'italic'), fg='#388e3c', anchor='w')
        self.opt_total_cost.pack(fill=tk.X, padx=10, pady=2)
        
    def toggle_optimized(self):
        self.show_optimized = not self.show_optimized
        self.opt_btn.config(text="Hide Optimized Area" if self.show_optimized else "Show Optimized Area")
        if not self.show_optimized:
            self.opt_red_count.config(text="")
            self.opt_red_cost.config(text="")
            self.opt_blue_count.config(text="")
            self.opt_blue_cost.config(text="")
            self.opt_area.config(text="")
            self.opt_total_cost.config(text="")

    def detect_sticks(self, frame):
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
        red_lower1 = np.array([0, 120, 70])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([170, 120, 70])
        red_upper2 = np.array([180, 255, 255])
        blue_lower = np.array([100, 150, 0])
        blue_upper = np.array([140, 255, 255])
        
        red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        
        kernel = np.ones((5,5), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
        
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        self.red_sticks = 0
        self.blue_sticks = 0