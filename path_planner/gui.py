import ctypes
import os
from random import random
from glob import glob

import PySimpleGUI as sg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from src.trajectory import calc_trajectory
from src.ui import Render, paths_to_json, paths_from_json

ctypes.windll.shcore.SetProcessDpiAwareness(1)


def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    try:
        if canvas.children:
            for child in canvas.winfo_children():
                child.destroy()
        if canvas_toolbar.children:
            for child in canvas_toolbar.winfo_children():
                child.destroy()
    except AttributeError:
        pass
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='x', expand=.5)


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


def path_data(data: np.array, speed: float, decelerate: bool):
    return {"positions": data, "speed": speed, "decelerate": decelerate}


DEFAULT_SPEED = -7.0
path_names = glob("paths/*/", )

layout = [
    # [sg.T('Trajectory Planner')],
    [sg.Text("Create a new trajectory"), sg.Text("Trajectory name"),
     sg.InputText(key="-TRAJ-NAME-", default_text="default"),
     sg.B("Start"), ],
    [sg.Text("Load and modify trajectory"), sg.Text("Trajectory name"), sg.Combo(path_names, key="-LOAD-TRAJ-NAME-"),
     sg.B("Load")],
    [sg.Column(layout=[[sg.Text("Speed adjustment")],
                       [sg.Slider(range=(-10, 10), default_value=DEFAULT_SPEED, tick_interval=2, resolution=1,
                                  enable_events=True,
                                  key="-SPEED-", tooltip="Forward is negative", orientation="h")],
                       [sg.Text("Path:"),
                        sg.Combo(path_names, key="-PATH_NAMES-", disabled=True, enable_events=True)]]),
     sg.Column(layout=[[sg.Checkbox('Decelerate', default=True, key="-DECEL-")],
                       [sg.Checkbox('Inplace', default=False, key="-INPLACE-")], [sg.B('New path'), ],
                       ])],
    [sg.T('Controls:')],
    [sg.Canvas(key='controls_cv'), sg.Canvas(key='-OUT-CANVAS-')],
    [sg.T('Path:')],
    [sg.Column(
        layout=[
            [sg.Canvas(key='fig_cv',
                       size=(300 * 2, 300)
                       )]
        ],
        background_color='#DAE0E6',
        pad=(0, 0)
    )],
    [sg.B("Generate path file")]

]
sg.theme('Dark Gray 13')
window = sg.Window('Trajectory230 ', layout, icon="images/favicon.ico", resizable=True, auto_size_buttons=True,
                   auto_size_text=True)
positions = []

plt.style.use('dark_background')
r = Render()
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == "Load":
        dir_name = values["-LOAD-TRAJ-NAME-"]
        paths = list(paths_from_json(dir_name))
        for path in paths:
            x, y = zip(*path.data)
            raw = np.column_stack([x, y])
            path.data = r.field.scale_down(raw).tolist()
        r = Render(paths, [(random(), random(), random()) for i in range(len(paths))])
        r.selected_path = 0
        speed, decelerate, inplace = r.get_path()
        window["-SPEED-"].update(value=speed)
        window["-DECEL-"].update(value=decelerate)
        window["-INPLACE-"].update(value=inplace)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, r.fig, window['controls_cv'].TKCanvas)
    elif event == "Generate path file":
        if values["-LOAD-TRAJ-NAME-"]:
            path_name = os.path.basename(os.path.normpath(values["-LOAD-TRAJ-NAME-"]))
        else:
            path_name = values["-TRAJ-NAME-"]
        dir_name = f'paths/{values["-TRAJ-NAME-"]}/'
        os.makedirs(dir_name, exist_ok=True)
        speed = float(values["-SPEED-"])
        r.update_path(speed, values["-DECEL-"], values["-INPLACE-"])
        r.convert_points()
        paths_to_json(r.paths, dir_name)
        filelist = [f for f in os.listdir(dir_name) if not f.endswith(".json")]
        for f in filelist:
            os.remove(os.path.join(dir_name, f))
        calc_trajectory(r.paths, path_name, plot=False)
        r.fig.savefig(f"{dir_name}/raw_map.png", dpi=300)
        break
    elif event == "Start":
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, r.fig, window['controls_cv'].TKCanvas)

    elif event == 'New path':
        color = (random(), random(), random())
        speed = float(values["-SPEED-"])
        r.reset_positions(color, speed, values["-DECEL-"], values["-INPLACE-"])
    elif event == "-PATH_NAMES-":
        speed = float(values["-SPEED-"])
        r.update_path(speed, values["-DECEL-"], values["-INPLACE-"])

        r.selected_path = values["-PATH_NAMES-"].id
        speed, decelerate, inplace = r.get_path()
        window["-SPEED-"].update(value=speed)
        window["-DECEL-"].update(value=decelerate)
        window["-INPLACE-"].update(value=inplace)
    if len(r.paths) > 0:
        path = r.get_selected_path()
        window["-PATH_NAMES-"].update(value=path, values=r.paths, disabled=False)

window.close()
