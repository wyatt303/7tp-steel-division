# Samochód ciężarowy Polski Fiat 621L

Wojskowa ciężarówka 2,5 t z kabiną zamkniętą i drewnianą skrzynią, w dwóch wariantach:

| Wariant | Folder | Plik ustawień |
|---|---|---|
| z plandeką | `models/PF621L` | `scripts/spec_pf621.py` |
| bez plandeki, z otwartą skrzynią | `models/PF621L_OPEN` | `scripts/spec_pf621_open.py` (dziedziczy wszystko poza plandeką) |

## Budowa jak w modelach z gry

Układ węzłów skopiowano z Opla Blitza od Eugen (`GER/Vehicule.zip`):

| Węzeł | Rola |
|---|---|
| `Chassis` | rama, maska z dwoma rzędami żaluzji, osłona chłodnicy z kratą, pusta w środku kabina z daszkiem, przezroczystymi szybami (przednia i boczne), ławką, deską rozdzielczą i kierownicą, skrzynia (z plandeką albo bez), błotniki, stopnie, skrzynka narzędziowa, zbiornik paliwa, koło zapasowe, rurowy zderzak, reflektory |
| `Roue_Droite_01`, `Roue_Gauche_01` | przednie koła skrętne, bez rodzica |
| `Roue_02` | tylna oś z kołami bliźniaczymi po obu stronach, jedna siatka |
| `Driver` | kierowca po lewej stronie |
| `Remorque_1` | hak holowniczy z tyłu |
| `Fx_Stress_01/02`, `FX_Fumee_Roue_D1/G1` | efekty |

Opel Blitz nie ma wieży ani broni, więc ten model też ich nie ma.

## Kabina i przód według rysunku (27 listopada 2026 r.)

Kabinę, maskę, błotniki i wysokości skrzyni zmierzono na rysunku w skali 1:25 „Polski Fiat 621 L Truck (1937-1939)” (vector-templates.com) od użytkownika. Na tym rysunku to około 0,0103 m na piksel. Wymiary odmierzono od przedniej osi.

| Element | Wartość z rysunku |
|---|---:|
| Koła | Ø 0,80 m, rozstaw przednich 1,60 m |
| Osłona chłodnicy | 0,19 m przed osią, krata 0,46 m szerokości, od 0,55 do 1,30 m |
| Maska | góra 1,33 m, do 0,85 m za osią, dwa rzędy żaluzji z tyłu maski; z góry mocno rozszerza się do kabiny: połowa szerokości 0,29–0,34 m przy chłodnicy, 0,61 m przy kabinie (widok z góry na kolorowym rysunku i zdjęcie modelu) |
| Kabina | od 1,05 do 2,07 m za osią (1,02 m), szerokość 1,51 m, dach 2,00 m, szyba pochylona o 0,09 m do tyłu, okno w drzwiach od 1,39 do 1,83 m |
| Błotnik przedni | od czubka 0,46 m przed osią (0,67 m nad ziemią) przez łuk nad kołem (0,92 m) do stopnia 0,74 m za osią |
| Skrzynia | podłoga 1,02 m, burty do 1,65 m, szerokość 1,90 m |
| Reflektory | 0,80 m od siebie, na wysokości 0,94 m |

Z danych technicznych (angielska Wikipedia, techno-science.net) pozostały rozstaw osi 3,65 m, długość 5,78 m i wysokość z plandeką 2,62 m. Rysunek ma krótszy rozstaw osi (3,2 m) i krótszą skrzynię. Od rysunku wzięto kabinę i przód, a od danych rozstaw osi i długość skrzyni.

Szczegóły ze zdjęć modeli plastikowych od użytkownika i kolorowego rysunku z czterech stron:
- daszek nad szybą,
- deski tylnej ściany kabiny z małym okienkiem,
- dwa rzędy żaluzji maski,
- rurowy zderzak z krótkimi wystającymi końcówkami,
- słupki burt,
- zaokrąglona plandeka.

## Wymiary modelu

| | z plandeką | bez plandeki |
|---|---:|---:|
| Długość | 5,79 m | 5,79 m |
| Szerokość | 2,02 m | 2,02 m |
| Wysokość | 2,62 m | 2,00 m (dach kabiny) |
| Trójkąty High / Mid / Low | 5296 / 2712 / 1124 | 5064 / 2684 / 1104 |
| Opel Blitz (Eugen) High / Mid / Low | 5179 / 1849 / 599 | |

Wersje Low są większe niż w Oplu Blitzie, bo bliźniacze koła, pełne błotniki i wnętrze kabiny dokładają trójkąty.

## Stan

Malowanie to kamuflaż z 1936 r., tak jak na modelu muzealnym. Przednia szyba i okna w drzwiach są przezroczyste, zrobione jak w pojazdach z gry (drugi materiał `Chassis`, zob. [SZYBY.md](SZYBY.md)), a kabina ma za nimi wnętrze (28 listopada 2026 r.). Małe tylne okienko kabiny i okienka w plandece są tylko malowane na ciemno przez `GLASS_BOXES`. Ramki okienek w plandece są w siatce tylko w wersji High.

Wszystkie sześć plików przechodzi eksport wtyczką. Wtyczka zgłasza tylko brak wieży i gąsienic, co jest oczekiwane.

## Jednostka w grze (27 listopada 2026 r.)

Wariant z plandeką jest jednostką `PF621L_POL` w `data/units.toml`, z układem `truck` w `scripts/create_battlegroup.py`. Wariant bez plandeki nie ma jeszcze wpisu.

| Co | Skąd |
|---|---|
| Dane jednostki: polskie głosy i flaga, przewóz piechoty, holowanie armat (`Armes_tractees`), 3 miejsca | polski Bedford QLD z gry (`Truck_Bedford_POL`) |
| Wygląd: ruch kół, dźwięk silnika, miejsce na holowaną armatę (`SubDepictionTowedUnit`) | Opel Blitz z gry (ten sam układ węzłów), z polskim kierowcą |
| Broń | brak, jak w Bedfordzie i Oplu |
| Prędkość | 18 km/h w terenie, 55 km/h na drodze (Opel 20 / 85, Bedford 20 / 80); prawdziwy 621L miał 46 KM i jechał 50–55 km/h, Opel Blitz 68–75 KM i 80–85 km/h |
| Wytrzymałość, pancerz | 6, `Vehicule` z dachem `Toit`, jak Bedford |
| Znaczek nad jednostką | ikona ciężarówki z gry (`Texture_RTS_H_Truck_GMC`), jak u Bedforda |
| Gdzie w grze | ciągnik armaty wz. 36 w jej paczce (zakładka przeciwpancerna) |

Model trafia do `Assets\3D\Units\POL\Vehicule\PF621L`. Generowanie moda przechodzi bez błędów. W grze Fiat nie był jeszcze sprawdzany.

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
foreach ($v in @(@('spec_pf621', 'build\pf621'), @('spec_pf621_open', 'build\pf621_open'))) {
    $env:TK_SPEC = $v[0]
    & $blender --background --factory-startup --python scripts\build_pf621.py -- $v[1]
    & $blender --background --factory-startup --python scripts\texture_tk.py -- $v[1]
    & $blender --background --factory-startup --python scripts\finalize_tk.py -- $v[1]
}
```

Pliki `.blend`, `.fbx`, tekstury i rendery kopiuje się potem do `models/PF621L` i `models/PF621L_OPEN`.

## Źródła

- [Polski Fiat 621, angielska Wikipedia](https://en.wikipedia.org/wiki/Polski_Fiat_621)
- [Fiat Polski 621, techno-science.net](https://www.techno-science.net/fr/definitions/fiat-polski-621)
- Rysunek 1:25 „Polski Fiat 621 L Truck (1937-1939)”, vector-templates.com (od użytkownika, nie jest częścią repozytorium).
- Zdjęcia modeli plastikowych i kolorowy rysunek z czterech stron (od użytkownika).
- Wcześniej: zdjęcia z Wikimedia Commons „Polski Fiat 621L.jpg”, „POL PL fiat 621 military.jpg”, „Polski Fiat 621 L Warsaw.JPG”.
