rmdir /S /Q build
rmdir /S /Q dist
rmdir /S /Q Release
TIMEOUT 2
md Release

set "cwd=%~dp0"
set "destPath=Release"
set "distPath=dist"

start /wait pyinstaller RMImageTransfer.spec

set "distFile=%distPath%\RaspMedia Image Transfer.exe"
set "destFile=%destPath%\RaspMedia Image Transfer.exe"
copy "%distFile%" "%destFile%"

rmdir /S /Q build dist

start /wait pyinstaller RaspMediaApp.spec

set "distFile=%distPath%\RaspMedia Control.exe"
set "destFile=%destPath%\RaspMedia Control.exe"
copy "%distFile%" "%destFile%"

rmdir /S /Q build dist

start /wait pyinstaller RMCopyTool.spec

set "distFile=%distPath%\RaspMedia Copy Tool.exe"
set "destFile=%destPath%\RaspMedia Copy Tool.exe"
copy "%distFile%" "%destFile%"

rmdir /S /Q build dist
