import tkinter as tk
from PIL import ImageTk
import operator
import time

from src.constants import ChangeType
from src.controller import RunStatus
from src.gui.nodeEditor import NodeEditor

from src.grid import Grid


class CanvasMap(tk.Canvas):
    """
    The canvas widget used to edit the placement of nodes and display the edges while solving the problem

    Attributes:
        controller: The controller to perform various functions
        image: The PIL image of the background
        image_tk: The scaled ImageTk that is drawn on the canvas
        background_item: The tk item tag that belongs to the background
        min_scale: The minimum scale that the background should be set to
        max_scale: The maximum scale that the background should be set to
        grid: The grid that holds the scale and provides conversion functions between them
        running: Should only be true while the simulation is running
        edges: A map of edges to the tk item drawn on the canvas. Each edge is stored as a frozenset of two nodes,
            eg. frozenset([node1, node2])
        self.nodes: A map of node model objects to a (circle, text) pair of tk items drawn on the canvas
        x_last: The last x position that was either clicked or dragged on the canvas
        y_last: The last y position that was either clicked or dragged on the canvas
        click_time: This is set when the user clicks on the canvas and provides the time of the last clicked
        dragging: True only if the user is currently dragging a node
        editor: The editor widget that's beig used to edit a node
    """
    CIRCLE_RADIUS = 20

    def __init__(self, parent, controller, *args, **kwargs):
        tk.Canvas.__init__(self, parent, highlightthickness=0, *args, **kwargs)
        self.controller = controller
        self.controller.model.register(self.on_model_update)
        self.controller.model.nodes.register(self.on_node_change)
        self.controller.annealing.register(self.on_edge_change)
        self.controller.register(self.on_run)
        self.controller.max_dist_func = self.max_dist
        self.image = None
        self.image_tk = None
        self.background_item = None
        self.min_scale = 1
        self.max_scale = 1
        self.grid = None
        self.running = False
        self.edges = {}

        # For node bindings
        self.nodes = {}
        self.x_last = 0
        self.y_last = 0
        self.click_time = 0
        self.dragging = False
        self.editor = None

        self.bind('<Control-MouseWheel>', self.on_scroll)
        self.bind('<Button-1>', self.on_click)
        self.bind('<Double-Button-1>', self.on_double_click)

    def max_dist(self):
        """
        Returns the maximum distance (diagonal screen distance) that an edge could have in the graph
        """
        width, height = self.grid.to_grid_coordinates(self.winfo_width(), self.winfo_height())
        return (width**2+height**2)**(1/2)

    def draw_tk(self):
        """
        Draws the ImageTk item on the canvas and deletes the old one if it exists
        """
        if self.background_item:
            self.delete(self.background_item)
        width, height = self.image.size
        self.config(width=width*self.grid.scale, height=height*self.grid.scale)
        scaled_img = self.image.resize((int(width * self.grid.scale), int(height * self.grid.scale)))
        self.image_tk = ImageTk.PhotoImage(scaled_img)
        self.background_item = self.create_image([size // 2 for size in scaled_img.size], image=self.image_tk)

    def get_recommended_scale(self, percentage, width, height):
        """
        Gets the scale that would cause the window to take up 'percentage' of the total available screen space
        :param percentage:
        :param width:
        :param height:
        :return:
        """
        width_scale = (self.winfo_screenwidth() * percentage) / width
        height_scale = (self.winfo_screenheight() * percentage) / height
        return min(width_scale, height_scale)

    def edit_node(self, node):
        """
        Opens the node editor that edits the node name or deletes it at the last clicked location. Make sure to draw it
        so it does not go past the edge of the screen

        Args:
            node: The node model to edit
        """
        x, y = self.x_last, self.y_last
        self.delete_editor()
        self.editor = NodeEditor(self, self.controller, node)
        self.editor.place(x=self.x_last, y=self.y_last)
        self.editor.update()
        width, height = self.editor.winfo_width(), self.editor.winfo_height()
        redraw = False
        if x + width > self.winfo_width():
            x = x - width
            redraw = True
        if y + height > self.winfo_height():
            y = y - height
            redraw = True
        if redraw:
            self.editor.place_configure(x=x, y=y)

    def delete_editor(self):
        """
        If the editor for editing a single node exists, deletes it
        """
        if self.editor:
            self.editor.destroy()
            self.editor = None

    # ---------------------------------------------Observer Functions---------------------------------------------------
    def on_run(self, run_status):
        """
        Sets the running flag based on if the simulation is running an deletes all edges if it is running

        Args:
            run_status: Whether or not the simulation is running or stopped
        """
        if run_status == RunStatus.START:
            self.running = True
            self.delete('edge')
        elif run_status == RunStatus.END:
            self.running = False

    def on_node_change(self, change_type, node):
        """
        Run when a node is added or deleted to the model. Draws the node on the canvas and attaches bindings or deletes

        Args:
            change_type: Whether the node is being added or deleted
            node: The node to be added or deleted
        """
        if change_type == ChangeType.ADD:
            x_scaled, y_scaled = self.grid.from_grid_coordinates(node.x, node.y)
            pos = (x_scaled-self.CIRCLE_RADIUS, y_scaled-self.CIRCLE_RADIUS,
                   x_scaled+self.CIRCLE_RADIUS, y_scaled+self.CIRCLE_RADIUS)
            circ = self.create_oval(pos, outline='black', fill='grey', width=3, tags='node')
            text = self.create_text(x_scaled, y_scaled, text=node.name, fill='black', tags='node')
            self.nodes[node] = (circ, text)
            node.register(lambda key: self.itemconfigure(text, text=node.name) if key == 'name' else None)
            for tag in circ, text:
                self.tag_bind(tag, '<B1-Motion>', lambda event: self.on_node_drag(event, node))
                self.tag_bind(tag, '<Button-1>', self.on_node_click)
                self.tag_bind(tag, '<ButtonRelease-1>', lambda event: self.on_node_release(node))
        elif change_type == ChangeType.REMOVE:
            for item in self.nodes[node]:
                self.delete(item)

    def on_edge_change(self, change_type, node1, node2):
        """
        Run when an edge is added or deleted from the simulation

        Args:
            change_type: Whether the node is being added or deleted from the simulation
            node1: The first node of the edge
            node2: The second node of the edge
        """
        if change_type == ChangeType.ADD:
            start = self.grid.from_grid_coordinates(node1.x, node1.y)
            end = self.grid.from_grid_coordinates(node2.x, node2.y)
            self.edges[frozenset((node1, node2))] = self.create_line((start[0], start[1], end[0], end[1]), width=3, tags='edge')
            self.update()
        if change_type == ChangeType.REMOVE:
            self.delete(self.edges[frozenset([node1, node2])])

    def on_model_update(self, key):
        """
        Run when the main CanvasMap model is changed. If the background was changed updates it on the canvas

        Args:
            key: The key that was changed in the model.
        """
        if key == 'background':
            self.image = self.controller.model.background
            x, y = self.image.size
            self.grid = Grid(self.get_recommended_scale(.7, x, y))
            self.min_scale = self.get_recommended_scale(.2, x, y)
            self.max_scale = self.get_recommended_scale(.8, x, y)
            self.draw_tk()

    # ------------------------------------------------Canvas bindings---------------------------------------------------
    def on_scroll(self, event):
        """
        Run on canvas scroll, and will resize the window if the simulation is not running
        """
        if self.running:
            return False
        change = .05 * self.grid.scale
        if event.delta > 0 and self.grid.scale + change < self.max_scale:
            self.grid.scale += change
        elif event.delta < 0 and self.grid.scale - change > self.min_scale:
            self.grid.scale -= change
        else:
            return
        self.delete('node')
        self.delete('edge')
        self.delete_editor()
        self.draw_tk()
        for node in self.controller.get_nodes():
            self.on_node_change(ChangeType.ADD, node)

    def on_click(self, event):
        """
        If the simulation is not running, deletes the node editor if it exists
        """
        if self.running:
            return False
        self.delete('edge')
        if time.time() - self.click_time > .25 and self.editor:
            self.editor.destroy()

    def on_double_click(self, event):
        """
        Creates a new node if the simulation is not running
        """
        if self.running:
            return False
        x, y = event.x, event.y
        scaled_x, scaled_y = self.grid.to_grid_coordinates(x, y)
        self.controller.create_node(int(scaled_x), int(scaled_y))

    # -------------------------------------------------Node bindings----------------------------------------------------
    def on_node_click(self, event):
        """
        Records the time and location of a click on a node to create an editor on a mouse release
        """
        if self.running:
            return False
        self.click_time = time.time()
        self.x_last = event.x
        self.y_last = event.y

    def on_node_release(self, node):
        """
        Draws an editor to edit a node if the node is not being dragged, otherwise updates in the model

        Args:
            node: The node being released
        """
        if self.running:
            return False
        if self.dragging:
            # Set model coordinates to coordinates of text
            node.x, node.y = [int(x) for x in self.grid.to_grid_coordinates(*self.coords(self.nodes[node][1]))]
            self.dragging = False
        else:
            if time.time() - self.click_time < .5:
                self.edit_node(node)

    def on_node_drag(self, event, node):
        """
        Run when a node is being dragged, moves the drawn items on the screen if it will not go past the edge of the
        canvas

        Args:
            event: The event object
            node: The node to move
        """
        if self.running:
            return False
        self.delete_editor()
        self.dragging = True
        current_pos = self.coords(self.nodes[node][1])
        change = event.x-self.x_last, event.y-self.y_last
        future_pos = list(map(operator.add, current_pos, change))
        if self.CIRCLE_RADIUS <= future_pos[0] <= self.winfo_width() - self.CIRCLE_RADIUS \
                and self.CIRCLE_RADIUS <= future_pos[1] <= self.winfo_height() - self.CIRCLE_RADIUS:
            for item in self.nodes[node]:
                self.move(item, *change)
            self.x_last = event.x
            self.y_last = event.y

    # ------------------------------------------------------------------------------------------------------------------
