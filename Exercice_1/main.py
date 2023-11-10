# Division euclidienne de deux entiers positifs
def divEntier(x: int, y: int) -> int:
    if x < 0 or y < 0:
        raise ZeroDivisionError("Les valeurs entrées doivent être supérieures à zéro")
    if y == 0:
        raise RecursionError("y doit être différent de zéro")
    if x < y:
        return 0
    else:
        x = x - y
        return divEntier(x, y) + 1


if __name__ == '__main__':
    try:
        x = int(input("x = "))
        y = int(input("y = "))
        test = divEntier(x, y)

    except ValueError:
        print("La valeur entrée doit être un entier")
    except RecursionError as err:
        print(err)
    except ZeroDivisionError as err:
        print(err)

    else:
        print(test)
