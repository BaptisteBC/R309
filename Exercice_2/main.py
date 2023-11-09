if __name__ == '__main__':
    try:

        with open("U:/Bureau/fich.txt", "r") as f:
            try:
                fichier = f.read()
                print(fichier)

            finally:
                f.close()
    except FileNotFoundError as err:
        print("Le fichier que vous souhaitez lire n'existe pas")
