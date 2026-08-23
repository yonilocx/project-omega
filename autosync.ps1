Write-Host "Auto-sync active. Watching for file changes..." -ForegroundColor Green

while ($true) {
    # Check if there are any modified files
    $status = git status --porcelain
    
    if ($status) {
        Write-Host "Changes detected! Syncing to GitHub..." -ForegroundColor Yellow
        
        # Add, commit, and push
        git add .
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        git commit -m "Auto-sync update: $timestamp"
        git push origin main
        
        Write-Host "Sync complete." -ForegroundColor Green
    }
    
    # Wait 10 seconds before checking again (prevents spamming your CPU)
    Start-Sleep -Seconds 10
}
