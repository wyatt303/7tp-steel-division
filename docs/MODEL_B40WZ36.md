# Armata przeciwlotnicza 40 mm wz. 36 (Bofors)

Polski wz. 36 to ta sama szwedzka armata Bofors 40 mm L/60 na tym samym dwuosiowym łożu co brytyjski QF 40 mm Mk I/III. Dlatego model nie jest budowany od zera. Bierzemy Boforsa 40 mm z paczki do modowania (`USA/Canon.zip`, `Canon/Bofors_40mm`) i przemalowujemy go w polski kamuflaż z 1936 r.

## Jak powstaje

Skrypt `scripts/build_bofors40.py` uruchamia instalator przy każdej instalacji moda (krok „Modele z danych gry”). Wynik trafia do `build/generated/B40WZ36`, a nie do `models/`, bo pochodzi z danych gry i nie może trafić do repozytorium.

1. Rozpakowuje z paczki wersje High, Mid i Low oraz `Boites_Bofors_40mm`.
2. Importuje je importerem [`import_ase2ndfbin.py`](IMPORT_MODELI.md). Zostają nazwy węzłów, punkty obrotu i ich kolejność, więc animacje Boforsa z gry pasują bez zmian.
3. Przemalowuje teksturę koloru każdej wersji. Tam, gdzie oryginał pokazuje oliwkową farbę, kolor zastępuje kamuflaż z 1936 r. Używa tych samych barw i wzoru co nasze modele, liczonych z położenia każdego teksela na modelu. Cieniowanie i szczegóły oryginału zostają, a oliwkowe pola zachowują jasność oryginalnej farby. Opony, metal, mosiężne łuski i oznaczenia zostają bez zmian. Farbą okazało się 86–88% pokrytej tekstury.
4. Tekstury normalnych, połysku, specular i przezroczystości kopiuje bez zmian pod nową nazwą.
5. Kilka UV wersji Low wychodzi minimalnie poza zakres 0–1 (do 1,0018). Skrypt przycina je, bo nasz eksporter takich nie przepuszcza.
6. Zapisuje `B40WZ36.blend`, `_MID`, `_LOW`, `Boites_B40WZ36.blend` i render do kart.

| Wersja | Trójkąty | Tekstura koloru |
|---|---:|---:|
| High | 6766 | 2048 × 2048 |
| Mid | 1703 | 1024 × 1024 |
| Low | 595 | 256 × 256 |

## Jednostka w grze (27 listopada 2026 r.)

Wpis `B40WZ36_POL` w `data/units.toml`, układ `gun`.

| Co | Skąd |
|---|---|
| Dane jednostki, broń, obsługa, animacje | polski Bofors z gry (`DCA_Bofors_POL`). Jego wygląd korzysta z modeli i animacji amerykańskiego (`DCA_Bofors_US`), więc `depiction_replace` podmienia modele na nasze. |
| Amunicja | `Ammo_Bofors40_wz36_HE` (cele naziemne) i `_AA` (samoloty): kopie amunicji Boforsa z gry z polską nazwą, serie po 8 nabojów, 0,6 s między strzałami. Zapas 240 nabojów (30 serii), jak w grze. |
| Obrót | pełny (gra zapisuje 2π) |
| Wytrzymałość, prędkość, pancerz | 8, 10 km/h, `Canon`, jak w grze |
| Cena | 70 (polski Bofors z gry z 1941 r. kosztuje 80) |
| Znaczek nad jednostką | ikona Boforsa z gry (`Texture_RTS_H_DCA_Bofors`) |
| Paczka | zakładka przeciwlotnicza (`DCA`), od fazy A, jedna armata z ciągnikiem gąsienicowym C2P na kartę ([MODEL_C2P](MODEL_C2P.md)), 2 karty |

Generowanie moda przechodzi bez błędów. W grze armata nie była jeszcze sprawdzana.

## Różnice względem prawdziwego wz. 36

Geometria to model brytyjsko-amerykański z gry. Jeśli polski wz. 36 różnił się szczegółami (celowniki, siedzenia, osłony), trzeba to sprawdzić na zdjęciach i dopiero wtedy zmieniać model.
