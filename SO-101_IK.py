"""Animate the SO-101 arm following a figure-eight IK target."""

import matplotlib.pyplot as plt
import numpy as np

from so101_visualization import RobotArtists, load_chain, set_line_points, style_axes
from utils import generate_figure_8, generate_square


def IK_demo():
    chain = load_chain()
    angles = np.zeros(len(chain.links))
    targets = generate_figure_8(N=30).T * 0.2 + np.array([0.2, 0, 0])
    # targets = generate_square()+np.array([0.4,0,0])

    fig = plt.figure(figsize=(10, 8), facecolor="#f7f9fc")
    ax = fig.add_subplot(111, projection="3d")
    fig.subplots_adjust(left=0.04, right=0.96, top=0.94, bottom=0.04)
    # The IK path extends farther sideways than the slider demo's initial pose.
    style_axes(ax, "SO-101  |  IK error: --", (-0.14, 0.48),
               (-0.34, 0.34), (-0.18, 0.44))
    robot = RobotArtists(ax)

    ax.plot(targets[:, 0], targets[:, 1], targets[:, 2],
            color="#8a78b7", lw=1.8, ls="--", alpha=0.55,
            label="target path")
    target_marker, = ax.plot([], [], [], color="#bc4785", marker="x",
                             markersize=11, markeredgewidth=2.5, ls="None",
                             label="target")
    error_line, = ax.plot([], [], [], color="#bc4785", lw=1.5,
                           ls=":", alpha=0.65)
    ax.legend(loc="upper left", framealpha=0.85, fontsize=9)

    stopped = False

    def on_press(event):
        nonlocal stopped
        if event.key == "q":
            stopped = True

    fig.canvas.mpl_connect("key_press_event", on_press)
    plt.show(block=False)
    while not stopped and plt.fignum_exists(fig.number):
        for target in targets:
            if stopped or not plt.fignum_exists(fig.number):
                break
            angles = chain.inverse_kinematics(
                target, initial_position=[False, *angles[1:]], optimizer="scalar"
            )
            tip = robot.update(chain, angles)
            set_line_points(target_marker, target[None, :])
            set_line_points(error_line, np.vstack((tip, target)))
            error_mm = np.linalg.norm(tip - target) * 1000
            ax.set_title(f"SO-101  |  IK error: {error_mm:.1f} mm",
                         color="#25344a", pad=16)
            fig.canvas.draw_idle()
            plt.pause(0.01)


if __name__ == "__main__":
    IK_demo()
