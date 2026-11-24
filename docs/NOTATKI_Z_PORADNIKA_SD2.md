# Notatki z poradnika modowania Steel Division 2

Źródła: `Steel Division 2\Mods\Modding Manual.pdf` (24 strony) i `NDF Reference Manual.pdf` (8 stron). Projekt dotyczy **Steel Division: Normandy 44**, więc poniżej są tylko rzeczy, które prawdopodobnie działają też w SD44. Numery stron dotyczą poradnika SD2.

## Co potwierdza nasze założenia

- `Chassis` jest korzeniem hierarchii. Łańcuch broni to `Tourelle_01` → `Axe_Canon_01` → `Canon_01` → `Fx_tourelle1_tir_01` (s. 22).
- `Roue_Elev_*` porusza się w pionie i ciągnie koło oraz zeskinowane wierzchołki gąsienicy. Obrót nadaje się samemu kołu. `Fake` zbiera pozostałe wierzchołki gąsienicy (s. 21).
- Przy eksporcie zaznaczone jest tylko **Force Rigid Skinning**, czyli jedna kość na wierzchołek. Nasza wtyczka robi tak samo (s. 23).
- Rejestracja siatki: pliki trafiają do `GameData/Assets/...`, opis siatki jednostki wskazuje nowe `FileName`, a `CivMask` zmienia się na `CivMask/MeshModding` (s. 23).
- Poziomy szczegółów robi się ręcznie (s. 20–21):

  | | Trójkąty | Tekstury |
  |---|---|---|
  | High | 6000–7000 | 2048 px oraz osobny zestaw gąsienic 256 px |
  | Mid | około 2000 | 1024 px, gąsienice wtopione w główną teksturę i nieruchome |
  | Low | poniżej 500 | 256 px |

## Czego jeszcze nie wykorzystujemy

- **Gąsienice:** poradnik wymaga osobnego materiału dla każdej strony z tagiem `chenilledroite` lub `chenillegauche`, z osobnymi teksturami (s. 18). Nasze materiały `M_Chenille_D` i `M_Chenille_G` mają tagi, ale używają tych samych plików tekstur. W 7TP to działało, więc to tylko uwaga na wypadek kłopotów z ruchem gąsienic.
- **Prototypy NDF:** zapis `Nowy is Istniejacy ( Pole = wartość )` kopiuje obiekt i zmienia tylko wskazane pola (NDF Reference, s. 6). Przyda się do klonowania jednostki pod nową nazwą.
- `+` łączy listy i mapy, np. `[a] + [b]` (NDF Reference, s. 3). To jedyny opisany sposób dopisywania.
- Tokeny lokalizacji mogą mieć najwyżej 10 znaków (s. 9–10).
- Tylko obiekty AI (`TPoolModel`) wymagają własnego GUID (s. 12). Dla jednostek poradnik tego nie mówi, ale może to być przyczyna ignorowania nowych wpisów.

## Czego poradnik nie wyjaśnia

- Jak dodać zupełnie nową jednostkę. Opisany jest tylko sposób z przejęciem istniejącego wpisu, którego już używamy.
- Wraki, modele zniszczonych pojazdów, skręt kół, kurz spod kół, pomocniki załogi i holowania (`Driver`, `Tireur`, `Remorque_1`) oraz skala 203 j./m.
- Kolejność ładowania kilku modów i konflikty między nimi.

## Tylko w SD2

3ds Max i wtyczki z `Utils\Meshes\PluginInstallers`, typy `...Modded` dla interfejsu i dźwięku, podział na `Divisions.ndf` i `Packs.ndf`, AI Steelmana, a w `Config.ini` klucze `DeckFormatVersion` i `ModGenVersion`. W SD44 trzeba to sprawdzić osobno, zanim się z tego skorzysta.
