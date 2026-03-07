@echo off
setlocal

set MSBUILD26="C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\amd64\MSBuild.exe"
set MSBUILD22="C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"

echo === Building VS 2026 extension ===
%MSBUILD26% "%~dp0src\InaVsTheme.csproj" -p:Configuration=Release -restore -v:minimal
if errorlevel 1 goto :error

echo.
echo === Building VS 2022 extension ===
%MSBUILD22% "%~dp0vs22\InaVsTheme22.csproj" -p:Configuration=Release -restore -v:minimal
if errorlevel 1 goto :error

echo.
echo === Build complete ===
echo VS 2026: src\bin\Release\InaVsTheme.vsix
echo VS 2022: vs22\bin\Release\InaVsTheme-VS2022.vsix
goto :eof

:error
echo Build FAILED
exit /b 1
