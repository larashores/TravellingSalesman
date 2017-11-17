from tkinter import ttk
import tkinter as tk

from src.controller import RunStatus
from src.gui.algorithmParameters import Linear, Ratio
from src.gui.canvasMap import CanvasMap
from src.runtime_models.simulatedAnnealingModel import SuccessorChooseType


class Editor(ttk.Frame):
    """
    Main editor for the travelling salesman problems. Sets up the canvas and the column to run the simulation
    """
    def __init__(self, parent, controller, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.controller = controller
        simulation = SimulationFrame(self, controller)
        simulation.pack(side=tk.RIGHT, expand=tk.YES, padx=(5, 5))
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH, pady=(10, 10))
        self.canvas = CanvasMap(self, controller)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)


class SimulationFrame(ttk.Frame):
    """
    Frame used to edit the information of the simulation. Provides a box that selects the algorithm to use and then
    displays a widget used to edit information for the algorithm
    """
    COOLING_MAP = {'Linear': Linear, 'Constant Ratio': Ratio}
    SUCCESSOR_MAP = {'Two Random Cities': SuccessorChooseType.BOTH_RANDOM,
                     'One Random Pair': SuccessorChooseType.RANDOM_NEIGHBORS}

    def __init__(self, parent, controller, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.controller = controller
        self.controller.get_successor_type = lambda: self.SUCCESSOR_MAP[self.successors_combo.get()]
        self.controller.model.register(lambda key: self.run.state(['!disabled']) if key == 'background' else None)
        self.controller.register(self.on_run)
        self.steps_var = tk.IntVar(self)
        self.steps_var.set(1000)
        self.generate_graphs_var = tk.BooleanVar(self)

        cooling_schedules = sorted(self.COOLING_MAP.keys())
        successor_algorithms = sorted(self.SUCCESSOR_MAP.keys())

        successor_label = ttk.Label(self, text='Choose Successors')
        self.successors_combo = ttk.Combobox(self, justify=tk.CENTER)

        algorithm_label = ttk.Label(self, text='Cooling Schedule')
        self.algorithm_combo = ttk.Combobox(self, justify=tk.CENTER)
        self.algorithm_widget = self.COOLING_MAP[cooling_schedules[0]](self, self.controller)
        self.run = ttk.Button(self, text='Run', command=self.run)
        generate_graphs = ttk.Checkbutton(self, text='Generate Graphs', variable=self.generate_graphs_var)

        successor_label.pack()
        self.successors_combo.pack()

        algorithm_label.pack()
        self.algorithm_combo.pack()
        self.algorithm_widget.pack(expand=tk.YES, fill=tk.BOTH)
        self.run.pack(side=tk.BOTTOM)
        generate_graphs.pack(side=tk.BOTTOM, pady=(20, 5))

        self.nodes = {}
        self.algorithm_combo['values'] = cooling_schedules
        self.algorithm_combo.set(cooling_schedules[0])
        self.algorithm_combo.bind("<<ComboboxSelected>>", self.on_algorithm_changed)
        self.algorithm_combo.state(['readonly'])

        self.successors_combo['values'] = successor_algorithms
        self.successors_combo.set(successor_algorithms[0])
        self.successors_combo.state(['readonly'])

        self.run.state(['disabled'])

    def on_algorithm_changed(self, event):
        """
        When the algorithm changes updates the widget used to edit the algorithm parameters
        """
        self.algorithm_widget.destroy()
        self.algorithm_widget = self.COOLING_MAP[self.algorithm_combo.get()](self, self.controller)
        self.algorithm_widget.pack(expand=tk.YES, fill=tk.BOTH)

    def run(self):
        """
        Gets the list of temperatures from the algorithm widget and runs the simulation
        """
        self.controller.run(self.algorithm_widget.get_temperatures(),
                            notify_canvas=True,
                            generate_graphs=self.generate_graphs_var.get(),
                            graph_scale=self.algorithm_widget.graph_scale())

    def on_run(self, status):
        """
        Disables/Enables the run button while the simulation is running/stopped
        """
        self.run.state(['disabled' if status == RunStatus.START else '!disabled'])
