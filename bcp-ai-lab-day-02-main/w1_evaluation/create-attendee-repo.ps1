param(
    [Parameter(Mandatory = $true)] [string]$AttendeeId,
    [Parameter(Mandatory = $true)] [string]$RequirementId,
    [Parameter(Mandatory = $true)] [string]$IssueUrl,
    [Parameter(Mandatory = $true)] [string]$RequirementText,
    # La carpeta CONTENEDORA de los 3 templates (no uno de ellos, no esta
    # carpeta de bcp-ai-lab-day-02): la que tiene adentro, una al lado de
    # otra, workshop-auth-backend-template, workshop-login-frontend-template
    # y workshop-requirements-api-template.
    [Parameter(Mandatory = $true)] [string]$TemplatesRoot,
    [string]$Destination = "generated"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $TemplatesRoot)) {
    throw "TemplatesRoot '$TemplatesRoot' no existe."
}
$sourceRoot = (Resolve-Path $TemplatesRoot).Path
foreach ($name in @("workshop-auth-backend-template", "workshop-login-frontend-template", "workshop-requirements-api-template")) {
    if (-not (Test-Path (Join-Path $sourceRoot $name))) {
        throw "TemplatesRoot '$sourceRoot' no contiene '$name'."
    }
}
$destinationRoot = $Destination
if (-not (Test-Path $destinationRoot)) {
    New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null
}
$targetRoot = Join-Path (Resolve-Path $destinationRoot).Path "attendee-$AttendeeId"

if (Test-Path $targetRoot) { throw "Destination already exists: $targetRoot" }
New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $targetRoot "caso-login") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $targetRoot "caso-login\backend"), (Join-Path $targetRoot "caso-login\frontend"), (Join-Path $targetRoot "caso-login\requirements-api") -Force | Out-Null
Get-ChildItem (Join-Path $sourceRoot "workshop-auth-backend-template") -Force | Where-Object Name -ne ".git" | Copy-Item -Destination (Join-Path $targetRoot "caso-login\backend") -Recurse
Get-ChildItem (Join-Path $sourceRoot "workshop-login-frontend-template") -Force | Where-Object Name -ne ".git" | Copy-Item -Destination (Join-Path $targetRoot "caso-login\frontend") -Recurse
Get-ChildItem (Join-Path $sourceRoot "workshop-requirements-api-template") -Force | Where-Object Name -ne ".git" | Copy-Item -Destination (Join-Path $targetRoot "caso-login\requirements-api") -Recurse
Copy-Item (Join-Path $PSScriptRoot "EVALUACION-W1.md") (Join-Path $targetRoot "EVALUACION-W1.md")
New-Item -ItemType Directory -Path (Join-Path $targetRoot "docs"), (Join-Path $targetRoot "prompts"), (Join-Path $targetRoot ".github\skills\login-skill"), (Join-Path $targetRoot "tools"), (Join-Path $targetRoot "mcp"), (Join-Path $targetRoot "tests\evidence") -Force | Out-Null

$evaluationPath = Join-Path $targetRoot "EVALUACION-W1.md"
$evaluation = Get-Content $evaluationPath -Raw
$evaluation = $evaluation.Replace("{{REQUIREMENT_ID}}", $RequirementId).Replace("{{GITHUB_ISSUE_URL}}", $IssueUrl).Replace("{{FUNCTIONAL_REQUIREMENT}}", $RequirementText)
Set-Content -Path $evaluationPath -Value $evaluation -Encoding utf8
@("# Requirements", "", "Requirement ID: $RequirementId", "Issue: $IssueUrl", "", $RequirementText) | Set-Content (Join-Path $targetRoot "docs\requirements.md") -Encoding utf8
git -C $targetRoot init --quiet
Write-Output "Created attendee repository: $targetRoot"