# Instalacja moda Wrzesien1939

Mod `Mod_Wrzesien1939` w całości powstaje z plików tego projektu. Instaluje go jeden skrypt.

## Wymagania

- Steel Division: Normandy 44 w `C:\Program Files (x86)\Steam\steamapps\common\Steel Division`.
- Blender 5.3 w `C:\Program Files\Blender Foundation\Blender 5.3`. Jego Python wystarcza, nic nie trzeba doinstalowywać ani pobierać.
- Gra musi być zamknięta.
- Opcjonalnie `portret_rowecki.png` w głównym folderze projektu (portret dowódcy battlegroupy). Bez niego portretem jest render czołgu.

## Uruchomienie

Dwuklik na `zainstaluj_mod.bat` w głównym folderze projektu albo:

```powershell
powershell -ExecutionPolicy Bypass -File D:\Mod\Wrzesien1939\zainstaluj_mod.ps1
```

Opcje:

| Opcja | Znaczenie |
|---|---|
| `-ModName Nazwa` | inna nazwa moda niż `Mod_Wrzesien1939` |
| `-NoActivate` | nie zmieniaj listy włączonych modów w `Config.ini` |
| `-Yes` | nie pytaj, czy przenieść istniejący mod do kopii |
| `-GameDir`, `-Blender` | inne położenie gry albo Blendera |

`-ExecutionPolicy Bypass` działa tylko dla tego jednego uruchomienia i nie zmienia ustawień systemu.

## Co robi skrypt

1. Sprawdza, czy gra jest zamknięta i czy są gra, Blender i jego Python.
2. Jeśli mod już istnieje, po potwierdzeniu przenosi go w całości do `build\mod_backup\<data>_<nazwa>`.
3. Tworzy nowy mod skryptem gry `CreateNewMod.bat`.
4. Eksportuje modele z `models\` naszą wtyczką (`scripts\export_models.py`), na razie oba 7TP.
5. Dodaje jednostki, broń, paczki i battlegroupę „TOMASZÓW 39” (`scripts\create_battlegroup.py`).
6. Robi karty jednostek, portret i emblemat (`scripts\make_unit_cards.py`) oraz ikony i obrazki broni (`scripts\make_unit_icons.py`, `scripts\patch_unit_icons.py`).
7. Uruchamia `GenerateMod.bat`. To trwa kilka minut.
8. Włącza mod: w `Saved Games\EugenSystems\SteelDivision\mod\Config.ini` ustawia `ActivatedMods = Mod_Wrzesien1939|`. Kopia poprzedniego pliku trafia do `build\mod_backup`. Inne mody zostają wyłączone, bo naraz powinien działać jeden.

Zmiany napisów i cen zrobione wcześniej w edytorze jednostek nie przetrwają ponownej instalacji. Instalator buduje mod od zera z wartości w `scripts\create_battlegroup.py`. Stary mod zostaje w kopii.

## Czego mod jeszcze nie zawiera

Pozostałe modele z `models\` (tankietki, samochody pancerne, samoloty, Sokół, Fiat, armata wz. 36) oraz piechota z 1939 r. nie są jeszcze jednostkami w battlegroupie. Gdy powstaną dla nich wpisy w `create_battlegroup.py`, trzeba je też dopisać do listy `MODELS` w `scripts\export_models.py`.
