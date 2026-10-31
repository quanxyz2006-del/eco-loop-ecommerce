$ErrorActionPreference = "Stop"

$dataRoot = "D:\CodexData\eco-loop"
$composeEnv = Join-Path $dataRoot "compose.env"
$directories = @(
    $dataRoot,
    (Join-Path $dataRoot "mysql"),
    (Join-Path $dataRoot "caddy\data"),
    (Join-Path $dataRoot "caddy\config"),
    (Join-Path $dataRoot "migration")
)

foreach ($directory in $directories) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}

if (Test-Path -LiteralPath $composeEnv) {
    throw "Đã có cấu hình $composeEnv; giữ nguyên để tránh ghi đè bí mật/dữ liệu hiện tại."
}

function New-HexSecret([int]$byteCount) {
    $buffer = [byte[]]::new($byteCount)
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generator.GetBytes($buffer) } finally { $generator.Dispose() }
    return [System.BitConverter]::ToString($buffer).Replace("-", "").ToLowerInvariant()
}

$lines = @(
    "MYSQL_DATABASE=eco_loop",
    "MYSQL_USER=eco_loop",
    "MYSQL_PASSWORD=$(New-HexSecret 32)",
    "MYSQL_ROOT_PASSWORD=$(New-HexSecret 32)",
    "SECRET_KEY=$(New-HexSecret 64)",
    "SUPERADMIN_EMAIL=quanxyz2006@gmail.com",
    "SITE_ADDRESS=:80",
    "HTTP_PORT=8080",
    "HTTPS_PORT=8443"
)

[System.IO.File]::WriteAllLines($composeEnv, $lines, [System.Text.UTF8Encoding]::new($false))
Write-Output "Đã tạo cấu hình bí mật và thư mục dữ liệu tại $dataRoot (không in giá trị bí mật)."
