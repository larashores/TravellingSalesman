import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename


class Menu(tk.Menu):
    """
    Menu for the travelling salesman solver.
    """

    def __init__(self, controller):
        """
        Initializes the menu widget and adds all commands
        """
        tk.Menu.__init__(self)
        self.controller = controller

        file = tk.Menu(self, tearoff=0)
        file.add_command(label='New', command=self.new)
        file.add_command(label='Save', command=self.save)
        file.add_command(label='Load', command=self.load)
        self.add_cascade(label='File', menu=file)

        self.controller = controller

        file.entryconfig(1, state=tk.DISABLED)
        controller.model.register(lambda key: file.entryconfig(1, state=tk.NORMAL) if key == 'background' else None)

    def save(self):
        """
        Prompts the user for a filename and saves the configuration
        """
        name = asksaveasfilename(parent=self,
                                 title='Save Configuration',
                                 defaultextension='.tscfg',
                                 filetypes=(('Configuration', '.tscfg'), ))
        if name:
            print(name)
            self.controller.save(name)

    def load(self):
        """
        Prompts the user for a filename and loads the configuration
        """
        name = askopenfilename(parent=self,
                               title='Open Configuration',
                               filetypes=(('Configuration', '.tscfg'), ('all files', '*')))
        if name:
            self.controller.load(name)

    def new(self):
        """
        Prompts the user for a filename for an image and creates a new configuration
        """
        name = askopenfilename(parent=self,
                               title='Open Map Background',
                               filetypes=(('all files', '*'), ('PNG', '.png'), ('JPG', '.jpg')))
        if name:
            self.controller.new(name)
