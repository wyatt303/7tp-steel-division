# Samochód ciężarowy Polski Fiat 621L

Folder: `models/PF621L`. Wojskowa ciężarówka 2,5 t z kabiną zamkniętą, drewnianą skrzynią i plandeką.

## Budowa jak w modelach z gry

Układ węzłów skopiowano z Opla Blitza od Eugen (`GER/Vehicule.zip`):

| Węzeł | Rola |
|---|---|
| `Chassis` | rama, maska, kabina, skrzynia z plandeką, błotniki, zderzak, reflektory |
| `Roue_Droite_01`, `Roue_Gauche_01` | przednie koła skrętne, bez rodzica |
| `Roue_02` | tylna oś z kołami bliźniaczymi, jedna siatka |
| `Driver` | kierowca po lewej stronie |
| `Remorque_1` | hak holowniczy z tyłu |
| `Fx_Stress_01/02`, `FX_Fumee_Roue_D1/G1` | efekty |

Opel Blitz nie ma wieży ani broni, więc ten model też ich nie ma.

## Wymiary

| Element | Wartość | Pochodzenie |
|---|---:|---|
| Długość | 5,78 m (model 5,75–5,92 m z zderzakiem i hakiem) | angielska Wikipedia, techno-science.net |
| Szerokość | 2,07 m (model 2,12 m z lusterkami i błotnikami) | jw. |
| Wysokość | 2,62 m (plandeka) | jw. |
| Rozstaw osi | 3,65 m | jw. |
| Koła | Ø 0,86 m | **szacunek ze zdjęć** |
| Zwisy, rozstaw kół, wysokość kabiny i skrzyni | | **szacunek ze zdjęć** |

Wygląd wzięto ze zdjęć z Wikimedia Commons, oglądanych w przeglądarce: odrestaurowanego wojskowego 621L, modelu muzealnego w kamuflażu z 1936 r. i wozu strażackiego z Warszawy.

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
| Trójkąty High | 3772 | 5179 |
| Trójkąty Mid | 1748 | 1849 |
| Trójkąty Low | 560 | 599 |

Wszystkie trzy pliki przechodzą eksport wtyczką. Wtyczka zgłasza tylko brak wieży i gąsienic, co jest oczekiwane. Szyby są przyciemnione przez `GLASS_BOXES` w `spec_pf621.py`.
