import tkinter as tk

from src.controller import Controller
from src.gui.mainGui import Editor
from src.gui.menu import Menu


def main():
    """
    Runs the main editor for solving the travelling salesman problem
    """
    import matplotlib.pyplot as plt
    plt.style.use('ggplot')

    root = tk.Tk()
    controller = Controller()
    menu = Menu(controller)
    editor = Editor(root, controller)
    editor.pack(expand=tk.YES, fill=tk.BOTH)
    root.config(menu=menu)
    root.title('Traveling Salesman Solver')
    root.mainloop()


if __name__ == '__main__':
    main()
