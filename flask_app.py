from flask import Flask, render_template, jsonify, request
import chess
import chess.engine
import os
import requests

app = Flask(__name__)

# Global chess board instance
board = chess.Board()

# Get the absolute path to the engines directory
ENGINES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engines', 'stockfish')
# Add these constants at the top of your file
LICHESS_API_URL = "https://lichess.org/api"
# Get API token from environment variable for security
LICHESS_API_TOKEN = os.getenv('LICHESS_API_TOKEN')


# Initialize Stockfish engine
def get_engine():
	if os.name == 'nt':  # Windows
		engine_path = os.path.join(ENGINES_DIR, "stockfish-windows-x86-64.exe")
	else:  # Linux/Mac
		engine_path = os.path.join(ENGINES_DIR, "stockfish")
		app.logger.info(f"Engine path: {engine_path}")

	# Verify engine exists
	if not os.path.exists(engine_path):
		raise FileNotFoundError(f"Stockfish engine not found at {engine_path}")

	# Make sure the engine is executable (Linux/Mac)
	if os.name != 'nt':
		os.chmod(engine_path, 0o755)

	return chess.engine.SimpleEngine.popen_uci(engine_path)


@app.route('/')
def index():
	return render_template('index.html')


def get_computer_move_local(board, depth=3):
	try:
		with get_engine() as engine:
			result = engine.play(board, chess.engine.Limit(depth=depth))
			app.logger.info(f"Engine move: {result.move}")
			return result.move
	except Exception as e:
		app.logger.info(f"Engine error: {e}")
		return None


def get_computer_move(board, depth=20):
	"""Get best move using Lichess API"""
	try:
		headers = {"Authorization": f"Bearer {LICHESS_API_TOKEN}", "Content-Type": "application/json"}

		params = {"fen": board.fen(), "depth": depth, "multiPv": 1}

		response = requests.get(f"{LICHESS_API_URL}/cloud-eval", headers=headers, params=params)

		if response.status_code == 200:
			data = response.json()
			if "pvs" in data and len(data["pvs"]) > 0:
				best_move = data["pvs"][0]["moves"].split()[0]
				return chess.Move.from_uci(best_move)
		return None

	except Exception as e:
		app.logger.error(f"API error: {e}")
		return None


def get_computer_move_with_fallback(board):
	# Try Lichess API first
	move = get_computer_move(board)
	if move:
		return move

	# Fallback to another service or local engine if needed
	# Implement alternative move generation here
	return None


@app.route('/make_move', methods=['POST'])
def make_move():
	data = request.get_json()
	from_square = data['from']
	to_square = data['to']

	# Make player's move if it's legal
	player_move = chess.Move.from_uci(from_square + to_square)
	if player_move in board.legal_moves:
		board.push(player_move)

		# Check if game is over after player's move
		if board.is_game_over():
			return jsonify({'fen': board.fen(), 'legal': True, 'game_over': True, 'computer_move': None})

		# Make computer's move
		# computer_move = find_best_move(board)
		computer_move = get_computer_move(board)
		if computer_move:
			board.push(computer_move)
			return jsonify({'fen': board.fen(), 'legal': True, 'game_over': board.is_game_over(), 'computer_move': computer_move.uci()})

	return jsonify({'legal': False})


if __name__ == '__main__':
	app.run(debug=True)
