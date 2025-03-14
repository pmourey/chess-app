import platform
import os

# Initialize Stockfish engine
def get_engine(engine_path: str) -> str:
	if os.name == 'nt':  # Windows
		engine_path = os.path.join(engine_path, "stockfish-windows-x86-64.exe")
	else:  # Linux/Mac
		system = platform.system()

		if system == "Darwin":  # macOS
			engine_path = os.path.join(engine_path, "stockfish")
		elif system == "Linux":
			engine_path = os.path.join(engine_path, "stockfish-ubuntu-x86-64-avx2")
		else:
			raise OSError(f"Unsupported operating system: {system}")

	# Verify engine exists
	if not os.path.exists(engine_path):
		raise FileNotFoundError(f"Stockfish engine not found at {engine_path}")

	# Make sure the engine is executable (Linux/Mac)
	if os.name != 'nt':
		os.chmod(engine_path, 0o755)

	return engine_path