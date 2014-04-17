while True:
    vPath = "/home/pi/vid";
    vidCommand = 'sudo omxplayer';
    for vidFilename in os.listdir(vPath):
        #curVid = vidCommand + ' ' + shellquote(vPath + '/' + vidFilename);
        print "Starting video:";

        print "CWD: " + cwd;
        subprocess.call([cwd + '/omxplay.sh', vPath + '/' + vidFilename]);

    # process image folder
    path = "/home/pi/img";
    imgCommand = 'sudo fbi -noverbose -readahead -blend 500 -t 4 --once -T 2';
    cmdList = ['sudo', 'fbi' , '-noverbose', '-readahead', '-blend', '500', '-t', '3', '--once', '-T', '2'];
    
    print "Starting image processing...";
    for filename in os.listdir(path):
        #cmdList.append(path + '/' + filename);
        subProc = subprocess.Popen(["sudo","fbi","--once","-noverbose","-T","2", path + "/" + filename]);
        time.sleep(4);
        subProc.kill();
        subProc.wait();
        #imgCommand += ' ' + shellquote(path + "/" + filename);
    