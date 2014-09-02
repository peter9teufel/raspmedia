import threading, time
from packages.rmnetwork import udpserver, tcpfilesocket, udpbroadcaster, messages
from constants import *

class GroupManager():
    def __init__(self, config):
        self.groupName = config["group"]
        self.memberCount = config["group_member_count"]
        self.groupMasterName = config["group_master_name"]
        self.groupMaster = config["group_master"]
        self.actions = config["actions"]

        if self.groupMaster:
            # init action handler thread
            self.actionHandler = GroupActionHandler(self.actions)
            self.actionHandler.daemon = True
            self.actionHandler.start()
            GroupMasterRoutine()


    def GroupMasterRoutine(self):
        # send member request broadcast
        msgData = messages.getMessage(GROUP_MEMBER_REQUEST)
        udpbroadcaster.sendBroadcast(msgData, True)

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

    def AddGroupMember(self, host):
        if self.groupMaster:
            self.actionHandler.AddHost(host)



class GroupActionHandler(threading.Thread):
    def __init__(self, actions):
        self.actions = actions
        self.runevent = threading.Event()
        self.updateevent = threading.Event()
        self.actionThreads = []
        self.hosts = []
        self.running = True
        # bool flag to indicate we're in startup phase
        self.startUp = True

        threading.Thread.__init__(self, name="GroupActionHandler_Thread")

    def AddHost(self, host):
        self.hosts.append(host)

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

            for action in actions:
                if "type" in action:
                    # only process actions with defined type
                    type = action["type"]
                    if type == ACTION_TYPE_ONETIME:
                        if action["event"] == ACTION_EVENT_STARTUP:
                            startupActions.append(action)
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
            if self.startUp:
                for sAction in startupActions:
                    self.actions.remove(sAction)
                    t = threading.Thread(target=self.__ProcessStartupAction, args=[action])
                    t.daemon = True
                    t.start()
                self.startUp = False

            # wait for update event
            self.updateevent.wait()
            update = True

        # stop all action threads
        for t in self.actionThreads:
            t["stop_event"].set()



    def __ProcessPeriodicAction(self, action, stopevent):
        # processes given action, call method in separate Thread!
        pType = action["periodic_type"]
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
        interval = action["periodic_interval"] * mult

        while not stopevent.is_set():
            # get action command and send it to members
            self.__SendCommandToHosts(action)
            # sleeps for the given interval, then loop proceeds - wakes up if event is set to stop thread
            stopevent.wait(interval)


    def __ProcessStartupAction(self, action):
        # delay in seconds before triggering command
        delay = action["delay"]
        time.sleep(int(delay))

        self.__SendCommandToHosts(action)

    def __SendCommandToHosts(self, action):
        # get action command and send it to members
        cmd = action["command"]
        msgData = messages.getMessage(int(cmd))
        udpbroadcaster.sendMessageToHosts(msgData, self.hosts)
