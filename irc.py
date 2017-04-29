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

    def raw_send(self, msg, log_this = True):
        msg = msg.strip("\r\n ")
        if log_this:
            self._logger.debug(f"SENT: {msg}")
        self._socket.send(bytes(msg + "\r\n", "UTF-8"))
    
    def user(self, username, password, realname):
        self.raw_send(f"USER {username} {self._host} {password} :{realname}", False)
    
    def nick(self, nickname):
        self.raw_send(f"NICK {nickname}")
               
    def send_message(self, target, message):
        self.raw_send(f"PRIVMSG {target} :{message}")

    def pong(self, name):
        self.raw_send(f"PONG :{name}", False)
        
    def get_lines(self):
        chunk = self._socket.recv(512).decode("UTF-8")
        return self._chunk_processor(chunk)
            
        