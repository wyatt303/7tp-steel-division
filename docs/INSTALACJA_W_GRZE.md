# Instalacja modelu w grze

Modele zastępują na razie istniejące jednostki, więc w grze mają ich nazwę, statystyki i broń.

| Model | Zastępuje | Plik jednostki |
|---|---|---|
| `TP7_JW` | polski Stuart M3A3 | `Stuart_M3A3_POL.ndf` |
| `TP7_DW` | polski dowódczy Stuart M3A3 | `Stuart_M3A3_Command_POL.ndf` |

## 1. Utwórz mod

W folderze `Steel Division\Mods` uruchom:

```powershell
.\CreateNewMod.bat Mod_7TP
```

## 2. Wyeksportuj modele

W Blenderze wyeksportuj wersje High, Mid i Low do folderu:

```text
Mods\Mod_7TP\GameData\Assets\3D\Units\POL\Char\TP7_JW\
```

Pliki muszą nazywać się `TP7_JW.Ase2NdfBin`, `TP7_JW_MID.Ase2NdfBin` i `TP7_JW_LOW.Ase2NdfBin`. Dla wersji dwuwieżowej użyj `TP7_DW`.

## 3. Podepnij model

Otwórz `Mods\Mod_7TP\GameData\Gameplay\Gfx\Units\POL\Char\Stuart_M3A3_POL.ndf` i zmień trzy ścieżki:

```text
'GameData:Assets\3D\Units\POL\Char\TP7_JW\TP7_JW.Ase2NdfBin'
'GameData:Assets\3D\Units\POL\Char\TP7_JW\TP7_JW_MID.Ase2NdfBin'
'GameData:Assets\3D\Units\POL\Char\TP7_JW\TP7_JW_LOW.Ase2NdfBin'
```

W tym samym pliku zmień każde `CivMask/OTAN` na `CivMask/MeshModding`. Dla `TP7_DW` zrób to samo w `Stuart_M3A3_Command_POL.ndf`.

## 4. Wygeneruj mod

W folderze moda uruchom:

```powershell
.\GenerateMod.bat
```

Zapis `.\` jest ważny, gdy w systemie ustawiono `NoDefaultCurrentDirectoryInExePath`.

## 5. Włącz mod

Włącz mod w **Mod Center** i uruchom grę ponownie. Jednocześnie włączaj tylko jeden mod zmieniający te same jednostki.

## Gdy gra się wywala

1. Wyłącz mod w `Zapisane gry\EugenSystems\SteelDivision\mod\Config.ini`, czyszcząc wartość `ActivatedMods`.
2. Zrzut awarii znajdziesz w `%TEMP%\CrashRpt_*\crashdump.dmp`.
3. Najczęstsza przyczyna to gąsienice z UV poza zakresem 0–1. Wtyczka teraz blokuje taki eksport.
