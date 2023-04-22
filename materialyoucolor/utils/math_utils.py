def signum(num):
    if num < 0:
        return -1
    elif num == 0:
        return 0
    else:
        return 1


def lerp(start, stop, amount):
    return (1.0 - amount) * start + amount * stop


def clampInt(min, max, input):
    if input < min:
        return min
    elif input > max:
        return max
    return input


def clampDouble(min, max, input):
    if input < min:
        return min
    elif input > max:
        return max
    return input


def sanitizeDegreesInt(degrees):
    degrees = degrees % 360
    if degrees < 0:
        degrees = degrees + 360
    return degrees


def sanitizeDegreesDouble(degrees):
    degrees = degrees % 360.0
    if degrees < 0:
        degrees = degrees + 360.0
    return degrees


def differenceDegrees(a, b):
    return 180.0 - abs(abs(a - b) - 180.0)


def matrixMultiply(row, matrix):
    a = row[0] * matrix[0][0] + row[1] * matrix[0][1] + row[2] * matrix[0][2]
    b = row[0] * matrix[1][0] + row[1] * matrix[1][1] + row[2] * matrix[1][2]
    c = row[0] * matrix[2][0] + row[1] * matrix[2][1] + row[2] * matrix[2][2]
    return [a, b, c]
