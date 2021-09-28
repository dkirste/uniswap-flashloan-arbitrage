import datetime

class Logger:
    def __init__(self, _path):
        self.logfile = open(_path, "w")

    def logInfo(self, _process, _msg):
        severity = 'INFO'
        timestamp = datetime.datetime.utcnow()
        self.writeLog(timestamp, severity, _process, _msg)

    def logEvent(self, _process, _msg):
        severity = 'EVENT'
        timestamp = datetime.datetime.utcnow()
        self.writeLog(timestamp, severity, _process, _msg)

    def logError(self, _process, _msg):
        severity = 'ERROR'
        timestamp = datetime.datetime.utcnow()
        self.writeLog(timestamp, severity, _process, _msg)


    def writeLog(self, _timestamp, _severity, _process, _msg):
        if _msg[-1] != "\n":
            self.logfile.write("{0} {1} [{2}] {3}\n".format(_timestamp, _severity, _process, _msg))
        else:
            self.logfile.write("{0} {1} [{2}] {3}".format(_timestamp, _severity, _process, _msg))

if __name__ == '__main__':
    logger = Logger("test.txt")
    logger.logInfo("main", "test")