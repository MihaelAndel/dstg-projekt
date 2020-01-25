from itertools import groupby
import heapq

kodovi = {}
kodoviObrnuto = {}
putanjaOriginal = r'./datoteke/tekst.txt'
putanjaKompresija = r'./datoteke/kompresija.bin'
putanjaDekompresija = r'./datoteke/dekompresija.txt'
frekvencijePojavljivanja = {}
cvorovi = []

class Cvor(object):
  lijevoDijete = None
  desnoDijete = None
  znak = None
  vrijednost = 0

  def __init__(self, znak, vrijednost):
    self.znak = znak
    self.vrijednost = vrijednost

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
  for znak in tekst:
    if not znak in frekvencijePojavljivanja:
      frekvencijePojavljivanja[znak] = 0
  
    frekvencijePojavljivanja[znak] += 1

def stvoriCvorove():
  for znak in frekvencijePojavljivanja:
    cvor = Cvor(znak, frekvencijePojavljivanja[znak])
    heapq.heappush(cvorovi, cvor)
  
def spojiCvorove(): 
  while len(cvorovi) > 1:
    lijevi = heapq.heappop(cvorovi)
    desni = heapq.heappop(cvorovi)

    roditelj = Cvor(None, lijevi.vrijednost + desni.vrijednost)
    roditelj.desnoDijete = desni
    roditelj.lijevoDijete = lijevi

    heapq.heappush(cvorovi, roditelj)

def izradiKodove(s, cvor):
  if cvor.znak:
    if not s:
      kodovi[cvor.znak] = '0'
    else:
      kodovi[cvor.znak] = s
      kodoviObrnuto[s] = cvor.znak
  else:
    izradiKodove(s + '0', cvor.lijevoDijete)
    izradiKodove(s + '1', cvor.desnoDijete)

def kodirajTekst(tekst):
  kodiraniTekst = ''

  for znak in tekst:
    kodiraniTekst += kodovi[znak]
  
  return kodiraniTekst

def dodajPadding(tekst):
  paddingExtra = 8 - len(tekst) % 8
  for i in range(paddingExtra):
    tekst += '0'

  paddingInfo = "{0:08b}".format(paddingExtra)
  tekst = paddingInfo + tekst
  return tekst

def stvoriKodiraneBajtove(kodiraniTekst):
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
    bajt = ord(bajt)
    bits = bin(bajt)[2:].rjust(8, '0')
    bitovi += bits
    bajt = komprimiranaDatoteka.read(1)

  komprimiranaDatoteka.close()
  return bitovi

def makniPadding(tekst):
  paddingInfo = tekst[:8]
  paddingExtra = int(paddingInfo, 2)

  tekst = tekst[8:]
  kodiraniTekst = tekst[:-1 * paddingExtra]
  
  return kodiraniTekst

def dekodirajTekst():
  kod = ''
  dekodiraniTekst = ''
  for bit in kodiraniTekst:
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