import ImageUtil, platform

if platform.system() == "Windows":
    import Wind32DeviceDetector
elif platform.system() == "Darwin":
    import MacDriveDetector
