import re
import chess

class SANParser:
    def __init__(self):
        self.move_pattern = self._compile_patterns()
        self.turns = []  # List of tuples (white_move, black_move)
        self.board = chess.Board()

    def _compile_patterns(self):
        letra = r"[a-h]"
        numero = r"[1-8]"
        casilla = f"{letra}{numero}"
        pieza = r"[KQRBN]"
        promocion = f"={pieza}"
        jaque_mate = r"[+#]"
        captura = r"x"
        desambiguacion = f"(?:{letra}|{numero}|{letra}{numero})"

        enroque = r"O-O-O|O-O"
        movimiento_pieza = (
            f"{pieza}"
            f"(?:{desambiguacion})?"
            f"(?:{captura})?"
            f"{casilla}"
            f"(?:{promocion})?"
            f"(?:{jaque_mate})?"
        )
        peon_avance = (
            f"{casilla}"
            f"(?:{promocion})?"
            f"(?:{jaque_mate})?"
        )
        peon_captura = (
            f"{letra}x{casilla}"
            f"(?:{promocion})?"
            f"(?:{jaque_mate})?"
        )
        movimiento_peon = f"(?:{peon_captura}|{peon_avance})"

        jugada = f"^(?:{enroque}|{movimiento_pieza}|{movimiento_peon})$"
        return re.compile(jugada)

    def validate_move(self, move: str) -> bool:
        return bool(self.move_pattern.match(move))

    def add_turn(self, white: str, black: str = None):
        self.turns.append((white, black))

    def play_move(self, san_move: str) -> bool:
        try:
            move = self.board.parse_san(san_move)
            self.board.push(move)
            return True
        except Exception:
            return False

    def print_board_with_labels(self):
        rows = str(self.board).split('\n')
        print("    a b c d e f g h")
        print("  +-----------------+")
        for i, row in enumerate(rows):
            rank = 8 - i
            print(f"{rank} | {' '.join(row.split())} |")
        print("  +-----------------+")

    def generate_tree(self):
        def _build_tree(depth, prefix, is_last):
            if depth >= len(self.turns):
                return

            white, black = self.turns[depth]

            # Rama blanca
            connector = '└── ' if is_last else '├── '
            print(f"{prefix}{connector}{white}")

            # Rama negra
            if black:
                new_prefix = prefix + ('    ' if is_last else '│   ')
                print(f"{new_prefix}└── {black}")
                # Llamada recursiva para siguiente turno
                _build_tree(depth + 1, new_prefix + '    ', False)
            else:
                _build_tree(depth + 1, prefix + '│   ', False)

            # Nueva variación si existe
            if depth == 0 and len(self.turns) > 1:
                _build_tree(1, prefix.replace('├──', '│   ').replace('└──', '    '), True)

        print("Partida")
        if self.turns:
            _build_tree(0, "", len(self.turns) == 1)

    def display_moves(self):
        lines = []
        for idx, (w, b) in enumerate(self.turns, start=1):
            if b:
                lines.append(f"{idx}. {w} {b}")
            else:
                lines.append(f"{idx}. {w}")
        print(" ".join(lines))

    def display_result(self):
        board_copy = chess.Board()
        flat = []
        for w, b in self.turns:
            if w:
                mv = board_copy.parse_san(w)
                piece = board_copy.piece_at(mv.from_square).symbol().upper()
                frm = chess.square_name(mv.from_square)
                to = chess.square_name(mv.to_square)
                flat.append(f"{piece}{frm} {to}")
                board_copy.push(mv)
            if b:
                mv = board_copy.parse_san(b)
                piece = board_copy.piece_at(mv.from_square).symbol().upper()
                frm = chess.square_name(mv.from_square)
                to = chess.square_name(mv.to_square)
                flat.append(f"{piece}{frm} {to}")
                board_copy.push(mv)
        parts = [f"{i+1}. {m}" for i, m in enumerate(flat)]
        print("  ".join(parts))

    def display_progress(self):
        print()
        self.display_moves()
        print("\nEstado actual del tablero:")
        self.print_board_with_labels()


def main():
    parser = SANParser()
    print("Validación interactiva de una partida en SAN hasta jaque mate")
    print("\nTablero inicial:")
    parser.print_board_with_labels()

    turn = 1
    while True:
        cmd = input(f"Turno {turn} - Jugada de las Blancas: ").strip()
        if cmd.lower() == 'arbol':
            parser.generate_tree()
            continue
        if cmd.upper() == "RESULTADO":
            parser.display_result()
            continue
        if parser.validate_move(cmd) and parser.play_move(cmd):
            parser.add_turn(cmd)
            parser.display_progress()
        else:
            print(f"Jugada inválida para Blancas en el turno {turn}: '{cmd}'. Intenta de nuevo.")
            continue
        if '#' in cmd or parser.board.is_checkmate():
            print(f"\n¡Jaque mate detectado en movimiento de las Blancas ('{cmd}')! Partida finalizada.")
            break

        # Movimiento de las negras
        while True:
            resp = input(f"Turno {turn} - Jugada de las Negras: ").strip()
            if resp.lower() == 'arbol':
                parser.generate_tree()
                continue
            if resp.upper() == "RESULTADO":
                parser.display_result()
                continue
            if not resp:
                parser.turns[-1] = (parser.turns[-1][0], None)
                parser.display_progress()
                black = None
                break
            if parser.validate_move(resp) and parser.play_move(resp):
                parser.turns[-1] = (parser.turns[-1][0], resp)
                parser.display_progress()
                black = resp
                break
            print(f"Jugada inválida para Negras en el turno {turn}: '{resp}'. Intenta de nuevo o presiona enter para omitir.")
        if black and ('#' in black or parser.board.is_checkmate()):
            print(f"\n¡Jaque mate detectado en movimiento de las Negras ('{black}')! Partida finalizada.")
            break
        turn += 1

if __name__ == '__main__':
    main()
