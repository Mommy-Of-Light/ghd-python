$Exports = Join-Path $PSScriptRoot "exports"
$Dest    = Join-Path $PSScriptRoot "container_root/home/user"

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
    $saves = Get-ChildItem $Exports -File | Sort-Object Name
}

$total = $saves.Count
$per_page = 9
$page = 1

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "===============================" -ForegroundColor Yellow
    Write-Host "         AVAILABLE SAVES       " -ForegroundColor Yellow
    Write-Host "===============================" -ForegroundColor Yellow
    Write-Host ""

    $start = ($page - 1) * $per_page
    $end = [Math]::Min($start + $per_page - 1, $total - 1)

    Write-Host "Page $page ($($start+1) - $($end+1) of $total)"
    Write-Host ""
    Write-Host " 0. Run empty workspace" -ForegroundColor Green

    for ($i = $start; $i -le $end; $i++) {
        $slot = $i - $start + 1
        Write-Host " $slot. $($saves[$i].Name)"
    }

    if ($total -gt $per_page) {
        Write-Host ""
        Write-Host "Commands: n=next page, p=previous page, number=select"
    }

    Write-Host ""
}

# --- MAIN MENU LOOP ---
while ($true) {
    Show-Menu
    $choice = Read-Host "Select option"

    # --- AUTO-EXIT WHEN NO SAVES AND USER PRESSES ENTER ---
    if ($total -eq 0 -and [string]::IsNullOrWhiteSpace($choice)) {
        $choice = "0"
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
                try {
                    tar -xf $selected.Name
                }
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
Write-Host "`nRunning container..." -ForegroundColor Cyan
docker-compose run --rm fm

Clear-Host
Write-Host "`nCleaning workspace..." -ForegroundColor Cyan
Get-ChildItem $Dest -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Clear-Host
Write-Host "`nDone." -ForegroundColor Green
pause

Clear-Host