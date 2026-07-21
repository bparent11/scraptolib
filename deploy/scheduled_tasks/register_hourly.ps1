# Scraptolib — Hourly task
# Runs every hour between 5:30 and 17:30
# Scrapes 2 days, saves all

$taskName = "ScraptoLib-Hourly"
$workDir = "C:\Users\Lenovo\Documents\2-Projets\DataScience\Scraping\scraptolib\deploy"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -Command `"Set-Location '$workDir'; `$env:SCRAPE_DAYS='2'; `$env:ACTUALLY_SAVED_DAYS_END='0'; docker compose up --build`"" `
    -WorkingDirectory $workDir

# Trigger: daily at 6:00, repeats every hour for 12h (5:30, 6:30, ..., 17:30)
$trigger = New-ScheduledTaskTrigger -Daily -At "05:30"
$trigger.Repetition = (New-ScheduledTaskTrigger -Once -At "05:30" `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration (New-TimeSpan -Hours 12)).Repetition

# Settings matching existing ScraptoLib task
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -ExecutionTimeLimit (New-TimeSpan -Days 3) `
    -MultipleInstances IgnoreNew

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
    -Description "Scraptolib: scrape 2 days, save all, every hour (5:30-17:30)"

Write-Host "Task '$taskName' registered successfully."
