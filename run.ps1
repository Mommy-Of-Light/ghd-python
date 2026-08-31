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

function Display-Delay {
    param(
        [string[]] $DelayText,
        [int] $DelayTime,
        [ScriptBlock] $CallbackDisplayer = { param($t) Write-Host $t },
        [int] $LoopCount = 1,
        [bool] $InMillisecond = $true
    )

    $loops = $LoopCount * $DelayText.Count

    for ($i = 0; $i -lt $loops; $i++) {
        Clear-Host
        
        $text = $DelayText[$i % $DelayText.Count]
        & $CallbackDisplayer $text   # invoke callback with the text
        
        if ($InMillisecond) {
            Start-Sleep -Milliseconds $DelayTime
        }
        else {
            Start-Sleep -Seconds $DelayTime
        }
    }
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

    Show-Header "AVAILABLE SAVES FROM NEWEST TO OLDEST"
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
    Write-Host "  q. Quit" -ForegroundColor Yellow
    Write-Host "  d <number>  Delete save file" -ForegroundColor Red
    Write-Host "  da  Delete all save files" -ForegroundColor Red

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

    if ($choice -eq "0" -or $choice -eq "") { break }
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

    if ($choice -eq "q") {
        Display-Delay `
            -DelayText @("Preparing closing", "Preparing closing.", "Preparing closing..", "Preparing closing...") `
            -DelayTime 250 `
            -CallbackDisplayer { param($t) Show-BoxTitle $t } `
            -LoopCount 1 `
            -InMillisecond $true
        Clear-Host
        exit 0
    }
}

Display-Delay `
    -DelayText @("Preparing the installation", "Preparing the installation.", "Preparing the installation..", "Preparing the installation...") `
    -DelayTime 250 `
    -CallbackDisplayer { param($t) Show-BoxTitle $t } `
    -LoopCount 1 `
    -InMillisecond $true
Clear-Host

Clear-Host
Write-Host "`nBuilding Docker image..." -ForegroundColor Cyan
docker build -t console-file-manager:latest .
Clear-Host

Clear-Host
Write-Host "`nRunning container..." -ForegroundColor Cyan
docker compose run --rm fm
Clear-Host

Display-Delay `
    -DelayText @("Preparing Cleaning", "Preparing Cleaning.", "Preparing Cleaning..", "Preparing Cleaning...") `
    -DelayTime 250 `
    -CallbackDisplayer { param($t) Show-BoxTitle $t } `
    -LoopCount 3 `
    -InMillisecond $true
Clear-Host

Clear-Host
Read-Host "Execution finished. Press Enter to clean workspace and exit."

Write-Host "`nCleaning workspace..." -ForegroundColor Cyan
Get-ChildItem $Dest -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Read-Host "Workspace cleaned. Press Enter to continue."

Write-Host "`nCleaning Docker images..." -ForegroundColor Cyan
docker image rm console-file-manager:latest -f
Read-Host "Docker image removed. Press Enter to continue."

Write-Host "`nCleaning dangling Docker images..." -ForegroundColor Cyan
$dangling = docker images -f "dangling=true" -q
if ($dangling) {
    docker rmi $dangling -f
    Read-Host "Dangling images removed. Press Enter to continue."
}
else {
    Write-Host "No dangling images found." -ForegroundColor Green
    Read-Host "Press Enter to continue."
}

Write-Host "`nCleaning unused Docker volumes..." -ForegroundColor Cyan
$volumes = docker volume ls -qf "dangling=true"
if ($volumes) {
    docker volume rm $volumes
    Read-Host "Unused volumes removed. Press Enter to continue."
}
else {
    Write-Host "No unused volumes found." -ForegroundColor Green
    Read-Host "Press Enter to continue."
}

Write-Host "`nCleaning unused Docker networks..." -ForegroundColor Cyan
$networks = docker network ls -qf "dangling=true"
if ($networks) {
    docker network rm $networks
    Read-Host "Unused networks removed. Press Enter to continue."
}
else {
    Write-Host "No unused networks found." -ForegroundColor Green
    Read-Host "Press Enter to continue."
}

Write-Host "`nCleaning stopped containers..." -ForegroundColor Cyan
$containers = docker ps -a -q -f "status=exited"
if ($containers) {
    docker rm $containers -f
    Read-Host "Stopped containers removed. Press Enter to continue."
}
else {
    Write-Host "No stopped containers found." -ForegroundColor Green
    Read-Host "Press Enter to continue."
}

Write-Host "`nCleaning build cache..." -ForegroundColor Cyan
docker builder prune -f
Read-Host "Build cache cleaned. Press Enter to continue."

Write-Host "`nAll cleanup operations completed." -ForegroundColor Green
Read-Host "Press Enter to exit."
Clear-Host