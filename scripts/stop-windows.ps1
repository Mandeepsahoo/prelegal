$ErrorActionPreference = "SilentlyContinue"

docker rm -f prelegal | Out-Null
Write-Output "Prelegal stopped."
