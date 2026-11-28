# Import modeli z gry do Blendera

Skrypt `scripts/import_ase2ndfbin.py` wczytuje plik `.Ase2NdfBin` z paczek Steel Division Modding Assets i zapisuje go jako `.blend`. To odwrotność naszej wtyczki eksportu.

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
& $blender --background --factory-startup --python scripts\import_ase2ndfbin.py -- <plik.Ase2NdfBin> <wynik.blend>
```

## Co przenosi

| Z pliku gry | W Blenderze |
|---|---|
| wierzchołki (jednostki gry: X do przodu, Y w lewo, 203 na metr) | metry, przód w +Y, prawo w +X, jak w naszych modelach |
| węzły (`NodeName`, `NodeParent`, `TM_POS`) | obiekty z punktem obrotu w miejscu węzła i tym samym rodzicem |
| trójkąty z UV i normalnymi w narożnikach | siatka z mapą UV `UVMap` i własnymi normalnymi |
| materiał z teksturami | materiał z teksturą koloru i właściwościami `eug_diffuse`, `eug_specular`, `eug_glossiness`, `eug_normal`, `eug_alpha`, których używa eksporter |
| pomocniki | puste obiekty z `eug_helper_class` |

Obroty zapisane w `NodeTM` nie są stosowane, bo wierzchołki są już w układzie całego modelu. Trafiają do właściwości `eug_tm`.

Zaimportowany model można od razu wyeksportować z powrotem naszą wtyczką. Sprawdzono to na Boforsie 40 mm: 6766 trójkątów i 23 węzły, jak w oryginale.

## Zasady

Modele z gry służą jako wzór i podstawa do budowy modeli do moda. Zaimportowane pliki trzymamy w `build/import/`, który nie trafia do repozytorium. Nie publikujemy ich.

## Bofors 40 mm (QF 40 mm Mk I/III), 27 listopada 2026 r.

Źródło: `USA/Canon.zip`, folder `Canon/Bofors_40mm` (z tego modelu korzysta też polski Bofors z gry, `DCA_Bofors_POL`). Wynik jest w `build/import/bofors40`:

| Plik | Trójkąty |
|---|---:|
| `Bofors_40mm.blend` | 6766 |
| `Bofors_40mm_MID.blend` | 1703 |
| `Bofors_40mm_LOW.blend` | 595 |
| `Boites_Bofors_40mm.blend` | miejsca obsługi |

Węzły z siatkami: `Chassis`, `support_canon`, `Pied_avant`, `Pied_arriere`, `Bras_droit`, `Pied_droit`, `Bras_gauche`, `Pied_gauche`, `Tourelle_01`, `Axe_Canon_01`, `Canon_01`, `Roue_G1`, `Roue_D1`, `Roue_D2` i `Roue_G2`. Do tego 8 pomocników. Model ma rozmiar 4,97 × 6,76 × 2,59 m z rozłożonymi wysięgnikami.

Paczka gry ma też 8 animacji tego działa (`Bofors_40mm_Deploy`, `_Fold`, `_Fire`, `_Idle`, `_Move`, `_Move_Back`, `_Turn_Left`, `_Turn_Right`). Zapisują one położenia węzłów bezwzględnie, tak jak animacje M3 37 mm. Model wz. 36 zbudowany na tym Boforsie zachowuje więc jego węzły, ich kolejność i punkty obrotu. Buduje go `scripts/build_bofors40.py`, zob. [MODEL_B40WZ36](MODEL_B40WZ36.md).
