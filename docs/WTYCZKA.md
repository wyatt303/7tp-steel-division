# Wtyczka Steel Division Ase2NdfBin Exporter

Eksportuje scenę Blendera do pliku `.Ase2NdfBin`, który przyjmuje `ModGen` ze Steel Division: Normandy 44. Zastępuje 3ds Max 2015 i wtyczki Eugen.

Wymaga Blendera 4.2 lub nowszego. Testowana na Blenderze 5.3.

## Instalacja

Przeciągnij `blender_addon/dist/steel_division_ase2ndfbin-1.3.0.zip` do okna Blendera albo wybierz **Edit > Preferences > Add-ons > strzałka w prawym górnym rogu > Install from Disk**.

## Eksport

1. Otwórz scenę z czołgiem.
2. Wybierz **File > Export > Steel Division Tank (.Ase2NdfBin)**.
3. Wskaż folder docelowy w modzie i nazwę pliku.
4. Zostaw **Units per Metre = 203** i włączone **Copy Textures**.

Wersje High, Mid i Low to osobne pliki `.blend`, więc każdą eksportuje się osobno.

## Wymagania wobec sceny

**Układ:** czołg patrzy w stronę +Y, prawa burta to +X, góra to +Z, a 1 jednostka to 1 metr. Skala obiektów musi być zastosowana.

**Wymagane nazwy obiektów:**

| Obiekt | Typ | Rola |
|---|---|---|
| `Chassis` | siatka | główny element |
| `Tourelle_0N` | siatka lub empty | wieża N |
| `Axe_Canon_0N` | siatka lub empty | oś podniesienia |
| `Canon_0N` | **siatka** | lufa, gra animuje jej odrzut |
| `Fx_tourelleN_tir_01` | empty | wylot lufy |
| `Roue_D1…`, `Roue_G1…` | siatka | koła prawe i lewe |
| `Roue_Elev_D1…`, `Roue_Elev_G1…` | empty | uniesienie kół |
| `Chenille_Droite_01`, `Chenille_Gauche_01` | siatka | gąsienice |
| `Fake` | empty | wierzchołki gąsienic niezwiązane z kołem |
| `Fx_Stress_01/02`, `FX_Fumee_Chenille_D1/G1` | empty | efekty |

Koła numeruje się od koła napędowego do napinającego. Jednostki zwykle oczekują czterech zestawów broni, od `Tourelle_01` do `Tourelle_04`.

**Materiały** potrzebują właściwości niestandardowych:

| Właściwość | Przykład |
|---|---|
| `eug_diffuse` | `TP7_JW.png` |
| `eug_specular` | `TP7_JW_SC.png` |
| `eug_glossiness` | `TP7_JW_GLO.png` |
| `eug_normal` | `TP7_JW_NM.png` |
| `eug_alpha` | `TP7_JW_tracks_A.png` (gąsienice) |
| `eug_tag` | `chenilledroite` lub `chenillegauche` (gąsienice) |
| `eug_transparent` | `True` dla szyby: przezroczystość włączona, `eug_alpha` zamiast `eug_normal` |

**Szyby:** siatka z kilkoma slotami materiałów (np. `Chassis` z farbą w slocie 0 i szybą w slocie 1) trafia do pliku jako materiał `Multi\Sub-Object`, a każdy trójkąt dostaje numer slotu w `MESH_MTLID`, tak jak w pojazdach z gry. Zob. [SZYBY.md](SZYBY.md).

**Gąsienice:** Skin zapisuje się w grupach wierzchołków o nazwach `Roue_Elev_D2`, `Fake` itd. Każdy wierzchołek przypisany jest do jednej grupy.

**UV:** wszystkie współrzędne muszą mieścić się w zakresie 0–1. Na gąsienicach oś U biegnie w poprzek, a V wzdłuż.

## Co sprawdza wtyczka

Eksport zostaje przerwany, gdy:

- brakuje `Chassis` lub elementów wieży,
- `Canon_0N` nie jest siatką,
- obiekt nie ma UV lub materiału albo ma niezastosowaną skalę,
- **UV wychodzi poza zakres 0–1**, co w testach powodowało awarię gry przy podglądzie jednostki.

Ostrzega też przy ponad 7000 trójkątów i brakujących teksturach.

## Pojazdy kołowe i samoloty

Wtyczka eksportuje też modele bez gąsienic. Brak `Chenille_*` zgłasza wtedy tylko jako ostrzeżenie.

- Samochody pancerne: zobacz [MODEL_WZ34.md](MODEL_WZ34.md) i [MODEL_WZ28.md](MODEL_WZ28.md).
- Samoloty: zobacz [MODEL_P11.md](MODEL_P11.md).

Od wersji 1.3.0 wtyczka zapisuje węzły w kolejności z właściwości sceny `eug_node_order` (potrzebne do animacji armat z gry) oraz siatki z kilkoma materiałami i przezroczyste szyby.

Od wersji 1.1.0 wtyczka eksportuje również sceny z samymi pomocnikami, na przykład plik `<nazwa>_train` samolotu. Od wersji 1.2.0 także pliki `_train` z siatkami chowanego podwozia (`Train`, `Roue_Avant`, `Roue_Arriere`). Taka scena nie potrzebuje `Chassis`.
