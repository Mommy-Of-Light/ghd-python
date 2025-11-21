$Exports = Join-Path $PSScriptRoot "exports"
$Dest = Join-Path $PSScriptRoot "container_root/home/user"

Write-Host "`nPreparing workspace..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

# Docker detection
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "`nERROR: Docker is not installed or not in PATH." -ForegroundColor Red
    pause
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "`nERROR: docker-compose is not installed or not in PATH." -ForegroundColor Red
    pause
    exit 1
}

# Load save files
$saves = @()
if (Test-Path $Exports) {
    $saves = Get-ChildItem $Exports -File | Sort-Object Name -Descending
}

$total = $saves.Count
$per_page = 9
$page = 1

# ===== THEME =====
$Theme = @{
    HeaderFG = "White"
    HeaderBG = "DarkRed"

    TitleFG  = "Yellow"
    TitleBG  = "DarkBlue"

    MenuFG   = "White"
    MenuBG   = "Black"

    FooterFG = "Magenta"
    FooterBG = "DarkBlue"
}

function Write-FullLine {
    param(
        [string] $Text = "",
        [ConsoleColor] $Foreground = "White",
        [ConsoleColor] $Background = "Black"
    )

    $width = $Host.UI.RawUI.WindowSize.Width
    $padded = $Text.PadRight($width).Substring(0, $width)

    Write-Host $padded -ForegroundColor $Foreground -BackgroundColor $Background
}

function Show-Header {
    param([string]$Title = "")

    Write-FullLine "" -Foreground $Theme.HeaderFG -Background $Theme.HeaderBG
    Write-FullLine (" $Title ") -Foreground $Theme.HeaderFG -Background $Theme.HeaderBG
    Write-FullLine "" -Foreground $Theme.HeaderFG -Background $Theme.HeaderBG
}

function Show-Footer {
    param([string]$Text = "")

    Write-FullLine "" -Foreground $Theme.FooterFG -Background $Theme.FooterBG
    Write-FullLine (" $Text ") -Foreground $Theme.FooterFG -Background $Theme.FooterBG
    Write-FullLine "" -Foreground $Theme.FooterFG -Background $Theme.FooterBG
}

function Write-BoxLine {
    param(
        [string] $Text,
        [ConsoleColor] $Foreground = "White",
        [ConsoleColor] $Background = "Black"
    )

    $width = $Host.UI.RawUI.WindowSize.Width - 2
    $padded = $Text.PadRight($width).Substring(0, $width)

    Write-Host "│$padded│" -ForegroundColor $Foreground -BackgroundColor $Background
}

function Show-BoxTitle {
    param([string]$Title)

    $width = $Host.UI.RawUI.WindowSize.Width - 2
    Write-Host ("┌" + ("─" * $width) + "┐") -ForegroundColor $Theme.TitleFG
    Write-BoxLine $Title -Foreground $Theme.TitleFG
    Write-Host ("└" + ("─" * $width) + "┘") -ForegroundColor $Theme.TitleFG
}

# Add new menu option in Show-Menu
function Show-Menu {
    Clear-Host

    Show-Header "AVAILABLE SAVES"
    Show-BoxTitle "Select a workspace to load or delete a save"

    $start = ($page - 1) * $per_page
    $end = [Math]::Min($start + $per_page - 1, $total - 1)

    Write-Host " Page $page  ($($start+1) - $($end+1) of $total )" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "  0. Run empty workspace" -ForegroundColor Green

    for ($i = $start; $i -le $end; $i++) {
        $slot = $i - $start + 1
        Write-Host ("  $slot. " + $saves[$i].Name) -ForegroundColor $Theme.MenuFG
    }

    Write-Host ""
    Write-Host "  d <number>  Delete save file" -ForegroundColor Red

    if ($total -gt $per_page) {
        Write-Host ""
        Write-Host "Commands:  n=next page,  p=previous page,  number=select, d <num|" -ForegroundColor Yellow
    }

    Show-Footer "Press Enter to continue"
}

# MAIN LOOP MODIFICATION
while ($true) {
    Show-Menu
    $choice = Read-Host "Select option"

    if ($total -eq 0 -and [string]::IsNullOrWhiteSpace($choice)) {
        $choice = "0"
    }

    # Handle deletion: d <numbers> or da (delete all)
    if ($choice -match "^da$") {
        Write-Host "Deleting ALL saves..." -ForegroundColor Red
        Get-ChildItem $Exports -File | Remove-Item -Force
        $saves = @()
        $total = 0
        continue
    }

    # Multi or single deletion: d 1,2,5
    if ($choice -match "^d\s+(.+)$") {
        $items = $Matches[1] -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^[0-9]+$' }
        foreach ($n in $items) {
            $global = ($page - 1) * $per_page + ([int]$n) - 1
            if ($global -lt $total -and $global -ge 0) {
                $target = $saves[$global]
                Write-Host "Deleting save: $($target.Name)" -ForegroundColor Red
                Remove-Item $target.FullName -Force
            }
        }
        # Reload
        $saves = Get-ChildItem $Exports -File | Sort-Object Name -Descending
        $total = $saves.Count
        continue
    }

    if ($choice -eq "0") { break }
    if ($choice -eq "n") {
        $maxpage = [Math]::Ceiling($total / $per_page)
        if ($page -lt $maxpage) { $page++ }
        continue
    }
    if ($choice -eq "p") {
        if ($page -gt 1) { $page-- }
        continue
    }

    if ($choice -match '^[1-9]$') {
        $global = ($page - 1) * $per_page + [int]$choice - 1
        if ($global -lt $total) {
            $selected = $saves[$global]
            Write-Host "`nSelected: $($selected.Name)" -ForegroundColor Cyan

            Copy-Item $selected.FullName $Dest -Force

            Push-Location $Dest
            if ($selected.Extension -eq ".zip") {
                Expand-Archive -Path $selected.Name -DestinationPath . -Force
            }
            else {
                try { tar -xf $selected.Name }
                catch {
                    Write-Host "ERROR extracting file with tar." -ForegroundColor Red
                    pause
                    exit 1
                }
            }
            Remove-Item $selected.Name -Force
            Pop-Location

            break
        }
    }
}


Clear-Host
Write-Host "`nBuilding Docker image..." -ForegroundColor Cyan
docker build -t console-file-manager:latest .
Clear-Host

Clear-Host
Write-Host "`nRunning container..." -ForegroundColor Cyan
docker-compose run --rm fm
Clear-Host

Clear-Host
Write-Host "`nCleaning workspace..." -ForegroundColor Cyan
Get-ChildItem $Dest -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Clear-Host

Clear-Host
Write-Host "`nDone." -ForegroundColor Green
Clear-Host