from tkinter import ttk
import tkinter as tk
import numpy as np
from src.integercheck import int_validate
from src.algorithms.temperatureAlgorithms import linear_temperature, decrease_ratio
from src.graphing.graphing import draw
from src.graphing.subplot import SubPlot
from src.graphing.graph import Graph


class Linear(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.steps_var = tk.IntVar()
        self.steps_var.set(1000)
        self.ratio_var = tk.DoubleVar()
        steps_label = ttk.Label(self, text='Number of Steps')
        steps_entry = ttk.Entry(self, textvariable=self.steps_var, justify=tk.CENTER)
        int_validate(steps_entry, (0, 100000))
        self.ratio_label = ttk.Label(self)
        ratio_scale = ttk.Scale(self, orient=tk.HORIZONTAL , from_=1, to=10,
                                variable=self.ratio_var, command=self.on_ratio_change)

        steps_label.pack()
        steps_entry.pack(expand=tk.YES, fill=tk.X)
        self.ratio_label.pack()
        ratio_scale.pack(expand=tk.YES, fill=tk.X)

        self.ratio_var.set(5)
        self.on_ratio_change(None)

    def on_ratio_change(self, event):
        self.ratio_label.config(text='Initial Start Ratio: {:.2f}'.format(self.ratio_var.get()))

    def get_temperatures(self):
        return linear_temperature(self.controller.max_dist_func(), self.steps_var.get())

    @staticmethod
    def graph_scale():
        return None


class Ratio(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.model.register(lambda key: self.test_button.state(['!disabled'])
                                       if key == 'background' else None)
        self.steps_var = tk.IntVar()
        self.steps_var.set(1000)
        self.ratio_var = tk.DoubleVar()
        steps_label = ttk.Label(self, text='Number of Steps')
        steps_entry = ttk.Entry(self, textvariable=self.steps_var, justify=tk.CENTER)
        int_validate(steps_entry, (0, 100000))
        self.ratio_label = ttk.Label(self)
        ratio_scale = ttk.Scale(self, orient=tk.HORIZONTAL, from_=0, to=1,
                                variable=self.ratio_var, command=self.on_ratio_change)
        self.test_button = ttk.Button(self, text='Test Ratio', command=self.on_test)

        steps_label.pack()
        steps_entry.pack(expand=tk.YES, fill=tk.X)
        self.ratio_label.pack()
        ratio_scale.pack(expand=tk.YES, fill=tk.X)
        self.test_button.pack()

        self.ratio_var.set(.9)
        self.on_ratio_change(None)
        self.test_button.state(['disabled'])

    def on_ratio_change(self, event):
        self.ratio_label.config(text='Ratio: {:.2f}'.format(self.ratio_var.get()))

    def get_temperatures(self):
        return decrease_ratio(self.controller.max_dist_func(), self.ratio_var.get(), self.steps_var.get())

    def on_test(self):
        steps = self.steps_var.get()
        max_ = self.controller.max_dist_func()
        graphs = []
        ratios = list(np.arange(0, 1, .2))
        ratios.extend((0.9, .95))
        for ratio in ratios:
            temps = decrease_ratio(max_, ratio, steps)
            list_of_values = []
            for _ in range(25):
                final_value, values = self.controller.run(temps, track_lengths=True, notify_canvas=False)
                list_of_values.append(values)
            average_values = list(map(lambda val: sum(val)/len(val), zip(*list_of_values)))
            graphs.append(Graph(list(range(len(temps))), average_values, plot_type='-',
                                legend_label='Ratio={:.2f}'.format(ratio)))

        plots = [[SubPlot(*graphs, x_label='Step', y_label='Total Path Length')]]

        draw(plots, title='Average Path Length for Various Ratios Over 25 Runs')

    @staticmethod
    def graph_scale():
        return 'y'
