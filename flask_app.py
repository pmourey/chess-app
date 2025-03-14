from flask import Flask, render_template, jsonify, request
import chess
import chess.engine
import os

app = Flask(__name__)

# Global chess board instance
board = chess.Board()

# Get the absolute path to the engines directory
ENGINES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engines', 'stockfish')


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


def find_best_move(board, depth=3):
	try:
		with get_engine() as engine:
			result = engine.play(board, chess.engine.Limit(depth=depth))
			app.logger.info(f"Engine move: {result.move}")
			return result.move
	except Exception as e:
		app.logger.info(f"Engine error: {e}")
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
		computer_move = find_best_move(board)
		if computer_move:
			board.push(computer_move)
			return jsonify({'fen': board.fen(), 'legal': True, 'game_over': board.is_game_over(), 'computer_move': computer_move.uci()})

	return jsonify({'legal': False})


if __name__ == '__main__':
	app.run(debug=True)
