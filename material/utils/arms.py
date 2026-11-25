from dataclasses import dataclass
from pathlib import Path

from serial.tools import list_ports

from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

CALIBRATION_DIR = Path(__file__).parent.parent / "calibrations"

@dataclass
class Arm:
	port: str
	serial: str

	@property
	def calibration_path(self):
		return CALIBRATION_DIR / f"{self.serial}.json"

	@property
	def calibrated(self):
		return self.calibration_path.is_file()

	def follower(self):
		return SO101Follower(SO101FollowerConfig(port=self.port, id=self.serial, calibration_dir=CALIBRATION_DIR, use_degrees=True))

	@staticmethod
	def scan():
		return [Arm(port.device, port.serial_number) for port in sorted(list_ports.comports(), key=lambda port: port.device) if port.serial_number]

	@staticmethod
	def find():
		return [arm for arm in Arm.scan() if arm.calibrated]

	@staticmethod
	def pick(port=None):
		arms = [arm for arm in Arm.find() if port in (None, arm.port)]
		if not arms:
			raise RuntimeError(f"No calibrated arm found{f' on {port}' if port else ''}, calibrations are in {CALIBRATION_DIR}")

		print(f"Using arm {arms[0].serial} on {arms[0].port}")
		return arms[0]
