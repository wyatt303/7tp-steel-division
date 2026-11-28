# Format Ase2NdfBin

Opis ustalony przez analizę plików z narzędzia Steel Division Modding Assets. Nie jest to oficjalna dokumentacja Eugen Systems.

## Kontener

| Offset | Typ | Znaczenie |
|---:|---|---|
| `0x00` | 4 bajty | `EUG0` |
| `0x08` | 4 bajty | `CNDF` |
| `0x0C` | u32 | `0x80`, dane skompresowane |
| `0x10` | u64 | offset tabeli sekcji |
| `0x18` | u64 | rozmiar nagłówka, 40 |
| `0x20` | u64 | rozmiar całości po rozpakowaniu |
| `0x28` | u32 | rozmiar danych po rozpakowaniu |
| `0x2C` | zlib | dane, poziom 9, zakończone `Z_SYNC_FLUSH` |

Na końcu danych jest tabela `TOC0`: u32 z liczbą sekcji, a potem wpisy `nazwa(4) + u32 0 + offset(u64) + rozmiar(u64)`.

Sekcje w kolejności: `OBJE`, `TOPO`, `CHNK`, `CLAS`, `PROP`, `STRG`, `TRAN`, `IMPR`, `EXPR`.

## Obiekty

Każdy obiekt w `OBJE` to `id klasy (u32)`, a potem pola `id właściwości (u32) + typ (u32) + wartość`. Obiekt kończy znacznik `0xABABABAB`. Pola o wartości zerowej zwykle są pomijane.

| Typ | Znaczenie | Zapis |
|---:|---|---|
| `0x00` | bool | 1 bajt |
| `0x02` | int32 | 4 bajty |
| `0x03` | uint32 | 4 bajty |
| `0x05` | float32 | 4 bajty |
| `0x07` | tekst | indeks w `STRG` |
| `0x09` | referencja | `0xBBBBBBBB`, indeks obiektu, id klasy |
| `0x0B` | wektor | 3 × float32 |
| `0x0E` | trójka liczb | 3 × uint32 |
| `0x0F` | macierz | 16 × float32 |
| `0x11` | lista | liczba, potem `typ + wartość` |
| `0x12` | mapa | liczba, potem `typ klucza + klucz + typ wartości + wartość` |
| `0x14` | blob | długość i bajty, w plikach skompilowanych |

## Scena

Korzeń to `TMemASE`. Najważniejsze klasy:

- `TMemASEGeomObject`: siatka, `NodeName`, `NodeParent`, `NodeTM`, `Mesh`, `MaterialRef`.
- `TMemASEHelperObject`: punkt pomocniczy.
- `TMemASEMesh`: wierzchołki, ściany, normalne oraz mapy `TFaceMap` i `TVertexMap`.
- `TMemASEMaterial1`: parametry `EugSurfaceMaterial`, w tym tekstury i tagi gąsienic.
- Materiał z podmateriałami: `TMemASEMaterial1` z `Classe = Multi\Sub-Object` i lista `SubMaterialList` z kolejnymi `TMemASEMaterial` (od drugiego z `SubNo`). Trójkąt wybiera podmateriał polem `MESH_MTLID` w `TMemASEMeshFace` (brak pola to 0). Tak pojazdy z gry mają szyby, zob. [SZYBY.md](SZYBY.md).
- `TMemASEPhysiqueModifier`: Skin gąsienic i macierze pozy.
- `TMemASETMAnimation`: 101 próbek, co 160 ticków.

## Konwencje

- Układ gry: X do przodu, Y w lewo, Z do góry.
- Wierzchołki są zapisane w przestrzeni świata.
- Macierze pozy kół mają translację `(x, -y, z)`.
- Skala czołgów to około 203 jednostki na metr.
- `Canon_0N` w oryginalnych modelach zawsze jest siatką.

## Pułapka: UV gąsienic

W 70 z 72 sprawdzonych oryginalnych gąsienic UV mieści się w zakresie 0–1. Oś U biegnie w poprzek, V wzdłuż.

Gdy UV wyszło poza ten zakres, `ModGen` wybrał format wierzchołków `TexCoord0_2f` z tagiem `TexCoord0_HasTiling`. Plik kompilował się bez błędu, ale gra padała przy rysowaniu jednostki. Po przywróceniu zakresu 0–1 `ModGen` użył formatu `TexCoord0_2wn` i awaria zniknęła.
