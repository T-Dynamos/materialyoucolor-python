from materialyoucolor.utils.color_utils import argbFromLstar, lstarFromArgb
from materialyoucolor.utils.math_utils import sanitizeDegreesDouble, clampDouble
from materialyoucolor.hct.cam16 import Cam16
from materialyoucolor.hct.viewing_conditions import ViewingConditions

CHROMA_SEARCH_ENDPOINT = 0.4
DE_MAX = 1.0
DL_MAX = 0.2
LIGHTNESS_SEARCH_ENDPOINT = 0.01


def findCamByJ(hue, chroma, tone):
    low = 0.0
    high = 100.0
    mid = 0.0
    bestdL = 1000.0
    bestdE = 1000.0
    bestCam = None
    while abs(low - high) > LIGHTNESS_SEARCH_ENDPOINT:
        mid = low + (high - low) / 2
        camBeforeClip = Cam16.fromJch(mid, chroma, hue)
        clipped = camBeforeClip.toInt()
        clippedLstar = lstarFromArgb(clipped)
        dL = abs(tone - clippedLstar)
        if dL < DL_MAX:
            camClipped = Cam16.fromInt(clipped)
            dE = camClipped.distance(
                Cam16.fromJch(camClipped.j, camClipped.chroma, hue)
            )
            if dE <= DE_MAX and dE <= bestdE:
                bestdL = dL
                bestdE = dE
                bestCam = camClipped
        if bestdL == 0 and bestdE == 0:
            break
        if clippedLstar < tone:
            low = mid
        else:
            high = mid
    return bestCam


def getIntInViewingConditions(hue, chroma, tone, viewingConditions):
    if chroma < 1.0 or round(tone) <= 0.0 or round(tone) >= 100.0:
        return argbFromLstar(tone)

    hue = sanitizeDegreesDouble(hue)
    high = chroma
    mid = chroma
    low = 0.0
    isFirstLoop = True
    answer = None
    while abs(low - high) >= CHROMA_SEARCH_ENDPOINT:
        possibleAnswer = findCamByJ(hue, mid, tone)
        if isFirstLoop:
            if possibleAnswer != None:
                return possibleAnswer.viewed(viewingConditions)
            else:
                isFirstLoop = False
                mid = low + (high - low) / 2.0
                continue
        if possibleAnswer == None:
            high = mid
        else:
            answer = possibleAnswer
            low = mid
        mid = low + (high - low) / 2.0
    if answer == None:
        return argbFromLstar(tone)
    return answer.viewed(viewingConditions)


def getInt(hue, chroma, tone):
    return getIntInViewingConditions(
        sanitizeDegreesDouble(hue),
        chroma,
        clampDouble(0.0, 100.0, tone),
        ViewingConditions.DEFAULT,
    )


class Hct:
    def __init__(self, internalHue, internalChroma, internalTone):
        self.internalHue = internalHue
        self.internalChroma = internalChroma
        self.internalTone = internalTone
        self.setInternalState(self.toInt())

    @staticmethod
    def fromHct(hue, chroma, tone):
        return Hct(hue, chroma, tone)

    @staticmethod
    def fromInt(argb):
        cam = Cam16.fromInt(argb)
        tone = lstarFromArgb(argb)
        return Hct(cam.hue, cam.chroma, tone)

    def toInt(self):
        return getInt(self.internalHue, self.internalChroma, self.internalTone)

    def get_hue(self):
        return self.internalHue

    def set_hue(self, newHue):
        self.setInternalState(
            getInt(
                sanitizeDegreesDouble(newHue), self.internalChroma, self.internalTone
            )
        )

    def get_chroma(self):
        return self.internalChroma

    def set_chroma(self, newChroma):
        self.setInternalState(getInt(self.internalHue, newChroma, self.internalTone))

    def get_tone(self):
        return self.internalTone

    def set_tone(self, newTone):
        self.setInternalState(getInt(self.internalHue, self.internalChroma, newTone))

    def setInternalState(self, argb):
        cam = Cam16.fromInt(argb)
        tone = lstarFromArgb(argb)
        self.internalHue = cam.hue
        self.internalChroma = cam.chroma
        self.internalTone = tone

    hue = property(get_hue, set_hue)
    chroma = property(get_chroma, set_chroma)
    tone = property(get_tone, set_tone)
