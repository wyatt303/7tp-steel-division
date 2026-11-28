# Szyby pojazdów

## Jak robi to Eugen

Sprawdzone 28 listopada 2026 r. na Oplu Blitzu, Kübelwagenie, Jeepie, Bedfordzie, GMC i M5A1 z paczki do modowania. Wszystkie mają szyby zrobione tak samo:

- Szyba jest częścią siatki `Chassis`, nie osobnym węzłem. Materiał kadłuba to `Multi\Sub-Object` z dwoma podmateriałami. Trójkąty szyby mają `MESH_MTLID 1`, reszta 0.
- Podmateriał szyby ma `transparency = True`, `twoSided` wyłączone i teksturę przezroczystości (`OpacityTexture`) w miejscu mapy normalnych.
- Tekstury szyby (`vitre*.png`, w Bedfordzie `glass*.png`) są jednolite, 4 × 4 lub 64 × 64 px:

| Tekstura | Opel, Jeep, Kübelwagen, GMC, M5A1 | Bedford |
|---|---:|---:|
| kolor | 0 (czarny) | 114 |
| przezroczystość `_A` | 76 (kryje ok. 30%) | 98 |
| połysk `_GLO` | 246 | 234 |
| odbłysk `_SC` | 76 | 79 |

- Szyba to jedna warstwa trójkątów bez grubości, zwrócona na zewnątrz: przednia szyba Jeepa ma 2 trójkąty, Kübelwagena 6, M5A1 4, wszystkie szyby kabiny Opla 41. Za szybą jest wnętrze kabiny.

## Jak robimy to my

- `scripts/glass.py` tworzy materiał `M_Vitre` z `eug_transparent` i cztery własne tekstury 4 × 4 o wartościach jak u Opla: `<STEM>_Vitre.png`, `_SC`, `_GLO`, `_A`.
- Skrypt budowy dodaje tafle jako osobne obiekty `Vitre_*`. `texture_tk.py` ich nie maluje i chowa je przy wypalaniu cieni, żeby nie zaciemniały wnętrza.
- `finalize_tk.py` dołącza je do `Chassis` jako drugi slot materiału.
- Wtyczka od wersji 1.3.0 zapisuje siatkę z kilkoma slotami jako `Multi\Sub-Object` z `MESH_MTLID`, a materiał z `eug_transparent` z przezroczystością i bez mapy normalnych. Importer czyta to z powrotem.

| Model | Szyby |
|---|---|
| Polski Fiat 621L (oba warianty) | przednia (2 tafle) i w drzwiach; kabina pusta w środku, z ławką, deską rozdzielczą i kierownicą |
| C2P | przednia (2 tafle) |

Tylne okienko Fiata i okienka w plandece (celuloid) zostają malowane w `GLASS_BOXES`.

Struktura eksportu jest taka sama jak u Opla (sprawdzone odczytem pliku). W grze przezroczystości jeszcze nie sprawdzano.
