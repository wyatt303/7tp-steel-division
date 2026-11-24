# Tankietki TK-3 i TKS

## Warianty

| | TK-3 | TKS |
|---|---|---|
| Folder | `models/TK3` | `models/TKS` |
| Nadbudówka | kanciasta, pionowe ściany, skrzynkowa osłona ckm | wielościenna, skośne ściany, jarzmo kuliste, peryskop |
| Uzbrojenie na modelu | ckm Hotchkiss wz. 25 | ckm Hotchkiss wz. 25 |
| Trójkąty High / Mid / Low | 5408 / 1572 / 492 | 5512 / 1636 / 496 |

Tekstury, kamuflaż z 1936 r. i gąsienice powstają tak samo jak w 7TP. Mapy w High mają 2048 px, w Mid 1024 px, a w Low 256 px.

## Wymiary

| Element | TK-3 | TKS | Pochodzenie |
|---|---:|---:|---|
| Długość całkowita | 2,58 m | 2,58 m | dane techniczne (w modelu 2,60–2,63) |
| Szerokość | 1,78 m | 1,796 m | dane techniczne (w modelu 1,80) |
| Wysokość | 1,32 m | 1,326 m | dane techniczne |
| Prześwit | 0,30 m | 0,325 m | dane techniczne |
| Szerokość gąsienicy | 140 mm | 170 mm | dane techniczne |
| Rozstaw gąsienic | 1,475 m | 1,45 m | dane techniczne |
| Koło napędowe (przód) | Ø 0,38 m | Ø 0,38 m | **szacunek z planszy** |
| Koło napinające (tył) | Ø 0,34 m | Ø 0,34 m | **szacunek z planszy** |
| Koła jezdne | 4 × Ø 0,22 m | 4 × Ø 0,22 m | **szacunek z planszy** |

W TK-3 tłumik wystaje nad dach, więc model ma 1,355 m wysokości, zgodnie z planszą.

## Założenia i niepewności

- Wymiary podwozia i nadbudówki odczytano z kolorowych plansz bocznych, w skali około 2,6 mm na piksel. Szerokości pochodzą z rysunków z góry.
- Koło napędowe jest z przodu, tak jak na planszach i zdjęciu. Niebieski rysunek z Biura Konstrukcyjnego pokazuje odwrotny układ, prawdopodobnie prototypu, więc go pominięto.
- Karabin jest po prawej stronie (dowódca), w `X = +0,40 m`. To szacunek z rysunków z góry.
- Karabin to `Tourelle_01`, `Axe_Canon_01` i `Canon_01`. Zakres obrotu i podniesienia ustala plik jednostki. Sloty 2–4 to ukryte atrapy.
- Belka zawieszenia, resor i wózki są częścią kadłuba, więc się nie uginają. Tak samo jest w 7TP.
- Modele nie mają własnych wpisów jednostek, broni ani ikon. W grze nie były jeszcze sprawdzane.

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_VARIANT = 'tks'   # albo 'tk3'
$out = 'build\tks'
& $blender --background --factory-startup --python scripts\build_tk.py -- $out
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```

Wymiary są w `scripts/spec_tk.py`. Wynik to `TKS.blend`, `TKS_MID.blend`, `TKS_LOW.blend` z plikami `.fbx` i folderem `textures`.
