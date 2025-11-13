from typing import Literal, Optional

TonePolarity = Literal[
    "darker", "lighter", "nearer", "farther", "relative_darker", "relative_lighter"
]
DeltaConstraint = Literal["exact", "nearer", "farther"]


class ToneDeltaPair:
    def __init__(
        self,
        role_a: "DynamicColor",
        role_b: "DynamicColor",
        delta: float,
        polarity: TonePolarity,
        stay_together: bool,
        constraint: Optional[DeltaConstraint] = "exact",
    ):
        self.role_a = role_a
        self.role_b = role_b
        self.delta = delta
        self.polarity = polarity
        self.stay_together = stay_together
        self.constraint = constraint
