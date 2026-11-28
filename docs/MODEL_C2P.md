# Ciągnik artyleryjski C2P

C2P (1937) to podwozie tankietki TKS wydłużone i obniżone z tyłu. Ma koło napędowe z przodu, cztery koła jezdne w dwóch wózkach na zewnętrznej belce i duże szprychowe koło napinające opuszczone do ziemi. Na podwoziu stoi otwarte, nitowane nadwozie szerokie jak gąsienice. Silnik jest pod walcową osłoną pośrodku, chłodnica w skrzyni z tyłu, z przodu jest szyba, a nad przedziałem dwa pałąki plandeki. Załoga to kierowca i trzech artylerzystów. W 1939 r. C2P ciągnął głównie armaty przeciwlotnicze 40 mm wz. 36.

| | |
|---|---|
| Folder | `models/C2P` |
| Wymiary | `scripts/spec_c2p.py` |
| Budowa | `scripts/build_c2p.py` (podwozie, gąsienice i koła z `build_tk.py`), potem `texture_tk.py` i `finalize_tk.py` |
| Trójkąty High / Mid / Low | 9376 / 1840 / 604 |
| Wymiary modelu | 2,89 × 1,86 × 1,59 m (High, z uchwytami na burtach) |

## Źródła i wymiary

- Dane techniczne: 2,85 × 1,82 × 1,65 m, do 45 km/h.
- Kolorowa plansza boczna (470 px na całą długość, ok. 6,2 mm na piksel): położenia kół, wysokości burt, osłony silnika, skrzyni chłodnicy i pałąków.
- Arkusz modelu kartonowego (widoki z boku, z góry, z przodu i z tyłu): układ przedziału, siedzenia, kierownica, szyba.
- Zdjęcie z epoki z plandeką i zdjęcie repliki z muzeum: szyba z dwiema taflami, walcowa osłona silnika, kratka chłodnicy.

| Element | Model | Pochodzenie |
|---|---:|---|
| Długość / szerokość | 2,85 / 1,82 m | dane techniczne |
| Burty | 0,50–0,79 m nad ziemią | plansza |
| Szczyt pałąków | 1,57 m | plansza |
| Koło napędowe | Ø 0,38 m, środek 1,10 m przed środkiem pojazdu | plansza, jak w TKS |
| Koła jezdne | 4 × Ø 0,22 m | jak w TKS |
| Koło napinające | Ø 0,43 m, na ziemi | plansza |
| Rozstaw gąsienic | 1,45 m | jak w TKS |

Wymiary odczytane z planszy to szacunki.

## Węzły

Nazwy jak w Loyd Carrierze z gry, na którym oparta jest jednostka: `Chassis`, `Chenille_Droite_01`, `Chenille_Gauche_01`, koła `Roue_D1`–`D6` i `Roue_G1`–`G6` na pomocnikach `Roue_Elev_*`, `Fake`, `Driver` (miejsce kierowcy, lewe przednie siedzenie) i hak `Remorque_1` na tylnej płycie. Model nie ma broni, więc `finalize_tk.py` nie dodaje mu atrap uzbrojenia.

Szyba to dwie przezroczyste tafle w ramie, zrobione jak w pojazdach z gry: drugi materiał siatki `Chassis` (zob. [SZYBY.md](SZYBY.md)). Przez nią widać siedzenia i kierownicę.

Wersja High ma dodatkowo opaski i korek na osłonie silnika, kratkę chłodnicy, gaśnicę i trzy karabiny w stojaku, tylną lampę, tablicę, ucha holownicze z przodu, reflektorek na słupku szyby, uchwyty na burtach i łopatę.

## Jednostka w grze (28 listopada 2026 r.)

Wpis `C2P_POL` w `data/units.toml`, układ `truck`.

| Co | Skąd |
|---|---|
| Dane jednostki i wygląd | polski Loyd Carrier z gry (`Carrier_Loyd_POL`): ciągnik bez broni, 3 miejsca, holowanie armat, gąsienice, dźwięk silnika, polski kierowca |
| Prędkość | 22 km/h w terenie (szacunek), 45 km/h po drodze (dane techniczne) |
| Wytrzymałość, pancerz | 6 i `Blindage_1`, jak Loyd |
| Cena | 0, transport wliczony w paczkę |
| Ciągnie | obecnie nic: armatę 40 mm wz. 36 ciągnie Fiat 621L bez plandeki. Żeby wrócić do C2P, ustaw `transporter = "C2P_POL"` przy `B40WZ36_POL` |

Sprawdzony w grze 28 listopada 2026 r. w podglądzie talii jako ciągnik Boforsa 40 mm: model, gąsienice i kierowca wyświetlają się poprawnie. W bitwie jeszcze nie.

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_SPEC = 'spec_c2p'
$out = 'build\c2p'
& $blender --background --factory-startup --python scripts\build_c2p.py -- $out
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```

Pliki `C2P.blend`, `C2P_MID.blend`, `C2P_LOW.blend`, pliki `.fbx`, tekstury i rendery kopiuje się potem do `models/C2P`.

## Niepewności

- Pancerz: nadwozie z cienkich blach, przyjęto pancerz Loyda.
- Prędkość w terenie to szacunek.
- Plandeki nie ma, są tylko pałąki, jak na kolorowej planszy. Wariant z plandeką, jak na zdjęciu z epoki, można dodać osobno.
