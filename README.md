# War Breakout

Breakout spēle ar krītošiem kvadrātiem, uzrakstīta ar Pygame. Rezultāti (laiks) tiek sūtīti uz paša rakstītu serveri (FastAPI + SQLite).

## Kā palaist

Vajag Python 3.11 vai jaunāku. Visas komandas izpildi projekta mapē.

### 1. Uzstādīšana (tikai pirmo reizi)

```
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

### 2. Palaid serveri (pirmajā terminālī, atstāj to atvērtu)

```
cd C:\Prakses-spele\game
py -m uvicorn api.main:app --reload
```

### 3. Palaid spēli (otrajā terminālī)

```
cd C:\Prakses-spele\game
py -m client.main
```

Serverim jābūt ieslēgtam, lai varētu pieteikties un saglabāt rezultātu. Datubāzes fails `game.db` izveidojas pats.

## Kā spēlēt

Nospied **Start Game**, ievadi vārdu un paroli un spied **Register** (pirmo reizi) vai **Log in**. Kad pabeidz visus 3 līmeņus, kopējais laiks automātiski aiziet uz serveri. Ātrākais laiks ir augšā līderu tabulā.

| Taustiņš | Darbība |
|---|---|
| ← → | Pārvieto platformu |
| Space | Palaiž bumbiņu (sāk taimeri) |
| Pele | Izvēlnes pogas |

## Noteikumi

- Iznīcini visus kubus ar bumbiņu, pirms tie sasniedz platformu. Jauna kubu rinda parādās ik pēc 8 sekundēm.
- Ir 3 līmeņi. Taimeris sākas pirmajā bumbiņas palaišanā un skrien cauri visiem līmeņiem.

| Kubs | Dzīvības | Piezīme |
|---|---|---|
| 1, 2, 3 | 1, 2, 3 | parasts kritiena ātrums |
| S (zelts) | 5 | kad iznīcināts, nomet kapsulu |
| B (liels, violets) | 20 | krīt ātrāk, aizņem 2x2 lauciņus |

Ja noķer kapsulu ar platformu, parādās palīgs (ne vairāk kā 10 vienlaikus):

| Palīgs | Iespēja | Šāvieni |
|---|---|---|
| Kājnieks | 75% | reizi sekundē, 0,5 bojājumi |
| Tanks | 25% | reizi 5 sekundēs, 8 bojājumi |