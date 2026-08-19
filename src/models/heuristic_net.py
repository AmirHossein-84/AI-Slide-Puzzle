"""PyTorch Neural Network architecture for puzzle cost-to-go / heuristic estimation."""

from __future__ import annotations

from typing import List, Sequence, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from src.environment.puzzle_state import PuzzleState


class ResidualBlock(nn.Module):
    """Convolutional residual block with batch normalization and ReLU."""

    def __init__(self, channels: int) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = F.leaky_relu(self.bn1(self.conv1(x)), negative_slope=0.01)
        out = self.bn2(self.conv2(out))
        out += residual
        return F.leaky_relu(out, negative_slope=0.01)


class PuzzleHeuristicNet(nn.Module):
    """Deep residual network estimating cost-to-go h_theta(s) for puzzle boards."""

    def __init__(
        self,
        rows: int = 7,
        cols: int = 6,
        has_pocket: bool = False,
        hidden_channels: int = 64,
        num_res_blocks: int = 3,
    ) -> None:
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.has_pocket = has_pocket

        if has_pocket and rows == 7 and cols == 6:
            self.in_channels = 43
            self.in_h = 8
            self.in_w = 6
        else:
            self.in_channels = rows * cols
            self.in_h = rows
            self.in_w = cols

        # Initial feature projection
        self.in_conv = nn.Conv2d(self.in_channels, hidden_channels, kernel_size=3, padding=1)
        self.in_bn = nn.BatchNorm2d(hidden_channels)

        # Residual tower
        self.res_blocks = nn.ModuleList(
            [ResidualBlock(hidden_channels) for _ in range(num_res_blocks)]
        )

        # Output regression head
        self.head = nn.Sequential(
            nn.Conv2d(hidden_channels, 32, kernel_size=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(negative_slope=0.01),
            nn.Flatten(),
            nn.Linear(32 * self.in_h * self.in_w, 128),
            nn.LeakyReLU(negative_slope=0.01),
            nn.Linear(128, 1),
            nn.ReLU(),  # Distance is strictly non-negative
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.
        
        Args:
            x: Float tensor of shape (batch_size, num_tiles, rows, cols).

        Returns:
            Float tensor of shape (batch_size, 1) with estimated remaining cost.
        """
        out = F.leaky_relu(self.in_bn(self.in_conv(x)), negative_slope=0.01)
        for block in self.res_blocks:
            out = block(out)
        return self.head(out)

    @torch.no_grad()
    def predict_states(
        self,
        states: Sequence[PuzzleState],
        device: Union[str, torch.device] = "cpu",
    ) -> np.ndarray:
        """Predicts heuristic values for a batch of PuzzleState objects.

        Args:
            states: Sequence of PuzzleState objects.
            device: Device to perform inference on ('cpu', 'cuda', etc.).

        Returns:
            1D NumPy array of predicted heuristic costs.
        """
        if not states:
            return np.array([], dtype=np.float32)

        self.eval()
        tensors = [torch.from_numpy(s.to_one_hot()) for s in states]
        batch = torch.stack(tensors).to(device)

        preds = self(batch).squeeze(-1).cpu().numpy()
        return np.atleast_1d(preds)
