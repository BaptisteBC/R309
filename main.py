def divEntier(x: int, y: int) -> int:
    if x < y:
        return 0
    else:
        x = x - y
        return divEntier(x, y) + 1


if __name__ == '__main__':
    flag = False
    while not flag:
        try:
            a = int(input("Saisir a: "))
        except ValueError:
            print("a n'est pas un entier")
        else:
            flag = True
    flag = False
    while not flag:
        try:
            b = int(input("Saisir b: "))
            div = divEntier(a, b)
        except ValueError:
            print("b n'est pas un entier")
        except RecursionError:
            print("b doit être différent de 0")
        else:
            flag = True

    print(f"Résultat : {div}")