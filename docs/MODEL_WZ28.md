# Samochód pancerny wz. 28

Półgąsienicowy samochód pancerny na podwoziu Citroën-Kégresse B2 10CV, w wersji późnej z obrotową wieżą.

## Warianty

| | Z ckm | Z armatką |
|---|---|---|
| Folder | `models/WZ28_CKM` | `models/WZ28_37` |
| Uzbrojenie | ckm Hotchkiss wz. 25 w jarzmie kulistym | armata Puteaux SA 18 37 mm w jarzmie prostokątnym |

## Budowa jak w modelach z gry

Układ węzłów skopiowano z półgąsienicowego SdKfz 250 od Eugen (`GER/Vehicule.zip`):

| Węzeł | Rola |
|---|---|
| `Chassis`, `Tourelle_01` → `Axe_Canon_01` → `Canon_01` | kadłub, wieża i uzbrojenie, sloty 2–4 jako ukryte atrapy |
| `Chenille_Droite_01`, `Chenille_Gauche_01`, `Fake` | gumowe gąsienice Kégresse'a ze skinem jak w czołgach |
| `Roue_D1…D6`, `Roue_G1…G6` pod `Roue_Elev_*` | 1 przedni bęben, 2–5 koła jezdne, 6 tylne koło napędowe |
| `Roue_Droite_01`, `Roue_Gauche_01` | przednie koła skrętne, bez rodzica |
| `FX_Fumee_Chenille_D1/G1`, `Fx_Stress_01/02`, `Remorque_1` | efekty i hak holowniczy |

## Wymiary

| Element | Wartość | Pochodzenie |
|---|---:|---|
| Długość | 3,50 m | polska Wikipedia |
| Szerokość | 1,40 m (model 1,42 m) | polska Wikipedia |
| Wysokość | 2,10 m (model 2,15 m z pokrywami kopułki) | polska Wikipedia |
| Prześwit | 0,28 m | polska Wikipedia |
| Rozstaw kół przednich | 1,24 m | rysunek z góry |
| Rozstaw gąsienic / szerokość | 1,22 m / 164 mm | rysunek z góry |
| Koła przednie | Ø 0,74 m | rysunek z boku |

Bryłę zmierzono na rysunku M. C. Bella w skali 1:76, przy 4,09 mm na piksel powiększonego wycinka. Przy tej skali długość z danych daje wysokość 2,13 m.

## Założenia i niepewności

- Model przedstawia późną wersję z rysunku: wieża ośmioboczna, bez błotników przednich, ze skrzynkami po bokach maski.
- Koło napędowe gąsienicy jest z tyłu, a przedni bęben jest gładki. Takie oznaczenie wynika z rysunku.
- Zawieszenie gąsienicy (rama wózka, sprężyny) jest uproszczone i nie ugina się.
- Wikipedia podaje, że armatę 37 mm miała mniej więcej co trzecia sztuka.
- Modele nie mają jeszcze wpisów jednostek i w grze nie były sprawdzane.

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_SPEC = 'spec_wz28'
$env:AC_VARIANT = 'ckm'   # albo '37'
$out = 'build\wz28_ckm'
& $blender --background --factory-startup --python scripts\build_wz28.py -- $out
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```

## Źródła

- M. C. Bell, *Samochod pancerny wz 28, late model*, 1:76, 1981, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Samoch%C3%B3d_Pancerny_wz._28,_Half-Tracked_Armoured_Car_Model_28,_Late_Type.png), licencja CC BY 4.0. Rysunek nie jest częścią repozytorium.
- [Samochód pancerny wz. 28, polska Wikipedia](https://pl.wikipedia.org/wiki/Samoch%C3%B3d_pancerny_wz._28)

## Stan

| | Z ckm | Z armatką | SdKfz 250/1 (Eugen) |
|---|---:|---:|---:|
| Trójkąty High | 5732 | 5516 | 6224 |
| Trójkąty Mid | 1704 | 1684 | — |
| Trójkąty Low | 536 | 528 | — |

Wszystkie sześć plików przechodzi eksport wtyczką bez ostrzeżeń. Gąsienica ma na razie teksturę stalowych ogniw z tankietek, a nie gumowej taśmy.
