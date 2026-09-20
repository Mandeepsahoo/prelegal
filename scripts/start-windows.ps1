$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$ImageName = "prelegal"
$ContainerName = "prelegal"

docker build -t $ImageName .
docker rm -f $ContainerName 2>$null | Out-Null
docker run -d --name $ContainerName -p 8000:8000 --env-file .env $ImageName

Write-Output "Prelegal is running at http://localhost:8000"
Start-Process "http://localhost:8000"
