"""High-performance 43-slot sliding tile puzzle state representation and math engine.

Physical 42-tile Digimon puzzle:
- 42 numbered tiles (1..42) in a 6x7 rectangular grid (rows 0..6, cols 0..5).
- 1 dedicated parking pocket on the LEFT side of Row 6 (position (7, 0) in memory, adjacent to (6, 0) via LEFT/RIGHT).
- In the solved goal state:
  - Positions (0, 0) to (6, 5) hold tiles 1 to 42.
  - Pocket position (7, 0) on the left holds 0 (empty space).
"""

from __future__ import annotations

from enum import IntEnum
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union
import numpy as np


class Action(IntEnum):
    """Actions representing the directional movement of the blank space (tile 0)."""
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    @property
    def opposite(self) -> Action:
        """Returns the inverse action."""
        if self == Action.UP:
            return Action.DOWN
        if self == Action.DOWN:
            return Action.UP
        if self == Action.LEFT:
            return Action.RIGHT
        return Action.LEFT


ACTION_DELTAS: Dict[Action, Tuple[int, int]] = {
    Action.UP: (-1, 0),
    Action.DOWN: (1, 0),
    Action.LEFT: (0, -1),
    Action.RIGHT: (0, 1),
}


class PuzzleState:
    """Immutable 43-slot (or NxM) sliding tile puzzle state representation."""

    __slots__ = ("_board", "_rows", "_cols", "_has_pocket", "_blank_pos", "_hash")

    POCKET_POS: Tuple[int, int] = (7, 0)       # Pocket slot (left of Row 6)
    POCKET_ENTRY_POS: Tuple[int, int] = (6, 0) # Slot (6, 0) in main grid

    def __init__(
        self,
        board: Union[np.ndarray, Sequence[Sequence[int]], Sequence[int]],
        rows: int = 7,
        cols: int = 6,
        has_pocket: bool = True,
    ) -> None:
        arr = np.asarray(board, dtype=np.int32)

        if has_pocket and rows == 7 and cols == 6:
            if arr.ndim == 1 and len(arr) == 43:
                grid_part = arr[:42].reshape((7, 6))
                pocket_row = np.full((1, 6), -1, dtype=np.int32)
                pocket_row[0, 0] = arr[42]
                arr = np.vstack([grid_part, pocket_row])
            elif arr.ndim == 2 and arr.shape == (7, 6):
                pocket_row = np.full((1, 6), -1, dtype=np.int32)
                pocket_row[0, 0] = 0
                arr = np.vstack([arr, pocket_row])
            elif arr.ndim != 2 or arr.shape != (8, 6):
                raise ValueError(f"Invalid 43-slot board shape {arr.shape}, expected (8, 6) or length 43.")
            self._has_pocket = True
            self._rows = 7
            self._cols = 6
        else:
            if arr.ndim == 1:
                arr = arr.reshape((rows, cols))
            self._has_pocket = False
            self._rows = arr.shape[0]
            self._cols = arr.shape[1]

        self._board = arr
        self._board.flags.writeable = False

        blank_indices = np.argwhere(self._board == 0)
        if len(blank_indices) != 1:
            raise ValueError(f"Puzzle must contain exactly one blank tile (0), found {len(blank_indices)}.")
        self._blank_pos: Tuple[int, int] = (int(blank_indices[0][0]), int(blank_indices[0][1]))
        self._hash: Optional[int] = None

    @classmethod
    def create_goal(cls, rows: int = 7, cols: int = 6, has_pocket: bool = True) -> PuzzleState:
        """Creates the solved goal state (42 tiles on 6x7 grid + blank 0 in side pocket)."""
        if has_pocket and rows == 7 and cols == 6:
            board = np.full((8, 6), -1, dtype=np.int32)
            board[:7, :] = np.arange(1, 43, dtype=np.int32).reshape((7, 6))
            board[7, 0] = 0  # Blank in pocket
            return cls(board, rows=7, cols=6, has_pocket=True)
        else:
            total_tiles = rows * cols
            goal_arr = np.arange(1, total_tiles + 1, dtype=np.int32)
            goal_arr[-1] = 0
            return cls(goal_arr.reshape((rows, cols)), rows=rows, cols=cols, has_pocket=False)

    @property
    def board(self) -> np.ndarray:
        return self._board

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def has_pocket(self) -> bool:
        return self._has_pocket

    @property
    def blank_pos(self) -> Tuple[int, int]:
        return self._blank_pos

    def is_solved(self) -> bool:
        """Checks if board is in solved goal state."""
        if self._has_pocket:
            if self._blank_pos != self.POCKET_POS:
                return False
            grid_flat = self._board[:7, :].ravel()
            return bool(np.all(grid_flat == np.arange(1, 43, dtype=np.int32)))
        else:
            flat = self._board.ravel()
            return flat[-1] == 0 and bool(np.all(flat[:-1] == np.arange(1, self._rows * self._cols, dtype=np.int32)))

    def is_valid_action(self, action: Action) -> bool:
        """Checks if action is valid from current blank position."""
        br, bc = self._blank_pos

        if self._has_pocket:
            # Blank in pocket (7, 0) on the LEFT of (6, 0)
            if (br, bc) == self.POCKET_POS:
                # Can ONLY move RIGHT into (6, 0)
                return action == Action.RIGHT

            # Blank at (6, 0)
            if (br, bc) == self.POCKET_ENTRY_POS:
                if action == Action.LEFT:
                    # Move LEFT into side pocket (7, 0)
                    return True
                # Normal grid moves from (6, 0): UP, RIGHT
                return action in (Action.UP, Action.RIGHT)

            # Standard main grid bounds (0..6, 0..5)
            dr, dc = ACTION_DELTAS[action]
            nr, nc = br + dr, bc + dc
            return 0 <= nr < 7 and 0 <= nc < 6
        else:
            dr, dc = ACTION_DELTAS[action]
            nr, nc = br + dr, bc + dc
            return 0 <= nr < self._rows and 0 <= nc < self._cols

    def get_valid_actions(self) -> List[Action]:
        """Returns list of legal actions."""
        return [action for action in Action if self.is_valid_action(action)]

    def apply_action(self, action: Action) -> PuzzleState:
        """Returns a new PuzzleState resulting from executing action."""
        if not self.is_valid_action(action):
            raise ValueError(f"Illegal action {action.name} from {self._blank_pos}.")

        br, bc = self._blank_pos

        if self._has_pocket:
            if (br, bc) == self.POCKET_POS and action == Action.RIGHT:
                nr, nc = self.POCKET_ENTRY_POS
            elif (br, bc) == self.POCKET_ENTRY_POS and action == Action.LEFT:
                nr, nc = self.POCKET_POS
            else:
                dr, dc = ACTION_DELTAS[action]
                nr, nc = br + dr, bc + dc
        else:
            dr, dc = ACTION_DELTAS[action]
            nr, nc = br + dr, bc + dc

        new_board = self._board.copy()
        new_board[br, bc], new_board[nr, nc] = new_board[nr, nc], new_board[br, bc]
        return PuzzleState(new_board, rows=self._rows, cols=self._cols, has_pocket=self._has_pocket)

    def is_solvable(self) -> bool:
        """Mathematical parity solvability theorem for 43-slot or NxM puzzles."""
        if self._has_pocket:
            grid_flat = self._board[:7, :].ravel()
            grid_tiles = grid_flat[grid_flat > 0]

            inversions = 0
            n = len(grid_tiles)
            for i in range(n):
                inversions += int(np.sum(grid_tiles[i] > grid_tiles[i + 1:]))

            if self._blank_pos == self.POCKET_POS:
                return inversions % 2 == 0
            else:
                blank_r = self._blank_pos[0]
                return (inversions + (6 - blank_r)) % 2 == 0
        else:
            flat = self._board.ravel()
            tiles = flat[flat != 0]
            inversions = 0
            n = len(tiles)
            for i in range(n):
                inversions += int(np.sum(tiles[i] > tiles[i + 1:]))

            if self._cols % 2 != 0:
                return inversions % 2 == 0
            blank_row_from_bottom = self._rows - self._blank_pos[0]
            return (inversions + blank_row_from_bottom) % 2 != 0

    def scramble(self, steps: int = 50, seed: Optional[int] = None) -> Tuple[PuzzleState, List[Action]]:
        """Scrambles the puzzle via random walk, guaranteeing 100% solvability."""
        rng = np.random.default_rng(seed)
        current = self
        action_history: List[Action] = []
        last_action: Optional[Action] = None

        for _ in range(steps):
            valid_actions = current.get_valid_actions()
            if last_action is not None and len(valid_actions) > 1:
                opposite = last_action.opposite
                filtered = [a for a in valid_actions if a != opposite]
                candidates = filtered if filtered else valid_actions
            else:
                candidates = valid_actions

            chosen_action = candidates[int(rng.integers(len(candidates)))]
            current = current.apply_action(chosen_action)
            action_history.append(chosen_action)
            last_action = chosen_action

        return current, action_history

    def manhattan_distance(self) -> int:
        """Calculates Manhattan distance sum to goal positions."""
        total_dist = 0
        grid_rows = 7 if self._has_pocket else self._rows
        grid_cols = 6 if self._has_pocket else self._cols

        for r in range(grid_rows):
            for c in range(grid_cols):
                val = self._board[r, c]
                if val <= 0:
                    continue
                target_r = (val - 1) // grid_cols
                target_c = (val - 1) % grid_cols
                total_dist += abs(r - target_r) + abs(c - target_c)

        if self._has_pocket and self._board[7, 0] > 0:
            val = self._board[7, 0]
            target_r = (val - 1) // grid_cols
            target_c = (val - 1) % grid_cols
            total_dist += abs(6 - target_r) + abs(0 - target_c) + 1

        return total_dist

    def linear_conflicts(self) -> int:
        """Calculates linear conflicts for tiles in their target rows and columns."""
        conflicts = 0
        grid_rows = 7 if self._has_pocket else self._rows
        grid_cols = 6 if self._has_pocket else self._cols

        # Row linear conflicts
        for r in range(grid_rows):
            row_tiles = []
            for c in range(grid_cols):
                val = self._board[r, c]
                if val > 0 and (val - 1) // grid_cols == r:
                    row_tiles.append((c, (val - 1) % grid_cols))

            for i in range(len(row_tiles)):
                for j in range(i + 1, len(row_tiles)):
                    if row_tiles[i][1] > row_tiles[j][1]:
                        conflicts += 1

        # Column linear conflicts
        for c in range(grid_cols):
            col_tiles = []
            for r in range(grid_rows):
                val = self._board[r, c]
                if val > 0 and (val - 1) % grid_cols == c:
                    col_tiles.append((r, (val - 1) // grid_cols))

            for i in range(len(col_tiles)):
                for j in range(i + 1, len(col_tiles)):
                    if col_tiles[i][1] > col_tiles[j][1]:
                        conflicts += 1

        return conflicts

    def heuristic_cost(self) -> int:
        return self.manhattan_distance() + 2 * self.linear_conflicts()

    def to_one_hot(self, dtype: np.dtype = np.float32) -> np.ndarray:
        """Returns one-hot tensor representation."""
        if self._has_pocket:
            one_hot = np.zeros((43, 8, 6), dtype=dtype)
            for r in range(8):
                for c in range(6):
                    val = self._board[r, c]
                    if val >= 0:
                        one_hot[val, r, c] = 1.0
            return one_hot
        else:
            total_tiles = self._rows * self._cols
            one_hot = np.zeros((total_tiles, self._rows, self._cols), dtype=dtype)
            for r in range(self._rows):
                for c in range(self._cols):
                    val = self._board[r, c]
                    one_hot[val, r, c] = 1.0
            return one_hot

    def to_list(self) -> List[int]:
        """Returns a list of 43 integers representing the board in order."""
        if self._has_pocket:
            grid = [int(x) for x in self._board[:7, :].ravel()]
            grid.append(int(self._board[7, 0]))
            return grid
        return [int(x) for x in self._board.ravel()]

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self._board.tobytes())
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PuzzleState):
            return False
        return bool(np.array_equal(self._board, other._board))

    def __repr__(self) -> str:
        return f"PuzzleState(43-slot, blank={self._blank_pos})\n{self._board}"
