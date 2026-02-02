# ==============================================================================
# DCKP Solver - Build Script (Windows PowerShell)
# ==============================================================================
# Uso: .\scripts\build.ps1 [-Clean] [-Verbose]
# ==============================================================================

param(
    [switch]$Clean,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$BuildDir = Join-Path $ProjectRoot "build"

function Write-Banner {
    param([string]$Message, [string]$Color = "Cyan")
    Write-Host ""
    Write-Host ("=" * 50) -ForegroundColor $Color
    Write-Host $Message -ForegroundColor $Color
    Write-Host ("=" * 50) -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-Host "`n>> $Message" -ForegroundColor Yellow
}

# Banner inicial
Write-Banner "DCKP Solver v2.0 - Build" "Cyan"

# Limpar build se solicitado
if ($Clean -and (Test-Path $BuildDir)) {
    Write-Step "Limpando diretorio de build..."
    Remove-Item -Recurse -Force $BuildDir
}

# Criar diretório de build
if (!(Test-Path $BuildDir)) {
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

Set-Location $BuildDir

try {
    # Configurar CMake
    Write-Step "Configurando CMake..."
    $cmakeArgs = @("..", "-G", "MinGW Makefiles", "-DCMAKE_BUILD_TYPE=Release")
    if ($Verbose) {
        $cmakeArgs += "-DCMAKE_VERBOSE_MAKEFILE=ON"
    }
    cmake @cmakeArgs

    if ($LASTEXITCODE -ne 0) {
        throw "Falha na configuracao do CMake!"
    }

    # Compilar
    Write-Step "Compilando..."
    $jobs = [Environment]::ProcessorCount
    cmake --build . --config Release -- -j$jobs

    if ($LASTEXITCODE -ne 0) {
        throw "Falha na compilacao!"
    }

    # Sucesso
    Write-Banner "Build concluido com sucesso!" "Green"
    Write-Host "Executavel: build\bin\dckp_solver.exe" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Banner "ERRO: $_" "Red"
    exit 1
}
finally {
    Set-Location $ProjectRoot
}
