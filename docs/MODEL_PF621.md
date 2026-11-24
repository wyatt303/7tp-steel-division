# Samochód ciężarowy Polski Fiat 621L

Folder: `models/PF621L`. Wojskowa ciężarówka 2,5 t z kabiną zamkniętą, drewnianą skrzynią i plandeką.

## Budowa jak w modelach z gry

Układ węzłów skopiowano z Opla Blitza od Eugen (`GER/Vehicule.zip`):

| Węzeł | Rola |
|---|---|
| `Chassis` | rama, maska, kabina z daszkiem nad szybą, skrzynia z plandeką i okienkami, błotniki, stopnie, skrzynka narzędziowa, zbiornik paliwa, koło zapasowe, zderzak, reflektory |
| `Roue_Droite_01`, `Roue_Gauche_01` | przednie koła skrętne, bez rodzica |
| `Roue_02` | tylna oś z kołami bliźniaczymi, jedna siatka |
| `Driver` | kierowca po lewej stronie |
| `Remorque_1` | hak holowniczy z tyłu |
| `Fx_Stress_01/02`, `FX_Fumee_Roue_D1/G1` | efekty |

Opel Blitz nie ma wieży ani broni, więc ten model też ich nie ma.

## Wymiary

| Element | Wartość | Pochodzenie |
|---|---:|---|
| Długość | 5,78 m według danych; model 5,67 m bez haka, jak na rysunku z boku | angielska Wikipedia, techno-science.net, rysunek |
| Szerokość | 2,07 m (model 2,12 m z błotnikami) | jw. |
| Wysokość | 2,62 m (plandeka) | jw. |
| Rozstaw osi | 3,65 m | jw. |
| Koła | Ø 0,88 m | rysunek z boku |
| Zwis przedni / tylny | 0,60 / 1,42 m | rysunek z boku |
| Maska | od chłodnicy (0,28 m przed osią) do 1,08 m za osią | rysunek z boku |
| Kabina | 0,94 m długości, dół 0,62 m, dach 2,20 m, daszek 0,22 m przed szybą | rysunek z boku |
| Skrzynia | od 0,06 m za kabiną do tyłu wozu, podłoga 1,06 m, burty do 1,58 m | rysunek z boku |
| Rama, stopnie, reflektory | rama 0,45–0,60 m, stopnie 0,50 m, reflektory 1,07 m | rysunek z boku |

Wymiary zmierzono w pikselach na kolorowym rysunku z boku w kamuflażu z 1936 r. (2,62 m wysokości to około 0,0115 m na piksel). Z rysunków w instrukcji obsługi (schemat smarowania 621L widziany z góry, tylny most z kołami bliźniaczymi, przednie zawieszenie i układ kierowniczy) wzięto ramę, rozstaw kół bliźniaczych i kierownicę po lewej stronie. Ze zdjęcia modelu plastikowego wzięto zderzak, reflektory na wspornikach, żaluzje maski, słupki burt i skrzynkę pod skrzynią. Wcześniej korzystano też ze zdjęć z Wikimedia Commons: odrestaurowanego wojskowego 621L, modelu muzealnego w kamuflażu z 1936 r. i wozu strażackiego z Warszawy.

## Stan

Malowanie to kamuflaż z 1936 r., tak jak na modelu muzealnym. Szyby są tylko malowane na ciemno, bez osobnego materiału `vitre`. Model nie ma wpisu jednostki i w grze nie był sprawdzany.

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_SPEC = 'spec_pf621'
$out = 'build\pf621'
& $blender --background --factory-startup --python scripts\build_pf621.py -- $out
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```

## Źródła

- [Polski Fiat 621, angielska Wikipedia](https://en.wikipedia.org/wiki/Polski_Fiat_621)
- [Fiat Polski 621, techno-science.net](https://www.techno-science.net/fr/definitions/fiat-polski-621)
- Zdjęcia z Wikimedia Commons: „Polski Fiat 621L.jpg”, „POL PL fiat 621 military.jpg”, „Polski Fiat 621 L Warsaw.JPG”.

| | Fiat 621L | Opel Blitz (Eugen) |
|---|---:|---:|
| Trójkąty High | 4300 | 5179 |
| Trójkąty Mid | 1896 | 1849 |
| Trójkąty Low | 636 | 599 |

Wszystkie trzy pliki przechodzą eksport wtyczką. Wtyczka zgłasza tylko brak wieży i gąsienic, co jest oczekiwane. Szyby kabiny i okienka w plandece są przyciemnione przez `GLASS_BOXES` w `spec_pf621.py`. Ramki okienek w plandece są w siatce tylko w wersji High.
