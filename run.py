#-*- coding: utf-8 -*-

from urllib.request import urlopen
from listadane import ListaDane
import urllib.parse
import re

'''
Tutaj wczytujemy frazy z pliku 'frazy.txt' i z tych fraz tworzymy zapytanie do wyszukiwarki w postaci adresu https://...
polskie ogonki nie mogą występować w adresach więc musimy je przekonwertować do postaci w jakiej mogą być w adresie czyli zrobić URL encoding
we frazach zamieniamy spację na jakiś ciąg, w naszym przypadku "XhhX" (tak sobie wymyśliłem :) może być dowolny inny aby był tylko na tyle dziwny by nie występował "naturalnie")
gdyż potem musimy ten ciąg znaków zamienić z powrotem na "+" a nie chcemy samej spacji poddawać URL encodingowi
a polskie ogonki konwertujemy funkcją wbudowana w Pythona --> urllib.parse.quote("coś")
'''

wczytaj = ListaDane("frazy.txt") #ListaDane to moja funkcja, która z wczytanych fraz stworzy nam ładną listę, moduł jest w pliku listadane.py, nie wymaga modyfikacji
frazy = wczytaj.lista #utworzenie listy fraz
frazy_po = []
adresy = []

#ten for zamienia nam ewentualną spację we frazach na "XhhX", zmienne i,j są tymczasowe, nowe frazy lądują w liście frazy_po
for i in frazy:
    j = i.replace(" ", "XhhX")
    frazy_po.append(j)

#ten for tworzy nam już ładne adresy którymi będziemy odpytywać portal, gotowe adresy lądują w liście o nazwie 'adresy' należy pamiętać że kolejność dodania do listy ma znaczenie
#w tej kolejności potem będzie tworzony raport czyli w tym przypadku kolejność to: portal, zywienie, uroda
for i in frazy_po:
    j = urllib.parse.quote(i)
    j = j.replace("XhhX", '+')
    portal = "https://portal.abczdrowie.pl/szukaj?q=" + j + "&type=article"
    zywienie = "https://zywienie.abczdrowie.pl/szukaj?q=" + j + "&type=article"
    uroda = "https://uroda.abczdrowie.pl/szukaj?q=" + j + "&type=article"
    adresy.append(portal)
    adresy.append(zywienie)
    adresy.append(uroda)

################# Koniec tworzenia adresów #################

def odpytaj_portal(adresik):
    '''
    Funkcja odpytuje portal, którego adres podajemy w argumencie funkcji ('adresik').
    W sekcji try: pobieramy HTML strony z którego usuwamy wszystkie znaki końca linii i formatowania dzięki czemu uzyskujemy HTML w jednej linijce :)
    jest to ważne gdyż wtedy przeszukiwany HTML daje się ładnie 'obrabiać' wyrażeniami regularnymi (re) w celu poszukiwania fraz pomiędzy znacznikami HTML i nie tylko
    funkcja zwraca wartość '0' w przypadku gdy wyszukiwarka portalu nie zwróci żadnego wyniku czyli: 'PODANA FRAZA - 'coś' - NIE ZOSTAŁA ZNALEZIONA'
    funkcja zwraca wartość '1' w przypadku gdy wyszukiwarka portalu zwróci wynik w postaci szukanej frazy
    jeżeli szukana fraza składa się z większej ilości fraz niż 1 i nie wszystkie frazy wystąpią w tytułach wyniku funkcja oblicza ilość wystąpień i zwraca wynik w postaci np "2/4'
    co oznacza że znaleziono tylko 2 pasujące frazy na 4 szukane.
    Do przeszukiwania HTML wykorzystujemy wyrażenie regularne w postaci: re.findall(r'<początek>(.*?)<koniec>', input_data)
    należy zwrócić uwagę że nie muszą to być pełne znaczniki HTML, to ma być po prostu jakiś string, który będzie punktem startowym a kolejny string będzie punktem końcowym
    jeżeli te ciągi znaków występują w kodzie HTML funkcja 're' zwróci wszystko w postaci stringa co znajduję się pomiędzy tymi 2 stringami.
    wyniki_szukajki to lista do której dodajemy tytuły jakie wyszukiwarka odnalazła podczas szukania danej frazy,
    następnie uzyskaną listę przeszukujemy na ilość wystąpienia szukanych fraz które funkcja zlicza i zwraca wynik.
    W sekcji except mamy obsługę błędów, gdyby np. strona nie odpowiadała lub adres był zły, zostanie stworzony wyjątek który zapisze się w raporcie.
    '''
    try:
        input_data = urlopen(adresik).read().decode('utf-8').replace('\n', '').replace('\r', '')
        
        if 'A ZNALEZIONA' in input_data:
            return '0'
        else:
            fraza = ""
            wynik_fraza = []
            wyniki_szukajki = []
            for i in re.findall(r'<h3 class="results__unit__h3">                                        (.*?)                                    </h3>', input_data):
                a = i.lower()
                a = a.split(" ")
                for i in a:
                    wyniki_szukajki.append(i)
            for i in re.findall(r'<input type="search" class="search-results__input" data-event="search-input" name="q" value="(.*?)" autocomplete="off"', input_data):
                fraza = i.lower()
            wynik_fraza = fraza.split(" ")
            zdanie_wyniki_szukajki = " ".join(wyniki_szukajki)
            licznik_prawdy = 0
            for i in wynik_fraza:
                if i in zdanie_wyniki_szukajki:
                    licznik_prawdy = licznik_prawdy + 1
                else:
                    pass
            if licznik_prawdy == len(wynik_fraza):
                return '1'
            else:
                return str(licznik_prawdy) + "/" + str(len(wynik_fraza))

    except urllib.error.HTTPError as err:
        err = f"Jakis blad na stronie {adresik}"
        return err
    except urllib.error.URLError as err:
        err = f"Jakis blad na stronie {adresik}"
        return err


rapo = open("raport.txt","w") #tworzymy plik raport.txt

while len(adresy) > 0:
    wynik1 = odpytaj_portal(adresy[0])
    wynik2 = odpytaj_portal(adresy[1]) #w tym przypadku przeszukujemy 3 portale na raz więc tworzymy 3 wyniki
    wynik3 = odpytaj_portal(adresy[2])
    raport = str(frazy[0]) + ";" + wynik1 + ";" + wynik2 + ";" + wynik3 + ";" + adresy[0] + ";" + adresy[1] + ";" + adresy[2] + "\n"
    rapo.write(raport)
    del adresy[0:3] #kasujemy 3 adresy z listy 'adresy' (bo odpytujemy od razu po 3 adresy) by zmniejszać listę, która po osiągnięciu wartości 0 zakończy pętle 'while' i cały program
    del frazy[0] #kasujemy frazę aby kolejna mogła być zapisana do raportu
    print(f"Pozostalo {len(frazy)} fraz do odpytania") #print licznika

rapo.close() #zamykamy plik raport.txt