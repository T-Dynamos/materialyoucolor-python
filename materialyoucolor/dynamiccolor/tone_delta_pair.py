from dataclasses import dataclass, field
from typing import Literal, Optional

TonePolarity = Literal[
    "darker",
    "lighter",
    "nearer",
    "farther",
    "relative_darker",
    "relative_lighter",
]

DeltaConstraint = Literal["exact", "nearer", "farther"]


@dataclass
class ToneDeltaPair:
    role_a: "DynamicColor"
    role_b: "DynamicColor"
    delta: int
    polarity: TonePolarity
    stay_together: bool
    constraint: DeltaConstraint = field(default="exact")

    def __post_init__(self):
        if self.constraint not in ("exact", "nearer", "farther"):
            self.constraint = "exact"
