import threading, time, ast
import udpserver, tcpfilesocket, udpbroadcaster, messages
from constants import *

groupManager = None
startup = True

class GroupManager():
    def __init__(self, config):
        self.groupName = config["group"]
        self.memberCount = 0
        self.groupMasterName = config["group_master_name"]
        self.groupMaster = config["group_master"]
        self.actions = config["actions"]
        self.memberHosts = []

        self.masterHost = ""

        if self.groupMaster:
            # init action handler thread
            self.actionHandler = GroupActionHandler(self.actions)
            self.actionHandler.daemon = True
            self.actionHandler.start()
            self.GroupMasterRoutine()
        else:
            # player is a group member --> broadcast acknowledge with request flag set to false in case master is already online
            byRequest = "0"
            msgData = messages.getMessage(GROUP_MEMBER_ACKNOWLEDGE, ["-s", str(self.groupName), "-i", byRequest])
            udpbroadcaster.sendBroadcast(msgData)


    def GroupMasterRoutine(self):
        # add localhost to host list to receive commands on master player as well
        self.memberHosts.append('127.0.0.1')
        self.actionHandler.AddHost('127.0.0.1', True)
        # send member request broadcast
        msgData = messages.getMessage(GROUP_MEMBER_REQUEST, ["-s", str(self.groupName)])
        udpbroadcaster.sendBroadcast(msgData, True)

    def HandleGroupMemberRequest(self, reqGroupName, masterIP):
        if not self.groupMaster and reqGroupName == self.groupName:
            self.masterHost = masterIP
            # member of requested group --> send acknowledge
            byRequest = "1"
            msgData = messages.getMessage(GROUP_MEMBER_ACKNOWLEDGE, ["-s", str(self.groupName), "-i", byRequest])
            udpbroadcaster.sendMessage(msgData, self.masterHost)

    def HandleGroupMemberAcknowledge(self, ackGroupName, memberIP, byRequest):
        if self.groupMaster and ackGroupName == self.groupName:
            print "MEMBER ACKNOWLEDGED: ", memberIP
            if not memberIP in self.memberHosts:
                self.memberHosts.append(memberIP)
                self.memberCount += 1
            self.actionHandler.AddHost(memberIP, byRequest)

    def ScheduleActions(self):
        if self.groupMaster:
            # start thread if not already alive
            if not self.actionHandler.isAlive():
                self.actionHandler.start()
            # set runevent to trigger action scheduling
            self.actionHandler.runevent.set()

    def StopActionHandling(self):
        if self.groupMaster:
            self.actionHandler.runevent.clear()
            # set update event --> causes handler to proceed and exit loop
            self.actionHandler.updateevent.set()



class GroupActionHandler(threading.Thread):
    def __init__(self, actions):
	self.actions = []
	for action in actions:
        try:
            ad = ast.literal_eval(action)
            action = ad
        except:
            pass
	    self.actions.append(action)
        self.runevent = threading.Event()
        self.updateevent = threading.Event()
        self.actionThreads = []
        self.hosts = []
        self.running = True

        threading.Thread.__init__(self, name="GroupActionHandler_Thread")

    def AddHost(self, host, byRequest):
        if not host in self.hosts:
            self.hosts.append(host)
        # if not localhost and host added not in response to a member request --> New player online event --> check actions
        if not host == "127.0.0.1" and not byRequest:
            # check if actions are defined that should be processed when a new group host came online
            for action in self.actions:
                # convert action to dict if needed
                try:
                    actionDict = ast.literal_eval(action)
                    action = actionDict
                except:
                    pass
                if "type" in action and int(action['type']) == ACTION_TYPE_ONETIME and int(action['event']) == ACTION_EVENT_NEW_PLAYER:
                    print "New Player found --> triggering action ", action
                    # action found, handled like a startup action using the defined delay
                    t = threading.Thread(target=self.__ProcessStartupAction, args=[action])
                    t.daemon = True
                    t.start()


    def run(self):
        # wait to get started
        self.runevent.wait()
        startupActions = []
        update = False
        while self.runevent.is_set():
            if update:
                # TODO: update run of loop
                # --> check for new actions and schedule them
                # --> check for removed actions and stop them
                pass

            for action in self.actions:
                # convert action to dict if needed
                try:
                    actionDict = ast.literal_eval(action)
                    action = actionDict
                except:
                    pass
                if "type" in action:
                    # only process actions with defined type
                    type = int(action["type"])
                    if type == ACTION_TYPE_ONETIME:
                        if action["event"] == ACTION_EVENT_STARTUP:
                            print "Triggering startup action ", action
                            startupActions.append(action)
                        elif action["event"] == ACTION_TYPE_SPECIFIC_TIME:
                            t_stop = threading.Event()
                            t = threading.Thread(target=self.__ProcessSpecificTimeAction, args=(action, t_stop))
                            t.daemon = True
                            # save references to thread and stop event
                            tList = {}
                            tList["thread"] = t
                            tList["stop_event"] = t_stop
                            self.actionThreads.append(tList)
                            t.start()
                    elif type == ACTION_TYPE_PERIODIC:
                        t_stop = threading.Event()
                        t = threading.Thread(target=self.__ProcessPeriodicAction, args=(action, t_stop))
                        t.daemon = True
                        # save references to thread and stop event
                        tList = {}
                        tList["thread"] = t
                        tList["stop_event"] = t_stop
                        self.actionThreads.append(tList)
                        t.start()
                else:
                    # no type defined, action ignored
                    pass

            # periodic actions are started in threads, check if startup actions have to be handled
            global startup
            if startup:
                for sAction in startupActions:
                    index = self.actions.index(sAction)
                    del self.actions[index]
                    t = threading.Thread(target=self.__ProcessStartupAction, args=[action])
                    t.daemon = True
                    t.start()
                    startup = False

            # wait for update event
            self.updateevent.wait()
            update = True

        # stop all action threads
        for t in self.actionThreads:
            t["stop_event"].set()


    def __ProcessSpecificTimeAction(self, action, stopevent):
        startTime = datetime.time(int(action['hour']),int(action['minute']))
        while not stopevent.is_set():
            while startTime > datetime.today().time() and not stopevent.is_set(): # you can add here any additional variable to break loop if necessary
                # wait 1 second then check time again
                stopevent.wait(1)
            # wait loop passed --> trigger time for action
            self.__SendCommandToHosts(action)

    def __ProcessPeriodicAction(self, action, stopevent):
        # processes given action, call method in separate Thread!
        pType = int(action["periodic_type"])
        mult = 0
        if pType == PERIODIC_SEC:
            mult = 1
        elif pType == PERIODIC_MIN:
            mult = 60
        elif pType == PERIODIC_HOUR:
            mult = 3600
        elif pType == PERIODIC_DAY:
            mult = 86400

        # calculate interval in seconds according to periodic type
        interval = int(action["periodic_interval"]) * mult
        print "Starting periodic process of action ", action
        while not stopevent.is_set():
            # get action command and send it to members
            self.__SendCommandToHosts(action)
            # sleeps for the given interval, then loop proceeds - wakes up if event is set to stop thread
            stopevent.wait(interval)


    def __ProcessStartupAction(self, action):
        # delay in seconds before triggering command
        delay = int(action["delay"])
        print "Processing onetime action in %d seconds" % delay
        time.sleep(delay)

        self.__SendCommandToHosts(action)

    def __SendCommandToHosts(self, action):
        # get action command and send it to members
        cmd = action["command"]
        print "Sending Command to hosts: ", cmd
        print "Hosts: ", self.hosts
        msgData = messages.getMessage(int(cmd))
        udpbroadcaster.sendMessageToHosts(msgData, self.hosts)


#### ACCESS METHODS FOR CREATION AND MODIFICATION ####
def InitGroupManager(groupConfig):
    global groupManager
    groupManager = GroupManager(groupConfig)

def Schedule():
    global groupManager
    groupManager.ScheduleActions()

def ReInitGroupManager(groupConfig):
    InitGroupManager(groupConfig)
    global startup
    startup = False
    Schedule()

def MemberRequest(groupName, masterIP):
    global groupManager
    groupManager.HandleGroupMemberRequest(groupName, masterIP)

def MemberAcknowledge(groupName, memberIP, byRequest):
    global groupManager
    groupManager.HandleGroupMemberAcknowledge(groupName, memberIP, byRequest)

def UpdateActions():
    global groupManager
    groupManager.actionHandler.updateevent.set()
