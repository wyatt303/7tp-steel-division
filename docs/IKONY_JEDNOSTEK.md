# Ikony jednostek w interfejsie gry

Jednostki 7TP w `Mod_Wrzesien1939` są sklonowane z Cromwella V i Stuarta M3A3, więc na początku miały ich obrazki: niebieską sylwetkę Cromwella nad czołgiem i obrazki działa Stuarta oraz karabinu M1919 w panelu jednostki. Nasze własne obrazki podmieniają to.

## Gdzie gra trzyma te obrazki

| Obrazek | Pole w NDF | Oryginał w grze | Rozmiar i wygląd |
|---|---|---|---|
| Znaczek nad jednostką i ikona w menu | `RTSTexture`, `MenuIconForInterface` w `UniteDescriptor.ndf` i `UniteCadavreDescriptor.ndf` | `LabelIcons\RTS\Cromwell_V_H.png` | 42 × 26 px, biała sylwetka z czarnym obrysem, przodem w lewo. Gra barwi ją kolorem gracza. |
| Widok z góry | `TopViewForInterface` | `LabelIcons\TopViews\Cromwell_V_POL.png` | 100 × 75 px, kolorowy, przodem w prawo |
| Obrazek broni w panelu | `InterfaceWeaponTexture` w amunicji (`Ammunition.ndf`) | `UnitsIcons\Armes\Panel_Info\Canon_M6_37mmL_Stuart.png`, `M1919_7_62mm.png` | 132 × 50 px, kolorowy, wylot lufy w prawo |

Oryginały są w paczce `pc\texture\pack\vfxbank_gfxeverything.ppk` (archiwum EDat w `ZZ_4.dat`) jako nieskompresowane `A8R8G8B8` w plikach `.tgv`. Rozmiary i styl wzięto z nich. Samych obrazków gry nie kopiujemy.

## Jak powstają nasze obrazki

1. `scripts/make_unit_icons.py` (Blender) renderuje je z naszych modeli: sylwetki i widoki z góry obu 7TP, wieżę jednowieżowego z armatą Bofors oraz prosty ckm wz. 30 zbudowany w skrypcie.
2. `scripts/patch_unit_icons.py` kopiuje je do `AssetsModding` moda i dopisuje tekstury `TUIResourceTexture_CommonModded`:
   - sylwetki i widoki z góry do `LabelDescripors.ndf`,
   - obrazki broni do `UI\Resources\Textures\Generated\WeaponTextures.ndf`.

   Potem podmienia odwołania tylko we wpisach 7TP i ich amunicji. Przed zmianą kopiuje każdy plik do folderu kopii.
3. Potem trzeba uruchomić `.\GenerateMod.bat`.

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$python = 'C:\Program Files\Blender Foundation\Blender 5.3\5.3\python\bin\python.exe'
$mod = 'C:\Program Files (x86)\Steam\steamapps\common\Steel Division\Mods\Mod_Wrzesien1939'
& $blender --background --factory-startup --python scripts\make_unit_icons.py -- . build\unit_icons
& $python -I scripts\patch_unit_icons.py $mod build\unit_icons build\mod_backup\ikony
```

Jednostki i amunicja szukają tekstur w `$/GFX/Everything`, ale nie widzą tych samych plików:

- **Jednostki** widzą `LabelDescripors.ndf`, a nowych wpisów w plikach tekstur interfejsu nie widzą (uwaga z `create_battlegroup.py`).
- **Amunicja** odwrotnie: nie widzi `LabelDescripors.ndf`. ModGen zgłosił wtedy błąd `object not found: $/GFX/Everything/Texture_Interface_Weapon_TP7_...`. Widzi natomiast nowe wpisy w `WeaponTextures.ndf`.

Z tymi ustawieniami `GenerateMod.bat` przechodzi bez błędów (26 listopada 2026 r.).

Pole `NATOTextureName = "Cromwell_V"` zostaje bez zmian. To nazwa, a nie obrazek.
