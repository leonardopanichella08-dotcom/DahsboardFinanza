# Minimal PowerShell static file server for frontend/
param([int]$Port = 5173)

$root = Join-Path $PSScriptRoot "frontend"
$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Start()
Write-Host "Serving $root on http://localhost:$Port"

$mime = @{
  '.html'=  'text/html; charset=utf-8'
  '.css'=   'text/css'
  '.js'=    'application/javascript'
  '.ts'=    'application/javascript'
  '.json'=  'application/json'
  '.svg'=   'image/svg+xml'
  '.png'=   'image/png'
  '.ico'=   'image/x-icon'
  '.woff2'= 'font/woff2'
}

while ($listener.IsListening) {
  $ctx = $listener.GetContext()
  $req = $ctx.Request
  $res = $ctx.Response
  $path = $req.Url.LocalPath -replace '^/+',''
  if ($path -eq '' -or $path -eq '/') { $path = 'index.html' }
  $file = Join-Path $root $path
  if (-not (Test-Path $file -PathType Leaf)) { $file = Join-Path $root 'index.html' }
  try {
    $bytes = [System.IO.File]::ReadAllBytes($file)
    $ext = [System.IO.Path]::GetExtension($file)
    $ct = $mime[$ext]; if (-not $ct) { $ct = 'application/octet-stream' }; $res.ContentType = $ct
    $res.ContentLength64 = $bytes.Length
    $res.StatusCode = 200
    $res.OutputStream.Write($bytes, 0, $bytes.Length)
  } catch {
    $res.StatusCode = 404
  }
  $res.Close()
}
