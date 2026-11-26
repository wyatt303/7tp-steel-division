# Własne grafiki interfejsu

Pliki z tego folderu instalator (`zainstaluj_mod.bat`) wstawia do moda zamiast grafik generowanych z renderów. Brakujący plik oznacza, że zostaje grafika wygenerowana. Można więc podmieniać je po jednej.

## Układ

```text
graphic\
├── <MODEL>\             nazwa jak pliki w models\: TP7_JW, TP7_DW, TK3, TKS, WZ34_CKM, PF621L, ...
│   ├── RTS.png          42 × 26   znaczek nad jednostką i ikona w menu
│   ├── TopView.png     100 × 75   widok z góry
│   ├── Button.png      160 × 82   karta w talii i w pasku zakupów
│   └── Visual.png      388 × 224  duży obrazek w oknie jednostki
├── weapons\
│   ├── Bofors37.png    132 × 50   armata Bofors 37 mm
│   └── CkmWz30.png     132 × 50   ckm wz. 30
└── battlegroup\
    ├── Emblem.png      256 × 256  emblemat battlegroupy
    └── Portrait.png    410 × 505  portret dowódcy
```

## Zasady

- Wszystko w PNG z przezroczystością. Nazwy plików dokładnie jak wyżej, bez polskich liter i spacji.
- Rozmiary są takie jak w oryginałach z gry. Inny rozmiar daje tylko ostrzeżenie, bo gra skaluje obrazki, ale proporcje warto zachować.
- `RTS.png`: biała sylwetka z czarnym obrysem, przodem w lewo. Gra barwi ją kolorem gracza.
- `TopView.png`: przodem w prawo. Obrazki broni: wylot lufy w prawo.
- Wzory z gry są w `build\ikony_z_gry\oryginaly_z_gry` (poza repozytorium).
- Nazwa obrazka broni to nazwa broni z `scripts\create_battlegroup.py`. Nowe bronie trzeba dopisać do `WEAPON_FILES` w `scripts\apply_graphics.py`.
- Grafiki modelu, który nie jest jeszcze jednostką w battlegroupie, są pomijane z komunikatem `UNUSED`.

**Repozytorium:** własne rysunki mogą być w Git. Grafik przerobionych z oryginałów gry nie dodawaj do repozytorium.

## Podmiana bez pełnej instalacji

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.3\5.3\python\bin\python.exe' -I scripts\apply_graphics.py D:\Mod\Wrzesien1939 'C:\Program Files (x86)\Steam\steamapps\common\Steel Division\Mods\Mod_Wrzesien1939'
```

Potem uruchom `GenerateMod.bat` w folderze moda albo kliknij „Generuj mod” w edytorze jednostek.
