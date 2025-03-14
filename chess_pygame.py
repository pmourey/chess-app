import os

import chess
import chess.engine
import pygame

from common import get_engine

SQUARE_SIZE = 80  # Made smaller for better display
BOARD_SIZE = 8
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE


def draw_board(screen):
	"""Draw the chess board squares"""
	for row in range(BOARD_SIZE):
		for col in range(BOARD_SIZE):
			color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
			pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board, images):
	"""Draw the chess pieces on the board"""
	for square in chess.SQUARES:
		piece = board.piece_at(square)
		if piece:
			# Convert chess.Square to row, col
			row = 7 - chess.square_rank(square)  # Flip row because chess board is displayed bottom-up
			col = chess.square_file(square)

			piece_symbol = piece.symbol()
			if piece_symbol in images:
				screen.blit(images[piece_symbol], (col * SQUARE_SIZE, row * SQUARE_SIZE))


def get_square_from_mouse(pos):
	"""Convert mouse position to chess square"""
	x, y = pos
	col = x // SQUARE_SIZE
	row = y // SQUARE_SIZE
	row = 7 - row  # Flip row because chess board is displayed bottom-up
	return chess.square(col, row)


def find_best_move(board, engine_path="stockfish"):
	engine_path = get_engine(engine_path)
	engine = chess.engine.SimpleEngine.popen_uci(engine_path)
	result = engine.play(board, chess.engine.Limit(time=0.1))
	return result.move


# Define the piece images
def load_piece_images():
	white_pieces = ["P", "R", "N", "B", "Q", "K"]
	black_pieces = ["p", "r", "n", "b", "q", "k"]
	pieces = {'b': black_pieces, 'w': white_pieces}
	images = {}
	for color in ["w", "b"]:
		for piece in pieces[color]:
			img = pygame.image.load(f"images/chess-{color}{piece}.png")
			img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
			images[piece] = img
	return images


def show_popup_message(screen, message):
    """Display a transparent popup message and wait for user input - 'y' to continue, any other key to exit"""
    original_surface = screen.copy()

    # Create semi-transparent overlay
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # RGBA: last value is alpha (128 = 50% transparent)
    screen.blit(overlay, (0, 0))

    # Create transparent popup box
    popup_width = 400
    popup_height = 150
    popup = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
    # popup.fill((255, 255, 255, 200))  # White with 78% opacity
    popup.fill((255, 255, 255, 128))  # White with 50% opacity
    # popup.fill((255, 255, 255, 64))  # White with 25% opacity


    # Add a border to the popup
    border_color = (100, 100, 100, 255)  # Gray border
    border_width = 2
    pygame.draw.rect(popup, border_color, (0, 0, popup_width, popup_height), border_width)

    # Create main message text
    font = pygame.font.Font(None, 25)
    text = font.render(message, True, (0, 0, 0))  # Solid black text
    text_rect = text.get_rect(center=(popup_width // 2, popup_height // 3))
    popup.blit(text, text_rect)

    # Create instruction text
    instruction = "Press 'Y' to continue, any other key to exit"
    instruction_text = font.render(instruction, True, (100, 100, 100))  # Gray text
    instruction_rect = instruction_text.get_rect(center=(popup_width // 2, 2 * popup_height // 3))
    popup.blit(instruction_text, instruction_rect)

    # Position popup in center of screen
    popup_x = (screen.get_width() - popup_width) // 2
    popup_y = (screen.get_height() - popup_height) // 2
    screen.blit(popup, (popup_x, popup_y))

    # Update display
    pygame.display.flip()

    # Wait for key press
    waiting_for_key = True
    continue_game = False

    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    continue_game = True
                waiting_for_key = False
            elif event.type == pygame.QUIT:
                waiting_for_key = False

    # Restore original screen
    screen.blit(original_surface, (0, 0))
    pygame.display.flip()

    return continue_game


def handle_player_move(board, selected_square, clicked_square, engine_path):
	"""Handle player's move and AI's response"""
	move = chess.Move(selected_square, clicked_square)
	if move in board.legal_moves:
		board.push(move)

		# AI's turn (Black)
		if not board.is_game_over():
			ai_move = find_best_move(board, engine_path)
			if ai_move:
				board.push(ai_move)
		return True
	return False


def handle_click(board, pos, selected_square):
	"""Handle mouse click events"""
	clicked_square = get_square_from_mouse(pos)

	if selected_square is None:
		# First click - select piece
		piece = board.piece_at(clicked_square)
		if piece and piece.color == chess.WHITE:
			return clicked_square
	return None


def draw_game_state(screen, board, images, selected_square):
	"""Draw the current state of the game"""
	draw_board(screen)
	draw_pieces(screen, board, images)

	if selected_square is not None:
		row = 7 - chess.square_rank(selected_square)
		col = chess.square_file(selected_square)
		pygame.draw.rect(screen, (255, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

	pygame.display.flip()


def main():
	pygame.init()
	screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
	pygame.display.set_caption("Chess Game")
	clock = pygame.time.Clock()

	board = chess.Board()
	images = load_piece_images()
	# engine_path = "engines/stockfish/stockfish"
	engine_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engines', 'stockfish')
	selected_square = None

	running = True
	while running:
		# Event handling
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				break

			if event.type == pygame.MOUSEBUTTONDOWN and board.turn == chess.WHITE:
				clicked_square = get_square_from_mouse(event.pos)

				if selected_square is None:
					# First click - select piece
					selected_square = handle_click(board, event.pos, selected_square)
				else:
					# Second click - try to make move
					if handle_player_move(board, selected_square, clicked_square, engine_path):
						selected_square = None
					else:
						# Invalid move, check if clicking another valid piece
						new_selection = handle_click(board, event.pos, None)
						selected_square = new_selection if new_selection else None

		# Draw current game state
		draw_game_state(screen, board, images, selected_square)

		# Check for game over
		if board.is_game_over():
			message = ""
			if board.is_checkmate():
				winner = "Black" if board.turn == chess.WHITE else "White"
				message = f"{winner} wins by checkmate!"
			elif board.is_stalemate():
				message = "Draw by stalemate!"

			continue_game = show_popup_message(screen, message)
			if not continue_game:
				running = False
			else:
				# Reset the game
				board = chess.Board()
				selected_square = None

		clock.tick(60)

	pygame.quit()


if __name__ == "__main__":
	main()
