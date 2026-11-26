# Armata przeciwpancerna 37 mm wz. 36 (Bofors)

Folder: `models/WZ36_BOFORS`.

## Budowa jak w modelach z gry

Układ węzłów jest taki jak w armatach od Eugen: PaK 36 (`GER/Canon.zip`) i amerykańskiej M3 37 mm (`USA/Canon.zip`). Obie mają te same nazwy węzłów.

| Węzeł | Rola |
|---|---|
| `Chassis` | oś kół, korzeń modelu |
| `Tourelle_01` | łoże górne i tarcza: pionowe płyty dolne przed kołami i dwie górne połówki pochylone o 45° do tyłu nad koła, ze szczeliną na lufę i otworem celownika |
| `Axe_Canon_01` | kołyska, opornik, zamek, pokrętła i celownik |
| `Canon_01` | lufa L/45 z hamulcem wylotowym |
| `Bras_Gauche`, `Bras_Droit` | ogony łoża rozłożone na ±25°, jak w położeniu bojowym |
| `Roue_D1`, `Roue_G1` | koła, dzieci `Chassis` |
| `Remorque_2` | ucho holownicze na końcu prawego ogona |
| `Fx_tourelle1_tir_01`, `Fx_Stress_01/02`, `FX_Fumee_Roue_D1/G1` | efekty |

Miejsca obsługi są w osobnym pliku `Boites_WZ36_BOFORS` z pomocnikami `Canon_AT`, `servant_G` i `servant_D`. Ich położenie jest takie jak w `Boites_PaK_36` i `Boites_M3_37mm`, bo oba pliki gry są identyczne.

## Animacje z M3 37 mm (26 listopada 2026 r.)

Nasza wtyczka nie eksportuje animacji. Armata korzysta więc z ośmiu animacji amerykańskiej M3 37 mm z gry (`M3_37mm_Idle`, `_Fire`, `_Deploy`, `_Fold`, `_Move`, `_Move_Back`, `_Turn_Left` i `_Turn_Right`).

| Animacja | Węzły | Ruch |
|---|---|---|
| `Fire` | `Canon_01`, `Chassis`, `Bras_*`, `Roue_*` | lufa cofa się o około 0,4 m, a cała armata podskakuje o około 7 cm |
| `Fold` / `Deploy` | `Chassis`, `Bras_*` | ogony schodzą się o około 25° i armata pochyla się o 14,5° do holowania, potem z powrotem |
| `Move`, `Move_Back`, `Turn_*` | `Chassis`, `Roue_*` | pochylona armata, obracające się koła |

Pliki animacji zapisują położenie i obrót każdego węzła w układzie całego modelu, a nie zmianę względem położenia spoczynkowego. Na przykład `Chassis` ma w każdej klatce wysokość 72,4 jednostki. Dlatego osie wszystkich animowanych węzłów naszego modelu leżą dokładnie tam, gdzie w M3 (`PIVOTS` w `scripts/spec_wz36.py`), a model zbudowano wokół nich:

- Oś kół jest 0,33 m przed początkiem układu i 0,357 m nad ziemią, jak w M3. Dlatego koła mają teraz średnicę 0,71 m; wcześniej było to 0,60 m, czyli szacunek ze zdjęć.
- Bryła zachowuje kształt Boforsa. Część może leżeć obok swojej osi, ale tylko wzdłuż osi obrotu. Koła mają rozstaw Boforsa (1,22 m), a punkty obrotu kół są szerzej, w miejscach z M3. Lufa jest na wysokości linii ognia Boforsa (0,62 m), a jej punkt obrotu jest niżej, w miejscu z M3.
- Zawiasy ogonów są blisko zawiasów M3, więc ogony składają się prawie w tym samym miejscu.
- Tarcza stoi przed kołami, jak na zdjęciach z 1939 r. i egzemplarzy muzealnych. Pierwsza wersja z pionową tarczą tuż przed osią wchodziła w koła o średnicy 0,71 m. Tarcza obraca się z `Tourelle_01` wokół punktu z M3, który leży daleko za nią, więc jej brzeg zatacza szeroki łuk. Położenie tarczy dobrano tak, żeby przy obrocie do ±15° żaden punkt płyt nie wchodził w koła. Sprawdza to skrypt zliczający punkty płyt wewnątrz kół. Dlatego obrót w grze to ±15°, jak w M3, a nie ±25° prawdziwego Boforsa.
- Model ma dokładnie te same 13 węzłów co M3 (bez `Fx_Stress_02`) i w tej samej kolejności: rodzic przed dzieckiem, najpierw siatki, potem pomocniki. Kolejność zapisuje `build_wz36.py` we właściwości sceny `eug_node_order`, a eksporter wtyczki ją stosuje. Wcześniej eksporter układał węzły alfabetycznie i gra wywalała się przy podglądzie 3D armaty. Podejrzenie: skompilowane animacje M3 wskazują węzły po numerze.

M3 pasuje do Boforsa lepiej niż PaK 36. W grze linia ognia M3 jest na wysokości 0,63 m, a PaK 36 na 0,94 m; Bofors ma 0,62 m. Prawdziwa M3 ma 0,96 m wysokości, a Bofors 1,01 m.

Jak to wygląda w ruchu, nie było jeszcze sprawdzane w grze.

## Wymiary

| Element | Wartość | Pochodzenie |
|---|---:|---|
| Długość w położeniu bojowym | 3,05 m (model 3,12 m) | Wikipedia, valka.cz |
| Szerokość | 1,22 m (koła), tarcza 1,20 m | jw. |
| Wysokość | 1,01 m | jw. |
| Lufa | L/45 = 1,665 m | jw. |
| Wysokość linii ognia | 0,62 m | polska Wikipedia |
| Rozłożenie ogonów | ±25° | jw. |
| Koła | Ø 0,71 m | wysokość osi w M3 z gry (wcześniej Ø 0,60 m, szacunek ze zdjęć) |
| Długość ogona | 1,65 m | **szacunek z długości całkowitej** |

Wygląd tarczy, kół, ogonów z płytami oporowymi i kołyski wzięto ze zdjęć egzemplarzy muzealnych z Wikimedia Commons, oglądanych w przeglądarce.

## Jednostka w grze

Wpis `WZ36_POL` w `data/units.toml`, układ `gun` w `scripts/create_battlegroup.py`.

| Co | Skąd |
|---|---|
| Dane jednostki: polska flaga, głosy, portret obsługi | polski 6-pdr z gry (`Canon_6pdr_POL`) |
| Broń i efekty strzału | M3 37 mm (`Canon_37mmAT_US`) |
| Wygląd | cały plik wyglądu M3, ze zmienionymi nazwami: nasz model i `Boites_WZ36_BOFORS`, animacje M3, polska obsługa z gry |
| Amunicja | `Ammo_Bofors_wz36_AP`, kopia pocisku M3: przebicie 6 (jak Bofors w 7TP; M3 ma 8), celność 5, 1000 m, 12 strz./min |
| Obrót w poziomie | ±15°, jak M3 w grze (prawdziwy Bofors ±25°, ale tarcza weszłaby w koła) |
| Znaczek nad jednostką | ikona armaty z gry (`Texture_RTS_H_Canon_37mmAT`) |
| Paczka | zakładka przeciwpancerna, od fazy A, po dwie armaty z ciągnikiem Loyd z gry, 3 karty |

Zapas amunicji (60) to założenie; do sprawdzenia w źródłach.

Wpisy wyglądu trafiają do plików polskiego 6-pdr w modzie (`Gfx\Units\POL\Canon\Canon_6pdr_POL*.ndf`). Model trafia do `Assets\3D\Units\POL\Canon\WZ36_BOFORS`, razem z `Boites_WZ36_BOFORS`.

Plik `Boites_WZ36_BOFORS` ładuje się przez osobny szablon z `CivMask/MeshModding`, jak każdy model z moda. Pierwsza wersja używała szablonu M3 z `CivMask/OTAN`, czyli maski paczek gry, i gra się wywaliła (26 listopada 2026 r.). Żołnierze obsługi są modelami z gry, więc zostają przy `CivMask/OTAN`.

Generowanie moda przechodzi bez błędów. W grze armata nie była jeszcze sprawdzana.

## Obsługa (żołnierze)

Żołnierzy obsługi nie trzeba modelować, bo gra dokłada ich sama. Dwaj żołnierze to osobne modele piechoty, podpięte do pomocników `servant_G` i `servant_D` z pliku `Boites_`.

Wszystkie armaty w grze mają te same animacje obsługi. Definiuje je `Units\US\Canon\Servant_Anims.ndf` (`DepictionOperator_Animation_Servant_Gauche/Droite`), a pliki `Gunner_L_*` i `Gunner_R_*` są tylko w spakowanych danych gry. Żołnierz ma animacje `Fire`, `Reload`, `Deploy`, `Fold`, `Move`, `Move_Back`, `Turn_Left`, `Turn_Right`, `Ready_to_Fire` i `Dead`.

Armata ma obsługę `ModelFile_Servant_AT_POL` (`Polish_Rifle`) i `ModelFile_Servant_AT_POL_Secondary` (`Polish_Rifle_2`) z gry. Definiuje je `Common\Gfx_infanterie.ndf`. To żołnierze Polskich Sił Zbrojnych na Zachodzie z 1944 r., w mundurach i hełmach brytyjskich, a nie w mundurach z 1939 r. z hełmem wz. 31. Obsługę z 1939 r. opisuje [PIECHOTA_1939](PIECHOTA_1939.md).

## Budowanie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$env:TK_SPEC = 'spec_wz36'
$out = 'build\wz36'
& $blender --background --factory-startup --python scripts\build_wz36.py -- $out
& $blender --background --factory-startup --python scripts\texture_tk.py -- $out
& $blender --background --factory-startup --python scripts\finalize_tk.py -- $out
```

Pliki `WZ36_BOFORS*.blend`, `.fbx`, `Boites_WZ36_BOFORS.blend`, tekstury i rendery kopiuje się potem do `models/WZ36_BOFORS`.

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
