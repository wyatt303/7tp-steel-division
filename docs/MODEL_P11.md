# Samolot myśliwski PZL P.11c

## Budowa jak w samolotach z gry

Układ skopiowano z samolotów ze stałym podwoziem od Eugen: Fieseler Storch i Ju 87D (`GER/Avion.zip`). Porównano go też z polskim Hurricane'em Mk II (`POL/Avion.zip`).

| Węzeł | Typ | Rola |
|---|---|---|
| `Chassis` | siatka | kadłub, skrzydło, usterzenie stałe, podwozie, osłona silnika |
| `Bloc_Moteur_1` → `Helice_LS_1` | siatki | kołpak i dwułopatowe śmigło, oś obrotu na osi śmigła |
| `Aileron_D/G`, `Elevator_D/G`, `Rudder` | siatki | lotki, stery wysokości i kierunku, osie na zawiasach |
| `Roue_Avant`, `Roue_Arriere` | siatki | oba koła główne w jednej siatce oraz płoza ogonowa |
| `Tourelle_01` → `Axe_Canon_01` → `Canon_01` | pomocnik, pomocnik, siatka | cztery karabiny maszynowe |
| `Fx_tourelle1_tir_01…04` | pomocniki | wyloty luf: dwa w kadłubie, dwa w skrzydłach |
| `Pilot`, `FX_Vortex_D/G`, `Fx_Stress_01/02` | pomocniki | pilot, smugi z końców skrzydeł, dym przy trafieniu |

Samoloty z gry mają osobny plik `<nazwa>_train` z dwoma pomocnikami, którymi są punkty styku z ziemią. Tutaj to `P11C_train` z `Train_Avant` pod kołami i `Train_Arriere` pod płozą. Wtyczka eksportuje teraz także sceny z samymi pomocnikami.

Model jest w położeniu lotu: oś śmigła leży poziomo w `Z = 0`, a początek układu na około 30% cięciwy skrzydła, tak jak w modelach Eugen. Ziemia jest na wysokości `Z = −1,86 m`.

## Wymiary

| Element | Wartość | Pochodzenie |
|---|---:|---|
| Rozpiętość | 10,72 m | dane techniczne, skala rysunku |
| Długość | 7,41 m (dane 7,55 m) | rysunek |
| Średnica śmigła | 2,8 m | rysunek |
| Rozstaw kół | 2,42 m | rysunek z przodu |

Rysunek „PZL 11c.svg” z Wikimedia Commons (licencja CC BY-SA 3.0) zmierzono w skali 7,97 mm na piksel podglądu o wysokości 2000 px. Rysunek nie jest częścią repozytorium.

## Malowanie

Wrzesień 1939: góra khaki, spód jasny niebieskoszary, biało-czerwone szachownice na obu powierzchniach skrzydeł i na bokach tylnej części kadłuba. Kolory i rozmieszczenie szachownic są przybliżone. Malowanie ustawia funkcja `paint_color` w `spec_p11.py`.

## Założenia i niepewności

- Skrzydło ma profil NACA o grubości 12–13% u nasady i 6% na końcu. Profil to szacunek.
- Kabina jest otwarta, a wiatrochron należy do kadłuba, bez osobnego materiału szyby `vitre` z modeli Eugen.
- Silnik Mercury ma w wersji High dziewięć uproszczonych cylindrów.
- Low ma około 800 trójkątów, czyli więcej niż Hurricane Low od Eugen (599).
- Model nie ma wpisu jednostki i w grze nie był sprawdzany. Rozpiętość Hurricane'a od Eugen jest około 6% większa od rzeczywistej, więc skala samolotów może być w grze nieco inna niż pojazdów.

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_SPEC = 'spec_p11'
$out = 'build\p11'
& $blender --background --factory-startup --python scripts\build_p11.py -- $out
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```

Plik `P11C_train.blend` eksportuje się wtyczką osobno, tak jak wersje Mid i Low.
