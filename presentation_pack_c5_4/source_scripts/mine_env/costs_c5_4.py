from __future__ import annotations

from mine_env.costs_c5_3 import C5_3CostModel


class C5_4CostModel(C5_3CostModel):
    """TCO cost model for C5.4 -- identical structure to C5.3.

    TCO = pm + cm + downtime + degradation + unmet_demand (production/cycle excluded -- the
    RL-Lab idle-exploit fix). PM is now a *decision* in C5.4, but the cost numbers are reused
    verbatim from C5.3/C6 (anti-overclaim: not re-tuned). A thin subclass keeps the two
    versions byte-identical on cost so any C5.4 vs C5.3 difference is attributable to the
    decision change, never to a quietly altered price. See ``mine_env/costs_c5_3.py``.
    """


__all__ = ["C5_4CostModel"]
