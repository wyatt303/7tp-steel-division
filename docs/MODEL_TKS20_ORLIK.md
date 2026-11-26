# TKS z nkm 20 mm: as „Orlik”

Pierwsza unikatowa jednostka battlegroupy: tankietka TKS przezbrojona w 1939 r. w najcięższy karabin maszynowy (nkm) 20 mm wz. 38 FK-A, jak czołg kpr. pchor. Romana Orlika.

## Model

Folder `models/TKS20`. Kadłub, podwozie i malowanie są takie jak w TKS (`docs/MODEL_TK.md`). Zamiast ckm Hotchkiss w kulistym jarzmie jest nkm 20 mm: gruba tuleja oporowa, długa cienka lufa i hamulec wylotowy. Lufa sięga około 1,06 m przed oś jarzma, poza nos tankietki. Długość wystającej części jest szacunkiem ze zdjęć.

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_VARIANT = 'tks20'
$out = 'build\tks20'
& $blender --background --factory-startup --python scripts\build_tk.py -- $out
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```

Trójkąty High / Mid / Low: 9308 / 1656 / 496.

## Jednostka w grze

Wpis `TKS20_ACE_POL` w `data/units.toml`. Jednostka kopiuje dwa wpisy gry:

| Co | Wzór | Dlaczego |
|---|---|---|
| Dane jednostki, rola, zachowanie | Stuart M3A3 (POL) | rozpoznanie pancerne (`ArmoReco`), gąsienice, nie przewozi piechoty. Universal Carrier z gry jest transporterem, więc się nie nadawał. |
| Broń, efekty strzałów, wygląd w bitwie | Panzer II C (dowódczy) | działko 20 mm KwK 38 z amunicją AP i HE ze wspólnego zapasu |

Jak u asów z gry (Panzer IV H „Kretzschmar”): `IsAce = True` i stałe nazwisko dowódcy `FixedName = 'AceOrlik'`, czyli „Roman Orlik” w napisach. Paczka ma jedną jednostkę na najwyższym poziomie doświadczenia (3, „elita”), jedną kartę, od fazy A, w zakładce rozpoznania.

| Parametr | Wartość | Uwagi |
|---|---|---|
| Cena | 50 | |
| Prędkość | 28 / 65 km/h | szybszy od 7TP (TKS ok. 40 km/h po drodze) |
| Pancerz | 1 / 1 / 1, dach zamknięty | TKS 8–10 mm |
| Wytrzymałość | 5 | Universal Carrier 6, czołgi 8 |
| Maskowanie | 2,5 | jak piechota rozpoznania, najlepiej z pojazdów |
| Optyka | 200 | jak zwiadowcze wersje czołgów |
| nkm 20 mm | AP 5, celność 6 (w ruchu 4), 800 m, 171 strz./min | wzór KwK 38: AP 4. Przebicie podniesione o 1. |
| Zapas | 200 nabojów (10 serii po 20) | **do sprawdzenia w źródłach** |
| Obrót działka | ±12° | jarzmo kuliste w kadłubie; do celu obraca się cała tankietka |

## Grafiki

Generowane z modelu: znaczek nad jednostką (`TKS20_RTS.png`), widok z góry, karta, duży obrazek i obrazek działka (`TKS20_Nkm20_Weapon.png`). Własne wersje wstawia się do `graphic/TKS20/`, a obrazek działka jako `graphic/TKS20/Turret.png`.

**Zdjęcie Orlika:** gra wkleja zdjęcie asa w duży obrazek jednostki. U Barkmanna i Kretzschmara zdjęcie jest częścią pliku `Visual`. Przy Orliku trzeba więc wkleić zdjęcie w `graphic/TKS20/Visual.png` (388 × 224), w prawym dolnym rogu, jak na wzorach w `build/ikony_z_gry/oryginaly_z_gry/asy/`.

## Niesprawdzone

- W grze nic z tego nie było jeszcze widziane.
- Nie wiadomo, czy gra pokaże „Roman Orlik” jako nazwisko dowódcy z naszego tokenu `AceOrlik`. Asy z gry mają tokeny w jej własnych słownikach.
- Zapas amunicji 20 mm i przebicie są przyjęte, a nie wzięte ze źródeł.
