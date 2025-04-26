Get-ChildItem -Path "Registry::HKEY_USERS" | Where-Object { $_.Name -match 'S-1-5-21' } | ForEach-Object {
    $Path = "Registry::$($_.Name)\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"
    if (Test-Path $Path) {
        Remove-Item -Path $Path -Recurse -Force
    }
}

exit
