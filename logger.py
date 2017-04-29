import os
import time

class Logger:
    
    # constants
    _INFO    = 1
    _WARNING = 2
    _ERROR   = 4
    _DEBUG   = 8
    NORMAL  = _INFO | _WARNING | _ERROR
    ALL     = _DEBUG | NORMAL

    # log prefixes
    _level = {}
    _level[_DEBUG]   = "DEBUG    ?"
    _level[_INFO]    = "INFO     :"
    _level[_WARNING] = "WARNING !!"
    _level[_ERROR]   = "ERROR   ##"

    # default logging level
    level = NORMAL
    
    # if true, every log message will be printed out too
    echo = False
    
    """ Logs to a specific file
    
        :param  logname:    A string that will be used to create 
                            the ./logs/logname.log file
    
    """
    def __init__(self, logname):
        basepath = os.path.dirname(os.path.realpath(__file__))
        logpath = basepath + "/logs/"
        os.makedirs(logpath, exist_ok = True)
        filename = logpath + logname + ".log"
        self._file = open(filename, "a", 1, encoding = "utf-8")
        print("self._file.encoding", self._file.encoding)

    # actual writing member
    def __write(self, level, *msg):
        if level & self.level:
            leveltext = self._level[level]
            msg = " ".join(str(m) for m in msg)
            if self.echo:
                print(leveltext, msg, flush = True)
            date = time.strftime("%Y-%m-%d %H:%M:%S")
            msg = " ".join((date, leveltext, msg, "\n"))
            self._file.write(msg)
    
    # shorthand for Logger.info()
    def __call__(self, *msg):
        self.__write(self._INFO, *msg)
    
    # proxy members
    def info(self, *msg):
        self.__write(self._INFO, *msg)
    
    def error(self, *msg):
        self.__write(self._ERROR, *msg)
    
    def warning(self, *msg):
        self.__write(self._WARNING, *msg)
        
    def debug(self, *msg):
        self.__write(self._DEBUG, *msg)
        
        