# Samochód pancerny wz. 34

## Warianty

| | Z ckm | Z armatką |
|---|---|---|
| Folder | `models/WZ34_CKM` | `models/WZ34_37` |
| Uzbrojenie | ckm Hotchkiss wz. 25 w jarzmie kulistym wz. 35 | armata Puteaux SA 18 37 mm w jarzmie prostokątnym |

Liczby trójkątów są w tabeli „Stan” na końcu dokumentu. Tekstury, kamuflaż i nity powstają tak jak dla tankietek, w rozdzielczościach 2048, 1024 i 256 px.

## Budowa jak w modelach z gry

Układ węzłów skopiowano z samochodów pancernych Eugen: SdKfz 221 (`GER/Vehicule.zip`) i Humber Mk III (`CAN/Vehicule.zip`).

| Węzeł | Rola |
|---|---|
| `Chassis` | kadłub z maską, błotnikami, kołem zapasowym i podwoziem |
| `Tourelle_01` → `Axe_Canon_01` → `Canon_01` | wieża, jarzmo i lufa |
| `Tourelle_02`–`04` | ukryte atrapy, jak w czołgach |
| `Roue_Droite_01`, `Roue_Gauche_01` | przednie koła skrętne, bez rodzica, oś w środku koła |
| `Roue_02` | cała tylna oś (cztery opony) jako jedna siatka, oś w środku osi |
| `FX_Fumee_Roue_D1/G1` | kurz spod tylnych kół, bez rodzica |
| `Fx_Stress_01/02` | punkty trafień |

Pojazdy kołowe nie mają gąsienic, `Fake` ani `Roue_Elev`. Wtyczka zgłasza wtedy brak gąsienic jako ostrzeżenie, a eksport się udaje.

## Wymiary

| Element | Wartość | Pochodzenie |
|---|---:|---|
| Długość | 3,62 m (model 3,67 m z hakiem i błotnikami) | polska Wikipedia |
| Szerokość | 1,91 m | polska Wikipedia |
| Wysokość | 2,20 m (model 2,26 m z relingiem na proporczyki) | polska Wikipedia |
| Rozstaw osi | 2,57 m | polska Wikipedia, zgodny z planszą |
| Prześwit | 0,25 m | polska Wikipedia |
| Opony | 30 × 5 cali, Ø 0,75 m, z tyłu bliźniacze | polska Wikipedia |
| Rozstaw kół przednich | 1,34 m | **szacunek ze zdjęcia z przodu** |

Kadłub, wieżę i błotniki zmierzono na kolorowej planszy bocznej „Samochód pancerny wz. 1934” w skali 3,894 mm na piksel. Szerokości oszacowano ze zdjęć z przodu i z tyłu na tablicy szkoleniowej.

## Założenia i niepewności

- Koło zapasowe jest na prawej burcie, jak podaje Wikipedia. Replika na zdjęciach z Wikimedia ma je po lewej.
- Wieżę uproszczono do ściętego ostrosłupa o ośmiu ścianach z sześciokątną kopułką. Kopułka ma dwie pokrywy i reling na proporczyki.
- Szczegóły podwozia (osie, resory, wał) są uproszczone.
- Modele nie mają jeszcze wpisów jednostek i w grze nie były sprawdzane.

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_SPEC = 'spec_wz34'
$env:AC_VARIANT = 'ckm'   # albo '37'
$out = 'build\wz34_ckm'
& $blender --background --factory-startup --python scripts\build_wz34.py -- $out
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```

Skrypty `texture_tk.py` i `finalize_tk.py` obsługują teraz różne pojazdy, a wybór odbywa się przez zmienną `TK_SPEC`.

## Źródła

- [Samochód pancerny wz. 34, polska Wikipedia](https://pl.wikipedia.org/wiki/Samoch%C3%B3d_pancerny_wz._34)
- Plansze i tablica szkoleniowa dostarczone przez autora. Skany nie są częścią repozytorium.
- Zdjęcia repliki z Wikimedia Commons, do porównania.

## Stan

| | Z ckm | Z armatką | SdKfz 221 (Eugen) |
|---|---:|---:|---:|
| Trójkąty High | 5584 | 5324 | 6607 |
| Trójkąty Mid | 2108 | 2088 | 1695 |
| Trójkąty Low | 460 | 452 | 639 |

Wszystkie sześć plików przechodzi eksport wtyczką. Wtyczka zgłasza tylko brak gąsienic, co jest oczekiwane.
