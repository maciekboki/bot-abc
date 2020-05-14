class ListaDane(object):
    def __init__(self, nazwa_pliku):
        self.dane = []
        self.nazwa_pliku = nazwa_pliku
        plik = open(self.nazwa_pliku, "r")
        self.dane = plik.readlines()
        plik.close()
        self.robListe()

    def robListe(self):
        self.lista = []
        j = len(self.dane)
        k = -j
        warunek = k < 0
        while warunek == True:
            for i in range(1):
                rap=(self.dane[k])
                rap2 = str(rap)
                rap2 = rap2.replace("\n", "")
                self.lista.append(rap2)
            k = k+1
            warunek = k < 0
