# Division euclidienne de deux entiers non nuls
def divEntier(x: int, y: int) -> int:
    if x < 0:
        raise ValueError
    if x < y:
        return 0
    else:
        x = x - y
        return divEntier(x, y) + 1


if __name__ == '__main__':
    try:
        flag = False
        while not flag:
            # Vérification : a doit être un entier
            try:
                a = int(input("Saisir a: "))
            except ValueError:
                print("a n'est pas un entier")
            else:
                flag = True
        flag = False
        while not flag:
            # Vérification : b doit être un entier
            try:
                b = int(input("Saisir b: "))
                div = divEntier(a, b)
            except ValueError:
                print("b n'est pas un entier")
            except RecursionError:
                print("b doit être différent de 0")
            else:
                flag = True
    finally:
        print(div)


