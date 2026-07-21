# Scraptolib — Weekly task
# Runs every 24 hours
# Scrapes 35 days, saves the last 21

$taskName = "ScraptoLib-Weekly"
$workDir = "C:\Users\Lenovo\Documents\2-Projets\DataScience\Scraping\scraptolib\deploy"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -Command `"Set-Location '$workDir'; `$env:SCRAPE_DAYS='35'; `$env:ACTUALLY_SAVED_DAYS_END='21'; docker compose up --build`"" `
    -WorkingDirectory $workDir

# Trigger: daily at 03:00
$trigger = New-ScheduledTaskTrigger -Daily -At "03:00"

# Settings matching existing ScraptoLib task
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -ExecutionTimeLimit (New-TimeSpan -Days 3) `
    -MultipleInstances IgnoreNew `
    -DeleteExpiredTaskAfter (New-TimeSpan -Days 30)

$settings.RunOnlyIfNetworkAvailable = $false
$settings.RunOnlyIfIdle = $false
$settings.StartWhenAvailable = $false
$settings.RestartCount = 3
$settings.RestartInterval = "PT1M"

# Principal: run as Lenovo, only when logged on, highest privileges
$principal = New-ScheduledTaskPrincipal `
    -UserId "Lenovo" `
    -LogonType S4U `
    -RunLevel Highest

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Scraptolib: scrape 35 days, save last 21, every 24h"

Write-Host "Task '$taskName' registered successfully."
