import argparse
import time

from arms import Arm

def calibrate(arm):
	print(f"Calibrating arm {arm.serial} on {arm.port}")
	robot = arm.follower()
	robot.connect(calibrate=False)
	robot.calibrate()
	robot.disconnect()

def watch():
	seen = {arm.serial for arm in Arm.scan() if arm.calibrated}
	if seen:
		print(f"Skipping plugged in arms that are already calibrated: {', '.join(sorted(seen))}")

	print("Plug in arms one at a time to calibrate them, Ctrl+C to stop")

	while True:
		arms = Arm.scan()
		for arm in arms:
			if arm.serial in seen:
				continue

			time.sleep(1)
			try:
				calibrate(arm)
			except Exception as e:
				print(f"Calibrating {arm.serial} failed: {e}")

			print("Unplug it and plug in the next arm")

		seen = {arm.serial for arm in arms}
		time.sleep(0.5)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--port")
	args = parser.parse_args()

	if args.port is None:
		watch()
		return

	arm = next((arm for arm in Arm.scan() if arm.port == args.port), None)
	if arm is None:
		raise SystemExit(f"No USB serial device with a serial number on {args.port}")

	calibrate(arm)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print()
