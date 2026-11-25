import argparse
import dataclasses
import sys
import termios
import tty

from arms import Arm

JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]
FULL_TURN_JOINTS = ["wrist_roll"]
KEYS = {key: (joint, sign) for keys, sign in (("qwert", 1), ("asdfg", -1)) for key, joint in zip(keys, JOINTS)}
STEP = 0.5
VELOCITY = 500
ACCELERATION = 10
ENCODER_STEPS = 4096
MAX_HOMING_OFFSET = 2047

def read_key():
	fd = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	try:
		tty.setcbreak(fd)
		return sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old)

def recentered(joint, calibration, goal):
	if joint in FULL_TURN_JOINTS:
		offset = calibration.homing_offset + goal - (calibration.range_min + calibration.range_max) // 2
		offset = (offset + ENCODER_STEPS // 2) % ENCODER_STEPS - ENCODER_STEPS // 2
		return dataclasses.replace(calibration, homing_offset=max(-MAX_HOMING_OFFSET, offset))

	if not calibration.range_min < goal < calibration.range_max:
		raise ValueError(f"{joint} is at {goal}, outside its range {calibration.range_min}-{calibration.range_max}")

	if goal > (calibration.range_min + calibration.range_max) / 2:
		return dataclasses.replace(calibration, range_min=2 * goal - calibration.range_max)

	return dataclasses.replace(calibration, range_max=2 * goal - calibration.range_min)

def save(robot):
	goals = robot.bus.sync_read("Goal_Position", JOINTS, normalize=False)
	calibration = {**robot.calibration, **{joint: recentered(joint, robot.calibration[joint], goal) for joint, goal in goals.items()}}

	with robot.bus.torque_disabled():
		robot.bus.write_calibration(calibration)
		robot.bus.sync_write("Goal_Position", dict.fromkeys(JOINTS, 0.0))

	robot.calibration = calibration
	robot._save_calibration()

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--port")
	args = parser.parse_args()

	robot = Arm.pick(args.port).follower()
	robot.connect()
	robot.bus.sync_write("Goal_Velocity", dict.fromkeys(JOINTS, VELOCITY))
	robot.bus.sync_write("Acceleration", dict.fromkeys(JOINTS, ACCELERATION))

	print("Q/W/E/R/T raise and A/S/D/F/G lower joints 1-5 by 0.5 degrees")
	print("Enter saves the current pose as zero, Esc quits and releases the arm, so support it")
	offsets = dict.fromkeys(JOINTS, 0.0)

	try:
		while True:
			robot.send_action({f"{joint}.pos": offset for joint, offset in offsets.items()})
			print("\r" + "  ".join(f"{joint} {offset:+.1f}" for joint, offset in offsets.items()), end="", flush=True)

			key = read_key().lower()
			if key in KEYS:
				joint, sign = KEYS[key]
				offsets[joint] += sign * STEP
			elif key == "\n":
				try:
					save(robot)
					offsets = dict.fromkeys(JOINTS, 0.0)
					print(f"\nSaved to {robot.calibration_fpath}")
				except ValueError as e:
					print(f"\nNot saved: {e}")
			elif key == "\x1b":
				break
	except KeyboardInterrupt:
		pass
	finally:
		print()
		robot.disconnect()

if __name__ == "__main__":
	main()
