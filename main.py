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

        for contour in red_contours:
            if cv2.contourArea(contour) > 200:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w)/h if w > h else float(h)/w
                if aspect_ratio > 2.0:
                    self.red_sticks += 1  # Each stick is 1 unit long
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        for contour in blue_contours:
            if cv2.contourArea(contour) > 200:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w)/h if w > h else float(h)/w
                if aspect_ratio > 2.0:
                    self.blue_sticks += 1  # Each stick is 1 unit long
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Ensure even numbers of sticks (round down to nearest even number)
        self.red_sticks = min(self.red_sticks - (self.red_sticks % 2), self.max_size)
        self.blue_sticks = min(self.blue_sticks - (self.blue_sticks % 2), self.max_size)
        
        return frame
    
    def calculate_optimal_sticks(self):
        # Maximize area (red * blue) within budget
        # Each stick is 1 unit long, must use even numbers of sticks
        max_area = 0
        opt_red = 0
        opt_blue = 0
        
        for red in range(0, self.max_size + 1, 2):  # Even numbers: 0, 2, 4, 6, 8, 10
            for blue in range(0, self.max_size + 1, 2):  # Even numbers: 0, 2, 4, 6, 8, 10
                cost = red * self.red_cost_per_stick + blue * self.blue_cost_per_stick
                if cost <= self.budget:
                    area = red * blue  # Each stick is 1 unit, so area = number of red * number of blue
                    if area > max_area:
                        max_area = area
                        opt_red = red
                        opt_blue = blue
        return opt_red, opt_blue

    def draw_rectangle(self):
        self.canvas.delete("all")
        
        # Draw grid (each cell represents 1 unit)
        for i in range(self.max_size + 1):
            self.canvas.create_line(i*self.cell_size, 0, i*self.cell_size, 
                                  self.max_size*self.cell_size, fill="gray", dash=(2, 2))
            self.canvas.create_line(0, i*self.cell_size, self.max_size*self.cell_size, 
                                  i*self.cell_size, fill="gray", dash=(2, 2))
        
        total_width = self.max_size * self.cell_size
        total_height = self.max_size * self.cell_size
        
        # Draw current rectangle if sticks are detected and not optimized
        if self.red_sticks > 0 and self.blue_sticks > 0 and not self.show_optimized:
            rect_width = self.red_sticks * self.cell_size  # Each stick is 1 unit
            rect_height = self.blue_sticks * self.cell_size  # Each stick is 1 unit
            start_x = (total_width - rect_width) // 2
            start_y = (total_height - rect_height) // 2
            
            self.canvas.create_rectangle(start_x, start_y, 
                                       start_x + rect_width, start_y + rect_height,
                                       fill='#e6f3ff', outline='')
            self.canvas.create_line(start_x, start_y, start_x + rect_width, start_y,
                                  fill="red", width=4)
            self.canvas.create_line(start_x, start_y + rect_height, 
                                  start_x + rect_width, start_y + rect_height,
                                  fill="red", width=4)
            self.canvas.create_line(start_x, start_y, start_x, start_y + rect_height,
                                  fill="blue", width=4)
            self.canvas.create_line(start_x + rect_width, start_y, 
                                  start_x + rect_width, start_y + rect_height,
                                  fill="blue", width=4)
            
        # Draw optimized rectangle when toggled
        if self.show_optimized:
            opt_red, opt_blue = self.calculate_optimal_sticks()
            opt_width = opt_red * self.cell_size  # Each stick is 1 unit
            opt_height = opt_blue * self.cell_size  # Each stick is 1 unit
            opt_start_x = (total_width - opt_width) // 2
            opt_start_y = (total_height - opt_height) // 2
            
            self.canvas.create_rectangle(opt_start_x, opt_start_y,
                                       opt_start_x + opt_width, opt_start_y + opt_height,
                                       fill='#e6ffe6', outline='')
            self.canvas.create_line(opt_start_x, opt_start_y, opt_start_x + opt_width, opt_start_y,
                                  fill="red", width=4)
            self.canvas.create_line(opt_start_x, opt_start_y + opt_height, 
                                  opt_start_x + opt_width, opt_start_y + opt_height,
                                  fill="red", width=4)
            self.canvas.create_line(opt_start_x, opt_start_y, opt_start_x, opt_start_y + opt_height,
                                  fill="blue", width=4)
            self.canvas.create_line(opt_start_x + opt_width, opt_start_y, 
                                  opt_start_x + opt_width, opt_start_y + opt_height,
                                  fill="blue", width=4)

    def calculate_costs(self):
        red_total = self.red_sticks * self.red_cost_per_stick
        blue_total = self.blue_sticks * self.blue_cost_per_stick
        total_cost = red_total + blue_total
        return red_total, blue_total, total_cost

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            frame = self.detect_sticks(frame)
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
            
            self.draw_rectangle()
            
            if not self.show_optimized:
                self.red_count.config(text=f"Red Sticks: {self.red_sticks}")
                self.blue_count.config(text=f"Blue Sticks: {self.blue_sticks}")
                area = self.red_sticks * self.blue_sticks
                self.area_label.config(text=f"Area: {area} units²")
                red_cost, blue_cost, total_cost = self.calculate_costs()
                self.red_cost.config(text=f"Red Cost: ${red_cost:.2f}")
                self.blue_cost.config(text=f"Blue Cost: ${blue_cost:.2f}")
                self.total_cost.config(text=f"Total Cost: ${total_cost:.2f}")
                
                self.opt_red_count.config(text="")
                self.opt_red_cost.config(text="")
                self.opt_blue_count.config(text="")
                self.opt_blue_cost.config(text="")
                self.opt_area.config(text="")
                self.opt_total_cost.config(text="")
            else:
                opt_red, opt_blue = self.calculate_optimal_sticks()
                opt_red_cost = opt_red * self.red_cost_per_stick
                opt_blue_cost = opt_blue * self.blue_cost_per_stick
                opt_total_cost = opt_red_cost + opt_blue_cost
                opt_area = opt_red * opt_blue
                
                self.red_count.config(text=f"Current Red Sticks: {self.red_sticks}")
                self.red_cost.config(text=f"Current Red Cost: ${self.red_sticks * self.red_cost_per_stick:.2f}")
                self.blue_count.config(text=f"Current Blue Sticks: {self.blue_sticks}")
                self.blue_cost.config(text=f"Current Blue Cost: ${self.blue_sticks * self.blue_cost_per_stick:.2f}")
                self.area_label.config(text=f"Current Area: {self.red_sticks * self.blue_sticks} units²")
                self.total_cost.config(text=f"Current Total Cost: ${self.calculate_costs()[2]:.2f}")
                
                self.opt_red_count.config(text=f"Optimal Red Sticks: {opt_red}")
                self.opt_red_cost.config(text=f"Optimal Red Cost: ${opt_red_cost:.2f}")
                self.opt_blue_count.config(text=f"Optimal Blue Sticks: {opt_blue}")
                self.opt_blue_cost.config(text=f"Optimal Blue Cost: ${opt_blue_cost:.2f}")
                self.opt_area.config(text=f"Optimal Area: {opt_area} units²")
                self.opt_total_cost.config(text=f"Optimal Total Cost: ${opt_total_cost:.2f}")