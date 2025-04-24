import tkinter as tk
from tkinter import scrolledtext, messagebox, font, Canvas
from voice.listen import listen
from voice.enhanced_speak import speak, set_visualization_callback
from core.commands import run_command
from core.local_brain import ask_local_llm as ask_gpt
import threading
import queue
import time
import os
import math
import random
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFilter
from datetime import datetime
import wave
import struct
import tempfile

class EdithGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("E.D.I.T.H. - Even Dead, I'm The Hero")
        self.root.geometry("1000x700")
        self.root.configure(bg="#000000")  # Black background
        self.root.minsize(800, 600)  # Minimum window size
        
        # Define colors - EDITH uses a red/orange accent scheme
        self.edith_red = "#E53935"
        self.edith_orange = "#FF5722"
        self.edith_light_red = "#EF9A9A"
        self.edith_dark = "#121212"
        self.edith_darker = "#0A0A0A"
        self.edith_text = "#FFFFFF"
        self.edith_accent = "#FF3D00"  # Bright orange-red accent
        self.edith_secondary = "#424242"  # Dark gray for secondary elements
        self.edith_success = "#00C853"  # Green for success indicators
        
        # Create custom fonts - more modern and tech-like
        self.title_font = font.Font(family="Arial", size=18, weight="bold")
        self.subtitle_font = font.Font(family="Arial", size=10)
        self.text_font = font.Font(family="Courier New", size=10)
        self.button_font = font.Font(family="Arial", size=10, weight="bold")
        self.mono_font = font.Font(family="Courier New", size=9)
        
        # Animation variables
        self.animation_frames = []
        self.current_frame = 0
        self.scanning_effect_active = False
        
        # Initialize time display
        self.current_time = ""
        self.current_date = ""
        self.update_time()
        
    def update_time(self):
        """Update the time and date display"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%A, %B %d, %Y")
        
        if hasattr(self, 'time_label') and self.time_label:
            self.time_label.config(text=time_str)
        
        if hasattr(self, 'date_label') and self.date_label:
            self.date_label.config(text=date_str)
        
        self.current_time = time_str
        self.current_date = date_str
        
        # Schedule the next update
        self.root.after(1000, self.update_time)
    
    def create_holographic_effect(self):
        """Create a subtle holographic effect overlay"""
        try:
            # Create a canvas for the holographic effect
            self.holo_canvas = tk.Canvas(
                self.root,
                highlightthickness=0,
                bg=""
            )
            self.holo_canvas.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Create particles for a futuristic effect
            self.particles = []
            self.create_particles()
            
            # Create scan lines
            num_lines = 100
            for i in range(num_lines):
                y = i * 7
                alpha = 20  # Very subtle
                self.holo_canvas.create_line(
                    0, y, 2000, y,
                    fill=f"#{alpha:02x}0000",
                    width=1,
                    dash=(1, 6)
                )
            
            # Create a subtle vignette effect
            self.create_vignette_effect()
            
            # Lower the canvas to the bottom so it doesn't interfere with interactions
            self.holo_canvas.lower()
            
            # Schedule periodic updates to the effect
            self.root.after(100, self.update_holographic_effect)
        except Exception as e:
            print(f"Error creating holographic effect: {e}")
    
    def create_vignette_effect(self):
        """Create a subtle vignette effect"""
        try:
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # Create a radial gradient image for the vignette
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a radial gradient
            for r in range(0, int(max(width, height) * 0.7), 2):
                # Decrease alpha as radius increases
                alpha = int(10 * (1 - r / (max(width, height) * 0.7)))
                if alpha <= 0:
                    break
                    
                # Draw a rectangle with decreasing alpha
                draw.rectangle(
                    [width//2 - r, height//2 - r, width//2 + r, height//2 + r],
                    outline=(80, 0, 0, alpha),
                    width=2
                )
            
            # Convert to PhotoImage
            self.vignette_img = ImageTk.PhotoImage(img)
            
            # Add to canvas
            self.vignette_id = self.holo_canvas.create_image(
                width//2, height//2,
                image=self.vignette_img
            )
        except Exception as e:
            print(f"Error creating vignette effect: {e}")
    
    def create_particles(self):
        """Create floating particles for a futuristic effect"""
        try:
            width = self.root.winfo_width() or 1000
            height = self.root.winfo_height() or 700
            
            # Create 50 particles
            for _ in range(50):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(1, 3)
                speed = random.uniform(0.2, 1.0)
                
                # Random color in the red/orange spectrum
                r = random.randint(150, 255)
                g = random.randint(20, 80)
                b = 0
                alpha = random.randint(10, 40)
                color = f"#{r:02x}{g:02x}{b:02x}"
                
                # Create the particle
                particle = self.holo_canvas.create_oval(
                    x, y, x + size, y + size,
                    fill=color,
                    outline="",
                    stipple="gray50"  # Makes it semi-transparent
                )
                
                # Store particle properties
                self.particles.append({
                    'id': particle,
                    'x': x,
                    'y': y,
                    'size': size,
                    'speed': speed,
                    'angle': random.uniform(0, 2 * math.pi),
                    'color': color
                })
        except Exception as e:
            print(f"Error creating particles: {e}")
    
    def update_particles(self):
        """Update particle positions and properties"""
        try:
            width = self.root.winfo_width() or 1000
            height = self.root.winfo_height() or 700
            
            for particle in self.particles:
                # Update position based on angle and speed
                particle['x'] += math.cos(particle['angle']) * particle['speed']
                particle['y'] += math.sin(particle['angle']) * particle['speed']
                
                # Wrap around screen edges
                if particle['x'] < 0:
                    particle['x'] = width
                elif particle['x'] > width:
                    particle['x'] = 0
                    
                if particle['y'] < 0:
                    particle['y'] = height
                elif particle['y'] > height:
                    particle['y'] = 0
                
                # Update particle position
                x, y = particle['x'], particle['y']
                size = particle['size']
                self.holo_canvas.coords(
                    particle['id'],
                    x, y, x + size, y + size
                )
                
                # Occasionally change direction
                if random.random() < 0.01:
                    particle['angle'] = random.uniform(0, 2 * math.pi)
                    
                # Occasionally change color slightly
                if random.random() < 0.05:
                    r = random.randint(150, 255)
                    g = random.randint(20, 80)
                    b = 0
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    self.holo_canvas.itemconfig(particle['id'], fill=color)
                    particle['color'] = color
        except Exception as e:
            print(f"Error updating particles: {e}")
    
    def update_holographic_effect(self):
        """Update the holographic effect periodically"""
        try:
            # Subtle animation for the holographic effect
            t = time.time()
            
            # Adjust scan line opacity based on time
            scan_lines = self.holo_canvas.find_withtag("all")
            for i, line_id in enumerate(scan_lines):
                if i % 5 == int(t) % 5 and i < 100:  # Only update scan lines, not particles
                    alpha = int(10 + 10 * abs(math.sin(t + i * 0.1)))
                    self.holo_canvas.itemconfig(
                        line_id, 
                        fill=f"#{alpha:02x}{int(alpha/3):02x}00"
                    )
            
            # Update particles
            self.update_particles()
            
            # Schedule the next update
            self.root.after(50, self.update_holographic_effect)
        except Exception as e:
            print(f"Error updating holographic effect: {e}")
            # Try again later
            self.root.after(1000, self.update_holographic_effect)
    
    def create_ui(self):
        """Create the main UI components"""
        # Create holographic effect
        self.root.after(500, self.create_holographic_effect)
        
        # Create main frames with a more complex layout
        self.main_frame = tk.Frame(self.root, bg=self.edith_darker)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar for system info and stats
        self.sidebar_frame = tk.Frame(self.main_frame, bg=self.edith_dark, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
        self.sidebar_frame.pack_propagate(False)  # Prevent shrinking
        
        # Right main content area
        self.right_frame = tk.Frame(self.main_frame, bg=self.edith_darker)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Header with EDITH logo/title
        self.header_frame = tk.Frame(self.right_frame, bg=self.edith_dark, height=60)
        self.header_frame.pack(fill=tk.X, padx=2, pady=2)
        self.header_frame.pack_propagate(False)  # Prevent shrinking
        
        # Content area
        self.content_frame = tk.Frame(self.right_frame, bg=self.edith_darker)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Footer with controls
        self.footer_frame = tk.Frame(self.right_frame, bg=self.edith_dark, height=80)
        self.footer_frame.pack(fill=tk.X, padx=2, pady=2)
        self.footer_frame.pack_propagate(False)  # Prevent shrinking
        
        # Create header content
        self.create_header()
        
        # Create sidebar content
        self.create_sidebar()
        
        # Create main content area
        self.create_content_area()
        
        # Create footer content
        self.create_footer()
    
    def create_header(self):
        """Create the header with EDITH branding"""
        # Left side - EDITH logo and title
        self.logo_frame = tk.Frame(self.header_frame, bg=self.edith_dark)
        self.logo_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Create a canvas for the 3D holographic logo
        self.logo_canvas = tk.Canvas(
            self.logo_frame,
            width=150,
            height=40,
            bg=self.edith_dark,
            highlightthickness=0
        )
        self.logo_canvas.pack(side=tk.TOP, anchor="w")
        
        # Create the main title
        self.title_text = self.logo_canvas.create_text(
            10, 20,
            text="E.D.I.T.H.",
            font=self.title_font,
            fill=self.edith_red,
            anchor="w"
        )
        
        # Create shadow/glow effects for 3D appearance
        self.shadow_text1 = self.logo_canvas.create_text(
            11, 21,
            text="E.D.I.T.H.",
            font=self.title_font,
            fill="#AA0000",
            anchor="w"
        )
        
        self.shadow_text2 = self.logo_canvas.create_text(
            12, 22,
            text="E.D.I.T.H.",
            font=self.title_font,
            fill="#550000",
            anchor="w"
        )
        
        # Lower the shadows below the main text
        self.logo_canvas.tag_lower(self.shadow_text1)
        self.logo_canvas.tag_lower(self.shadow_text2)
        
        # Start the logo animation
        self.animate_logo()
        
        self.subtitle_label = tk.Label(
            self.logo_frame, 
            text="Even Dead, I'm The Hero", 
            font=self.subtitle_font, 
            fg=self.edith_light_red, 
            bg=self.edith_dark
        )
        self.subtitle_label.pack(side=tk.TOP, anchor="w")
        
        # Right side - Status indicator and time
        self.status_frame = tk.Frame(self.header_frame, bg=self.edith_dark)
        self.status_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Time and date display
        self.time_label = tk.Label(
            self.status_frame, 
            text=self.current_time, 
            font=self.mono_font, 
            fg=self.edith_text, 
            bg=self.edith_dark
        )
        self.time_label.pack(side=tk.TOP, anchor="e")
        
        self.date_label = tk.Label(
            self.status_frame, 
            text=self.current_date, 
            font=("Courier New", 8), 
            fg="#AAAAAA", 
            bg=self.edith_dark
        )
        self.date_label.pack(side=tk.TOP, anchor="e")
        
        # Status indicator with a more advanced look
        self.status_indicator_frame = tk.Frame(self.header_frame, bg=self.edith_dark)
        self.status_indicator_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        self.status_canvas = tk.Canvas(
            self.status_indicator_frame, 
            width=30, 
            height=30, 
            bg=self.edith_dark, 
            highlightthickness=0
        )
        self.status_canvas.pack(side=tk.TOP)
        
        # Create a more complex status indicator
        self.status_outer = self.status_canvas.create_oval(2, 2, 28, 28, outline=self.edith_red, width=1)
        self.status_middle = self.status_canvas.create_oval(6, 6, 24, 24, outline=self.edith_orange, width=1)
        self.status_inner = self.status_canvas.create_oval(10, 10, 20, 20, fill=self.edith_red, outline="")
        
        self.status_label = tk.Label(
            self.status_indicator_frame, 
            text="ONLINE", 
            font=("Courier New", 8, "bold"), 
            fg=self.edith_red, 
            bg=self.edith_dark
        )
        self.status_label.pack(side=tk.TOP)
        
    def create_sidebar(self):
        """Create the sidebar with system info and stats"""
        # System info section
        self.system_frame = tk.Frame(self.sidebar_frame, bg=self.edith_dark)
        self.system_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # System section header
        self.system_header = tk.Label(
            self.system_frame,
            text="SYSTEM STATUS",
            font=("Courier New", 9, "bold"),
            fg=self.edith_orange,
            bg=self.edith_dark
        )
        self.system_header.pack(anchor="w", pady=(0, 5))
        
        # Separator line
        self.separator1 = tk.Frame(self.system_frame, height=1, bg=self.edith_orange)
        self.separator1.pack(fill=tk.X, pady=2)
        
        # System stats with tech-like formatting
        stats = [
            ("CPU", "NOMINAL"),
            ("MEMORY", "87% AVAILABLE"),
            ("NETWORK", "CONNECTED"),
            ("SECURITY", "ACTIVE"),
            ("PROTOCOLS", "ENABLED")
        ]
        
        for label, value in stats:
            stat_frame = tk.Frame(self.system_frame, bg=self.edith_dark)
            stat_frame.pack(fill=tk.X, pady=2)
            
            stat_label = tk.Label(
                stat_frame,
                text=f"{label}:",
                font=self.mono_font,
                fg="#AAAAAA",
                bg=self.edith_dark,
                width=10,
                anchor="w"
            )
            stat_label.pack(side=tk.LEFT)
            
            stat_value = tk.Label(
                stat_frame,
                text=value,
                font=self.mono_font,
                fg=self.edith_text,
                bg=self.edith_dark
            )
            stat_value.pack(side=tk.LEFT)
        
        # Training stats section
        self.training_stats_frame = tk.Frame(self.sidebar_frame, bg=self.edith_dark)
        self.training_stats_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Training section header
        self.training_header = tk.Label(
            self.training_stats_frame,
            text="LEARNING METRICS",
            font=("Courier New", 9, "bold"),
            fg=self.edith_orange,
            bg=self.edith_dark
        )
        self.training_header.pack(anchor="w", pady=(0, 5))
        
        # Separator line
        self.separator2 = tk.Frame(self.training_stats_frame, height=1, bg=self.edith_orange)
        self.separator2.pack(fill=tk.X, pady=2)
        
        # Create a canvas for a circular progress indicator
        self.progress_canvas = tk.Canvas(
            self.training_stats_frame, 
            width=120, 
            height=120, 
            bg=self.edith_dark,
            highlightthickness=0
        )
        self.progress_canvas.pack(pady=10)
        
        # Draw progress circle (will be updated with actual data)
        self.progress_bg = self.progress_canvas.create_oval(10, 10, 110, 110, outline=self.edith_secondary, width=5)
        self.progress_arc = self.progress_canvas.create_arc(
            15, 15, 105, 105, 
            start=90, extent=0, 
            style=tk.ARC, 
            outline=self.edith_orange, 
            width=5
        )
        
        # Progress text
        self.progress_text = self.progress_canvas.create_text(
            60, 60, 
            text="0%", 
            fill=self.edith_orange, 
            font=("Arial", 16, "bold")
        )
        
        # Progress label
        self.progress_label = self.progress_canvas.create_text(
            60, 85, 
            text="Success Rate", 
            fill="#AAAAAA", 
            font=("Arial", 8)
        )
        
        # Training stats with tech-like formatting
        self.training_stats_detail = tk.Frame(self.training_stats_frame, bg=self.edith_dark)
        self.training_stats_detail.pack(fill=tk.X, pady=5)
        
        # We'll update these with actual data
        self.examples_label = tk.Label(
            self.training_stats_detail,
            text="EXAMPLES: 0",
            font=self.mono_font,
            fg=self.edith_text,
            bg=self.edith_dark
        )
        self.examples_label.pack(anchor="w", pady=1)
        
        self.interactions_label = tk.Label(
            self.training_stats_detail,
            text="INTERACTIONS: 0",
            font=self.mono_font,
            fg=self.edith_text,
            bg=self.edith_dark
        )
        self.interactions_label.pack(anchor="w", pady=1)
        
        self.status_detail_label = tk.Label(
            self.training_stats_detail,
            text="STATUS: READY",
            font=self.mono_font,
            fg=self.edith_success,
            bg=self.edith_dark
        )
        self.status_detail_label.pack(anchor="w", pady=1)
    
    def create_content_area(self):
        """Create the main content area with conversation display"""
        # Create a frame for the conversation display with a tech border
        self.output_frame = tk.Frame(
            self.content_frame, 
            bg=self.edith_darker, 
            bd=0,
            highlightbackground=self.edith_orange,
            highlightthickness=1
        )
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a canvas for tech-like decorations around the text area
        self.decoration_canvas = tk.Canvas(
            self.output_frame,
            bg=self.edith_darker,
            highlightthickness=0,
            height=20
        )
        self.decoration_canvas.pack(fill=tk.X)
        
        # Add tech-like decorations
        self.decoration_canvas.create_line(
            0, 10, 20, 10, 
            fill=self.edith_orange, 
            width=1
        )
        self.decoration_canvas.create_line(
            0, 10, 0, 20, 
            fill=self.edith_orange, 
            width=1
        )
        
        self.decoration_canvas.create_text(
            40, 10,
            text="CONVERSATION LOG",
            fill=self.edith_orange,
            font=("Courier New", 8)
        )
        
        self.decoration_canvas.create_line(
            150, 10, 170, 10, 
            fill=self.edith_orange, 
            width=1
        )
        
        # Right side decoration
        self.decoration_canvas.create_line(
            self.output_frame.winfo_reqwidth() - 20, 10, 
            self.output_frame.winfo_reqwidth(), 10, 
            fill=self.edith_orange, 
            width=1,
            tags="right_line"
        )
        
        # Output text area with advanced styling
        self.output_text = scrolledtext.ScrolledText(
            self.output_frame, 
            height=20, 
            wrap=tk.WORD,
            font=self.text_font,
            bg="#0A0A0A",  # Very dark background
            fg=self.edith_text,
            insertbackground=self.edith_orange,
            selectbackground=self.edith_orange,
            selectforeground="white",
            bd=0,
            padx=10,
            pady=10
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Bottom decoration
        self.bottom_decoration = tk.Canvas(
            self.output_frame,
            bg=self.edith_darker,
            highlightthickness=0,
            height=20
        )
        self.bottom_decoration.pack(fill=tk.X)
        
        self.bottom_decoration.create_line(
            0, 10, 20, 10, 
            fill=self.edith_orange, 
            width=1
        )
        
        self.bottom_decoration.create_line(
            self.output_frame.winfo_reqwidth() - 20, 10, 
            self.output_frame.winfo_reqwidth(), 10, 
            fill=self.edith_orange, 
            width=1,
            tags="bottom_right_line"
        )
        
        # Configure text tags for styling
        self.output_text.tag_configure("user", foreground=self.edith_orange, font=("Courier New", 10, "bold"))
        self.output_text.tag_configure("user_text", foreground="#FFFFFF", font=("Courier New", 10))
        self.output_text.tag_configure("edith", foreground=self.edith_red, font=("Courier New", 10, "bold"))
        self.output_text.tag_configure("edith_text", foreground="#FFFFFF", font=("Courier New", 10))
        self.output_text.tag_configure("system", foreground="#78909C", font=("Courier New", 9, "italic"))
        
        # Add welcome message
        self.output_text.insert(tk.END, "EDITH: ", "edith")
        self.output_text.insert(tk.END, "Hello! I'm EDITH, your advanced AI assistant. How can I help you today?\n\n", "edith_text")
        self.output_text.yview(tk.END)
    
    def create_footer(self):
        """Create the footer with controls"""
        # Left side - microphone button
        self.mic_frame = tk.Frame(self.footer_frame, bg=self.edith_dark)
        self.mic_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Create a more advanced microphone button
        self.mic_button = tk.Button(
            self.mic_frame, 
            text="START LISTENING", 
            width=20, 
            height=2, 
            command=self.toggle_mic,
            bg=self.edith_dark,
            fg=self.edith_red,
            activebackground=self.edith_secondary,
            activeforeground=self.edith_red,
            font=("Courier New", 10, "bold"),
            bd=1,
            relief=tk.FLAT,
            highlightbackground=self.edith_red,
            highlightthickness=1
        )
        self.mic_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Right side - feedback buttons
        self.feedback_frame = tk.Frame(self.footer_frame, bg=self.edith_dark)
        self.feedback_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)
        
        self.feedback_label = tk.Label(
            self.feedback_frame, 
            text="RESPONSE EVALUATION",
            font=("Courier New", 9),
            fg=self.edith_text,
            bg=self.edith_dark
        )
        self.feedback_label.pack(pady=2)
        
        self.feedback_buttons_frame = tk.Frame(self.feedback_frame, bg=self.edith_dark)
        self.feedback_buttons_frame.pack()
        
        # Styled feedback buttons
        self.thumbs_up_button = tk.Button(
            self.feedback_buttons_frame, 
            text="APPROVE", 
            width=10, 
            command=lambda: self.provide_feedback(True),
            bg=self.edith_dark,
            fg=self.edith_success,
            activebackground=self.edith_secondary,
            activeforeground=self.edith_success,
            font=("Courier New", 9, "bold"),
            bd=1,
            relief=tk.FLAT,
            highlightbackground=self.edith_success,
            highlightthickness=1
        )
        self.thumbs_up_button.pack(side=tk.LEFT, padx=5)
        
        self.thumbs_down_button = tk.Button(
            self.feedback_buttons_frame, 
            text="REJECT", 
            width=10, 
            command=lambda: self.provide_feedback(False),
            bg=self.edith_dark,
            fg=self.edith_red,
            activebackground=self.edith_secondary,
            activeforeground=self.edith_red,
            font=("Courier New", 9, "bold"),
            bd=1,
            relief=tk.FLAT,
            highlightbackground=self.edith_red,
            highlightthickness=1
        )
        self.thumbs_down_button.pack(side=tk.LEFT, padx=5)
        
        # Center - training button
        self.train_frame = tk.Frame(self.footer_frame, bg=self.edith_dark)
        self.train_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        self.train_button = tk.Button(
            self.train_frame, 
            text="INITIATE TRAINING SEQUENCE", 
            command=self.trigger_training,
            bg=self.edith_dark,
            fg=self.edith_orange,
            activebackground=self.edith_secondary,
            activeforeground=self.edith_orange,
            font=("Courier New", 9, "bold"),
            bd=1,
            relief=tk.FLAT,
            highlightbackground=self.edith_orange,
            highlightthickness=1,
            padx=10,
            pady=2
        )
        self.train_button.pack(pady=5)
        
        # Version info
        self.version_frame = tk.Frame(self.footer_frame, bg=self.edith_dark)
        self.version_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.version_label = tk.Label(
            self.version_frame, 
            text="E.D.I.T.H. v2.0.0 • STARK INDUSTRIES",
            font=("Courier New", 8),
            fg="#555555",
            bg=self.edith_dark
        )
        self.version_label.pack(side=tk.RIGHT, padx=10, pady=2)
        
        self.mic_on = False
        
        # Store the last interaction for feedback
        self.last_query = ""
        self.last_response = ""
        
        # Create a queue for thread-safe communication
        self.message_queue = queue.Queue()
        
        # Start checking for messages
        self.check_queue()
        
        # Update training status periodically
        self.update_training_status()
        
        # Schedule periodic training status updates
        self.root.after(10000, self.schedule_training_status_update)
        
        # Start animations
        self.animate_status_indicator()

    def animate_status_indicator(self, angle=0):
        """Create a rotating effect for the status indicator"""
        try:
            # Pulse the inner circle
            pulse_value = abs(math.sin(math.radians(angle)))
            r = int(229 * pulse_value) + 26  # Base red value
            g = int(57 * pulse_value) + 20   # Base green value
            color = f'#{r:02x}{g:02x}00'     # Create color string
            
            self.status_canvas.itemconfig(self.status_inner, fill=color)
            
            # Schedule the next animation frame
            self.root.after(50, lambda: self.animate_status_indicator((angle + 5) % 360))
        except Exception as e:
            print(f"Animation error: {e}")
            # Try again later
            self.root.after(1000, lambda: self.animate_status_indicator(0))
    
    def update_progress_circle(self, percentage):
        """Update the circular progress indicator"""
        try:
            # Calculate the extent of the arc (0-359.9)
            extent = min(359.9, percentage * 3.6)  # 3.6 = 360/100
            
            # Update the arc
            self.progress_canvas.itemconfig(self.progress_arc, extent=extent)
            
            # Update the text
            self.progress_canvas.itemconfig(self.progress_text, text=f"{int(percentage)}%")
            
            # Update color based on percentage
            if percentage < 30:
                color = self.edith_red
            elif percentage < 70:
                color = self.edith_orange
            else:
                color = self.edith_success
                
            self.progress_canvas.itemconfig(self.progress_arc, outline=color)
            self.progress_canvas.itemconfig(self.progress_text, fill=color)
        except Exception as e:
            print(f"Error updating progress circle: {e}")
    
    def create_scanning_effect(self):
        """Create a scanning line effect over the output text"""
        try:
            if not hasattr(self, 'scan_line'):
                # Create a scan line overlay
                self.scan_line = tk.Canvas(
                    self.output_frame, 
                    bg='black', 
                    highlightthickness=0,
                    width=self.output_text.winfo_width(),
                    height=self.output_text.winfo_height()
                )
                self.scan_line.place(x=0, y=0, relwidth=1, relheight=1)
                
                # Create the line
                self.scan_line_obj = self.scan_line.create_line(
                    0, 0, self.output_text.winfo_width(), 0,
                    fill=self.edith_red,
                    width=1,
                    dash=(3, 2)
                )
            
            # Start the animation
            self.scanning_effect_active = True
            self.animate_scan_line(0)
        except Exception as e:
            print(f"Error creating scanning effect: {e}")
            self.scanning_effect_active = False
    
    def animate_scan_line(self, y_pos):
        """Animate the scanning line"""
        try:
            if not self.scanning_effect_active:
                return
                
            # Move the line
            self.scan_line.coords(
                self.scan_line_obj,
                0, y_pos, 
                self.output_text.winfo_width(), y_pos
            )
            
            # Loop the animation
            if y_pos > self.output_text.winfo_height():
                y_pos = 0
            
            # Schedule the next frame
            self.root.after(30, lambda: self.animate_scan_line(y_pos + 3))
        except Exception as e:
            print(f"Error animating scan line: {e}")
            self.scanning_effect_active = False
    
    def stop_scanning_effect(self):
        """Stop the scanning effect"""
        try:
            self.scanning_effect_active = False
            if hasattr(self, 'scan_line'):
                self.scan_line.place_forget()
        except Exception as e:
            print(f"Error stopping scanning effect: {e}")
            
    def create_typing_effect(self, text, tag="edith_text"):
        """Create a typing effect for text output"""
        try:
            # Get current position
            current_pos = self.output_text.index(tk.END)
            
            # Schedule typing effect
            self.type_text_gradually(text, 0, current_pos, tag)
        except Exception as e:
            print(f"Error creating typing effect: {e}")
            # Fall back to regular insert
            try:
                self.output_text.insert(tk.END, text, tag)
                self.output_text.see(tk.END)
            except:
                pass
    
    def type_text_gradually(self, text, index, position, tag):
        """Helper for typing effect"""
        try:
            if index < len(text):
                # Insert one character
                self.output_text.insert(position, text[index], tag)
                self.output_text.see(tk.END)
                
                # Random typing speed for realism
                typing_speed = random.randint(10, 30)
                
                # Schedule next character
                self.root.after(
                    typing_speed, 
                    lambda: self.type_text_gradually(text, index + 1, position, tag)
                )
        except Exception as e:
            print(f"Error in typing effect: {e}")
            # Try to insert the rest of the text at once
            try:
                self.output_text.insert(position, text[index:], tag)
                self.output_text.see(tk.END)
            except:
                pass
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("E.D.I.T.H. - Even Dead, I'm The Hero")
        self.root.geometry("1000x700")
        self.root.configure(bg="#000000")  # Black background
        self.root.minsize(800, 600)  # Minimum window size
        
        # Define colors - EDITH uses a red/orange accent scheme
        self.edith_red = "#E53935"
        self.edith_orange = "#FF5722"
        self.edith_light_red = "#EF9A9A"
        self.edith_dark = "#121212"
        self.edith_darker = "#0A0A0A"
        self.edith_text = "#FFFFFF"
        self.edith_accent = "#FF3D00"  # Bright orange-red accent
        self.edith_secondary = "#424242"  # Dark gray for secondary elements
        self.edith_success = "#00C853"  # Green for success indicators
        
        # Create custom fonts - more modern and tech-like
        self.title_font = font.Font(family="Arial", size=18, weight="bold")
        self.subtitle_font = font.Font(family="Arial", size=10)
        self.text_font = font.Font(family="Courier New", size=10)
        self.button_font = font.Font(family="Arial", size=10, weight="bold")
        self.mono_font = font.Font(family="Courier New", size=9)
        
        # Animation variables
        self.animation_frames = []
        self.current_frame = 0
        self.scanning_effect_active = False
        
        # Initialize time display
        self.current_time = ""
        self.current_date = ""
        self.update_time()
        
        # Create the UI components
        self.create_ui()
        
        self.mic_on = False
        
        # Store the last interaction for feedback
        self.last_query = ""
        self.last_response = ""
        
        # Create a queue for thread-safe communication
        self.message_queue = queue.Queue()
        
        # Start checking for messages
        self.check_queue()
        
        # Update training status periodically
        self.update_training_status()
        
        # Schedule periodic training status updates
        self.root.after(10000, self.schedule_training_status_update)
        
        # Start animations
        self.animate_status_indicator()
        self.update_progress_circle(0)  # Start with 0%
        
        # Create voice visualization
        self.create_voice_visualization()
        
        # Create scanning effect
        self.root.after(2000, self.create_scanning_effect)
        
        # Add welcome message with typing effect
        self.root.after(500, lambda: self.create_typing_effect(
            "Hello! I'm EDITH, your advanced AI assistant. How can I help you today?\n\n"
        ))
    
    def toggle_mic(self):
        if self.mic_on:
            self.mic_button.config(
                text="START LISTENING",
                fg=self.edith_red,
                highlightbackground=self.edith_red
            )
            self.status_label.config(text="ONLINE", fg=self.edith_red)
            self.mic_on = False
            self.stop_scanning_effect()
        else:
            self.mic_button.config(
                text="LISTENING...",
                fg="#F44336",  # Brighter red when listening
                highlightbackground="#F44336"
            )
            self.status_label.config(text="LISTENING", fg="#F44336")
            self.mic_on = True
            self.create_scanning_effect()
            self.start_listening()

    def update_output(self, text):
        # If called from the main thread, update directly
        # Otherwise, put the message in the queue
        try:
            # Apply styling based on who's speaking
            if text.startswith("You: "):
                self.output_text.insert(tk.END, "USER: ", "user")
                # Use typing effect for user messages too for consistency
                self.create_typing_effect(text[5:] + "\n\n", "user_text")
            elif text.startswith("Jarvis: ") or text.startswith("JARVIS: "):
                self.output_text.insert(tk.END, "EDITH: ", "edith")
                # Use typing effect for EDITH responses
                self.create_typing_effect(text[8:] + "\n\n", "edith_text")
            elif text.startswith("Edith: ") or text.startswith("EDITH: "):
                self.output_text.insert(tk.END, "EDITH: ", "edith")
                # Use typing effect for EDITH responses
                self.create_typing_effect(text[7:] + "\n\n", "edith_text")
            elif text.startswith("System: "):
                self.output_text.insert(tk.END, "SYSTEM: ", "system")
                self.output_text.insert(tk.END, text[8:] + "\n", "system")
                self.output_text.yview(tk.END)
            else:
                self.output_text.insert(tk.END, "SYSTEM: ", "system")
                self.output_text.insert(tk.END, text + "\n", "system")
                self.output_text.yview(tk.END)
        except Exception as e:
            print(f"Error updating output: {e}")
            # If not in main thread, queue the update
            try:
                self.message_queue.put(text)
            except:
                print("Failed to queue message")
    
    def check_queue(self):
        # Process any pending messages in the queue
        try:
            while True:
                message = self.message_queue.get_nowait()
                
                # Check for special training status messages
                if message == "TRAINING_COMPLETE":
                    self.status_detail_label.config(text="STATUS: TRAINING COMPLETE", fg=self.edith_success)
                    self.train_button.config(state=tk.NORMAL)
                    
                    # Update UI elements
                    messagebox.showinfo("Training Complete", "EDITH has been successfully trained with your interactions!")
                    
                    # Add system message to output
                    self.output_text.insert(tk.END, "SYSTEM: ", "system")
                    self.output_text.insert(tk.END, "Training sequence completed successfully.\n", "system")
                    self.output_text.yview(tk.END)
                    
                elif message == "TRAINING_FAILED":
                    self.status_detail_label.config(text="STATUS: TRAINING FAILED", fg=self.edith_red)
                    self.train_button.config(state=tk.NORMAL)
                    
                    # Update UI elements
                    messagebox.showerror("Training Failed", "EDITH training failed. Please check the console for errors.")
                    
                    # Add system message to output
                    self.output_text.insert(tk.END, "SYSTEM: ", "system")
                    self.output_text.insert(tk.END, "Training sequence failed. Error detected.\n", "system")
                    self.output_text.yview(tk.END)
                    
                elif message == "NO_TRAINING_DATA":
                    self.status_detail_label.config(text="STATUS: NO NEW DATA", fg=self.edith_orange)
                    self.train_button.config(state=tk.NORMAL)
                    
                    # Update UI elements
                    messagebox.showinfo("No Training Data", "No new interactions to train on. Continue using EDITH to generate more training data.")
                    
                    # Add system message to output
                    self.output_text.insert(tk.END, "SYSTEM: ", "system")
                    self.output_text.insert(tk.END, "Insufficient training data. Continue interactions to generate more examples.\n", "system")
                    self.output_text.yview(tk.END)
                    
                elif message.startswith("TRAINING_ERROR:"):
                    error_msg = message.split(":", 1)[1].strip()
                    self.status_detail_label.config(text="STATUS: ERROR", fg=self.edith_red)
                    self.train_button.config(state=tk.NORMAL)
                    
                    # Update UI elements
                    messagebox.showerror("Training Error", f"Error during training: {error_msg}")
                    
                    # Add system message to output
                    self.output_text.insert(tk.END, "SYSTEM: ", "system")
                    self.output_text.insert(tk.END, f"Training error detected: {error_msg}\n", "system")
                    self.output_text.yview(tk.END)
                    
                else:
                    # Regular message - use the styled update_output method
                    self.update_output(message)
                
                self.message_queue.task_done()
        except queue.Empty:
            pass
        
        # Schedule the next queue check
        self.root.after(100, self.check_queue)
        
    def start_listening(self):
        # This will trigger the listening process in the background
        threading.Thread(target=self.listen_for_commands, daemon=True).start()

    def listen_for_commands(self):
        try:
            # Show "Listening..." message with visual indicator
            self.message_queue.put("System: VOICE RECOGNITION ACTIVE")
            
            # Intensify the scanning effect
            if not self.scanning_effect_active:
                self.create_scanning_effect()
            
            command = listen()
            
            if command:
                # Store the query for feedback
                self.last_query = command
                
                # Put the user's command in the queue for display
                self.message_queue.put("You: " + command)
                
                # Show "Processing..." message
                self.message_queue.put("System: PROCESSING COMMAND")
                
                # Change status to "Processing"
                self.status_label.config(text="PROCESSING", fg=self.edith_orange)
                
                # Process the command
                action_response = run_command(command)
                
                if action_response:
                    # Store the response for feedback
                    self.last_response = action_response
                    
                    # Put the response in the queue for display
                    self.message_queue.put("EDITH: " + action_response)
                    
                    # Change status back to "Listening"
                    if self.mic_on:
                        self.status_label.config(text="LISTENING", fg="#F44336")
                    else:
                        self.status_label.config(text="ONLINE", fg=self.edith_red)
                        self.stop_scanning_effect()
                    
                    # Speak the response with visualization
                    speak(action_response, self)
                else:
                    # Change status to "Thinking"
                    self.status_label.config(text="ANALYZING", fg="#9C27B0")  # Purple
                    
                    # Show thinking message
                    self.message_queue.put("System: ANALYZING REQUEST")
                    
                    # Get response from GPT
                    response = ask_gpt(command)
                    
                    # Store the response for feedback
                    self.last_response = response
                    
                    # Put the response in the queue for display
                    self.message_queue.put("EDITH: " + response)
                    
                    # Change status back to "Listening"
                    if self.mic_on:
                        self.status_label.config(text="LISTENING", fg="#F44336")
                    else:
                        self.status_label.config(text="ONLINE", fg=self.edith_red)
                        self.stop_scanning_effect()
                    
                    # Speak the response with visualization
                    speak(response, self)
            else:
                # If no command was detected
                self.message_queue.put("System: NO VOICE INPUT DETECTED")
                
                # Reset status if still listening
                if self.mic_on:
                    self.status_label.config(text="LISTENING", fg="#F44336")
                else:
                    self.status_label.config(text="ONLINE", fg=self.edith_red)
                    self.stop_scanning_effect()
        except Exception as e:
            print(f"Error in listen_for_commands: {e}")
            self.message_queue.put(f"System: ERROR PROCESSING COMMAND: {e}")
            # Reset status
            if self.mic_on:
                self.status_label.config(text="LISTENING", fg="#F44336")
            else:
                self.status_label.config(text="ONLINE", fg=self.edith_red)
                self.stop_scanning_effect()

    def provide_feedback(self, positive):
        """
        Handle user feedback on JARVIS responses.
        
        Args:
            positive (bool): Whether the feedback is positive
        """
        if not self.last_query or not self.last_response:
            messagebox.showinfo("Feedback", "No recent interaction to provide feedback on.")
            return
        
        try:
            from core.self_training import provide_feedback
            provide_feedback(self.last_query, self.last_response, feedback_positive=positive)
            
            if positive:
                messagebox.showinfo("Feedback", "Thank you for your positive feedback! I'll remember this interaction.")
            else:
                messagebox.showinfo("Feedback", "Thank you for your feedback. I'll try to improve my responses.")
                
            # Clear the last interaction
            self.last_query = ""
            self.last_response = ""
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not process feedback: {e}")

    def trigger_training(self):
        """
        Manually trigger JARVIS self-training.
        """
        try:
            # Ask for confirmation
            confirm = messagebox.askyesno("Train JARVIS", 
                                         "Do you want to train JARVIS with your interactions?\n\n"
                                         "This process may take several minutes and will improve JARVIS's responses "
                                         "based on your previous interactions.")
            if not confirm:
                return
            
            # Start training in a separate thread
            threading.Thread(target=self._run_training, daemon=True).start()
            
            # Update status
            self.training_status.config(text="Training in progress...", fg="orange")
            self.train_button.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not start training: {e}")
    
    def _run_training(self):
        """
        Run the training process in a background thread.
        """
        try:
            from core.self_training import generate_training_data, train_model
            
            # Generate training data
            if generate_training_data():
                # Train the model
                if train_model():
                    # Update status in the main thread
                    self.message_queue.put("TRAINING_COMPLETE")
                else:
                    # Update status in the main thread
                    self.message_queue.put("TRAINING_FAILED")
            else:
                # Update status in the main thread
                self.message_queue.put("NO_TRAINING_DATA")
                
        except Exception as e:
            # Update status in the main thread
            self.message_queue.put(f"TRAINING_ERROR: {e}")
    
    def update_training_status(self):
        """
        Update the training status display with enhanced metrics.
        """
        try:
            from core.self_training import get_training_stats
            stats = get_training_stats()
            
            # Get stats
            success_rate = stats.get('success_rate', 0)
            examples = stats.get('training_examples', 0)
            interactions = stats.get('total_interactions', 0)
            successful = stats.get('successful_interactions', 0)
            
            # Update the progress circle
            self.update_progress_circle(success_rate)
            
            # Add additional metrics label if it doesn't exist
            if not hasattr(self, 'additional_metrics_label'):
                self.additional_metrics_label = tk.Label(
                    self.training_frame,
                    text=f"ACCURACY: {success_rate:.1f}% • SUCCESS: {successful}/{interactions}",
                    font=("Courier New", 9),
                    fg="#AAAAAA",
                    bg=self.edith_dark,
                    anchor="w"
                )
                self.additional_metrics_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 5))
            else:
                # Update the additional metrics
                self.additional_metrics_label.config(
                    text=f"ACCURACY: {success_rate:.1f}% • SUCCESS: {successful}/{interactions}"
                )
            
            # Update the stats labels
            self.examples_label.config(text=f"EXAMPLES: {examples}")
            self.interactions_label.config(text=f"INTERACTIONS: {interactions}")
            
            # Update the status label
            if stats.get('is_training', False):
                self.status_detail_label.config(text="STATUS: TRAINING", fg="#9C27B0")  # Purple for training
                self.train_button.config(state=tk.DISABLED)
                
                # Update main status indicator
                self.status_label.config(text="TRAINING", fg="#9C27B0")
                
                # Add a training message if not already shown
                if not hasattr(self, 'training_message_shown') or not self.training_message_shown:
                    self.message_queue.put("System: TRAINING SEQUENCE INITIATED")
                    self.training_message_shown = True
            else:
                # Format the status text based on success rate with more granular feedback
                if success_rate < 30:
                    status_color = self.edith_red
                    status_text = "STATUS: INITIAL LEARNING"
                elif success_rate < 50:
                    status_color = self.edith_red
                    status_text = "STATUS: DEVELOPING"
                elif success_rate < 70:
                    status_color = self.edith_orange
                    status_text = "STATUS: IMPROVING"
                elif success_rate < 85:
                    status_color = self.edith_orange
                    status_text = "STATUS: OPTIMIZING"
                elif success_rate < 95:
                    status_color = self.edith_success
                    status_text = "STATUS: ADVANCED"
                else:
                    status_color = self.edith_success
                    status_text = "STATUS: MASTERED"
                
                self.status_detail_label.config(text=status_text, fg=status_color)
                self.train_button.config(state=tk.NORMAL)
                
                # Reset training message flag
                self.training_message_shown = False
                
                # Reset main status indicator if not listening
                if not self.mic_on:
                    self.status_label.config(text="ONLINE", fg=self.edith_red)
                
        except Exception as e:
            self.status_detail_label.config(text=f"STATUS: ERROR", fg=self.edith_red)
            print(f"Error updating training status: {e}")
    
    def schedule_training_status_update(self):
        """
        Schedule periodic updates of the training status.
        """
        self.update_training_status()
        # Schedule the next update in 10 seconds
        self.root.after(10000, self.schedule_training_status_update)
    
    def provide_feedback(self, positive):
        """
        Handle user feedback on EDITH responses.
        
        Args:
            positive (bool): Whether the feedback is positive
        """
        if not self.last_query or not self.last_response:
            messagebox.showinfo("Feedback", "No recent interaction to evaluate.")
            return
        
        try:
            from core.self_training import provide_feedback
            provide_feedback(self.last_query, self.last_response, feedback_positive=positive)
            
            if positive:
                self.message_queue.put("System: RESPONSE APPROVED - ADDING TO TRAINING DATA")
                # Flash the success color
                self.thumbs_up_button.config(bg=self.edith_success)
                self.root.after(500, lambda: self.thumbs_up_button.config(bg=self.edith_dark))
            else:
                self.message_queue.put("System: RESPONSE REJECTED - MARKED FOR IMPROVEMENT")
                # Flash the error color
                self.thumbs_down_button.config(bg=self.edith_red)
                self.root.after(500, lambda: self.thumbs_down_button.config(bg=self.edith_dark))
                
            # Clear the last interaction
            self.last_query = ""
            self.last_response = ""
            
        except Exception as e:
            self.message_queue.put(f"System: ERROR PROCESSING FEEDBACK: {e}")

    def trigger_training(self):
        """
        Manually trigger EDITH self-training.
        """
        try:
            # Ask for confirmation
            confirm = messagebox.askyesno("Training Sequence", 
                                         "Initiate EDITH training sequence?\n\n"
                                         "This process will optimize EDITH's neural network using "
                                         "recorded interactions. Duration: 3-5 minutes.")
            if not confirm:
                return
            
            # Start training in a separate thread
            threading.Thread(target=self._run_training, daemon=True).start()
            
            # Update status
            self.status_detail_label.config(text="STATUS: TRAINING", fg=self.edith_orange)
            self.train_button.config(state=tk.DISABLED)
            
            # Show training message
            self.message_queue.put("System: INITIATING TRAINING SEQUENCE")
            
            # Create scanning effect
            self.create_scanning_effect()
            
        except Exception as e:
            self.message_queue.put(f"System: TRAINING ERROR: {e}")
    
    def _run_training(self):
        """
        Run the training process in a background thread.
        """
        try:
            from core.self_training import generate_training_data, train_model
            
            # Generate training data
            self.message_queue.put("System: GENERATING TRAINING DATA FROM INTERACTIONS")
            if generate_training_data():
                # Train the model
                self.message_queue.put("System: OPTIMIZING NEURAL NETWORK")
                if train_model():
                    # Update status in the main thread
                    self.message_queue.put("TRAINING_COMPLETE")
                    # Stop scanning effect
                    self.stop_scanning_effect()
                else:
                    # Update status in the main thread
                    self.message_queue.put("TRAINING_FAILED")
                    # Stop scanning effect
                    self.stop_scanning_effect()
            else:
                # Update status in the main thread
                self.message_queue.put("NO_TRAINING_DATA")
                # Stop scanning effect
                self.stop_scanning_effect()
                
        except Exception as e:
            # Update status in the main thread
            self.message_queue.put(f"TRAINING_ERROR: {e}")
            # Stop scanning effect
            self.stop_scanning_effect()
    
    def resize_handler(self, event):
        """Handle window resize events"""
        # Update the decoration lines if window size changes
        if hasattr(self, 'decoration_canvas'):
            width = self.output_frame.winfo_width()
            self.decoration_canvas.coords("right_line", width - 20, 10, width, 10)
            
        if hasattr(self, 'bottom_decoration'):
            width = self.output_frame.winfo_width()
            self.bottom_decoration.coords("bottom_right_line", width - 20, 10, width, 10)
            
        # Update voice visualization if it exists
        if hasattr(self, 'voice_canvas'):
            self.voice_canvas.config(width=self.footer_frame.winfo_width() - 40)
            
    def create_voice_visualization(self):
        """Create a voice visualization canvas"""
        try:
            # Create a frame for the visualization
            if not hasattr(self, 'voice_viz_frame'):
                self.voice_viz_frame = tk.Frame(
                    self.footer_frame, 
                    bg=self.edith_dark,
                    height=30
                )
                self.voice_viz_frame.pack(fill=tk.X, padx=20, pady=(5, 0))
                
                # Create canvas for visualization
                self.voice_canvas = tk.Canvas(
                    self.voice_viz_frame,
                    height=30,
                    bg=self.edith_dark,
                    highlightthickness=0,
                    width=self.footer_frame.winfo_width() - 40
                )
                self.voice_canvas.pack(fill=tk.X)
                
                # Create initial visualization bars
                self.voice_bars = []
                num_bars = 40
                bar_width = 4
                bar_spacing = 2
                bar_height = 2
                
                for i in range(num_bars):
                    x = i * (bar_width + bar_spacing) + 10
                    bar = self.voice_canvas.create_rectangle(
                        x, 15 - bar_height, 
                        x + bar_width, 15 + bar_height,
                        fill=self.edith_red,
                        outline=""
                    )
                    self.voice_bars.append(bar)
                
                # Add label
                self.voice_canvas.create_text(
                    10, 25,
                    text="VOICE MODULATION",
                    font=("Courier New", 7),
                    fill=self.edith_red,
                    anchor="w"
                )
                
                # Start idle animation
                self.animate_voice_idle()
        except Exception as e:
            print(f"Error creating voice visualization: {e}")
            
    def animate_voice_idle(self):
        """Animate voice visualization in idle state"""
        try:
            if not hasattr(self, 'voice_bars') or not self.voice_bars:
                return
                
            # Generate smooth idle pattern
            t = time.time() * 2  # Time factor for animation speed
            num_bars = len(self.voice_bars)
            
            for i, bar in enumerate(self.voice_bars):
                # Create a smooth wave pattern
                phase = i / num_bars * math.pi * 2
                height = 2 + 3 * abs(math.sin(t + phase))
                
                # Update bar height
                self.voice_canvas.coords(
                    bar,
                    self.voice_canvas.coords(bar)[0],
                    15 - height,
                    self.voice_canvas.coords(bar)[2],
                    15 + height
                )
                
                # Subtle color variation
                r = int(229 + 26 * math.sin(t + phase))
                g = int(57 + 20 * math.sin(t + phase + 1))
                color = f'#{r:02x}{g:02x}00'
                self.voice_canvas.itemconfig(bar, fill=color)
            
            # Continue animation
            self.root.after(50, self.animate_voice_idle)
        except Exception as e:
            print(f"Error in voice idle animation: {e}")
            # Try again later
            self.root.after(1000, self.animate_voice_idle)
            
    def animate_voice_speaking(self, amplitudes=None):
        """Animate voice visualization in speaking state"""
        try:
            if not hasattr(self, 'voice_bars') or not self.voice_bars:
                return
                
            num_bars = len(self.voice_bars)
            
            # If no amplitudes provided, generate random ones
            if amplitudes is None:
                # Generate more dynamic speaking pattern
                t = time.time() * 5  # Faster for speaking
                amplitudes = []
                
                for i in range(num_bars):
                    # Create a more dynamic pattern for speaking
                    phase = i / num_bars * math.pi * 4
                    # More variation in height
                    height = 2 + 10 * abs(math.sin(t + phase) * math.cos(t * 0.7 + phase * 1.3))
                    amplitudes.append(height)
            
            # Apply amplitudes to bars
            for i, bar in enumerate(self.voice_bars):
                height = amplitudes[i % len(amplitudes)]
                
                # Update bar height
                self.voice_canvas.coords(
                    bar,
                    self.voice_canvas.coords(bar)[0],
                    15 - height,
                    self.voice_canvas.coords(bar)[2],
                    15 + height
                )
                
                # More vibrant color for speaking
                intensity = min(255, int(200 + height * 5))
                self.voice_canvas.itemconfig(bar, fill=f'#{intensity:02x}3000')
        except Exception as e:
            print(f"Error in voice speaking animation: {e}")
            
    # Neural network visualization has been removed to improve performance
    
    def animate_logo(self, offset=0):
        """Animate the EDITH logo for a holographic effect"""
        try:
            # Subtle floating/pulsing effect
            t = time.time() * 2
            
            # Vertical floating motion
            y_offset = math.sin(t) * 1.5
            
            # Update positions
            self.logo_canvas.coords(
                self.title_text,
                10, 20 + y_offset
            )
            
            # Shadow follows with slight delay for 3D effect
            self.logo_canvas.coords(
                self.shadow_text1,
                11, 21 + y_offset * 0.8
            )
            
            self.logo_canvas.coords(
                self.shadow_text2,
                12, 22 + y_offset * 0.6
            )
            
            # Color pulsing for holographic effect
            intensity = int(200 + 55 * math.sin(t))
            r = intensity
            g = int(intensity * 0.2)
            self.logo_canvas.itemconfig(
                self.title_text,
                fill=f"#{r:02x}{g:02x}00"
            )
            
            # Schedule next frame
            self.root.after(50, self.animate_logo, (offset + 1) % 360)
        except Exception as e:
            print(f"Error animating logo: {e}")
            # Try again later
            self.root.after(1000, self.animate_logo, 0)
    
    def generate_voice_amplitudes(self, text):
        """Generate simulated voice amplitudes based on text"""
        try:
            # Create amplitudes based on text characteristics
            words = text.split()
            amplitudes = []
            
            for word in words:
                # Word length affects amplitude
                base_amp = 3 + min(len(word), 10) / 2
                
                # Add some randomness
                for _ in range(len(word)):
                    amp = base_amp + random.uniform(-1, 1)
                    amplitudes.append(amp)
                
                # Add pause between words
                for _ in range(2):
                    amplitudes.append(2)
            
            # Ensure we have enough amplitudes
            while len(amplitudes) < 40:
                amplitudes.extend(amplitudes)
            
            return amplitudes[:40]
        except Exception as e:
            print(f"Error generating voice amplitudes: {e}")
            return [3] * 40  # Default amplitudes

    def run(self):
        # Bind resize event
        self.root.bind("<Configure>", self.resize_handler)
        
        # Start the main loop
        self.root.mainloop()
