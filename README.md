# Polskie pojazdy pancerne dla Steel Division: Normandy 44

Polskie pojazdy pancerne z 1939 r. wymodelowane w Blenderze: dwa warianty czołgu lekkiego 7TP, tankietki TK-3 i TKS , samochody pancerne wz. 28 i wz. 34, samoloty PZL P.11c, PZL.23B Karaś i PZL.37B Łoś oraz motocykl Sokół 1000 z wózkiem i rkm. Do tego wtyczka eksportująca czołgi do formatu gry `.Ase2NdfBin` **bez 3ds Max**.

| 7TP jednowieżowy (Bofors 37 mm) | 7TP dwuwieżowy (2 × ckm wz. 30) |
|---|---|
| ![7TP jednowieżowy](models/7TP_jednowiezowy_Bofors/renders/render_przod_3_4.png) | ![7TP dwuwieżowy](models/7TP_dwuwiezowy_wz30/renders/render_przod_3_4.png) |

| Tankietka TK-3 (ckm Hotchkiss wz. 25) | Tankietka TKS (ckm Hotchkiss wz. 25) |
|---|---|
| ![TK-3](models/TK3/renders/render_przod_3_4.png) | ![TKS](models/TKS/renders/render_przod_3_4.png) |

| Samochód pancerny wz. 34 (ckm Hotchkiss wz. 25) | Samochód pancerny wz. 34 (armata 37 mm) |
|---|---|
| ![wz. 34 z ckm](models/WZ34_CKM/renders/render_przod_3_4.png) | ![wz. 34 z armatką](models/WZ34_37/renders/render_przod_3_4.png) |

| Samochód pancerny wz. 28 (ckm Hotchkiss wz. 25) | Samochód pancerny wz. 28 (armata 37 mm) |
|---|---|
| ![wz. 28 z ckm](models/WZ28_CKM/renders/render_przod_3_4.png) | ![wz. 28 z armatką](models/WZ28_37/renders/render_przod_3_4.png) |

| PZL P.11c | PZL P.11c z tyłu |
|---|---|
| ![PZL P.11c](models/P11C/renders/render_przod_3_4.png) | ![PZL P.11c z tyłu](models/P11C/renders/render_tyl_3_4.png) |

| Sokół 1000 z wózkiem i rkm | Sokół 1000 z tyłu |
|---|---|
| ![Sokół 1000](models/SOKOL1000/renders/render_przod_3_4.png) | ![Sokół 1000 z tyłu](models/SOKOL1000/renders/render_tyl_3_4.png) |

| PZL.23B Karaś | PZL.37B Łoś |
|---|---|
| ![PZL.23B Karaś](models/PZL23B/renders/render_przod_3_4.png) | ![PZL.37B Łoś](models/PZL37B/renders/render_przod_3_4.png) |

## Co jest w projekcie

| Folder | Zawartość |
|---|---|
| [`models/`](models) | 7TP, TK-3, TKS, wz. 28, wz. 34, P.11c, Karaś, Łoś i Sokół 1000: pliki `.blend` i `.fbx` w wersjach High, Mid, Low, tekstury i rendery |
| [`blender_addon/`](blender_addon) | Wtyczka do Blendera, gotowa paczka w `dist/` |
| [`scripts/`](scripts) | Skrypty budujące model i tekstury |
| [`docs/`](docs) | Dokumentacja |

## Szybki start

1. Zainstaluj wtyczkę z [`blender_addon/dist`](blender_addon/dist), przeciągając plik `.zip` do okna Blendera.
2. Otwórz model, np. `models/7TP_jednowiezowy_Bofors/TP7_JW.blend`.
3. Wybierz **File > Export > Steel Division Tank (.Ase2NdfBin)**.
4. Dodaj plik do moda według instrukcji [Instalacja w grze](docs/INSTALACJA_W_GRZE.md).

## Dokumentacja

- [Wtyczka do Blendera](docs/WTYCZKA.md)
- [Instalacja w grze](docs/INSTALACJA_W_GRZE.md)
- [Model 7TP: wymiary, założenia i ograniczenia](docs/MODEL_7TP.md)
- [Tankietki TK-3 i TKS: wymiary, założenia i ograniczenia](docs/MODEL_TK.md)
- [Samochód pancerny wz. 28](docs/MODEL_WZ28.md)
- [Samochód pancerny wz. 34](docs/MODEL_WZ34.md)
- [Samolot PZL P.11c](docs/MODEL_P11.md)
- [Motocykl Sokół 1000](docs/MODEL_SOKOL.md)
- [Samoloty PZL.23B Karaś i PZL.37B Łoś](docs/MODEL_KARAS_LOS.md)
- [Format Ase2NdfBin](docs/FORMAT_ASE2NDFBIN.md)
- [Przebudowa modelu ze skryptów](docs/BUDOWANIE.md)

## Stan projektu

| Element | Stan |
|---|---|
| Oba modele 7TP w grze, w podglądzie | Sprawdzone |
| Tankietki TK-3 i TKS | Gotowe modele, eksport wtyczką bez błędów, w grze niesprawdzone |
| Samochody pancerne wz. 28 i wz. 34 | Gotowe modele, eksport wtyczką bez błędów, w grze niesprawdzone |
| Samolot PZL P.11c | Gotowy model z plikiem `_train`, eksport wtyczką bez błędów, w grze niesprawdzony |
| Motocykl Sokół 1000 | Gotowy model, eksport wtyczką bez błędów, w grze niesprawdzony |
| Samoloty Karaś i Łoś | Gotowe modele z plikami `_train`, eksport wtyczką bez błędów, w grze niesprawdzone |
| Wersja jednowieżowa w bitwie | Sprawdzona na wcześniejszej wersji modelu |
| Wózki w grze | Sprawdzone wizualnie |
| Osobne jednostki z własną nazwą i statystykami | Jeszcze nie ma, modele zastępują dwa Stuarty M3A3 |
| Ruch wahaczy i resorów | Jeszcze nie ma, są częścią kadłuba |

## Zastrzeżenia

To nieoficjalny projekt fanowski, niezwiązany z Eugen Systems. Repozytorium nie zawiera plików gry ani Modding Assets. Do użycia modeli w grze potrzebna jest własna kopia Steel Division: Normandy 44.

## Licencje

- **Wtyczka** (`blender_addon/`): [GPL-3.0-or-later](blender_addon/LICENSE).
- **Modele, tekstury i rendery** (`models/`): [CC BY-NC 4.0](models/LICENSE). Można je używać, zmieniać i udostępniać w celach niekomercyjnych, z podaniem autora: `wyatt303`, wraz z linkiem do tego repozytorium i informacją o wprowadzonych zmianach.
- **Skrypty i dokumentacja** (`scripts/`, `docs/`, ten plik): wszelkie prawa zastrzeżone. Repozytorium można przeglądać, ale ponowne publikowanie tych plików wymaga zgody autora.
