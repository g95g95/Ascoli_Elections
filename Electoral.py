"""Command-line entry point for the Ascoli Piceno election simulator."""
from __future__ import annotations

import argparse
from dataclasses import asdict

from ascoli_elections import ElectionParameters, MonteCarloElection
from ascoli_elections.data import CANDIDATES_2019


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simula l'elezione del sindaco di Ascoli Piceno con metodo Monte Carlo.",
    )
    parser.add_argument(
        "--draws",
        type=int,
        default=10000,
        help="Numero di estrazioni Monte Carlo da eseguire.",
    )
    parser.add_argument(
        "--concentration",
        type=float,
        default=5000.0,
        help="Parametro di concentrazione della Dirichlet (maggiore = minore volatilità).",
    )
    parser.add_argument(
        "--abstention-volatility",
        type=float,
        default=0.02,
        help="Deviazione standard della stima di astensione (Gauss).",
    )
    parser.add_argument(
        "--runoff-elasticity",
        type=float,
        default=0.2,
        help="Elasticità con cui il Markov chain converge verso il risultato storico del ballottaggio.",
    )
    parser.add_argument(
        "--runoff-strength",
        type=float,
        default=600.0,
        help="Ampiezza efficace (alpha+beta) della Beta sul ballottaggio. 0 = deterministico.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    params = ElectionParameters(
        draws=args.draws,
        concentration=args.concentration,
        abstention_volatility=args.abstention_volatility,
        runoff_elasticity=args.runoff_elasticity,
        runoff_strength=args.runoff_strength,
    )

    simulator = MonteCarloElection(CANDIDATES_2019, params=params)
    win_rates = simulator.simulate()

    print("Parametri utilizzati:")
    for key, value in asdict(params).items():
        print(f"  {key}: {value}")

    print("\nFrequenze di vittoria:")
    for name, frequency in sorted(win_rates.items(), key=lambda item: item[1], reverse=True):
        print(f"  {name:25s}: {frequency:.2%}")


if __name__ == "__main__":
    main()

