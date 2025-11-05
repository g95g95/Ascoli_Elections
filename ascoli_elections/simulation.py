"""Monte Carlo simulator for the Ascoli Piceno mayoral race."""
from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Tuple

from .data import (
    ABSTENTION_RATE_FIRST_ROUND,
    ABSTENTION_RATE_RUNOFF,
    CANDIDATES_2019,
    CandidateResult,
)
from .markov import TransitionMatrix, calibrate_runoff_transition, normalise_distribution

if "NP_RANDOM_SEED" in os.environ:
    random.seed(int(os.environ["NP_RANDOM_SEED"]))


@dataclass
class ElectionParameters:
    """Parameters governing the Monte Carlo sampling."""

    draws: int = 10000
    concentration: float = 5000.0
    abstention_volatility: float = 0.02
    runoff_elasticity: float = 0.2
    runoff_strength: float = 600.0


class MonteCarloElection:
    """Simulate the Ascoli Piceno mayoral election."""

    def __init__(self, candidates: Iterable[CandidateResult], params: ElectionParameters | None = None) -> None:
        self.candidates: List[CandidateResult] = list(candidates)
        self.params = params or ElectionParameters()

        self.candidate_names = [candidate.name for candidate in self.candidates]
        baseline = [candidate.first_round_share for candidate in self.candidates]
        total = sum(baseline)
        self.first_round_baseline = [share / total for share in baseline]

        self.runoff_target = self._build_runoff_target()
        self.transition_matrix = self._build_transition_matrix()

    def _build_runoff_target(self) -> Dict[str, float]:
        target: Dict[str, float] = {candidate.name: candidate.runoff_share or 0.0 for candidate in self.candidates}
        target["Astensione"] = ABSTENTION_RATE_RUNOFF
        return normalise_distribution(target)

    def _build_transition_matrix(self) -> TransitionMatrix:
        first_round = {candidate.name: share for candidate, share in zip(self.candidates, self.first_round_baseline)}
        first_round["Astensione"] = ABSTENTION_RATE_FIRST_ROUND

        runoff_distribution = self.runoff_target
        runoff_states = [candidate.name for candidate in self.candidates if candidate.runoff_share]
        base_preferences = {
            "Marco Fioravanti": {"Marco Fioravanti": 0.96, "Piero Celani": 0.02, "Astensione": 0.02},
            "Piero Celani": {"Piero Celani": 0.96, "Marco Fioravanti": 0.02, "Astensione": 0.02},
            "Francesco Ameli": {"Piero Celani": 0.60, "Marco Fioravanti": 0.25, "Astensione": 0.15},
            "Gianluca Vecchi": {"Marco Fioravanti": 0.45, "Piero Celani": 0.35, "Astensione": 0.20},
            "Domenico Stallone": {"Marco Fioravanti": 0.65, "Piero Celani": 0.20, "Astensione": 0.15},
            "Astensione": {"Astensione": 0.60, "Marco Fioravanti": 0.20, "Piero Celani": 0.20},
        }
        return calibrate_runoff_transition(
            first_round_distribution=first_round,
            runoff_distribution=runoff_distribution,
            runoff_states=runoff_states,
            abstention_label="Astensione",
            base_preferences=base_preferences,
            elasticity=self.params.runoff_elasticity,
        )

    def _dirichlet_sample(self) -> List[float]:
        alpha = [share * self.params.concentration for share in self.first_round_baseline]
        gammas = [random.gammavariate(max(a, 1e-9), 1.0) for a in alpha]
        total = sum(gammas)
        return [value / total for value in gammas]

    def _draw_first_round(self) -> Tuple[List[float], Dict[str, float]]:
        shares = self._dirichlet_sample()
        abstention = _clamp(random.gauss(ABSTENTION_RATE_FIRST_ROUND, self.params.abstention_volatility), 0.0, 0.9)
        distribution = {name: share for name, share in zip(self.candidate_names, shares)}
        distribution["Astensione"] = abstention
        return shares, distribution

    def _runoff(self, first_round_distribution: Mapping[str, float], finalists: Iterable[str]) -> Dict[str, float]:
        projection = self.transition_matrix.project(first_round_distribution)
        total = sum(projection[name] for name in finalists)
        baseline = {name: projection[name] / total for name in finalists}

        if self.params.runoff_strength <= 0:
            return baseline

        finalists = list(finalists)
        first, second = finalists[0], finalists[1]
        alpha = max(baseline[first] * self.params.runoff_strength, 1e-6)
        beta = max(baseline[second] * self.params.runoff_strength, 1e-6)
        sample = random.betavariate(alpha, beta)
        return {first: sample, second: 1.0 - sample}

    def simulate(self) -> Dict[str, float]:
        """Run the Monte Carlo experiment and return win frequencies."""

        wins = {candidate.name: 0 for candidate in self.candidates}

        for _ in range(self.params.draws):
            shares, distribution = self._draw_first_round()

            majority = max(shares)
            if majority > 0.5:
                winner = self.candidate_names[shares.index(majority)]
                wins[winner] += 1
                continue

            finalists_idx = sorted(range(len(shares)), key=lambda idx: shares[idx], reverse=True)[:2]
            finalists = [self.candidate_names[i] for i in finalists_idx]
            runoff_distribution = self._runoff(distribution, finalists)
            winner = max(runoff_distribution, key=runoff_distribution.get)
            wins[winner] += 1

        return {name: wins[name] / self.params.draws for name in wins}


def run_default_simulation() -> Dict[str, float]:
    """Convenience helper returning win rates under default settings."""

    simulator = MonteCarloElection(CANDIDATES_2019)
    return simulator.simulate()


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


if __name__ == "__main__":
    win_rates = run_default_simulation()
    for name, frequency in sorted(win_rates.items(), key=lambda item: item[1], reverse=True):
        print(f"{name:25s}: {frequency:.3%}")

