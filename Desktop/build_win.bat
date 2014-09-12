rmdir /S /Q build dist Release
mkdir Release

set "cwd=%~dp0"
set "destPath=%cwd%\Release"
set "distPath=dist"

pyinstaller RaspMediaApp.spec

set "distFile=%distPath%\RaspMedia Control.exe"
set "destFile=%destPath%\RaspMedia Control.exe"
copy "%distFile%" "%destFile%"

rmdir /S /Q build dist

pyinstaller RMCopyTool.spec

set "distFile=%distPath%\RaspMedia Copy Tool.exe"
set "destFile=%destPath%\RaspMedia Copy Tool.exe"
copy "%distFile%" "%destFile%"

rmdir /S /Q build dist