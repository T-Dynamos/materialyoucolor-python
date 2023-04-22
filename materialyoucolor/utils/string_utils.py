from materialyoucolor.utils.color_utils import redFromArgb, greenFromArgb, blueFromArgb

def hexFromArgb(argb):
    r = redFromArgb(argb)
    g = greenFromArgb(argb)
    b = blueFromArgb(argb)
    outParts = [f"{r:x}", f"{g:x}", f"{b:x}"]
    for i, part in enumerate(outParts):
        if len(part) == 1:
            outParts[i] = "0" + part
    return "#" + "".join(outParts)

def argbFromHex(hex):
    hex = hex.replace("#", "")
    isThree = len(hex) == 3
    isSix = len(hex) == 6
    isEight = len(hex) == 8
    if not isThree and not isSix and not isEight:
        raise Exception("unexpected hex " + hex)
    r = 0
    g = 0
    b = 0
    if isThree:
        r = parseIntHex(hex[0:1] * 2)
        g = parseIntHex(hex[1:2] * 2)
        b = parseIntHex(hex[2:3] * 2)
    elif isSix:
        r = parseIntHex(hex[0:2])
        g = parseIntHex(hex[2:4])
        b = parseIntHex(hex[4:6])
    elif isEight:
        r = parseIntHex(hex[2:4])
        g = parseIntHex(hex[4:6])
        b = parseIntHex(hex[6:8])

    return rshift(
        ((255 << 24) | ((r & 0x0FF) << 16) | ((g & 0x0FF) << 8) | (b & 0x0FF)), 0
    )

def parseIntHex(value):
    return int(value, 16)

def argbFromRgb(r, g, b, a=255) -> int:
    return (a << 24) | (r << 16) | (g << 8) | b


def rgbFromArgb(self, argb):
    return (
        ((argb >> 16) & 0xFF) / 255,
        ((argb >> 8) & 0xFF) / 255,
        (argb & 0xFF) / 255,
        1,
    )

