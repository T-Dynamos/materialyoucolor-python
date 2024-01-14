import math
from materialyoucolor.hct import Hct
from materialyoucolor.utils.math_utils import (
    sanitize_degrees_int,
    sanitize_degrees_double,
)
from materialyoucolor.utils.color_utils import lab_from_argb


class TemperatureCache:
    def __init__(self, input_hct: Hct):
        self.input_hct = input_hct
        self.hcts_by_temp_cache = []
        self.hcts_by_hue_cache = []
        self.temps_by_hct_cache = {}
        self.input_hct_relative_temperature_cache = -1.0
        self.complement_cache = None

    @property
    def hcts_by_temp(self):
        if self.hcts_by_temp_cache:
            return self.hcts_by_temp_cache

        hcts = self.hcts_by_hue + [self.input_hct]
        temperatures_by_hct = self.temps_by_hct
        hcts.sort(key=lambda x: temperatures_by_hct[x])
        self.hcts_by_temp_cache = hcts
        return hcts

    @property
    def warmest(self) -> Hct:
        return self.hcts_by_temp[-1]

    @property
    def coldest(self) -> Hct:
        return self.hcts_by_temp[0]

    def analogous(self, count: int, divisions: int) -> list:
        start_hue = round(self.input_hct.hue)
        start_hct = self.hcts_by_hue[start_hue]
        last_temp = self.relative_temperature(start_hct)
        all_colors = [start_hct]

        absolute_total_temp_delta = 0.0
        for i in range(360):
            hue = int(sanitize_degrees_int(start_hue + i))
            hct = self.hcts_by_hue[hue]
            temp = self.relative_temperature(hct)
            temp_delta = abs(temp - last_temp)
            last_temp = temp
            absolute_total_temp_delta += temp_delta

        hue_addend = 1
        temp_step = absolute_total_temp_delta / divisions
        total_temp_delta = 0.0
        last_temp = self.relative_temperature(start_hct)

        while len(all_colors) < divisions:
            hue = int(sanitize_degrees_int(start_hue + hue_addend))
            hct = self.hcts_by_hue[hue]
            temp = self.relative_temperature(hct)
            temp_delta = abs(temp - last_temp)
            total_temp_delta += temp_delta

            desired_total_temp_delta_for_index = len(all_colors) * temp_step
            index_satisfied = total_temp_delta >= desired_total_temp_delta_for_index
            index_addend = 1

            while index_satisfied and len(all_colors) < divisions:
                all_colors.append(hct)
                desired_total_temp_delta_for_index = (
                    len(all_colors) + index_addend
                ) * temp_step
                index_satisfied = total_temp_delta >= desired_total_temp_delta_for_index
                index_addend += 1

            last_temp = temp
            hue_addend += 1

            if hue_addend > 360:
                while len(all_colors) < divisions:
                    all_colors.append(hct)
                break

        answers = [self.input_hct]

        increase_hue_count = int((count - 1) / 2.0)
        for i in range(1, increase_hue_count + 1):
            index = 0 - i
            while index < 0:
                index = len(all_colors) + index
            if index >= len(all_colors):
                index = index % len(all_colors)
            answers.insert(0, all_colors[index])

        decrease_hue_count = count - increase_hue_count - 1
        for i in range(1, decrease_hue_count + 1):
            index = i
            while index < 0:
                index = len(all_colors) + index
            if index >= len(all_colors):
                index = index % len(all_colors)
            answers.append(all_colors[index])

        return answers

    def complement(self) -> Hct:
        if self.complement_cache is not None:
            return self.complement_cache

        coldest_hue = self.coldest.hue
        coldest_temp = self.temps_by_hct[self.coldest]

        warmest_hue = self.warmest.hue
        warmest_temp = self.temps_by_hct[self.warmest]
        range_temp = warmest_temp - coldest_temp
        start_hue_is_coldest_to_warmest = TemperatureCache.is_between(
            self.input_hct.hue, coldest_hue, warmest_hue
        )
        start_hue = warmest_hue if start_hue_is_coldest_to_warmest else coldest_hue
        end_hue = coldest_hue if start_hue_is_coldest_to_warmest else warmest_hue
        direction_of_rotation = 1.0
        smallest_error = 1000.0
        answer = self.hcts_by_hue[round(self.input_hct.hue)]

        complement_relative_temp = 1.0 - self.input_relative_temperature
        for hue_addend in range(0, 360):
            hue = sanitize_degrees_double(
                start_hue + direction_of_rotation * hue_addend
            )
            if not TemperatureCache.is_between(hue, start_hue, end_hue):
                continue
            possible_answer = self.hcts_by_hue[round(hue)]
            relative_temp = (
                self.temps_by_hct[possible_answer] - coldest_temp
            ) / range_temp
            error = abs(complement_relative_temp - relative_temp)
            if error < smallest_error:
                smallest_error = error
                answer = possible_answer

        self.complement_cache = answer
        return self.complement_cache

    def relative_temperature(self, hct: Hct) -> float:
        range_temp = self.temps_by_hct[self.warmest] - self.temps_by_hct[self.coldest]
        difference_from_coldest = (
            self.temps_by_hct[hct] - self.temps_by_hct[self.coldest]
        )
        if range_temp == 0.0:
            return 0.5
        return difference_from_coldest / range_temp

    @property
    def input_relative_temperature(self) -> float:
        if self.input_hct_relative_temperature_cache >= 0.0:
            return self.input_hct_relative_temperature_cache

        self.input_hct_relative_temperature_cache = self.relative_temperature(
            self.input_hct
        )
        return self.input_hct_relative_temperature_cache

    @property
    def temps_by_hct(self) -> dict[Hct:float]:
        if self.temps_by_hct_cache:
            return self.temps_by_hct_cache

        all_hcts = self.hcts_by_hue + [self.input_hct]
        temperatures_by_hct = {}
        for e in all_hcts:
            temperatures_by_hct[e] = TemperatureCache.raw_temperature(e)

        self.temps_by_hct_cache = temperatures_by_hct
        return temperatures_by_hct

    @property
    def hcts_by_hue(self) -> list[Hct]:
        if self.hcts_by_hue_cache:
            return self.hcts_by_hue_cache

        hcts = [
            Hct.from_hct(hue, self.input_hct.chroma, self.input_hct.tone)
            for hue in range(0, 361)
        ]
        self.hcts_by_hue_cache = hcts
        return hcts

    @staticmethod
    def is_between(angle: float, a: float, b: float) -> bool:
        if a < b:
            return a <= angle <= b
        return a <= angle or angle <= b

    @staticmethod
    def raw_temperature(color: Hct) -> float:
        lab = lab_from_argb(color.to_int())
        hue = sanitize_degrees_double(math.atan2(lab[2], lab[1]) * 180.0 / math.pi)
        chroma = math.sqrt((lab[1] * lab[1]) + (lab[2] * lab[2]))
        temperature = -0.5 + 0.02 * (chroma**1.07) * math.cos(
            sanitize_degrees_double(hue - 50.0) * math.pi / 180.0
        )
        return temperature
