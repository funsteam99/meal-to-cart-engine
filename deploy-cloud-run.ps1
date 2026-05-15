param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [string]$ServiceName = "freshwise",
    [string]$Region = "asia-east1",
    [string]$Model = "gemini-2.5-flash",
    [string]$AnalyticsDataset = "freshwise_analytics",
    [string]$EventsTable = "events",
    [string]$SecretName = "freshwise-google-api-key",
    [string]$SecretsFile = ".streamlit/secrets.toml",
    [switch]$AllowUnauthenticated = $true,
    [switch]$EnableAnalytics,
    [switch]$GrantAnalyticsIam
)

$ErrorActionPreference = "Stop"

function Resolve-Gcloud {
    $defaultPath = Join-Path $env:LOCALAPPDATA "Google\Cloud SDK\google-cloud-sdk\bin\gcloud.ps1"
    if (Test-Path $defaultPath) {
        return $defaultPath
    }

    $cmd = Get-Command gcloud -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    throw "gcloud was not found. Install Google Cloud CLI, then rerun this script."
}

function Read-StreamlitSecret {
    param(
        [string]$Path,
        [string]$Key
    )

    if (-not (Test-Path $Path)) {
        return ""
    }

    $pattern = "^\s*$([regex]::Escape($Key))\s*=\s*['""](.+)['""]\s*$"
    foreach ($line in Get-Content $Path) {
        if ($line -match $pattern) {
            return $Matches[1]
        }
    }

    return ""
}

$gcloud = Resolve-Gcloud

& $gcloud config set project $ProjectId

& $gcloud services enable `
    run.googleapis.com `
    cloudbuild.googleapis.com `
    secretmanager.googleapis.com `
    generativelanguage.googleapis.com

if ($EnableAnalytics) {
    & $gcloud services enable bigquery.googleapis.com
}

$apiKey = Read-StreamlitSecret -Path $SecretsFile -Key "api_key"
if ($apiKey) {
    $secretExists = $true
    & $gcloud secrets describe $SecretName --project $ProjectId *> $null
    if ($LASTEXITCODE -ne 0) {
        $secretExists = $false
    }

    if ($secretExists) {
        $apiKey | & $gcloud secrets versions add $SecretName --project $ProjectId --data-file=-
    } else {
        $apiKey | & $gcloud secrets create $SecretName --project $ProjectId --data-file=-
    }
}

& $gcloud secrets describe $SecretName --project $ProjectId *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Secret '$SecretName' does not exist. Add api_key to $SecretsFile or create the secret manually before deploying."
}

$projectNumber = (& $gcloud projects describe $ProjectId --format "value(projectNumber)").Trim()
$runServiceAccount = "$projectNumber-compute@developer.gserviceaccount.com"
& $gcloud secrets add-iam-policy-binding $SecretName `
    --project $ProjectId `
    --member "serviceAccount:$runServiceAccount" `
    --role roles/secretmanager.secretAccessor

if ($EnableAnalytics -and $GrantAnalyticsIam) {
    & $gcloud projects add-iam-policy-binding $ProjectId `
        --member "serviceAccount:$runServiceAccount" `
        --role roles/bigquery.dataEditor
}

$authFlag = if ($AllowUnauthenticated) { "--allow-unauthenticated" } else { "--no-allow-unauthenticated" }
$envVars = "DEFAULT_MODEL=$Model"
if ($EnableAnalytics) {
    $envVars = "$envVars,BIGQUERY_PROJECT_ID=$ProjectId,BIGQUERY_DATASET=$AnalyticsDataset,BIGQUERY_EVENTS_TABLE=$EventsTable"
}

& $gcloud run deploy $ServiceName `
    --source . `
    --region $Region `
    --port 8080 `
    $authFlag `
    --set-env-vars $envVars `
    --set-secrets GOOGLE_API_KEY="${SecretName}:latest" `
    --quiet
