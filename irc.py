import socket

class ChunkProcessor:
 
	def __init__(self):
		self._buffer = ""
 
	def __call__(self, chunk):
	    self._buffer += chunk	    
	    lines = self._buffer.split("\r\n")
	    lines = list(map(str.strip, lines))
	    self._buffer = lines.pop()
	    lines = list(filter(None, lines))	
	    return lines


class Connection:
    
    def __init__(self, host, port, logger):
        self._socket = socket.socket()
        self._socket.connect((host, port))
        self._logger = logger
        self._chunk_processor = ChunkProcessor()
        self._host = host

    def _raw_send(self, msg, log_this = True):
        if log_this:
            stripped = msg.strip("\r\n ")
            self._logger.debug(f"SENT: {stripped}")
        self._socket.send(bytes(msg, "UTF-8"))
    
    """ ========================================================================
        public methods
    ======================================================================== """
    
    def user(self, username, password, realname):
        self._raw_send(f"USER {username} {self._host} {password} :{realname} \r\n", False)
    
    def nick(self, nickname):
        self._raw_send(f"NICK {nickname}\r\n")
               
    def send_message(self, target, message):
        self._raw_send(f"PRIVMSG {target} :{message}\r\n")

    def join_channel(self, channel):
        self._raw_send(f"JOIN :{channel}\r\n")

    def pong(self, name):
        self._raw_send(f"PONG :{name}\r\n", False)
        
    def get_lines(self):
        chunk = self._socket.recv(512).decode("UTF-8")
        return self._chunk_processor(chunk)
    
    def quit(self, message):
        self._raw_send(f"QUIT :{message}\r\n")

        
        