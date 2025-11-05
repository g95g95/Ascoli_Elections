"""Markov-chain utilities for modelling voter migrations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, MutableMapping, Sequence


@dataclass(frozen=True)
class TransitionMatrix:
    """Row-stochastic Markov matrix with labelled states."""

    states: Sequence[str]
    matrix: Sequence[Sequence[float]]

    def __post_init__(self) -> None:
        size = len(self.states)
        if any(len(row) != size for row in self.matrix):
            msg = "Transition matrix must be square"
            raise ValueError(msg)
        for row in self.matrix:
            if not _close(sum(row), 1.0):
                msg = "Rows must sum to 1"
                raise ValueError(msg)

    @property
    def as_dict(self) -> Dict[str, Dict[str, float]]:
        return {
            origin: {dest: float(prob) for dest, prob in zip(self.states, row)}
            for origin, row in zip(self.states, self.matrix)
        }

    def project(self, distribution: Mapping[str, float]) -> Dict[str, float]:
        """Left-multiply *distribution* by the matrix."""

        vector = [distribution[state] for state in self.states]
        result = [0.0 for _ in self.states]
        for j in range(len(self.states)):
            result[j] = sum(vector[i] * self.matrix[i][j] for i in range(len(self.states)))
        return {state: value for state, value in zip(self.states, result)}


def normalise_distribution(masses: Mapping[str, float]) -> Dict[str, float]:
    """Return a probability vector from raw masses."""

    total = float(sum(masses.values()))
    if total <= 0:
        msg = "Total probability mass must be positive"
        raise ValueError(msg)
    return {state: mass / total for state, mass in masses.items()}


def calibrate_runoff_transition(
    first_round_distribution: Mapping[str, float],
    runoff_distribution: Mapping[str, float],
    runoff_states: Iterable[str],
    abstention_label: str,
    base_preferences: Mapping[str, Mapping[str, float]],
    elasticity: float = 0.2,
) -> TransitionMatrix:
    """Create a Markov matrix describing flows into a runoff."""

    states = list(first_round_distribution.keys()) + [abstention_label]
    runoff_states = list(runoff_states)
    if abstention_label not in runoff_distribution:
        msg = "Runoff distribution must include abstention"
        raise ValueError(msg)

    runoff_target = [runoff_distribution.get(state, 0.0) for state in states]
    total_target = sum(runoff_target)
    runoff_target = [value / total_target for value in runoff_target]

    matrix = []
    for origin in states:
        base = dict(base_preferences.get(origin, {}))
        if not base:
            base = {origin: 1.0}

        base = _ensure_support(base, states)

        blend = [
            (1.0 - elasticity) * base[state] + elasticity * target_val
            for state, target_val in zip(states, runoff_target)
        ]
        normalised = _normalise_row(blend)
        matrix.append(normalised)

    return TransitionMatrix(states=states, matrix=matrix)


def _ensure_support(masses: MutableMapping[str, float], states: Sequence[str]) -> Dict[str, float]:
    for state in states:
        masses.setdefault(state, 0.0)
    return normalise_distribution(masses)


def _normalise_row(row: Sequence[float]) -> Sequence[float]:
    total = sum(row)
    if total == 0:
        return [1.0 / len(row) for _ in row]
    return [value / total for value in row]


def _close(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol

