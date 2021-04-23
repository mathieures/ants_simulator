from random import randint

def random_rgb():
    color = "#"
    for i in range(3):
        color += hex(randint(0, 255))[2:]
    return color