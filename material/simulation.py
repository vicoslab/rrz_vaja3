"""Interactive kinematic view of the SO-101 arm."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

from visualization import RobotArtists, load_chain, style_axes


def sliders():
    chain = load_chain()
    joints = chain.links[1:]
    angles = np.zeros(len(chain.links))

    fig = plt.figure(figsize=(10, 8), facecolor="#f7f9fc")
    ax = fig.add_subplot(111, projection="3d")
    fig.subplots_adjust(left=0.04, right=0.96, top=0.94, bottom=0.36)
    style_axes(ax, "SO-101  |  joint motion", (-0.09, 0.41),
               (-0.25, 0.25), (-0.04, 0.46))
    robot = RobotArtists(ax)

    def update(_=None):
        angles[1:] = np.deg2rad([slider.val for slider in controls])
        robot.update(chain, angles)
        fig.canvas.draw_idle()

    controls = []
    for i, joint in enumerate(joints):
        bottom = 0.045 + (len(joints) - 1 - i) * 0.047
        slider_ax = fig.add_axes((0.21, bottom, 0.64, 0.026), facecolor="#eaf0f7")
        lower, upper = np.rad2deg(joint.bounds)
        control = Slider(slider_ax, joint.name.replace("_", " "), lower, upper,
                         valinit=0, valfmt="%0.0f°", color="#2777a8")
        control.on_changed(update)
        controls.append(control)

    update()
    plt.show()


if __name__ == "__main__":
    sliders()
