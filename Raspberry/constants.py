	# UDP config
UDP_HOST = ""
UDP_PORT = 60001
UDP_BROADCAST_HOST = '<broadcast>'

# tcp tmp directory path
TCP_TEMP = "/home/pi/.tmp"

STARTUP_IF_TIMEOUT = 30
TYPE_RASPMEDIA_PLAYER = 0x03

# file types in TCP message
FILE_TYPE_IMAGE = 0xd0
FILE_TYPE_VIDEO = 0xd1

# predefined message flags
PLAYER_BOOT_COMPLETE = 0xeeee
SERVER_REQUEST = 0xffff
SERVER_REQUEST_ACKNOWLEDGE = 0xfffe
PLAYER_REBOOT = 0xefff
PLAYER_UPDATE_ERROR = 0xffee

CONFIG_UPDATE = 0x00
PLAYER_START = 0x01
PLAYER_STOP = 0x02
PLAYER_UPDATE = 0x03
FILELIST_REQUEST = 0x04
FILELIST_RESPONSE = 0x05
CONFIG_REQUEST = 0x06
DELETE_FILE = 0x07
PLAYER_IDENTIFY = 0x08
PLAYER_IDENTIFY_DONE = 0x09
PLAYER_RESTART = 0x10
DELETE_ALL_IMAGES = 0x11
# new message flags GROUP change
GROUP_CONFIG_REQUEST = 0x12
GROUP_CONFIG_UPDATE = 0x13
GROUP_CONFIG_ADD_ACTION = 0x14
GROUP_MEMBER_REQUEST = 0x15
GROUP_MEMBER_ACKNOWLEDGE = 0x16
GROUP_CONFIG = 0x17
GROUP_DELETE = 0x18
GROUP_CONFIG_ACTION_DELETE = 0x19
# new flags for IMAGE TRANSFER APP
FILE_DATA_REQUEST = 0x20
PLAYER_PAUSE = 0x21
DISK_INFO_REQUEST = 0x22

# flag for message to play file number
PLAYER_START_FILENUMBER = 0xb0


# Action types
ACTION_TYPE_ONETIME = 0xc1
ACTION_TYPE_PERIODIC = 0xc2
# type of periodic interval
PERIODIC_SEC = 0xc3
PERIODIC_MIN = 0xc4
PERIODIC_HOUR = 0xc5
PERIODIC_DAY = 0xc6
# type for specific time action
ACTION_TYPE_SPECIFIC_TIME = 0xc7

# Action events
ACTION_EVENT_STARTUP = 0xd1
ACTION_EVENT_NEW_PLAYER = 0xd2


WIFI_CONFIG = 0xf1
WIFI_AUTH_WPA = 0xf2
WIFI_AUTH_WEP = 0xf3
WIFI_AUTH_NONE = 0xf4

# msg interpreter result
INTERPRETER_SUCCESS = 0xf00
INTERPRETER_SERVER_REQUEST = 0xf01
INTERPRETER_ERROR = 0xf02
INTERPRETER_FILELIST_REQUEST = 0xf03
INTERPRETER_FILELIST_RESPONSE = 0xf04

# player states
PLAYER_STARTED = 0x80
PLAYER_STOPPED = 0x81
PLAYER_STATE_UNDEFINED = 0x82
PLAYER_STATE_SWITCHING = 0x83
PLAYER_PAUSED = 0x84

# filetypes
SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
SUPPORTED_VIDEO_EXTENSIONS = ('.mp4', '.m4v', '.mpeg', '.mpg', '.mpeg1', '.mpeg4', '.avi')
