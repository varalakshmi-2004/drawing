import tkinter as tk
from tkinter import colorchooser, filedialog
from PIL import Image, ImageDraw, ImageTk

class DrawingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Drawing App with Image Loading and Drawing")
        self.master.geometry("800x600")
        self.master.configure(bg='#f0f0f0')

        # Initialize color, brush size, and selected shape
        self.current_color = 'black'
        self.brush_size = 3
        self.bg_color = 'white'
        self.shape = 'line'  # Default shape

        # Initialize undo and redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # Create the canvas
        self.canvas = tk.Canvas(self.master, bg=self.bg_color, width=800, height=500)
        self.canvas.pack(padx=10, pady=10)

        # Initialize images
        self.image = Image.new("RGB", (800, 500), self.bg_color)
        self.current_image = self.image.copy()
        self.draw = ImageDraw.Draw(self.image)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_on_canvas)

        # Control buttons
        self.color_button = tk.Button(self.master, text="Choose Color", command=self.choose_color, font=("Arial", 12))
        self.color_button.pack(padx=10, pady=(0, 10))

        self.bg_color_button = tk.Button(self.master, text="Choose Background Color", command=self.choose_bg_color, font=("Arial", 12))
        self.bg_color_button.pack(padx=10, pady=(0, 10))

        self.brush_size_slider = tk.Scale(self.master, from_=1, to_=10, orient=tk.HORIZONTAL, label="Brush Size", length=200, sliderlength=20, font=("Arial", 12))
        self.brush_size_slider.set(self.brush_size)
        self.brush_size_slider.pack(padx=10, pady=(0, 10))

        # Shape selection
        self.shape_menu = tk.StringVar(value=self.shape)
        self.shape_menu_options = tk.OptionMenu(self.master, self.shape_menu, 'line', 'rectangle', 'oval')
        self.shape_menu_options.config(font=("Arial", 12))
        self.shape_menu_options.pack(padx=10, pady=(0, 10))

        # Action buttons
        self.save_button = tk.Button(self.master, text="Save", command=self.save_image, font=("Arial", 12))
        self.save_button.pack(padx=10, pady=(0, 10))

        self.clear_button = tk.Button(self.master, text="Clear", command=self.clear_canvas, font=("Arial", 12))
        self.clear_button.pack(padx=10, pady=(0, 10))

        self.undo_button = tk.Button(self.master, text="Undo", command=self.undo, font=("Arial", 12))
        self.undo_button.pack(padx=10, pady=(0, 10))

        self.redo_button = tk.Button(self.master, text="Redo", command=self.redo, font=("Arial", 12))
        self.redo_button.pack(padx=10, pady=(0, 10))

        self.load_button = tk.Button(self.master, text="Load Image", command=self.load_image, font=("Arial", 12))
        self.load_button.pack(padx=10, pady=(0, 10))

        # Track drawing state
        self.current_draw = ImageDraw.Draw(self.current_image)

    def start_draw(self, event):
        self.last_x, self.last_y = event.x, event.y
        self.save_state()

    def draw_on_canvas(self, event):
        shape = self.shape_menu.get()
        brush_size = self.brush_size_slider.get()

        if shape == 'line':
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, fill=self.current_color, width=brush_size)
            self.current_draw.line([self.last_x, self.last_y, event.x, event.y], fill=self.current_color, width=brush_size)
        elif shape == 'rectangle':
            self.canvas.create_rectangle(self.last_x, self.last_y, event.x, event.y, outline=self.current_color, width=brush_size)
            self.current_draw.rectangle([self.last_x, self.last_y, event.x, event.y], outline=self.current_color, width=brush_size)
        elif shape == 'oval':
            self.canvas.create_oval(self.last_x, self.last_y, event.x, event.y, outline=self.current_color, width=brush_size)
            self.current_draw.ellipse([self.last_x, self.last_y, event.x, event.y], outline=self.current_color, width=brush_size)

        self.last_x, self.last_y = event.x, event.y

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color

    def choose_bg_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.bg_color = color
            self.canvas.config(bg=self.bg_color)
            self.image = Image.new("RGB", (800, 500), self.bg_color)
            self.current_image = self.image.copy()
            self.current_draw = ImageDraw.Draw(self.current_image)
            self.clear_canvas()  # Clear the canvas to apply new background color

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image.paste(self.bg_color)
        self.current_image.paste(self.bg_color)
        self.current_draw = ImageDraw.Draw(self.current_image)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_canvas()

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.image.save(file_path)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif"), ("All files", "*.*")])
        if file_path:
            loaded_image = Image.open(file_path)
            loaded_image = loaded_image.resize((800, 500), Image.ANTIALIAS)
            self.image.paste(loaded_image)
            self.current_image = self.image.copy()
            self.current_draw = ImageDraw.Draw(self.current_image)
            self.update_canvas()

    def save_state(self):
        self.undo_stack.append(self.current_image.copy())
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.current_image.copy())
            self.current_image = self.undo_stack.pop()
            self.current_draw = ImageDraw.Draw(self.current_image)
            self.update_canvas()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.current_image.copy())
            self.current_image = self.redo_stack.pop()
            self.current_draw = ImageDraw.Draw(self.current_image)
            self.update_canvas()

    def update_canvas(self):
        self.tk_image = ImageTk.PhotoImage(self.current_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
