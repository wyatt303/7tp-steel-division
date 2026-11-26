# Edytor jednostek

Mała strona w przeglądarce do szybkiej zmiany napisów i cen naszych jednostek w modzie, z podglądem okna jednostki w stylu gry. Pliki są w [`tools/edytor_jednostek`](../tools/edytor_jednostek).

## Uruchomienie

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.3\5.3\python\bin\python.exe' -I tools\edytor_jednostek\server.py
```

Potem otwórz w przeglądarce `http://127.0.0.1:8744/`. Serwer działa tylko na tym komputerze. Zatrzymujesz go klawiszami Ctrl+C w oknie, w którym go uruchomiono. Domyślnie edytuje `Mod_7TP_Battlegroup`. Inny mod albo port podajesz jako argumenty: `server.py <folder moda> <port>`.

Python z Blendera wystarcza, nic nie trzeba doinstalowywać.

## Co można zmieniać

| Co | Gdzie w modzie |
|---|---|
| Nazwa jednostki | `GameData\Localisation\MODDING.csv`, token z `NameInMenuToken` |
| Nazwy broni | ten sam plik, token z pola `Name` amunicji. Nazwa jest wspólna dla wszystkich jednostek z tą bronią. |
| Napisy battlegroupy (nazwa, przydomek, opisy, podpowiedzi) | ten sam plik, przycisk „Napisy battlegroupy” |
| Cena | `ProductionPrice` w `UniteDescriptor.ndf`, tylko w naszych jednostkach |

Nasze jednostki to te, które `create_battlegroup.py` dopisał po swoim znaczniku. Nowe jednostki dodane tym skryptem pojawią się w edytorze same.

Prędkość, pancerz, wytrzymałość, rok, przebicie (AP) i zasięg broni są tylko do odczytu, w podglądzie. Zasięg w grze to wartość `PorteeMaximale` z NDF podzielona przez 5 (np. 3000 → 600 m dla MG34). Celności i szybkostrzelności podgląd nie pokazuje, bo gra liczy je z kilku pól.

## Zapis i generowanie

1. **Zapisz** sprawdza teksty: bez nowych linii i bez cudzysłowu `"`. Cena musi być od 0 do 1000. Przed zmianą kopiuje zmieniane pliki do `build\mod_backup\edytor_<data_godzina>`.
2. **Generuj mod** uruchamia `GenerateMod.bat` w folderze moda. Gra musi być zamknięta, edytor to sprawdza. Generowanie trwa kilka minut.
3. Po wygenerowaniu uruchom grę od nowa.

## Ograniczenia

- Duży obrazek i karta w podglądzie to nasze pliki z `AssetsModding`. Jeśli są starsze niż model (np. sprzed przemalowania), podgląd pokaże stary wygląd. Tak samo będzie w grze.
- Kolor znaczka nad jednostką jest przybliżony, bo gra barwi go kolorem gracza.
- Podgląd nie jest dokładną kopią okna gry: układ i czcionki są przybliżone.
