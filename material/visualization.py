"""Shared SO-101 chain loading and persistent Matplotlib artists."""

from pathlib import Path

import numpy as np
from ikpy.chain import Chain


URDF_PATH = Path(__file__).with_name("so101_new_calib.urdf")


def load_chain():
    return Chain.from_urdf_file(str(URDF_PATH), tip="gripper")


def set_line_points(line, points):
    """Move an existing 3D line without rebuilding the axes."""
    line.set_data(points[:, 0], points[:, 1])
    line.set_3d_properties(points[:, 2])


def style_axes(ax, title, xlim, ylim, zlim):
    ax.set_title(title, color="#25344a", pad=16)
    ax.set(xlabel="X (m)", ylabel="Y (m)", zlabel="Z (m)")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_zlim(*zlim)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=25, azim=-62)
    ax.tick_params(labelsize=8, colors="#52647b")
    ax.grid(True, color="#d8e1ec", alpha=0.45)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor("#edf3f9")
        axis.pane.set_alpha(0.16)


class RobotArtists:
    """Create the robot once and update its coordinates for each new pose."""

    def __init__(self, ax):
        self.arm, = ax.plot([], [], [], color="#2777a8", lw=6, marker="o",
                            markersize=7, markerfacecolor="#ffffff",
                            markeredgecolor="#2777a8", markeredgewidth=2,
                            solid_capstyle="round", label="arm")
        self.jaw, = ax.plot([], [], [], color="#e06a43", lw=5, marker="o",
                            markersize=7, markerfacecolor="#e06a43",
                            solid_capstyle="round", label="gripper")
        self.shadow, = ax.plot([], [], [], color="#60758b", lw=1.5,
                               ls="--", alpha=0.3)
        self.tool_axes = [
            ax.plot([], [], [], color=color, lw=2.5, alpha=0.85)[0]
            for color in ("#e15b64", "#39a774", "#5a78db")
        ]
        ax.legend(loc="upper left", framealpha=0.85, fontsize=9)
        self.floor_z = ax.get_zlim()[0] + 0.005

    def update(self, chain, angles):
        frames = chain.forward_kinematics(angles, full_kinematics=True)
        points = np.array([frame[:3, 3] for frame in frames])
        set_line_points(self.arm, points[:-1])
        set_line_points(self.jaw, points[-2:])
        floor_points = points.copy()
        floor_points[:, 2] = self.floor_z
        set_line_points(self.shadow, floor_points)

        tip = points[-1]
        for i, line in enumerate(self.tool_axes):
            direction = frames[-1][:3, i] * 0.035
            set_line_points(line, np.vstack((tip, tip + direction)))
        return tip
