#! /bin/sh

# clean up first
echo "Cleaning up old build and release directories..."
rm -rf build dist Release
mkdir Release

# get current directory and destination path
cwd=$(pwd)
destPath="$cwd/Release"
distPath="dist"


##### BUILD RASPMEDIA CONTROL #####
echo "Compiling RaspMedia Control..."
pyinstaller RaspMediaApp.spec

# copy built version to tools directory
echo "Making release file for RaspMedia Control..."
distFile="$distPath/RaspMedia Control"
destFile="$destPath/RaspMedia Control"
cp -r "$distFile" "$destFile"

# remove build directories
echo "Cleaning up..."
rm -rf build dist

##### BUILD RASPMEDIA COPY TOOL #####
echo "Compiling RaspMedia Copy Tool..."
pyinstaller RMCopyTool.spec

# copy built version to tools directory
echo "Making release file for RaspMedia Copy Tool..."
distFile="$distPath/RaspMedia Copy Tool"
destFile="$destPath/RaspMedia Copy Tool"
cp -r "$distFile" "$destFile"

# remove build directories
echo "Cleaning up..."
rm -rf build dist


echo "Build done, bye bye..."
