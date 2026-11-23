# Przebudowa modelu ze skryptów

Modele powstają proceduralnie, więc wymiary można zmienić w [`scripts/spec_7tp.py`](../scripts/spec_7tp.py) i zbudować wszystko od nowa.

| Skrypt | Rola |
|---|---|
| `spec_7tp.py` | wymiary i układ obu wariantów |
| `build_7tp.py` | geometria High, Mid, Low |
| `texture_7tp.py` | UV, kamuflaż, nity, cienie, mapy i rendery |
| `finalize_7tp.py` | węzły wymagane przez grę i końcowe nazwy plików |
| `preview_ndf.py` | podgląd gotowego `.Ase2NdfBin` |

## Kolejność

Przykład dla wersji jednowieżowej, uruchamiany z głównego folderu projektu. Dla dwuwieżowej ustaw `TP_VARIANT` na `dw`, a nazwę na `TP7_DW`.

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TP_VARIANT = 'jw'
$out = 'build\jw'
& $blender --background --factory-startup --python scripts\build_7tp.py -- $out
& $blender --background --factory-startup --python scripts\texture_7tp.py -- $out
Rename-Item "$out\Textures" 'textures_tmp'
Rename-Item "$out\textures_tmp" 'textures'
Get-ChildItem "$out\textures" -Filter '7TP*.png' | Rename-Item -NewName { 'TP7_JW' + $_.Name.Substring(3) }
& $blender --background --factory-startup --python scripts\finalize_7tp.py -- $out TP7_JW
```

Wynik pojawi się jako `TP7_JW.blend`, `TP7_JW_MID.blend` i `TP7_JW_LOW.blend`. Pliki pośrednie `7TP_*.blend` można potem usunąć. Eksport do gry wykonuje wtyczka.

Budowanie nie zmienia plików w `models/`, dopóki nie wskażesz tego folderu jako wyjściowego.
