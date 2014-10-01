#! /bin/sh

# clean up first
echo "Cleaning up old build and release directories..."
rm -rf build dist Release
mkdir Release

# get current directory and destination path
cwd=$(pwd)
destPath="$cwd/Release"
distPath="dist"

##### BUILD RASPMEDIA IMAGE TRANSFER #####
echo ""
echo "Compiling RaspMedia Image Transfer..."
pyinstaller RMImageTransfer.spec

# copy built version to tools directory
echo ""
echo "Making release file for RaspMedia Image Transfer..."
distFile="$distPath/RaspMedia Image Transfer.app"
destFile="$destPath/RaspMedia Image Transfer.app"
cp -r "$distFile" "$destFile"


# remove build directories
echo "Cleaning up..."
rm -rf build dist

##### BUILD RASPMEDIA CONTROL #####
echo ""
echo "Compiling RaspMedia Control..."
pyinstaller RaspMediaApp.spec

# copy built version to tools directory
echo ""
echo "Making release file for RaspMedia Control..."
distFile="$distPath/RaspMedia Control.app"
destFile="$destPath/RaspMedia Control.app"
cp -r "$distFile" "$destFile"

# modify plist file of app to be foreground
# echo "Updating Info.plist for RaspMedia Control Release..."
# plist="$destFile/Contents/Info"
# defaults write "$plist" LSBackgroundOnly -string NO
# plist="$plist.plist"
# plutil -convert xml1 "$plist"

# remove build directories
echo "Cleaning up..."
rm -rf build dist

##### BUILD RASPMEDIA COPY TOOL #####
echo ""
echo "Compiling RaspMedia Copy Tool..."
pyinstaller RMCopyTool.spec

# copy built version to tools directory
echo ""
echo "Making release file for RaspMedia Copy Tool..."
distFile="$distPath/RaspMedia Copy Tool.app"
destFile="$destPath/RaspMedia Copy Tool.app"
cp -r "$distFile" "$destFile"

# modify plist file of app to be foreground
# echo "Updating Info.plist for RaspMedia Copy Tool Release..."
# plist="$destFile/Contents/Info"
# defaults write "$plist" LSBackgroundOnly -string NO
# plist="$plist.plist"
# plutil -convert xml1 "$plist"

# remove build directories
echo "Cleaning up..."
rm -rf build dist


echo "Build done, bye bye..."
