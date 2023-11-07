import sys


def divEntier(x: int, y: int) -> int:
    if y == 0:
        raise ZeroDivisionError
    else:

        if x < y:
            return 0
        else:
            x = x - y
            return divEntier(x, y) + 1


if __name__ == '__main__':
    try:
        a = int(input("a: "))
        b = int(input("b: "))
        div = divEntier(a, b)
    except ValueError:
        print("Valeur de l'argument incorrect")
        while ValueError:
            try:
                a = int(input("a: "))
                b = int(input("b: "))
                div = divEntier(a, b)
            except ValueError:
                pass
            else:
                print(div)

    else:
        print(div)