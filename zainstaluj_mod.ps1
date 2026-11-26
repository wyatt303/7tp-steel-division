# Instalacja moda Wrzesien1939 w Steel Division: Normandy 44 z plikow tego projektu.
#
#   zainstaluj_mod.bat                      (dwuklik albo z wiersza polecen)
#   powershell -ExecutionPolicy Bypass -File zainstaluj_mod.ps1 [-ModName Mod_Wrzesien1939] [-NoActivate] [-Yes]
#
# Kroki:
#   1. sprawdza, czy gra jest zamknieta i czy sa gra, Blender i jego Python,
#   2. jesli mod juz jest, przenosi go do build\mod_backup\<data>_<nazwa> (po potwierdzeniu),
#   3. tworzy nowy mod skryptem gry CreateNewMod.bat,
#   4. eksportuje modele z models\ nasza wtyczka (scripts\export_models.py),
#   5. dodaje jednostki i battlegroupe (scripts\create_battlegroup.py),
#   6. robi karty jednostek, ikony i obrazki broni (make_unit_cards, make_unit_icons, patch_unit_icons),
#   7. generuje mod (GenerateMod.bat),
#   8. wlacza mod w Config.ini (kopia starego pliku trafia do build\mod_backup), chyba ze podasz -NoActivate.
#
# Nic nie jest pobierane z internetu. Skrypt zmienia tylko folder moda, plik Config.ini z lista
# wlaczonych modow i folder build\ w projekcie.

param(
    [string]$GameDir = 'C:\Program Files (x86)\Steam\steamapps\common\Steel Division',
    [string]$Blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe',
    [string]$ModName = 'Mod_Wrzesien1939',
    [switch]$NoActivate,
    [switch]$Yes
)

$ErrorActionPreference = 'Stop'
$Project = $PSScriptRoot
$Mods = Join-Path $GameDir 'Mods'
$ModDir = Join-Path $Mods $ModName
$Stamp = Get-Date -Format 'yyyy-MM-dd_HHmmss'
$BackupRoot = Join-Path $Project 'build\mod_backup'
$ConfigIni = Join-Path $env:USERPROFILE 'Saved Games\EugenSystems\SteelDivision\mod\Config.ini'

function Step($text) { Write-Host ''; Write-Host "== $text" -ForegroundColor Cyan }
function Fail($text) { Write-Host "BLAD: $text" -ForegroundColor Red; exit 1 }

function Invoke-Blender([string]$Script, [string]$Done, [string[]]$Arguments) {
    $output = & $Blender --background --factory-startup --python (Join-Path $Project "scripts\$Script") -- @Arguments | Out-String
    $output -split "`r?`n" | Where-Object { $_ -match '^(EXPORTED|EXPORT_FAILED|CARD|ICON|Error|Traceback)' } | ForEach-Object { Write-Host "   $_" }
    if ($output -notmatch $Done) { Write-Host $output; Fail "$Script nie skonczyl pracy poprawnie." }
}

function Invoke-Python([string]$Script, [string]$Done, [string[]]$Arguments) {
    $output = & $Python -I (Join-Path $Project "scripts\$Script") @Arguments | Out-String
    $output -split "`r?`n" | Where-Object { $_ } | ForEach-Object { Write-Host "   $_" }
    if ($output -notmatch $Done) { Fail "$Script nie skonczyl pracy poprawnie." }
}

Step 'Sprawdzanie'
if (-not (Test-Path (Join-Path $Mods 'CreateNewMod.bat'))) { Fail "Nie znaleziono gry w $GameDir (podaj -GameDir)." }
if (-not (Test-Path $Blender)) { Fail "Nie znaleziono Blendera: $Blender (podaj -Blender)." }
$Python = Get-ChildItem (Split-Path $Blender) -Recurse -Filter python.exe -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match '\\python\\bin\\python\.exe$' } | Select-Object -First 1 -ExpandProperty FullName
if (-not $Python) { Fail 'Nie znaleziono Pythona dolaczonego do Blendera.' }
if (Get-Process -Name 'SteelDivision' -ErrorAction SilentlyContinue) { Fail 'Gra jest uruchomiona. Zamknij ja i uruchom instalacje ponownie.' }
if (-not (Test-Path (Join-Path $Project 'portret_rowecki.png'))) {
    Write-Host '   Brak portret_rowecki.png: portret battlegroupy bedzie renderem czolgu.' -ForegroundColor Yellow
}
Write-Host "   Gra:    $GameDir"
Write-Host "   Mod:    $ModDir"
Write-Host "   Blender: $Blender"

if (Test-Path $ModDir) {
    Step "Mod $ModName juz istnieje"
    $target = Join-Path $BackupRoot "${Stamp}_$ModName"
    if (-not $Yes) {
        $answer = Read-Host "Przeniesc obecny mod do $target i zainstalowac od nowa? [t/n]"
        if ($answer -notmatch '^[tTyY]') { Fail 'Przerwano, nic nie zmieniono.' }
    }
    New-Item -ItemType Directory -Force $BackupRoot | Out-Null
    & robocopy $ModDir $target /E /MOVE /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8 -or (Test-Path $ModDir)) { Fail "Nie udalo sie przeniesc starego moda (robocopy $LASTEXITCODE)." }
    Write-Host "   Stary mod jest w $target"
}

Step 'Tworzenie nowego moda (CreateNewMod.bat)'
# ".\" is needed when Windows has NoDefaultCurrentDirectoryInExePath set.
& cmd /c "cd /d `"$Mods`" && .\CreateNewMod.bat `"$ModName`"" | ForEach-Object { Write-Host "   $_" }
if (-not (Test-Path (Join-Path $ModDir 'GenerateMod.bat'))) { Fail 'CreateNewMod.bat nie utworzyl moda.' }

Step 'Eksport modeli wtyczka'
Invoke-Blender 'export_models.py' 'EXPORT_DONE' @($Project, $ModDir)

Step 'Jednostki i battlegroupa'
Invoke-Python 'create_battlegroup.py' 'BATTLEGROUP_DONE' @($ModDir)

Step 'Karty jednostek i grafiki battlegroupy'
Invoke-Blender 'make_unit_cards.py' 'CARDS_DONE' @($Project, (Join-Path $ModDir 'AssetsModding'))

Step 'Ikony jednostek i obrazki broni'
$icons = Join-Path $Project 'build\unit_icons'
Invoke-Blender 'make_unit_icons.py' 'ICONS_DONE' @($Project, $icons)
Invoke-Python 'patch_unit_icons.py' 'ICONS_PATCHED' @($ModDir, $icons, (Join-Path $BackupRoot "${Stamp}_ikony"))

Step 'Generowanie moda (GenerateMod.bat), to potrwa kilka minut'
& cmd /c "cd /d `"$ModDir`" && .\GenerateMod.bat < NUL" | Select-Object -Last 3 | ForEach-Object { Write-Host "   $_" }
if ($LASTEXITCODE -ne 0) { Fail "GenerateMod.bat zakonczyl sie kodem $LASTEXITCODE." }
if (-not (Test-Path (Join-Path $ModDir 'Gen\PC\Mesh\Pack\GfxDescriptor\Mesh_Mod.spk'))) { Fail 'GenerateMod.bat nie zbudowal modeli moda.' }

if ($NoActivate) {
    Step 'Mod nie zostal wlaczony (-NoActivate)'
} else {
    Step 'Wlaczanie moda w Config.ini'
    New-Item -ItemType Directory -Force (Split-Path $ConfigIni) | Out-Null
    if (Test-Path $ConfigIni) {
        Copy-Item $ConfigIni (Join-Path $BackupRoot "${Stamp}_Config.ini")
        $text = [IO.File]::ReadAllText($ConfigIni)
        if ($text -match '(?m)^ActivatedMods\s*=') {
            $text = [regex]::Replace($text, '(?m)^ActivatedMods\s*=\s*[^;\r\n]*', "ActivatedMods = $ModName|")
        } else {
            $text = $text.TrimEnd() + "`r`nActivatedMods = $ModName|`r`n"
        }
    } else {
        $text = "[Config]`r`nActivatedMods = $ModName|`r`n"
    }
    [IO.File]::WriteAllText($ConfigIni, $text)
    Write-Host "   ActivatedMods = $ModName| (inne mody zostaly wylaczone; kopia starego pliku w build\mod_backup)"
}

Step 'Gotowe'
Write-Host "   Uruchom gre. Battlegroupa: Warszawska Bryg. Panc-Mot / TOMASZOW 39 (alianci)."
