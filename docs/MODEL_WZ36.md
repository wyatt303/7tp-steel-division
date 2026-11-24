# Armata przeciwpancerna 37 mm wz. 36 (Bofors)

Folder: `models/WZ36_BOFORS`.

## Budowa jak w modelach z gry

Układ węzłów skopiowano z PaK 36 od Eugen (`GER/Canon.zip/Canon/PaK_36`), działa tego samego kalibru i podobnej wielkości.

| Węzeł | Rola |
|---|---|
| `Chassis` | oś kół, korzeń modelu |
| `Tourelle_01` | łoże górne i tarcza: dwie górne płyty z otworem celownika i składane płyty dolne |
| `Axe_Canon_01` | kołyska, opornik, zamek, pokrętła i celownik |
| `Canon_01` | lufa L/45 z hamulcem wylotowym |
| `Bras_Gauche`, `Bras_Droit` | ogony łoża rozłożone na ±25°, jak w położeniu bojowym |
| `Roue_D1`, `Roue_G1` | koła, dzieci `Chassis` |
| `Remorque_2` | ucho holownicze na końcu prawego ogona |
| `Fx_tourelle1_tir_01`, `Fx_Stress_01/02`, `FX_Fumee_Roue_D1/G1` | efekty |

Model obsługi jest osobnym plikiem `Boites_WZ36_BOFORS` z pomocnikami `Canon_AT`, `servant_G` i `servant_D`. Ich położenie skopiowano z `Boites_PaK_36`.

**Animacje:** PaK 36 ma osobne pliki animacji (`_Deploy`, `_Fold`, `_Fire`, `_Idle`, `_Move`, `_Move_Back`, `_Turn_Left`, `_Turn_Right`). Animują one węzły o tych samych nazwach. Nasza wtyczka nie eksportuje animacji. Przy podmianie PaK 36 najprościej zostawić jego pliki animacji. Nie wiadomo jednak, czy zapisują one położenia bezwzględne, więc osie obrotu naszych węzłów mogą zostać przesunięte do miejsc z PaK 36. Trzeba to sprawdzić w grze.

## Wymiary

| Element | Wartość | Pochodzenie |
|---|---:|---|
| Długość w położeniu bojowym | 3,05 m (model 3,12 m) | Wikipedia, valka.cz |
| Szerokość | 1,22 m (koła), tarcza 1,20 m | jw. |
| Wysokość | 1,01 m | jw. |
| Lufa | L/45 = 1,665 m | jw. |
| Wysokość linii ognia | 0,62 m | polska Wikipedia |
| Rozłożenie ogonów | ±25° | jw. |
| Koła | Ø 0,60 m | **szacunek ze zdjęć** |
| Długość ogona | 1,55 m | **szacunek z długości całkowitej** |

Wygląd tarczy, kół, ogonów z płytami oporowymi i kołyski wzięto ze zdjęć egzemplarzy muzealnych z Wikimedia Commons, oglądanych w przeglądarce.

## Stan

Wszystkie pliki przechodzą eksport wtyczką. Malowanie to kamuflaż z 1936 r., jak na zachowanych armatach. Model nie ma wpisu jednostki i w grze nie był sprawdzany.

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_SPEC = 'spec_wz36'
$out = 'build\wz36'
& $blender --background --factory-startup --python scripts\build_wz36.py -- $out
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```

## Źródła

- [Bofors 37 mm anti-tank gun, angielska Wikipedia](https://en.wikipedia.org/wiki/Bofors_37_mm_anti-tank_gun)
- [37 mm armata przeciwpancerna Bofors, polska Wikipedia](https://pl.wikipedia.org/wiki/37_mm_armata_przeciwpancerna_Bofors)
- [valka.cz / armedconflicts.com](https://www.armedconflicts.com/topic/view/28848)
- Zdjęcia z Wikimedia Commons: „37mm wz36 antitank gun parola 1/2”, „Finnish bofors 37mm front”.

| | wz. 36 | PaK 36 (Eugen) |
|---|---:|---:|
| Trójkąty High | 1780 | 4166 |
| Trójkąty Mid | 1036 | 1476 |
| Trójkąty Low | 264 | 581 |
