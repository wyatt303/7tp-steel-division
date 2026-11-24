# Piechota w umundurowaniu z 1939 r.

## Jak zbudowana jest piechota w grze

Żołnierz to jedna siatka `Soldat` (około 1400 wierzchołków) ze skinningiem na szkielecie Biped z 3ds Max. Szkielet ma 34 kości, a jeden wierzchołek może zależeć od trzech kości. Kości są zapisane w pliku jako węzły `Bip01 …`. Animacje (chód, bieg, czołganie, strzelanie, obsługa działa) są wspólne dla całej piechoty i działają na tym szkielecie. Nasza wtyczka nie eksportuje takiego skinningu, dlatego piechotę robimy przez **przemalowanie** modeli z gry, a nie przez nowe modele.

## Przemalowanie

Skrypt [`scripts/retexture_infantry.py`](../scripts/retexture_infantry.py) bierze polskich strzelców z gry (`Polish_Rifle` i `Polish_Rifle_2` z `POL/Infanterie.zip`, Polskie Siły Zbrojne na Zachodzie, 1944) i przemalowuje ich tekstury:

| Element | 1944 (gra) | 1939 (wynik) |
|---|---|---|
| Mundur | brązowy battledress | bardziej zielone khaki wz. 36 |
| Szelki, pas, ładownice | jasne parciane, brytyjskie | brązowa skóra |
| Hełm | z siatką maskującą i orłem | gładki, oliwkowy, bez oznak |
| Naszywka „POLAND” na rękawie | czerwona | usunięta |
| Plecak, chlebak, oporządzenie (`_equipment`) | parciane, oliwkowe | brązowe płótno i skóra |

Siatka, szkielet i wagi zostają bajt w bajt takie same jak w grze. W kopii pliku `.Ase2NdfBin` skrypt zmienia tylko nazwy tekstur w tabeli napisów (`STRG`), więc animacje z gry działają bez zmian. Wszystkie pozostałe sekcje pliku sprawdzono pod kątem identyczności z oryginałem.

**Ograniczenie:** kształt hełmu pozostaje brytyjski, bo jest zapisany w siatce. Hełm wz. 31 wymagałby edycji siatki z zachowaniem skinningu, a tego wtyczka jeszcze nie umie.

## Użycie

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
# POL\Infanterie.zip z Modding Assets rozpakowany do folderu, np. build\src\Infanterie
& $blender --background --factory-startup --python scripts\retexture_infantry.py -- build\src\Infanterie build\pol39
```

Wynik trafia do `build/pol39`: `POL39_Rifle`, `POL39_Rifle_2` i ich wersje `_LOW`, każda z plikami `.png`, `_SC` i `_GLO`. **Te pliki pochodzą z danych gry, więc nie trafiają do repozytorium.** Odtwarza się je skryptem.

Plik [`ndf/POL39_Infanterie.ndf`](../ndf/POL39_Infanterie.ndf) definiuje te modele dla moda, w tym `ModelFile_Servant_AT_POL39` i `_Secondary` dla obsługi działa. Aby armata wz. 36 miała obsługę z 1939 r., w `ndf/WZ36_BOFORS_Depiction.ndf` trzeba zamienić `ModelFile_Servant_AT_POL` na `ModelFile_Servant_AT_POL39`.

W grze nic z tego nie było sprawdzane.
