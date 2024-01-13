from typing import Union

TonePolarity = Union["darker", "lighter", "nearer", "farther"]


class ToneDeltaPair:
    def __init__(
        self,
        role_a: None,  # DynamicColor,
        role_b: None,  # DynamicColor,
        delta: int,
        polarity: TonePolarity,
        stay_together: bool,
    ):
        self.role_a = role_a
        self.role_b = role_b
        self.delta = delta
        self.polarity = polarity
        self.stay_together = stay_together
