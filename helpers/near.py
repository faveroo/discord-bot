def near(a, b, target):
    if abs(a - target) < abs(b - target):
        return a, b
    else:
        return b, a