# Ustawienia jednostek: data/units.toml

Wszystkie liczby i napisy jednostek battlegroupy są w pliku [`data/units.toml`](../data/units.toml). Edytujesz go w dowolnym edytorze tekstu (Notatnik, VS Code), a potem uruchamiasz `zainstaluj_mod.bat`. Instalator zbuduje mod od nowa z tych wartości. Skrypt `scripts/create_battlegroup.py` czyta plik przy każdej instalacji.

Linie zaczynające się od `#` to komentarze. Liczby dziesiętne piszemy z kropką (`1.5`). Teksty są w cudzysłowie.

## Jednostki: `[units.<ID>]`

| Pole | Znaczenie | W grze |
|---|---|---|
| `model` | pliki modelu w `models\` | nie zmieniać |
| `name` | token nazwy z sekcji `[texts]` | tytuł okna jednostki |
| `alias` | nazwa w plikach gry | niewidoczna |
| `price` | cena | liczba w prawym górnym rogu |
| `year` | rok produkcji | |
| `speed_kmh` | prędkość w terenie | Speed, pierwsza liczba |
| `road_speed_kmh` | prędkość na drodze | Speed, druga liczba |
| `strength` | wytrzymałość (`MaxDamages`) | |
| `concealment` | maskowanie (`UnitConcealmentBonus`): 1.0 = Very bad, 1.5 = Bad | Stealth |
| `armor_front`, `armor_sides`, `armor_rear` | stopień pancerza 1–30 | liczby na tarczach przy widoku z góry |
| `armor_top` | rodzaj dachu, np. `Toit_Lourd` | Top: Enclosed |
| `ammo` | zapas amunicji w nabojach, osobno dla każdej amunicji | liczba obok AP lub HE |

Zapas jest dzielony przez `rounds_per_salvo` danej amunicji, bo gra liczy go w seriach. Jeśli liczba się nie dzieli, skrypt zaokrągla ją i wypisuje uwagę.

## Amunicja: `[ammo.<ID>]`

Amunicja jest wspólna dla wszystkich jednostek, które z niej korzystają. Ckm wz. 30 ma 7TP jednowieżowy i dwuwieżowy.

| Pole | Znaczenie | W grze |
|---|---|---|
| `copy_of` | wpis gry, z którego kopiowane są pozostałe pola | nie zmieniać |
| `name` | token nazwy broni z `[texts]` | dymek po najechaniu na broń |
| `caliber` | kaliber, `_` zamiast przecinka | napis przy obrazku broni |
| `penetration` | przebicie (tylko amunicja przeciwpancerna) | AP |
| `accuracy`, `accuracy_moving` | celność na postoju i w ruchu | ACC |
| `range_m` | zasięg w metrach | RANGE |
| `rounds_per_salvo`, `shots_per_salvo`, `seconds_between_shots`, `seconds_between_salvos` | serie i przerwy | ROF |

Szybkostrzelność w oknie jednostki:

```text
ROF = rounds_per_salvo × 60 / (seconds_between_salvos + (shots_per_salvo − 1) × seconds_between_shots)
```

Te same pola sterują strzelaniem w bitwie, więc zmiana ROF zmienia też siłę ognia.

## Napisy: `[texts]`

Każdy wiersz to `TOKEN = "tekst"`. Token ma najwyżej 10 znaków i jest wspólny dla jednostki i jej broni. Edytor jednostek zmienia te same napisy, ale tylko w zainstalowanym modzie. Żeby zmiana przetrwała ponowną instalację, wpisz ją tutaj.

## Czego plik jeszcze nie zawiera

- Optyki (`OpticalStrength`). Zostaje z wzorca, czyli Cromwella V.
- Paczek, czyli liczby kart i faz, oraz struktury battlegroupy. To jest w `PACKS` w skrypcie.
- Nowych układów broni. Jednostka z nowym układem (`layout`) wymaga zmian w `scripts/create_battlegroup.py`. Wzorce (`unit_base`, `weapon_base`), kolejność zapasów (`stocks`), rola (`type`), optyka (`optics`), obrót działka (`gun_traverse_deg`), as (`ace_name`), ikona z gry nad jednostką (`rts_texture`) i ciągnik w paczce (`transporter`) są już w pliku. Układy: `tp7_jw`, `tp7_dw`, `tks20`, `aircraft` i `gun` (armata holowana, zob. [MODEL_WZ36](MODEL_WZ36.md)).

Porównanie z czołgami z gry, przydatne przy balansie: [POROWNANIE_CZOLGOW.md](POROWNANIE_CZOLGOW.md).
