from tkinter import ttk
import tkinter as tk


class NodeEditor(ttk.Frame):
    """
    Widget to be drawn on the canvas to either edit the name of a node or delete the node
    """
    def __init__(self, parent, controller, node, *args, **kwargs):
        """
        Sets up the widget

        Args:
            parent: The parent widget
            controller: The controller object to destroy the node with
            node: The Node model, this will be directly edited
            args: Any positional arguments for the frame
            kwargs: Any keyword arguments for the frame
        """
        ttk.Frame.__init__(self, parent, borderwidth=3, relief=tk.RAISED, *args, **kwargs)
        self.controller = controller
        self.node = node
        self.entry_var = tk.StringVar()
        self.entry_var.set(node.name)

        top = ttk.Frame(self)
        bottom = ttk.Frame(self)

        label = ttk.Label(top, text='Name')
        self.entry = ttk.Entry(top, textvariable=self.entry_var)
        button = ttk.Button(bottom, text='Confirm', command=self.on_confirm)
        delete = ttk.Button(bottom, text='Delete', command=self.on_delete)

        top.pack(expand=tk.YES, fill=tk.BOTH, padx=(0, 3), pady=(3, 3))
        label.pack(side=tk.LEFT, expand=tk.YES)
        self.entry.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

        bottom.pack(expand=tk.YES, fill=tk.BOTH, pady=(0, 3))
        top.pack(expand=tk.YES, fill=tk.BOTH)
        button.pack(side=tk.LEFT, expand=tk.YES)
        delete.pack(side=tk.LEFT, expand=tk.YES)

    def on_confirm(self):
        """
        Edits the name of the node in the model an destroys the widget
        """
        self.node.name = self.entry.get()
        self.destroy()

    def on_delete(self):
        """
        Calls the controller in order to delete the node and destroys the widget
        """
        self.controller.delete_node(self.node)
        self.destroy()
