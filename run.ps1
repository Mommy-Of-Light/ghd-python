$Exports = "$PSScriptRoot\exports"
$Dest = "$PSScriptRoot\container_root\home\user"

Write-Host "Preparing workspace..."
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

# Load saves in ascending order
$saves = Get-ChildItem $Exports -File | Sort-Object Name 
$total = $saves.Count
$per_page = 9
$page = 1

function Show-Menu {
    Clear-Host
    Write-Host "==============================="
    Write-Host "         AVAILABLE SAVES"
    Write-Host "==============================="
    Write-Host ""

    $start = ($page - 1) * $per_page
    $end = [Math]::Min($start + $per_page - 1, $total - 1)

    Write-Host "Page $page ($($start+1) - $($end+1) of $total)"
    Write-Host ""

    for ($i = $start; $i -le $end; $i++) {
        $slot = $i - $start + 1
        Write-Host " $slot. $($saves[$i].Name)"
    }

    Write-Host ""
    Write-Host " 0. Run empty workspace"

    if ($total -gt $per_page) {
        Write-Host ""
        Write-Host "Commands: n=next page, p=previous page, number=select"
    }

    Write-Host ""
}

while ($true) {
    Show-Menu
    $choice = Read-Host "Select option"

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
            Write-Host "Selected: $($selected.Name)"
            Copy-Item $selected.FullName $Dest

            Push-Location $Dest
            if ($selected.Extension -eq ".zip") {
                Expand-Archive -Path $selected.Name -DestinationPath . -Force
            } else {
                tar -xf $selected.Name
            }
            Remove-Item $selected.Name
            Pop-Location
            break
        }
    }
}

Write-Host "Building Docker image..."
docker build -t console-file-manager:latest .

Clear-Host
Write-Host "Running container..."
docker-compose run --rm fm

Write-Host "Cleaning workspace..."
Get-ChildItem $Dest -Recurse | Remove-Item -Recurse -Force

Clear-Host
