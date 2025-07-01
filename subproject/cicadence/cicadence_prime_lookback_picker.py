"""
prime_lookback_picker.py
────────────────────────

Goal
----
Pick a prime-number “look-back window” (in days) that collides *least often*
with a set of common analytics windows **within the next decade** (3 650 days).

A *collision* means:               day  %  LCM(p, base) == 0
where  p     = candidate prime look-back
       base  = one of the base windows

We *weight* collisions by density:
If a day is a multiple of *three* base windows, it contributes 3 to the score.

The script:

1.  Lists every prime `p` such that 10 < p < 90.
2.  Counts the *weighted* collisions for each `p` versus the base windows  
    [7, 10, 30, 60, 90, 365, 730, 1095, 1825, 3650].
3.  Prints the full table and highlights the prime with the **lowest score**.

Output example
--------------
    Prime with the lowest weighted collision score = 89 (score=10)

    Prime : Weighted collision score (lower is better)
     11 : 99
     13 : 84
     ...
     89 : 10

Interpretation
--------------
• Lower score → fewer “overlap events” where analytic windows
  hit the same day.

• `89` wins because its first overlaps with the densest windows
  (7 × 89, 10 × 89, 30 × 89) are so far out that only a handful
  fit inside 10 years.

Customization
-------------
* Change `BASE_WINDOWS` to suit your organisation’s standard KPI windows.
* Change `HORIZON_DAYS` (default 3650) if you care about a shorter/longer
  planning horizon.
"""

from __future__ import annotations

from math import gcd, sqrt
from typing import List, Dict

# ----------------------------------------------------------------------#
# Configuration
# ----------------------------------------------------------------------#
BASE_WINDOWS: List[int] = [
    7, 10, 30, 60, 90,          # sub-quarter & quarter windows
    365, 730, 1095, 1825, 3650  # 1-, 2-, 3-, 5-, 10-year windows
]
HORIZON_DAYS: int = 3650        # evaluate collisions in first 10 years


# ----------------------------------------------------------------------#
# Utility functions
# ----------------------------------------------------------------------#
def is_prime(n: int) -> bool:
    """
    Simple deterministic primality test for small integers.

    Parameters
    ----------
    n : int
        Number to test.

    Returns
    -------
    bool
        True if *n* is prime, otherwise False.
    """
    if n < 2:
        return False
    # check divisibility by 2 and 3 first
    if n % 2 == 0 or n % 3 == 0:
        return n in (2, 3)
    # test odd divisors up to sqrt(n)
    for d in range(5, int(sqrt(n)) + 1, 6):
        if n % d == 0 or n % (d + 2) == 0:
            return False
    return True


def lcm(a: int, b: int) -> int:
    """
    Least Common Multiple using gcd for efficiency.

    Parameters
    ----------
    a, b : int
        Input integers.

    Returns
    -------
    int
        The LCM of *a* and *b*.
    """
    return a // gcd(a, b) * b


def weighted_collision_score(p: int, horizon: int = HORIZON_DAYS) -> int:
    """
    Calculate the *weighted* number of collision days for a candidate prime.

    A collision day contributes +1 for **each** base window that aligns with it.

    Parameters
    ----------
    p : int
        Candidate prime look-back window.
    horizon : int
        Days forward to check (inclusive).

    Returns
    -------
    int
        Sum of collision weights ≤ *horizon*.
    """
    score = 0
    for base in BASE_WINDOWS:
        step = lcm(p, base)          # distance between hits for (p, base)
        score += horizon // step     # how many multiples ≤ horizon
    return score


# ----------------------------------------------------------------------#
# Main evaluation
# ----------------------------------------------------------------------#
def evaluate_primes(lower: int = 11, upper: int = 700) -> Dict[int, int]:
    """
    Build a dict {prime: score} for all primes in (lower, upper).

    Note: every prime above 700 days, has a 0 within a 10 year window.

    Returns
    -------
    dict
        Mapping prime → weighted collision score.
    """
    return {p: weighted_collision_score(p)
            for p in range(lower, upper + 1) if is_prime(p)}


def main() -> None:
    scores = evaluate_primes()
    best_prime = min(scores, key=scores.get)

    print(f"Prime with the lowest weighted collision score = "
          f"{best_prime} (score={scores[best_prime]})\n")

    print("Prime : Weighted collision score (lower is better)\n")
    for p in sorted(scores):
        print(f"{p:>2} : {scores[p]}")


# ----------------------------------------------------------------------#
# CLI entry-point
# ----------------------------------------------------------------------#
if __name__ == "__main__":
    main()
