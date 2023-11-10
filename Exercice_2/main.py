fich = "U:/Bureau/fich.txt"
if __name__ == '__main__':
    try:
        with open(fich, "r") as f:
            for lecture in f:
                lecture = lecture.rstrip("\n\r")
    except FileNotFoundError:
        print("Le fichier demandé n'existe pas")
    except FileExistsError:
        print("Le fichier que vous essayez de créer existe déjà et ne peut pas être remplacé")
    except PermissionError:
        print("Vous n'avez pas les permission suffisantes pour modifier ce fichier")
    except IOError:
        print("L'opération que vous souhaitez réaliser est impossible")
    else:
        print(lecture)
    finally:
        pass
