# Samoloty PZL.23B Karaś i PZL.37B Łoś

## PZL.23B Karaś

Lekki bombowiec rozpoznawczy z trzyosobową załogą. Folder: `models/PZL23B`.

**Budowa jak w Ju 87D od Eugen** (jednosilnikowy bombowiec ze stałym podwoziem i tylnym strzelcem):

| Węzeł | Rola |
|---|---|
| `Chassis` | kadłub, gondola strzelca, skrzydło, usterzenie, owiewki podwozia, osłona NACA |
| `Bloc_Moteur_1` → `Helice_LS_1` | kołpak i śmigło |
| `Aileron_D/G`, `Elevator_D/G`, `Rudder` | stery |
| `Roue_Avant`, `Roue_Arriere` | koła główne w owiewkach i kółko ogonowe |
| `Tourelle_01` | stały karabin strzelający do przodu |
| `Tourelle_02`, `Tourelle_03` | karabin grzbietowy i karabin w gondoli brzusznej |
| `Pilot`, `Pilot2`, `Pilot3` | pilot, bombardier w gondoli i strzelec |
| `AS_1_1`, `AS_1_2`, `AS_2_1`, `AS_2_2` | zaczepy bomb pod skrzydłami |
| `PZL23B_train` | pomocniki `Train_Avant` i `Train_Arriere` |

**Wymiary:** rozpiętość 13,95 m, długość 9,68 m (model 9,47 m). Bryłę zmierzono na rysunku w trzech rzutach „PZL P.23B Karas.svg” z Wikimedia Commons (licencja CC BY-SA 3.0) w skali 9,33 mm na piksel.

## PZL.37B Łoś

Średni bombowiec dwusilnikowy z czteroosobową załogą. Folder: `models/PZL37B`.

**Budowa jak w Ju 88 i Ju 188 od Eugen** (dwusilnikowe bombowce z chowanym podwoziem):

| Węzeł | Rola |
|---|---|
| `Chassis` | kadłub, skrzydło, gondole silników, usterzenie z dwoma statecznikami, kabina |
| `Bloc_Moteur_1` → `Helice_LS_1` | lewy silnik (strona +Y w grze) |
| `Bloc_Moteur_2` → `Helice_LS_2` | prawy silnik |
| `Aileron_D/G`, `Elevator_D/G` | lotki i stery wysokości |
| `Rudder` | oba stery kierunku w jednej siatce, bo Ju 88 ma jeden węzeł `Rudder` |
| `Tourelle_01`, `Tourelle_02`, `Tourelle_03` | karabin w nosie, na grzbiecie i pod kadłubem |
| `Pilot`, `Pilot2`, `Pilot3` | pilot, nawigator w nosie i strzelec |
| `AS_1_1` … `AS_2_2` | bomby w kadłubie i w komorach centropłata |
| `PZL37B_train` | siatki `Train` (goleni), `Roue_Avant` (podwójne koła główne) i `Roue_Arriere` (kółko ogonowe) oraz pomocniki `Train_Avant` i `Train_Arriere` |

Model główny nie ma kół, bo podwozie jest chowane. Gra pokazuje je z pliku `_train`, tak jak w Ju 88. Plik `_train` ma własną teksturę.

**Wymiary:** rozpiętość 17,93 m, długość 12,92 m (model 13,35 m z lufą karabinu w nosie), wysokość 5,08 m.

**Pochodzenie kształtu:** na Wikimedia Commons nie ma pełnego rysunku Łosia w trzech rzutach. Proporcje odczytano z małego, 500-pikselowego podglądu rysunku „PZL P.37B Los B” na the-blueprints.com, oglądanego w przeglądarce. Dodatkowo użyto widoku bocznego i przekrojów z „Modelarza” (Wikimedia Commons, CC BY-SA 3.0) oraz zdjęć. Główne wymiary pochodzą z danych, a zarys kadłuba, gondoli i usterzenia jest przybliżony. Dokładniejszy rysunek pozwoliłby go poprawić.

## Wspólne

- Malowanie z września 1939: góra khaki, spód jasny niebieskoszary, szachownice na skrzydłach, a w Łosiu także na statecznikach. Oszklenie jest malowane ciemnym kolorem, bez osobnego materiału szyby `vitre`.
- Wtyczka w wersji 1.2.0 przyjmuje teraz pliki `_train` z siatkami podwozia i bez `Chassis`.
- Modele nie mają wpisów jednostek i w grze nie były sprawdzane.

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_SPEC = 'spec_karas'   # albo 'spec_los'
$out = 'build\karas'          # albo 'build\los'
& $blender --background --factory-startup --python scripts\build_karas.py -- $out   # albo build_los.py
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```
