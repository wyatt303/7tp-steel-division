# Model 7TP

## Warianty

| | Jednowieżowy | Dwuwieżowy |
|---|---|---|
| Folder | `models/7TP_jednowiezowy_Bofors` | `models/7TP_dwuwiezowy_wz30` |
| Nazwa plików | `TP7_JW` | `TP7_DW` |
| Uzbrojenie na modelu | armata Bofors 37 mm wz. 37, ckm wz. 30 | 2 × ckm wz. 30 |
| Wieża | seryjna dwubroniowa z niszą | dwie cylindryczne typu Vickers |
| Trójkąty High / Mid / Low | 7618 / 1888 / 488 | 7648 / 2000 / 584 |

Tekstury mają 2048 px w High, 1024 px w Mid i 256 px w Low. Wersja High ma też osobne tekstury gąsienic 256 px. Mapy to `Diffuse`, `_GLO`, `_SC` i `_NM` w konwencji DirectX, a gąsienice dodatkowo `_A`.

**Malowanie.** Jednowieżowy ma ogólny trójbarwny kamuflaż z 1936 r. (schemat `1936` w `scripts/texture_7tp.py`). Dwuwieżowy ma schemat `cieszyn38` według planszy „7TP (dwuwieżowy) z 3. Batalionu Pancernego, Cieszyn, październik 1938 roku”. Są tam duże plamy piaskowe (głównie dół kadłuba), żółtozielone i brązowe (głównie wieże) oraz białe godło batalionu, skaczący chart, na zewnętrznym boku obu wież. Kolory odczytano z planszy: (214, 203, 168), (150, 152, 70) i (118, 94, 61). Przyciemniono je współczynnikiem 0,6 jak resztę palety, bo druk jest dużo jaśniejszy niż farba w grze. Kształt plam nie odwzorowuje planszy plama w plamę, a sylwetka charta jest uproszczona. Schemat można wybrać zmienną `TP_SCHEME` (`1936` albo `cieszyn38`).

## Wymiary

| Element | Wartość | Pochodzenie |
|---|---:|---|
| Długość kadłuba | 4,091 m | rysunek szkieletu |
| Szerokość kadłuba | 1,626 m | rysunek szkieletu |
| Wysokość kadłuba | 1,097 m | rysunek szkieletu |
| Dach przedziału bojowego | 1,265 m | rysunek szkieletu |
| Dach przedziału silnika | 1,145 m | rysunek szkieletu |
| Pochylenie tylnej płyty | 30° | rysunek szkieletu |
| Prześwit | 0,38 m | dane techniczne, zgodne z przekrojem |
| Szerokość gąsienicy | 267 mm | dane techniczne |
| Długość całkowita | ok. 4,6 m | dane techniczne |
| Szerokość całkowita | 2,4 m | dane techniczne |
| Średnica kół jezdnych | ok. 0,28 m | **szacunek z przekroju** |
| Rozstaw kół jezdnych | ok. 0,40 m | **szacunek z przekroju** |

## Założenia i niepewności

- Rysunek z wymiarami dotyczy kadłuba wersji dwuwieżowej. Te same wymiary przyjęto dla jednowieżowej.
- Źródła różnią się co do wymiarów całkowitych: 4,60–4,88 m długości i 2,12–2,30 m wysokości.
- Położenie wież, kół i część detali odczytano ze skanów.
- Oba wózki są swoimi lustrzanymi odbiciami, tak jak na rysunku z boku. Przedni ma wygięte ramię skierowane do przodu, a resor do tyłu. Tylny ma ramię do tyłu, a resor do przodu, więc oba resory są zwrócone do środka czołgu. Do 26 listopada 2026 r. oba wózki miały ramię do przodu, przez co tylny był odwrócony.
- Kółka podtrzymujące gąsienicę są tarczowe, o średnicy 0,2 m, z gumową obręczą, wklęsłą tarczą i piastą, jak na zdjęciach. Mają taki sam wierzch jak wcześniejsze walce 0,15 m, więc gąsienica leży tak samo. W wersji Mid są prostymi walcami.
- Karabin maszynowy obok armaty w 7TP jednowieżowym ma okrągłą, krótką osłonę z wklęsłym czołem i otworem na lufę, po lewej stronie armaty, jak na zdjęciach i rysunku przodu wieży. Armata ma podobną grubszą tuleję.
- Wersje High mają przez to około 7600 trójkątów, ponad zalecane 7000.
- Kolory kamuflażu z 1936 r. są przybliżeniem, bo źródła opisują je słownie. Układ plam jest przykładowy.

## Znane ograniczenia

- Wahacze, resory i wózki są częścią kadłuba, więc nie uginają się razem z kołami.
- Wersja Low dwuwieżowego ma 584 trójkąty, powyżej zalecanych 500.
- Wersje High są blisko limitu około 7000 trójkątów.
- Modele nie mają jeszcze własnych wpisów jednostek, broni ani ikon.

## Uzbrojenie i zapas amunicji w grze

Wartości są wpisane w `scripts/create_battlegroup.py`, więc każda instalacja moda je odtwarza.

| | Dane historyczne | W grze |
|---|---|---|
| Bofors wz. 37, zapas | 80 nabojów, głównie przeciwpancerne, przydział odłamkowych niepewny | 70 AP + 10 HE |
| Bofors wz. 37, szybkostrzelność | ok. 10 strz./min w praktyce | 1 strzał co 6 s, czyli 10 r/m |
| ckm wz. 30 w 7TP jednowieżowym | 3960 nabojów, 12 taśm po 330 | 12 serii po 330 = 3960 |
| ckm wz. 30 w 7TP dwuwieżowym | ok. 6000 nabojów na oba karabiny | 2 × 9 serii po 330 = 5940 |
| ckm wz. 30, szybkostrzelność | ok. 600 strz./min teoretycznie, 400–450 w praktyce | 341 r/m, wyrównane do karabinów w grze (MG34 326) |

Gra liczy szybkostrzelność ze wzoru: naboje na serię × 60 / (przerwa między seriami + (strzały w serii − 1) × przerwa między strzałami). Historyczne 400–450 strz./min (przerwa 1,5 s) dawało 430, najwięcej ze wszystkich karabinów w grze, bo gra mocno zaniża ich szybkostrzelność. Dla balansu ckm ma przerwę 2 s: 330 × 60 / (10 + 24 × 2) = 341, czyli poziom MG34. Prędkość 22/58 km/h i maskowanie 1,5 też są wyrównane do lekkich czołgów w grze (docs/POROWNANIE_CZOLGOW.md). Celność, przebicie i zasięg zostały z wzorców (armata 37 mm M5 i M1919), oprócz przebicia Boforsa ustawionego na AP 6.

## Źródła

- Rysunki techniczne i schematy z dostarczonych skanów czasopism. Skany nie są częścią repozytorium.
- [Zdjęcia 7TP w Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:7TP)
- [7TP w polskiej Wikipedii](https://pl.wikipedia.org/wiki/7TP)
- [Kampania Wrześniowa 1939: 7TP](http://www.1939.pl/uzbrojenie/polskie/pojazdy/7tp/index.html)
- [Tank Archives: 7TP](https://www.tankarchives.com/2016/10/7tp-polish-vickers.html)
- [Malowanie polskich pojazdów pancernych 1939](https://lakiernik.com.pl/renowacje-pojazdow/barwy-wrzesnia-czyli-slow-o-malowaniu-polskich-pojazdow-pancernych-1939-r/)
- [Opis 7TP, derela.pl](https://derela.pl/7tp_pl.htm): zapas amunicji
- [Czołg 7TP, dobroni.pl](https://dobroni.pl/artykul/czolg-7tp-lekki-n565964): szybkostrzelność Boforsa
- [Ckm wz. 30, Muzeum im. Orła Białego](https://muzeum.skarzysko.pl/encyklopedia/item/518-ciezki-karabin-maszynowy-wz-30-browning.html): szybkostrzelność ckm
