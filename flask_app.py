import platform

from flask import Flask, render_template, jsonify, request
import chess
import chess.engine
import os
import requests

from common import get_engine

app = Flask(__name__)

# Config
app.config.from_object('config.Config')

# Global chess board instance
board = chess.Board()

# Add these constants at the top of your file
LICHESS_API_URL = app.config['LICHESS_API_URL']
# Get API token from environment variable for security
LICHESS_API_TOKEN = app.config['LICHESS_API_TOKEN']


@app.route('/')
def index():
	return render_template('index.html')


def get_computer_move_local(board, depth=5):
	try:
		engine_path = get_engine(app.config['ENGINES_DIR'])
		engine = chess.engine.SimpleEngine.popen_uci(engine_path)
		result = engine.play(board, chess.engine.Limit(depth=depth))
		return result.move
	except Exception as e:
		app.logger.error(f"Engine error: {e}")
		return None


def get_computer_move_api(board, depth=20):
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
	move = get_computer_move_api(board)
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
		app.logger.debug(f"Player move: {player_move}")
		board.push(player_move)

		# Check if game is over after player's move
		if board.is_game_over():
			return jsonify({'fen': board.fen(), 'legal': True, 'game_over': True, 'computer_move': None})

		# Make computer's move
		computer_move = get_computer_move_local(board)
		# computer_move = get_computer_move_api(board)
		if computer_move:
			app.logger.debug(f"Computer move: {computer_move}")
			board.push(computer_move)
			return jsonify({'fen': board.fen(), 'legal': True, 'game_over': board.is_game_over(), 'computer_move': computer_move.uci()})

	return jsonify({'legal': False})


if __name__ == '__main__':
	app.run(debug=True)
