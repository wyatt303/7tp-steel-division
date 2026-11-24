# Motocykl Sokół 1000 z wózkiem i rkm wz. 28

## Budowa jak w modelach z gry

Układ węzłów skopiowano z BMW R75 z wózkiem od Eugen (`GER/Vehicule.zip`), jedynego motocykla w Modding Assets.

| Węzeł | Typ | Rola |
|---|---|---|
| `Chassis` | siatka | rama, silnik V2, zbiornik, siodło, błotnik tylny, wózek z ramą i błotnikiem |
| `Axis` | siatka, dziecko `Chassis` | skręcająca część: widelec trapezowy, kierownica, reflektor, błotnik przedni; oś obrotu w główce ramy |
| `Motard` | siatka, dziecko `Chassis` | kierowca w mundurze i hełmie wz. 31 |
| `Tourelle_01` → `Axe_Canon_01` → `Canon_01` | siatki | sworzeń na wózku, rkm Browning wz. 28 i jego lufa |
| `Roue_Droite_01`, `Roue_03`, `Roue_02` | siatki bez rodzica | koło przednie (skrętne), tylne i koło wózka |
| `Roue_Gauche_01` | pomocnik pod `Canon_01` | skopiowany z R75; jego rola jest nieznana |
| `Tireur`, `Fx_Stress_01/02`, `Fx_tourelle1_tir_01`, `FX_Fumee_Roue_D1/G1` | pomocniki | strzelec w wózku, efekty |

Jak w R75, motocykl jest po lewej, a wózek po prawej. R75 nie ma atrap broni `Tourelle_02`–`04`, więc tu też ich nie ma.

## Wymiary

| Element | Wartość | Pochodzenie |
|---|---:|---|
| Długość | 2,23 m (model 2,35 m z lufą rkm) | Muzeum Inżynierii i Techniki w Krakowie |
| Szerokość | 1,68 m (model 1,69 m) | jw. |
| Wysokość | 1,23 m (model 1,11 m bez kierowcy, 1,53 m z kierowcą) | jw. |
| Rozstaw osi | 1,464 m | rysunek w trzech rzutach |
| Koła | Ø 0,69 m (opony 4.40-19), koło wózka Ø 0,68 m | rysunek, opis opon na modelu 3D |
| Długość samego motocykla | 2,22 m | rysunek, zgodna z danymi muzeum |
| Góra zbiornika / siodło / manetki / reflektor | 0,85 / 0,80 / 0,97 / 1,01 m | rysunek |

## Założenia i niepewności

- Motocykl odtworzono według rysunku w trzech rzutach z the-blueprints.com z wymiarem rozstawu osi 1464 mm (2,614 mm na piksel), dostarczonego przez autora. Pomocniczo użyto ilustracji bocznej i modelu 3D, które też dostarczył autor. Zdjęcia z Wikimedia Commons obejrzano w przeglądarce, bez pobierania. Zdjęcie z boku z muzeum (Sokół1000 MSPO14 DSC02336) posłużyło do ustalenia rozstawu osi (około dwóch średnic koła) oraz wysokości zbiornika, siodła, kierownicy i reflektora. Zdjęcia wojskowe („Rkm wz.28 na motocyklu Sokół”, „CWS M111 z ckm wz. 30”) pokazują wysoki sworzeń rkm i koło zapasowe na dziobie wózka.
- Układ wózka pochodzi z instrukcji malowania modelu kartonowego CWS M-111 z wózkiem, którą dostarczył autor. Instrukcja ma widok z przodu, z tyłu, z obu boków i z góry. Na tej podstawie kokpit jest z przodu, koło zapasowe leży płasko na tylnym pokładzie, kanister jest na ramie wózka, a na bagażniku motocykla jest poduszka dla pasażera.
- Wózek ma kształt łódki, jak na rysunku i w egzemplarzu muzealnym. Jedno ze zdjęć wojskowych pokazuje wózek skrzyniowy, więc wersje wojskowe mogły się różnić.
- Kierowca jest uproszczoną postacią z brył. W R75 ma osobny materiał z teksturą żołnierza, a tu jest na wspólnej teksturze, malowany przez `paint_color` w `spec_sokol.py`.
- Malowanie to jednolity khaki, bo motocykle zwykle nie miały kamuflażu z 1936 r.
- R75 ma osobną teksturę z przezroczystością na szprychy, a tutaj szprychy są geometrią w wersji High.
- Model nie ma wpisu jednostki i w grze nie był sprawdzany.

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_SPEC = 'spec_sokol'
$out = 'build\sokol'
& $blender --background --factory-startup --python scripts\build_sokol.py -- $out
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```

## Źródła

- [Motocykl CWS M111 z wózkiem bocznym, Muzeum Inżynierii i Techniki w Krakowie](https://www.mit.krakow.pl/?p=12979)
- [Sokół 1000, polska Wikipedia](https://pl.wikipedia.org/wiki/Sok%C3%B3%C5%82_1000)
- [Kategoria Sokół 1000 w Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Sok%C3%B3%C5%82_1000)

## Stan

| | Sokół 1000 | BMW R75 (Eugen) |
|---|---:|---:|
| Trójkąty High | 4450 | 10 883 |
| Trójkąty Mid | 2956 | 2728 |
| Trójkąty Low | 1096 | 802 |

Wszystkie trzy pliki przechodzą eksport wtyczką. Wtyczka zgłasza tylko brak gąsienic, co jest oczekiwane.
