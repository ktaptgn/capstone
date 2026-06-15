from __future__ import annotations

from mine_env.reliability_c5_3 import COMPONENTS, C5_3ReliabilityModel


class C5_4ReliabilityModel(C5_3ReliabilityModel):
    """Three-component reliability model for C5.4 -- identical physics to C5.3.

    C5.4 widens the *decision target* (PM scheduling becomes a policy choice alongside
    dispatch) but leaves the reliability surface untouched: the same 3-component HI
    (tire/engine/brake, truck HI = min), Gamma frailty, POMDP sensor noise and Weibull-like
    failure hazard validated in the RL Lab C6 stack and carried into C5.3. It is a thin
    subclass (zero parameter drift) so the C5.4 PM-vs-dispatch comparison runs on exactly the
    same honest cost surface as C5.3 -- only the maintenance authority changes (fixed CBM rule
    -> the policy). See ``mine_env/reliability_c5_3.py`` for the mechanics.
    """


__all__ = ["COMPONENTS", "C5_4ReliabilityModel"]
