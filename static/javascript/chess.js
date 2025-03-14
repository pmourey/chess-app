// Initialize chess board
const board = document.getElementById('board');
let selectedPiece = null;
let game = new Chess();

function createBoard() {
    board.innerHTML = '';
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.createElement('div');
            square.className = `square ${(row + col) % 2 ? 'black' : 'white'}`;
            square.dataset.square = `${String.fromCharCode(97 + col)}${8 - row}`;

            const piece = game.get(square.dataset.square);
            if (piece) {
                const pieceDiv = document.createElement('div');
                pieceDiv.className = 'piece';
                pieceDiv.innerHTML = getPieceUnicode(piece);
                square.appendChild(pieceDiv);
            }

            square.addEventListener('click', handleSquareClick);
            board.appendChild(square);
        }
    }
}

function getPieceUnicode(piece) {
    const pieces = {
        'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
        'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔'
    };
    // The piece object from chess.js has different properties
    return pieces[piece.color === 'w' ? piece.type.toUpperCase() : piece.type.toLowerCase()];
}

function handleSquareClick(event) {
    const square = event.target.closest('.square');
    if (!selectedPiece) {
        // Only allow selecting squares with pieces of the current player's color
        const piece = game.get(square.dataset.square);
        if (piece && piece.color === 'w') {  // 'w' for white (player's color)
            selectedPiece = square;
            square.classList.add('selected');
        }
    } else {
        const from = selectedPiece.dataset.square;
        const to = square.dataset.square;

        fetch('/make_move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ from, to })
        })
        .then(response => response.json())
        .then(data => {
            if (data.legal) {
                // Make player's move
                game.move({ from, to });

                // If computer made a move, apply it
                if (data.computer_move) {
                    const computerFrom = data.computer_move.slice(0, 2);
                    const computerTo = data.computer_move.slice(2, 4);

                    // Small delay to make the computer's move visible
                    setTimeout(() => {
                        game.move({ from: computerFrom, to: computerTo });
                        createBoard();

                        // Check for game over after computer's move
                        if (data.game_over) {
                            const winner = game.in_checkmate() ?
                                (game.turn() === 'w' ? 'Black' : 'White') : 'Draw';
                            alert(game.in_checkmate() ? `Game Over! ${winner} wins!` : 'Game Over! Draw!');
                        }
                    }, 600);
                }

                // Update board immediately after player's move
                createBoard();

                // Check for game over after player's move
                if (data.game_over && !data.computer_move) {
                    const winner = game.in_checkmate() ?
                        (game.turn() === 'w' ? 'Black' : 'White') : 'Draw';
                    alert(game.in_checkmate() ? `Game Over! ${winner} wins!` : 'Game Over! Draw!');
                }
            }

            // Clear selection
            selectedPiece.classList.remove('selected');
            selectedPiece = null;
        })
        .catch(error => {
            console.error('Error:', error);
            selectedPiece.classList.remove('selected');
            selectedPiece = null;
        });
    }
}

createBoard();