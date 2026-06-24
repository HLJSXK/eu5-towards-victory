# Towards Victory temporary rollback helper.
#
# Reserved for a possible EU5 1.2 rollback only. Do not call this script during
# normal 1.3+ development or validation. The active codebase should use the
# 1.3 modifier style where cost reductions are represented as positive
# *_efficiency values and cost increases as negative *_efficiency values.
#
# If the project must temporarily target EU5 1.2 again, run this helper from the
# repository root, then re-run the affected generators and validate against the
# 1.2 reference data. This script intentionally performs only the exact inverse
# of the 1.3 modifier migration.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$ModifierMap = @{
    "global_build_buildings_efficiency" = "global_build_buildings_cost"
    "global_foreign_build_buildings_efficiency" = "global_foreign_build_buildings_cost"
    "global_rural_build_buildings_efficiency" = "global_rural_build_buildings_cost"
    "global_urban_build_buildings_efficiency" = "global_urban_build_buildings_cost"
    "local_build_buildings_efficiency" = "local_build_buildings_cost"
    "stability_cost_efficiency" = "stability_cost"
    "court_spending_efficiency" = "court_spending_cost_modifier"
    "fort_maintenance_efficiency" = "fort_maintenance_cost"
    "local_fort_maintenance_efficiency" = "local_fort_maintenance_cost"
    "global_bureaucracy_maintenance_efficiency" = "global_bureaucracy_maintenance_cost_modifier"
}

$TargetFiles = @(
    "data/academy_laws.yaml",
    "data/arts_exhibition_laws.yaml",
    "data/govhouse_laws.yaml",
    "data/trade_league_laws.yaml",
    "data/victory_paths.yaml",
    "data/wonder_generic_rituals.yaml",
    "data/wonder_final_buildings.yaml",
    "data/unique_wonders.yaml",
    "src/in_game/common/static_modifiers/tv_diplomatic_alliance_parliament_modifiers.txt",
    "src/in_game/common/static_modifiers/tv_govhouse_modifiers.txt",
    "src/main_menu/common/static_modifiers/towards_victory_location_modifiers.txt",
    "src/in_game/common/laws/tv_academy_laws.txt",
    "src/in_game/common/laws/tv_arts_exhibition_laws.txt",
    "src/in_game/common/laws/tv_govhouse_laws.txt",
    "src/in_game/common/laws/tv_trade_league_laws.txt",
    "src/in_game/common/static_modifiers/towards_victory_modifiers.txt",
    "src/in_game/common/static_modifiers/tv_engineering_department_wonder_mechanics_modifiers.txt",
    "src/in_game/common/auto_modifiers/tv_engineering_department_wonder_mechanics_auto_modifiers.txt",
    "src/in_game/common/building_types/tv_engineering_department_wonder_mechanics_buildings.txt",
    "src/main_menu/common/static_modifiers/tv_engineering_department_wonder_ritual_auxiliary_location_modifiers.txt"
)

function Convert-SignedModifierValue {
    param([Parameter(Mandatory = $true)][string]$Value)

    if ($Value.StartsWith("-")) {
        return $Value.Substring(1)
    }
    if ($Value.StartsWith("+")) {
        return "-" + $Value.Substring(1)
    }
    if ($Value -match "^0(?:\.0*)?$") {
        return $Value
    }
    return "-" + $Value
}

function Read-TextPreservingBom {
    param([Parameter(Mandatory = $true)][string]$Path)

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $hasBom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
    $start = if ($hasBom) { 3 } else { 0 }
    $text = [System.Text.Encoding]::UTF8.GetString($bytes, $start, $bytes.Length - $start)
    return [PSCustomObject]@{
        Text = $text
        HasBom = $hasBom
    }
}

function Write-TextPreservingBom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][bool]$HasBom
    )

    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    $body = $utf8NoBom.GetBytes($Text)
    if (-not $HasBom) {
        [System.IO.File]::WriteAllBytes($Path, $body)
        return
    }

    $bom = [byte[]](0xEF, 0xBB, 0xBF)
    $combined = [byte[]]::new($bom.Length + $body.Length)
    [Array]::Copy($bom, 0, $combined, 0, $bom.Length)
    [Array]::Copy($body, 0, $combined, $bom.Length, $body.Length)
    [System.IO.File]::WriteAllBytes($Path, $combined)
}

$escapedKeys = ($ModifierMap.Keys | ForEach-Object { [regex]::Escape($_) }) -join "|"
$pattern = "(?<prefix>\b(?<key>$escapedKeys)\b\s*(?:[:=])\s*)(?<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+))"

foreach ($relativePath in $TargetFiles) {
    $path = Join-Path $RepoRoot $relativePath
    if (-not (Test-Path $path)) {
        continue
    }

    $source = Read-TextPreservingBom -Path $path
    $replacementCount = 0
    $newText = [regex]::Replace($source.Text, $pattern, {
        param($match)

        $script:replacementCount += 1
        $newKey = $match.Groups["key"].Value
        $oldKey = $ModifierMap[$newKey]
        $oldValue = Convert-SignedModifierValue -Value $match.Groups["value"].Value
        return $match.Groups["prefix"].Value.Replace($newKey, $oldKey) + $oldValue
    })

    if ($replacementCount -gt 0) {
        Write-TextPreservingBom -Path $path -Text $newText -HasBom $source.HasBom
        Write-Output "Reverted $relativePath ($replacementCount replacements)"
    }
}
