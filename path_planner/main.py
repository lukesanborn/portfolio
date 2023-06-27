from matplotlib import pyplot as plt

from src.trajectory.trajectory import Trajectory
from src.ui import Field
from src.ui.render import Render

from src.utils import Data

data = Data("", "path.npy")

# if not data.exists():
if True:
    field = Field(54, 27)
    fig, ax = field.create_field()
    r1 = Render(field, fig, ax, "green", draw_angles=False, draw_lines=True)
    r2 = Render(field, fig, ax, "orange", draw_angles=False, draw_lines=True)
    plt.show()
    # r.reset_positions("orange", 0,decelerate=True)
    # positions = r.positions[0]["positions"]
    # print("Saving path")
    # data.save_data(positions)
    positions = r.get_points()
else:
    print("Loading saved path")
    positions = data.load_data()

# t = Trajectory(positions, speed=-5.0)
# t.export(plot=True)
