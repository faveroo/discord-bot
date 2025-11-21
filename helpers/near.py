def near(a, b, target):
    if abs(a - target) < abs(b - target):
        return a
    else:
        return b