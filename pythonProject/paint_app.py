import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import simpledialog

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paint App")

        self.color = "black"
        self.brush_size = 5
        self.old_x = None
        self.old_y = None
        self.lines = []  # Track lines for undo
        self.current_tool = "brush"  # Track current tool
        self.is_blending = False
        self.blend_color = None
        self.smudge_radius = 10  # Radius for smudge effect

        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.set_start_point)
        self.canvas.bind("<B1-Motion>", self.use_tool)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        self.canvas.bind("<B3-Motion>", self.erase)  # Bind right mouse button for eraser
        self.canvas.bind("<ButtonRelease-3>", self.reset)  # Reset after erasing

        self.canvas.bind("<Button-4>", self.toggle_blend_tool)  # Bind mouse button #4 for blend tool toggle
        self.canvas.bind("<Button-5>", self.toggle_smudge_tool)  # Bind mouse button #5 for smudge tool toggle

        self.canvas.bind("<Button-2>", self.place_stamp)  # Middle mouse button to place shape stamp

        self.create_menu()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        brush_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Brush", menu=brush_menu)
        brush_menu.add_command(label="Brush Size", command=self.choose_brush_size)
        brush_menu.add_command(label="Brush Color", command=self.choose_brush_color)

        tool_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Tools", menu=tool_menu)
        tool_menu.add_command(label="Brush", command=lambda: self.set_tool("brush"))
        tool_menu.add_command(label="Blend", command=lambda: self.set_tool("blend"))
        tool_menu.add_command(label="Smudge", command=lambda: self.set_tool("smudge"))

        shape_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Shapes", menu=shape_menu)
        shape_menu.add_command(label="Rectangle", command=lambda: self.set_tool("rectangle"))
        shape_menu.add_command(label="Circle", command=lambda: self.set_tool("circle"))
        shape_menu.add_command(label="Triangle", command=lambda: self.set_tool("triangle"))

        edit_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear All", command=self.clear_canvas)
        edit_menu.add_command(label="Undo", command=self.undo)  # Add undo option

    def set_start_point(self, event):
        self.old_x = event.x
        self.old_y = event.y

    def use_tool(self, event):
        if self.current_tool == "brush":
            if self.is_blending:
                self.blend_paint(event)
            else:
                self.paint(event)
        elif self.current_tool == "smudge":
            self.smudge(event)

    def paint(self, event):
        if self.old_x and self.old_y:
            line = self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                           width=self.brush_size, fill=self.color,
                                           capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
            self.lines.append(line)  # Store line for undo
            self.old_x = event.x
            self.old_y = event.y

    def toggle_blend_tool(self, event):
        self.is_blending = not self.is_blending
        if self.is_blending:
            self.blend_color = askcolor(title="Select Blend Color")[1]

    def blend_paint(self, event):
        if self.old_x and self.old_y:
            # Blend the current brush color with the selected blend color
            blended_color = self.blend_colors(self.color, self.blend_color)
            line = self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                           width=self.brush_size, fill=blended_color,
                                           capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
            self.lines.append(line)  # Store line for undo
            self.old_x = event.x
            self.old_y = event.y

    def blend_colors(self, color1, color2):
        r1, g1, b1 = self.root.winfo_rgb(color1)
        r2, g2, b2 = self.root.winfo_rgb(color2)
        r = (r1 + r2) // 2 // 256
        g = (g1 + g2) // 2 // 256
        b = (b1 + b2) // 2 // 256
        return f'#{r:02x}{g:02x}{b:02x}'

    def reset(self, event):
        self.old_x = None
        self.old_y = None

    def choose_brush_size(self):
        size = simpledialog.askinteger("Brush Size", "Enter brush size:", initialvalue=self.brush_size)
        if size:
            self.brush_size = size

    def choose_brush_color(self):
        color = askcolor(color=self.color)[1]
        if color:
            self.color = color

    def clear_canvas(self):
        self.canvas.delete("all")
        self.lines.clear()  # Clear the list of lines for undo

    def undo(self):
        if self.lines:
            self.canvas.delete(self.lines.pop())  # Remove the last drawn line

    def erase(self, event):
        if self.old_x and self.old_y:
            eraser_size = self.brush_size * 2  # Eraser size can be different from brush size
            self.canvas.create_rectangle(event.x - eraser_size, event.y - eraser_size,
                                         event.x + eraser_size, event.y + eraser_size,
                                         fill="white", outline="white")
        self.old_x = event.x
        self.old_y = event.y

    def set_tool(self, tool):
        self.current_tool = tool

    def place_stamp(self, event):
        if self.current_tool == "rectangle":
            self.canvas.create_rectangle(event.x - 20, event.y - 10, event.x + 20, event.y + 10, fill=self.color)
        elif self.current_tool == "circle":
            self.canvas.create_oval(event.x - 20, event.y - 20, event.x + 20, event.y + 20, fill=self.color)
        elif self.current_tool == "triangle":
            self.canvas.create_polygon(event.x, event.y - 20, event.x - 20, event.y + 20, event.x + 20, event.y + 20, fill=self.color)

    def toggle_smudge_tool(self, event):
        if self.current_tool == "smudge":
            self.current_tool = "brush"
        else:
            self.current_tool = "smudge"

    def smudge(self, event):
        if self.old_x and self.old_y:
            nearby_objects = self.canvas.find_overlapping(event.x - self.smudge_radius, event.y - self.smudge_radius,
                                                          event.x + self.smudge_radius, event.y + self.smudge_radius)
            for obj_id in nearby_objects:
                obj_color = self.canvas.itemcget(obj_id, "fill")
                blended_color = self.blend_colors(self.color, obj_color)
                self.canvas.itemconfig(obj_id, fill=blended_color)

    def blend_colors(self, color1, color2):
        r1, g1, b1 = self.root.winfo_rgb(color1)
        r2, g2, b2 = self.root.winfo_rgb(color2)
        r = (r1 + r2) // 2 // 256
        g = (g1 + g2) // 2 // 256
        b = (b1 + b2) // 2 // 256
        return f'#{r:02x}{g:02x}{b:02x}'

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()