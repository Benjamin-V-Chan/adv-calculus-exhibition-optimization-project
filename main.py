import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

class fenceShapeDetector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("fence Shape Detector")
        self.root.configure(bg='#e0e0e0')
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open video capture device")
        
        # Display parameters
        self.cell_size = 50  # Pixels per unit (1 fence = 1 unit = 50 pixels)
        self.max_size = 10   # Max total fences per type (even: 0, 2, 4, 6, 8, 10)
        self.show_optimized = False
        
        # Cost parameters
        self.red_cost_per_fence = 5.00  # Cost per red fence (1 unit long)
        self.blue_cost_per_fence = 2.00 # Cost per blue fence (1 unit long)
        self.budget = 30.00             # Total budget in dollars
        
        self.setup_gui()
        self.red_fences = 0  # Total red fences detected
        self.blue_fences = 0  # Total blue fences detected
        
        self.update()
        self.root.mainloop()

    def setup_gui(self):
        self.main_frame = tk.Frame(self.root, bg='#e0e0e0')
        self.main_frame.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame, bg='#e0e0e0')
        self.left_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        self.canvas_frame = tk.LabelFrame(self.left_frame, text="Rectangle Display (1 fence = 1 unit)", 
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
                                     text=f"Red fence Cost: ${self.red_cost_per_fence:.2f} (1 unit)", 
                                     bg='#f5f5f5', font=('Arial', 10), fg='#d32f2f', anchor='w')
        self.const_red_cost.pack(fill=tk.X, padx=5, pady=1)
        
        self.const_blue_cost = tk.Label(self.constants_frame, 
                                      text=f"Blue fence Cost: ${self.blue_cost_per_fence:.2f} (1 unit)", 
                                      bg='#f5f5f5', font=('Arial', 10), fg='#1976d2', anchor='w')
        self.const_blue_cost.pack(fill=tk.X, padx=5, pady=1)
        
        self.const_max_size = tk.Label(self.constants_frame, 
                                     text=f"Max Total fences: {self.max_size} (even only)", 
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

        # Current Statistics Frame (Left Side)
        self.current_frame = tk.Frame(self.info_frame, bg='#f5f5f5')
        self.current_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        self.current_title = tk.Label(self.current_frame, text="Current Statistics", 
                                    bg='#f5f5f5', font=('Arial', 12, 'bold'), anchor='w')
        self.current_title.pack(fill=tk.X, pady=(0, 5))
        
        self.red_count = tk.Label(self.current_frame, text="Total Red fences: 0", bg='#f5f5f5',
                                font=('Arial', 12), fg='#d32f2f', anchor='w')
        self.red_count.pack(fill=tk.X, pady=2)
        
        self.red_cost = tk.Label(self.current_frame, text="Red Cost: $0.00", bg='#f5f5f5',
                               font=('Arial', 12), fg='#d32f2f', anchor='w')
        self.red_cost.pack(fill=tk.X, pady=2)
        
        self.blue_count = tk.Label(self.current_frame, text="Total Blue fences: 0", bg='#f5f5f5',
                                 font=('Arial', 12), fg='#1976d2', anchor='w')
        self.blue_count.pack(fill=tk.X, pady=2)
        
        self.blue_cost = tk.Label(self.current_frame, text="Blue Cost: $0.00", bg='#f5f5f5',
                                font=('Arial', 12), fg='#1976d2', anchor='w')
        self.blue_cost.pack(fill=tk.X, pady=2)
        
        self.area_label = tk.Label(self.current_frame, text="Area: 0 units²", bg='#f5f5f5',
                                 font=('Arial', 12), anchor='w')
        self.area_label.pack(fill=tk.X, pady=2)
        
        self.total_cost = tk.Label(self.current_frame, text="Total Cost: $0.00", bg='#f5f5f5',
                                 font=('Arial', 12, 'bold'), fg='#388e3c', anchor='w')
        self.total_cost.pack(fill=tk.X, pady=2)

        # Optimized Statistics Frame (Right Side)
        self.opt_frame = tk.Frame(self.info_frame, bg='#f5f5f5')
        self.opt_frame.pack(side=tk.RIGHT, padx=10, fill=tk.Y)
        
        self.opt_title = tk.Label(self.opt_frame, text="Optimized Statistics", 
                                bg='#f5f5f5', font=('Arial', 12, 'bold'), anchor='w')
        self.opt_title.pack(fill=tk.X, pady=(0, 5))
        
        self.opt_red_count = tk.Label(self.opt_frame, text="", bg='#f5f5f5',
                                    font=('Arial', 12, 'italic'), fg='#d32f2f', anchor='w')
        self.opt_red_count.pack(fill=tk.X, pady=2)
        
        self.opt_red_cost = tk.Label(self.opt_frame, text="", bg='#f5f5f5',
                                   font=('Arial', 12, 'italic'), fg='#d32f2f', anchor='w')
        self.opt_red_cost.pack(fill=tk.X, pady=2)
        
        self.opt_blue_count = tk.Label(self.opt_frame, text="", bg='#f5f5f5',
                                     font=('Arial', 12, 'italic'), fg='#1976d2', anchor='w')
        self.opt_blue_count.pack(fill=tk.X, pady=2)
        
        self.opt_blue_cost = tk.Label(self.opt_frame, text="", bg='#f5f5f5',
                                    font=('Arial', 12, 'italic'), fg='#1976d2', anchor='w')
        self.opt_blue_cost.pack(fill=tk.X, pady=2)
        
        self.opt_area = tk.Label(self.opt_frame, text="", bg='#f5f5f5',
                               font=('Arial', 12, 'italic'), anchor='w')
        self.opt_area.pack(fill=tk.X, pady=2)
        
        self.opt_total_cost = tk.Label(self.opt_frame, text="", bg='#f5f5f5',
                                     font=('Arial', 12, 'bold', 'italic'), fg='#388e3c', anchor='w')
        self.opt_total_cost.pack(fill=tk.X, pady=2)

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

    def detect_fences(self, frame):
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
        
        self.red_fences = 0
        self.blue_fences = 0
        
        for contour in red_contours:
            if cv2.contourArea(contour) > 200:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w)/h if w > h else float(h)/w
                if aspect_ratio > 2.0:
                    self.red_fences += 1
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        for contour in blue_contours:
            if cv2.contourArea(contour) > 200:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w)/h if w > h else float(h)/w
                if aspect_ratio > 2.0:
                    self.blue_fences += 1
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Ensure even numbers of fences
        self.red_fences = min(self.red_fences - (self.red_fences % 2), self.max_size)
        self.blue_fences = min(self.blue_fences - (self.blue_fences % 2), self.max_size)
        
        return frame

    def calculate_optimal_fences(self):
        max_area = 0
        opt_red = 0
        opt_blue = 0
        
        for red in range(0, self.max_size + 1, 2):
            for blue in range(0, self.max_size + 1, 2):
                cost = red * self.red_cost_per_fence + blue * self.blue_cost_per_fence
                if cost <= self.budget:
                    area = (red // 2) * (blue // 2)
                    if area > max_area:
                        max_area = area
                        opt_red = red
                        opt_blue = blue
        return opt_red, opt_blue

    def draw_rectangle(self, red_fences, blue_fences):
        self.canvas.delete("all")
        
        # Canvas center at (250, 250) aligns with unit (5, 5)
        canvas_width = self.max_size * self.cell_size  # 500 pixels
        canvas_height = self.max_size * self.cell_size  # 500 pixels
        center_x = canvas_width // 2  # 250 pixels
        center_y = canvas_height // 2  # 250 pixels
        
        # Draw grid: 11 lines (0 to 10), centered at (5, 5)
        for i in range(self.max_size + 1):  # 0 to 10
            x = i * self.cell_size
            y = i * self.cell_size
            self.canvas.create_line(x, 0, x, canvas_height, fill="gray", dash=(2, 2))
            self.canvas.create_line(0, y, canvas_width, y, fill="gray", dash=(2, 2))
        
        # Draw current rectangle (if any fences detected)
        if red_fences > 0 and blue_fences > 0:
            base = red_fences // 2  # Units wide
            height = blue_fences // 2  # Units tall
            
            # Center around (5, 5)
            start_unit_x = 5 - (base // 2)
            start_unit_y = 5 - (height // 2)
            end_unit_x = start_unit_x + base
            end_unit_y = start_unit_y + height
            
            start_x = start_unit_x * self.cell_size
            start_y = start_unit_y * self.cell_size
            end_x = end_unit_x * self.cell_size
            end_y = end_unit_y * self.cell_size
            
            # Light blue fill (no alpha, #ADD8E6)
            self.canvas.create_rectangle(start_x, start_y, end_x, end_y, 
                                       fill="#ADD8E6", outline="")
            
            # Draw red fences (solid, horizontal)
            for i in range(base):
                x0 = start_x + i * self.cell_size
                x1 = x0 + self.cell_size
                self.canvas.create_line(x0, start_y, x1, start_y, fill="red", width=4)
                self.canvas.create_line(x0, end_y, x1, end_y, fill="red", width=4)
            
            # Draw blue fences (solid, vertical)
            for j in range(height):
                y0 = start_y + j * self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_line(start_x, y0, start_x, y1, fill="blue", width=4)
                self.canvas.create_line(end_x, y0, end_x, y1, fill="blue", width=4)
        
        # Draw optimized rectangle (if toggled)
        if self.show_optimized:
            opt_red, opt_blue = self.calculate_optimal_fences()
            opt_base = opt_red // 2
            opt_height = opt_blue // 2
            
            # Center around (5, 5)
            opt_start_unit_x = 5 - (opt_base // 2)
            opt_start_unit_y = 5 - (opt_height // 2)
            opt_end_unit_x = opt_start_unit_x + opt_base
            opt_end_unit_y = opt_start_unit_y + opt_height
            
            opt_start_x = opt_start_unit_x * self.cell_size
            opt_start_y = opt_start_unit_y * self.cell_size
            opt_end_x = opt_end_unit_x * self.cell_size
            opt_end_y = opt_end_unit_y * self.cell_size
            
            # Light green fill (no alpha, #90EE90)
            self.canvas.create_rectangle(opt_start_x, opt_start_y, opt_end_x, opt_end_y, 
                                       fill="#90EE90", outline="")
            
            # Draw optimized red fences (dashed, horizontal)
            for i in range(opt_base):
                x0 = opt_start_x + i * self.cell_size
                x1 = x0 + self.cell_size
                self.canvas.create_line(x0, opt_start_y, x1, opt_start_y, fill="red", width=4, dash=(4, 2))
                self.canvas.create_line(x0, opt_end_y, x1, opt_end_y, fill="red", width=4, dash=(4, 2))
            
            # Draw optimized blue fences (dashed, vertical)
            for j in range(opt_height):
                y0 = opt_start_y + j * self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_line(opt_start_x, y0, opt_start_x, y1, fill="blue", width=4, dash=(4, 2))
                self.canvas.create_line(opt_end_x, y0, opt_end_x, y1, fill="blue", width=4, dash=(4, 2))

    def calculate_costs(self):
        red_total = self.red_fences * self.red_cost_per_fence
        blue_total = self.blue_fences * self.blue_cost_per_fence
        total_cost = red_total + blue_total
        return red_total, blue_total, total_cost

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            frame = self.detect_fences(frame)
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
            
            self.draw_rectangle(self.red_fences, self.blue_fences)
            
            # Always update current statistics
            self.red_count.config(text=f"Total Red fences: {self.red_fences}")
            self.red_cost.config(text=f"Red Cost: ${self.red_fences * self.red_cost_per_fence:.2f}")
            self.blue_count.config(text=f"Total Blue fences: {self.blue_fences}")
            self.blue_cost.config(text=f"Blue Cost: ${self.blue_fences * self.blue_cost_per_fence:.2f}")
            area = (self.red_fences // 2) * (self.blue_fences // 2)
            self.area_label.config(text=f"Area: {area} units²")
            self.total_cost.config(text=f"Total Cost: ${self.calculate_costs()[2]:.2f}")
            
            # Update optimized statistics only if toggled
            if self.show_optimized:
                opt_red, opt_blue = self.calculate_optimal_fences()
                opt_red_cost = opt_red * self.red_cost_per_fence
                opt_blue_cost = opt_blue * self.blue_cost_per_fence
                opt_total_cost = opt_red_cost + opt_blue_cost
                opt_area = (opt_red // 2) * (opt_blue // 2)
                
                self.opt_red_count.config(text=f"Total Red fences: {opt_red}")
                self.opt_red_cost.config(text=f"Red Cost: ${opt_red_cost:.2f}")
                self.opt_blue_count.config(text=f"Total Blue fences: {opt_blue}")
                self.opt_blue_cost.config(text=f"Blue Cost: ${opt_blue_cost:.2f}")
                self.opt_area.config(text=f"Area: {opt_area} units²")
                self.opt_total_cost.config(text=f"Total Cost: ${opt_total_cost:.2f}")
            else:
                self.opt_red_count.config(text="")
                self.opt_red_cost.config(text="")
                self.opt_blue_count.config(text="")
                self.opt_blue_cost.config(text="")
                self.opt_area.config(text="")
                self.opt_total_cost.config(text="")
            
            self.root.update()  # Force GUI refresh
        
        self.root.after(50, self.update)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    detector = fenceShapeDetector()