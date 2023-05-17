def signum(num: float) -> float:
    if num < 0:
        return -1.0
    elif num == 0:
        return 0.0
    else:
        return 1.0


def lerp(start: float, stop: float, amount: float) -> float:
    return (1.0 - amount) * start + amount * stop


def clamp_int(min_val: float, max_val: float, input_val: float) -> float:
    if input_val < min_val:
        return min_val
    elif input_val > max_val:
        return max_val
    return input_val


def clamp_double(min_val: float, max_val: float, input_val: float) -> float:
    if input_val < min_val:
        return min_val
    elif input_val > max_val:
        return max_val
    return input_val


def sanitize_degrees_int(degrees: float) -> float:
    degrees = degrees % 360.0
    if degrees < 0:
        degrees += 360.0
    return degrees


def sanitize_degrees_double(degrees: float) -> float:
    degrees = degrees % 360.0
    if degrees < 0:
        degrees += 360.0
    return degrees


def rotation_direction(from_angle: float, to_angle: float) -> float:
    increasing_difference = sanitize_degrees_double(to_angle - from_angle)
    return 1.0 if increasing_difference <= 180.0 else -1.0


def difference_degrees(a: float, b: float) -> float:
    return 180.0 - abs(abs(a - b) - 180.0)


def matrix_multiply(row: list[float], matrix: list[list[float]]) -> list[float]:
    a = row[0] * matrix[0][0] + row[1] * matrix[0][1] + row[2] * matrix[0][2]
    b = row[0] * matrix[1][0] + row[1] * matrix[1][1] + row[2] * matrix[1][2]
    c = row[0] * matrix[2][0] + row[1] * matrix[2][1] + row[2] * matrix[2][2]
    return [a, b, c]
