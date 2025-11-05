"""Election data for Ascoli Piceno."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class CandidateResult:
    """Container for first and (optionally) second round data."""

    name: str
    coalition: str
    first_round_votes: int
    first_round_share: float
    runoff_votes: Optional[int] = None
    runoff_share: Optional[float] = None


TOTAL_VALID_VOTES_FIRST_ROUND = 37826
"""Number of valid ballots in the 2019 first round."""

TOTAL_VALID_VOTES_RUNOFF = 27270
"""Number of valid ballots in the 2019 runoff."""

CANDIDATES_2019: List[CandidateResult] = [
    CandidateResult(
        name="Marco Fioravanti",
        coalition="Centrodestra",
        first_round_votes=14170,
        first_round_share=0.3747,
        runoff_votes=16199,
        runoff_share=0.5931,
    ),
    CandidateResult(
        name="Piero Celani",
        coalition="Civiche di centro",
        first_round_votes=12288,
        first_round_share=0.3248,
        runoff_votes=11101,
        runoff_share=0.4069,
    ),
    CandidateResult(
        name="Francesco Ameli",
        coalition="Centrosinistra",
        first_round_votes=8850,
        first_round_share=0.2338,
    ),
    CandidateResult(
        name="Gianluca Vecchi",
        coalition="Movimento 5 Stelle",
        first_round_votes=1985,
        first_round_share=0.0525,
    ),
    CandidateResult(
        name="Domenico Stallone",
        coalition="Civiche",
        first_round_votes=533,
        first_round_share=0.0141,
    ),
]
"""Official results (Eligendo) of the 2019 municipal election."""


ABSTENTION_RATE_FIRST_ROUND = 0.379
"""Share of eligible voters who abstained in the first round."""

ABSTENTION_RATE_RUNOFF = 0.565
"""Share of eligible voters who abstained in the runoff."""


def candidate_lookup() -> Dict[str, CandidateResult]:
    """Return a dictionary mapping candidate names to their result summary."""

    return {candidate.name: candidate for candidate in CANDIDATES_2019}

