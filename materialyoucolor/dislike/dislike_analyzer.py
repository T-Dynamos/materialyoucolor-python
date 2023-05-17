from materialyoucolor.hct import Hct


class DislikeAnalyzer:
    @staticmethod
    def is_disliked(hct: Hct) -> bool:
        hue_passes = round(hct.hue) >= 90.0 and round(hct.hue) <= 111.0
        chroma_passes = round(hct.chroma) > 16.0
        tone_passes = round(hct.tone) < 65.0
        return hue_passes and chroma_passes and tone_passes

    @staticmethod
    def fix_if_disliked(hct: Hct) -> Hct:
        if DislikeAnalyzer.is_disliked(hct):
            return Hct.from_hct(
                hct.hue,
                hct.chroma,
                70.0,
            )

        return hct
