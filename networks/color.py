from random import randrange

def random_color():
    """Retourne une couleur aléatoire au format '#xxxxxx'"""
    color = "#"
    for _ in range(3):
        current_color = hex(randrange(0, 256))[2:]
        # On rajoute un 0 avant s'il le faut
        color += f"{current_color.rjust(2, '0')}"
    return color