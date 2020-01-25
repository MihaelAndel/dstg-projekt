import heapq


kodovi = {} # Dictionary s odgovarajućim kodovima za svaki znak u tekstu
kodoviObrnuto = {} # Dictionary koji služi za dekodiranje iz kodova u znakove 
putanjaOriginal = r'./datoteke/tekst.txt'  # Putanja do datoteke s originalnim tekstom za kodiranje/dekodiranje
putanjaKompresija = r'./datoteke/kompresija.bin' # Putanja do datoteke s kodiranim tekstom
putanjaDekompresija = r'./datoteke/dekompresija.txt' # Putanja do datoteke s dekodiranim tekstom
frekvencijePojavljivanja = {} # Dictionary s frekvencijama pojavljivanja svakog znaka u tekstu
cvorovi = [] # Lista svih cvorova u stablu

class Cvor(object):
  lijevoDijete = None
  desnoDijete = None
  znak = None
  vrijednost = 0 # Frekvencija pojavljivanja znaka, odnosno zbroj frekvencija pojavljivanja u roditelju

  def __init__(self, znak, vrijednost):
    self.znak = znak
    self.vrijednost = vrijednost

  # Metode za usporedbu cvorova
  def __gt__(self, c):
    return self.vrijednost > c.vrijednost

  def __lt__(self, c):
    return self.vrijednost < c.vrijednost


def ucitajTekstIzDatoteke(putanja):
  datoteka = open(putanja, 'r+')
  tekst = datoteka.read()
  tekst = tekst.rstrip()
  datoteka.close()
  return tekst

def zapisiTekstUDatoteku(putanja, tekst):
  datoteka = open(putanja, 'w')
  datoteka.write(tekst)
  datoteka.close()

def popuniFrekvencijePojavljivanja(tekst):
  # Prolazi kroz svaki znak teksta i inkrementira 
  # odgovarajući zapis u dictionaryu
  for znak in tekst:
    if not znak in frekvencijePojavljivanja:
      frekvencijePojavljivanja[znak] = 0
  
    frekvencijePojavljivanja[znak] += 1

def stvoriCvorove():
  # Puni listu cvorova tako da lista predstavlja hrpu cvorova
  for znak in frekvencijePojavljivanja:
    cvor = Cvor(znak, frekvencijePojavljivanja[znak])
    heapq.heappush(cvorovi, cvor)
  
def spojiCvorove():
  # Rekurzivna funkcija koja "spaja" cvorove,
  # odnosno konstruira stablo na temelju liste cvorova
  while len(cvorovi) > 1:
    lijevi = heapq.heappop(cvorovi)
    desni = heapq.heappop(cvorovi)

    roditelj = Cvor(None, lijevi.vrijednost + desni.vrijednost)
    roditelj.desnoDijete = desni
    roditelj.lijevoDijete = lijevi

    heapq.heappush(cvorovi, roditelj)

def izradiKodove(s, cvor):
  # Rekurzivna funkcija koja puni dictionary
  # s kodovima za svaki znak u tekstu

  if cvor.znak: # Ako je cvor list (ima znak vezan uz sebe)
    if not s:
      kodovi[cvor.znak] = '0'
    else:
      # Dodijeli cvoru njegov Huffman kod
      kodovi[cvor.znak] = s
      kodoviObrnuto[s] = cvor.znak
  else:
    izradiKodove(s + '0', cvor.lijevoDijete)
    izradiKodove(s + '1', cvor.desnoDijete)

def kodirajTekst(tekst):
  # Funkcija koja generira string kodiranih
  # znakova originalnog teksta
  kodiraniTekst = ''

  for znak in tekst:
    kodiraniTekst += kodovi[znak]
  
  return kodiraniTekst

def dodajPadding(tekst):
  # Dodaje padding i formatira string
  # s kodovima znakova kako bi se korektno
  # mogli zapisatu u binarnom obliku u datoteku
  paddingExtra = 8 - len(tekst) % 8
  for i in range(paddingExtra):
    tekst += '0'

  paddingInfo = "{0:08b}".format(paddingExtra)
  tekst = paddingInfo + tekst
  return tekst

def stvoriKodiraneBajtove(kodiraniTekst):
  # Prima kodirani tekst s paddingom i pretvara
  # ga u niz bajtova
  bajtovi = bytearray()

  for i in range(0, len(kodiraniTekst), 8):
    bajt = kodiraniTekst[i:i + 8]
    bajtovi.append(int(bajt, 2))

  return bajtovi

def zapisiKodiraneBajtove(putanja, bajtovi):
  output = open(putanja, 'wb')
  output.write(bytes(bajtovi))
  output.close()

def ucitajKodiraneBajtove():
  komprimiranaDatoteka = open(putanjaKompresija, 'rb')
  bitovi = ''

  bajt = komprimiranaDatoteka.read(1)
  while (bajt != b''):
    # Radi toliko dugo dok ne dođe do kraja datoteke,
    # odnosno dok ne pročita bitove za prazan string
    bajt = ord(bajt)
    bits = bin(bajt)[2:].rjust(8, '0')
    bitovi += bits # Dodaje pročitane bitove u string koji se kasnije dekodira
    bajt = komprimiranaDatoteka.read(1)

  komprimiranaDatoteka.close()
  return bitovi

def makniPadding(tekst):
  # Funkcija miče prije dodan padding iz očitanog niza bitova
  paddingInfo = tekst[:8]
  paddingExtra = int(paddingInfo, 2)

  tekst = tekst[8:]
  kodiraniTekst = tekst[:-1 * paddingExtra]
  
  return kodiraniTekst

def dekodirajTekst():
  kod = ''
  dekodiraniTekst = ''
  for bit in kodiraniTekst:
    # Prolazi znak po znak kroz kodirani tekst. Dok nađe
    # niz koji odgovara nekom kodu u dictionaryu, stavlja odgovarajući
    # znak u string koji predstavlja dekodirani tekst.
    kod += bit
    if (kod in kodoviObrnuto):
      znak = kodoviObrnuto[kod]
      dekodiraniTekst += znak
      kod = ''
  return dekodiraniTekst

#########################################################
#########################################################

tekst = ucitajTekstIzDatoteke(putanjaOriginal)
print('Originalni tekst:', tekst)

popuniFrekvencijePojavljivanja(tekst)
stvoriCvorove()
spojiCvorove()
izradiKodove('', cvorovi[0])

kodiraniTekst = kodirajTekst(tekst)
kodiraniTekst = dodajPadding(kodiraniTekst)

bajtovi = stvoriKodiraneBajtove(kodiraniTekst)
zapisiKodiraneBajtove(putanjaKompresija, bajtovi)

bajtovi = ucitajKodiraneBajtove()
kodiraniTekst = makniPadding(bajtovi)
print('Kodirani tekst:', kodiraniTekst)

input('Pritisnite enter za dekompresiju datoteke...')

dekodiraniTekst = dekodirajTekst()
zapisiTekstUDatoteku(putanjaDekompresija, dekodiraniTekst)
print('Dekodirani tekst:', dekodiraniTekst)