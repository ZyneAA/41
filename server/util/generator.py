import random
import string

def generate_char(c=string.printable):
    return random.choice(c)

