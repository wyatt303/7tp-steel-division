# Lista modeli

Wszystkie modele mają wersje High, Mid i Low, tekstury i eksport wtyczką bez błędów. **Żaden z nowych modeli nie był jeszcze sprawdzany w grze.** W grze sprawdzono tylko oba 7TP. Liczby trójkątów podano w kolejności High / Mid / Low.

## Czołgi i tankietki

| Model | Folder | Wzór z gry | Trójkąty | Opis |
|---|---|---|---|---|
| 7TP jednowieżowy (Bofors 37 mm) | `7TP_jednowiezowy_Bofors` | czołgi Eugen | 7618 / 1888 / 488 | [MODEL_7TP](MODEL_7TP.md) |
| 7TP dwuwieżowy (2 × ckm wz. 30) | `7TP_dwuwiezowy_wz30` | czołgi Eugen | 7648 / 2000 / 584 | [MODEL_7TP](MODEL_7TP.md) |
| Tankietka TK-3 | `TK3` | Universal Carrier | 9304 / 1572 / 492 | [MODEL_TK](MODEL_TK.md) |
| Tankietka TKS | `TKS` | Universal Carrier | 9428 / 1636 / 496 | [MODEL_TK](MODEL_TK.md) |
| Tankietka TKS z nkm 20 mm (as Orlik) | `TKS20` | Universal Carrier | 9308 / 1656 / 496 | [MODEL_TKS20_ORLIK](MODEL_TKS20_ORLIK.md) |

## Samochody pancerne

| Model | Folder | Wzór z gry | Trójkąty | Opis |
|---|---|---|---|---|
| wz. 34 z ckm Hotchkiss | `WZ34_CKM` | SdKfz 221 | 5584 / 2108 / 460 | [MODEL_WZ34](MODEL_WZ34.md) |
| wz. 34 z armatką 37 mm | `WZ34_37` | SdKfz 221 | 5324 / 2088 / 452 | [MODEL_WZ34](MODEL_WZ34.md) |
| wz. 28 (półgąsienicowy) z ckm | `WZ28_CKM` | SdKfz 250 | 5732 / 1704 / 536 | [MODEL_WZ28](MODEL_WZ28.md) |
| wz. 28 (półgąsienicowy) z armatką 37 mm | `WZ28_37` | SdKfz 250 | 5516 / 1684 / 528 | [MODEL_WZ28](MODEL_WZ28.md) |

## Samoloty

| Model | Folder | Wzór z gry | Trójkąty | Opis |
|---|---|---|---|---|
| PZL P.11c (myśliwiec) | `P11C` + `P11C_train` | Fieseler Storch, Ju 87D | 4788 / 1960 / 800 | [MODEL_P11](MODEL_P11.md) |
| PZL.23B Karaś (bombowiec lekki) | `PZL23B` + `PZL23B_train` | Ju 87D | 4928 / 2440 / 1008 | [MODEL_KARAS_LOS](MODEL_KARAS_LOS.md) |
| PZL.37B Łoś (bombowiec średni) | `PZL37B` + `PZL37B_train` (podwozie, 840) | Ju 88 | 4912 / 2388 / 1220 | [MODEL_KARAS_LOS](MODEL_KARAS_LOS.md) |

## Pojazdy i działa

| Model | Folder | Wzór z gry | Trójkąty | Opis |
|---|---|---|---|---|
| Motocykl Sokół 1000 z wózkiem i rkm wz. 28 | `SOKOL1000` | BMW R75 | 4450 / 2956 / 1096 | [MODEL_SOKOL](MODEL_SOKOL.md) |
| Ciężarówka Polski Fiat 621L z plandeką i bez | `PF621L`, `PF621L_OPEN` | Opel Blitz | 4908 / 2364 / 824 (bez plandeki 4676 / 2336 / 804) | [MODEL_PF621](MODEL_PF621.md) |
| Armata plot 40 mm wz. 36 (Bofors) | `B40WZ36` + `Boites_B40WZ36`, generowany z modelu gry do `build/` | Bofors 40 mm z gry (przemalowany) | 6766 / 1703 / 595 | [MODEL_B40WZ36](MODEL_B40WZ36.md) |
| Armata ppanc 37 mm wz. 36 (Bofors) | `WZ36_BOFORS` + `Boites_WZ36_BOFORS` | M3 37 mm (osie i animacje) | 1780 / 1036 / 264 | [MODEL_WZ36](MODEL_WZ36.md) |

## Piechota

| Model | Gdzie | Wzór z gry | Opis |
|---|---|---|---|
| Strzelcy w mundurach z 1939 r. (`POL39_Rifle`, `POL39_Rifle_2`) | `build/pol39`, odtwarzane skryptem, poza repozytorium | `Polish_Rifle`, `Polish_Rifle_2` (przemalowanie) | [PIECHOTA_1939](PIECHOTA_1939.md) |

## Pliki NDF

| Plik | Zawartość |
|---|---|
| `ndf/POL39_Infanterie.ndf` | piechota z 1939 r., także jako obsługa działa |

## Jeszcze nie zrobione

- **Samochód pancerny wz. 29 Ursus:** brakuje dobrego widoku z boku.
