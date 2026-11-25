import warnings
warnings.filterwarnings("ignore")

import math, time
import numpy as np
np.set_printoptions(precision=2)
import argparse

import ikpy.chain
from ikpy.inverse_kinematics import inverse_kinematic_optimization
from ikpy.utils import geometry

import numpy as np

from arms import Arm

from utils import *

JOINT_NAMES = [
	'shoulder_pan',
	'shoulder_lift',
	'elbow_flex',
	'wrist_flex',
	'wrist_roll',
	'gripper',
]

def main():
	URDF_PATH = 'so101_new_calib.urdf'
	my_chain = ikpy.chain.Chain.from_urdf_file(URDF_PATH)
	my_chain.active_links_mask[0]=False

	parser = argparse.ArgumentParser()
	parser.add_argument("--port")
	args = parser.parse_args()

	robot = Arm.pick(args.port).follower()
	robot.connect()
	robot.bus.disable_torque()

	# IMPORTANT for setting maximum velocity and acceleration
	v = 500
	a = 10
	for j in JOINT_NAMES:
		robot.bus.write("Goal_Velocity", j, v)
		robot.bus.write("Acceleration", j, a)

	target_offset = [ 0.35, 0, 0.2]

	# points on a vertical line
	points = []
	length = 0.1
	N = 30
	ls = np.linspace(-length, length, N)
	ls = np.hstack((ls,ls[::-1]))

	for x in ls:
		pt = np.array([0,0, x])+target_offset
		points.append(pt)

	while True:
		for pt in points:

			ik = my_chain.inverse_kinematics(pt, optimizer='scalar')
			action = {JOINT_NAMES[i]+'.pos': np.rad2deg(v) for i, v in enumerate(ik[1:])}

			robot.send_action(action)
			# time.sleep(0.1)

if __name__=='__main__':
	main()