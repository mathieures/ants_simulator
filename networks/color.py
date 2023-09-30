from random import randint


def random_rgb():
    color = "#"
    for _ in range(3):
        c = hex(randint(0, 255))[2:]
        # On rajoute un 0 s'il faut
        color += '0' * (2 - len(c)) + c
    return color