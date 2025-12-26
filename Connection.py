import socket
import json
import threading
import time

import pygame

import BoardWindow
import GameConfig

import SoundControl



def thread_done_notification():
    MY_THREAD_DONE_EVENT = pygame.USEREVENT + 1
    event = pygame.event.Event(MY_THREAD_DONE_EVENT, {"msg": "thread finished"})
    pygame.event.post(event)

class Connection:
    # Local UDP settings
    _LOCAL_IP = "0.0.0.0"
    _LOCAL_PORT = 5000
    BROADCAST_IP = "255.255.255.255"
    

    # Peer UDP settings will be set when initializing the Connection
    def __init__(self):
        print("Initializing Connection...")
        self.is_connected = False
        self._peer_ping_lost = False
        self._waiting = True
        self.local_ip = self._LOCAL_IP
        self.local_port = self._LOCAL_PORT
        self.peer_ip = None
        self.peer_port = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind((self.local_ip, self.local_port))
        self.is_timeout = False
        self.has_existing_room = False

    def disconnect(self):
        self.is_connected = False
    # Send a message to the peer connected
    def send_message(self, message):
        data = json.dumps(message).encode("utf-8")
        self.sock.sendto(data, (self.peer_ip, self.peer_port))

    # Start a thread to receive messages
    def receive_thread_start(self, handle_message):
        threading.Thread(target=self.__receive_message, args=(handle_message,), daemon=True).start()

    # Private method to receive messages
    def __receive_message(self, handle_message):
        self.sock.settimeout(None)
        while self.is_connected:
            data, addr = self.sock.recvfrom(1024)
            try:
                message = json.loads(data.decode("utf-8"))
                handle_message(message)
            except json.JSONDecodeError:
                continue
            
        thread_done_notification()
        return
    
    # Start a thread to detect lost connection
    def lost_detection_start(self):
        threading.Thread(target=self.__lost_detection, daemon=True).start()
    
    
    
    # Private method to detect lost connection
    # ping the peer every 10 seconds
    # if no response for 3 times, consider the peer lost
    def __lost_detection(self):

        lost_count = 0
        while self.is_connected:
            self._peer_ping_lost = True
            msg = json.dumps({"type": "lost_ping"}).encode("utf-8")
            print(self.peer_ip,self.peer_port)
            self.sock.sendto(msg, (self.peer_ip, self.peer_port))
            threading.Event().wait(2)
            if self._peer_ping_lost:
                lost_count += 1
                print("lost "+ str(lost_count))
            else:
                lost_count = 0
                print("not lost")
            if lost_count >= 3:
                # Handle lost connection
                print("lost connection")
                pass
        thread_done_notification()
        return

    # Private method to get local IP address
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 这里连接一个外网 IP（谷歌 DNS），不会真的发数据
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def handle_message(self, message):
        if message.get("type") == "lost_ping":
            self._peer_ping_lost = False
        elif message.get("type") == "chat":
            # Handle chat message
            BoardWindow.chat_box.add_message(message.get("sender"), message.get("msg"),message.get("timestamp"))
        elif message.get("type") == "move":
            # Handle move message
            BoardWindow.place_stone(message.get("x"), message.get("y"),message.get("player"))
            BoardWindow.current_player = BoardWindow.WHITE_PLAYER if message.get("player") == BoardWindow.BLACK_PLAYER else BoardWindow.BLACK_PLAYER
            BoardWindow.board_enabled = True

        elif message.get("type") == "win":
            # Handle win message
            BoardWindow.winner = message.get("winner")
            BoardWindow.board_enabled = False
            if BoardWindow.get_this_player() == BoardWindow.winner:
                SoundControl.win_sound.play()
            else:
                SoundControl.lose_sound.play()

        
    # Be called when the game is ready to start.
    # Messages include game actions and chat messages.
    def start(self):
        self.lost_detection_start()
        self.receive_thread_start(self.handle_message)

    # detects if there is any existing room with the same id
    # return true if there is an existing room
    
    def existing_room_detection(self,room_id):
        threading.Thread(target=self.__existing_room_detection, args=(room_id,), daemon=True).start()
    
    def __existing_room_detection(self,room_id):
        BROADCAST_IP = "255.255.255.255"
        self.sock.sendto(json.dumps({
            "type": "existing_room_detection",
            "room_id": room_id,
            "ip": self.get_local_ip()
            }).encode("utf-8"), (BROADCAST_IP, self._LOCAL_PORT))
        timeout = 2.0
        start_time = time.time()
        self.is_timeout = False
        
        has_existing_room = False
        self._waiting = True
        while time.time()-start_time <= timeout and self._waiting:
            # print(time.time()-start_time)
            self.sock.settimeout(0.5)
            try:
                data, addr = self.sock.recvfrom(1024)
                response = json.loads(data.decode("utf-8"))
                if response.get("type") == "existing_room_response":
                    has_existing_room = True
                    break
            except socket.timeout:
                continue
            except json.JSONDecodeError:
                continue
        self.sock.settimeout(None)
        if time.time()-start_time > timeout:
            self.is_timeout = True
        self.has_existing_room = has_existing_room
        thread_done_notification()
        return

    def wait_for_joining(self, room_id):
        self._waiting = True
        threading.Thread(target=self.__wait_for_joining, args=(room_id,), daemon=True).start()
    # A while true loop waiting for a peer to join the room with the given room_id
    def __wait_for_joining(self, room_id):
        
        while self._waiting and not self.is_connected:
            self.sock.settimeout(1.0)
            try:
                data, addr = self.sock.recvfrom(1024)
                response = json.loads(data.decode("utf-8"))
                print(response)
                if response.get("type") == "join_room":
                    self.peer_ip = response.get("ip")
                    self.peer_port = response.get("port")
                    self.sock.sendto(json.dumps({
                        "type": "room_host_response",
                        "host_side": BoardWindow.get_this_player(),
                        "step_time": BoardWindow.step_time,
                        "host_ip": self.get_local_ip(),
                        "host_port": self.local_port
                    }).encode("utf-8"), addr)
                    self.is_connected = True
                    print("connnected")
                    
                elif response.get("type") == "existing_room_detection":
                    if response.get("room_id") == room_id:
                        msg = json.dumps({
                            "type": "existing_room_response",
                        }).encode("utf-8")
                        self.sock.sendto(msg, (response.get("ip"),self.local_port))
            except json.JSONDecodeError:
                continue
            except socket.timeout:
                continue
        if not self._waiting:
            self.is_connected = False
        thread_done_notification()
        return

    def cancle_waiting(self):
        self._waiting = False

    def join_room(self, room_id, timeout=5):
        self._waiting = True
        threading.Thread(target=self.__join_room, args=(room_id, timeout), daemon=True).start()

    # Broadcast to join a room with the given room_id
    # Returns (True, (ip, port)) if found, else (False, (None, None))
    def __join_room(self, room_id, timeout):
        
        
        PORT = self._LOCAL_PORT
        message = {
            "type": "join_room",
            "room_id": room_id,
            "ip": self.get_local_ip(),
            "port": self.local_port
        }
        data = json.dumps(message).encode("utf-8")
        self.sock.sendto(data, (self.BROADCAST_IP, PORT))
        self._waiting = True
        # Listen for responses
        # Keep broadcasting until timeout or room found
        self.sock.settimeout(1.0) # Set socket timeout to 1 second, receive msg every second
        start_time = time.time()
        while self._waiting and not self.is_timeout:
            if time.time() - start_time > timeout:
                self.is_timeout = True
                break
            try:
                data, addr = self.sock.recvfrom(1024)
            except socket.timeout:
                self.sock.sendto(data, (self.BROADCAST_IP, PORT))
                continue
            # prevent JSON decode error
            try:
                response = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            if response.get("type") == "room_host_response":
                self.peer_ip = response.get("host_ip")
                self.peer_port = response.get("host_port")
                self.sock.settimeout(None)  # Remove timeout
                BoardWindow.this_player = GameConfig.BLACK_PLAYER if response.get("host_side") == GameConfig.WHITE_PLAYER else GameConfig.WHITE_PLAYER
                BoardWindow.step_time = response.get("step_time")
                self.is_connected = True
                break
        self.sock.settimeout(None)  # Remove timeout
        if not self._waiting or self.is_timeout:
            self.is_connected = False
        thread_done_notification()
        return
        
    
    def send_win_message(self, winner):
        message = {
            "type": "win",
            "winner": winner
        }
        self.send_message(message)
    
    def send_move_message(self, x, y, player):
        message = {
            "type": "move",
            "x": x,
            "y": y,
            "player": player
        }
        self.send_message(message)
    def send_chat_message(self, sender, msg,timestamp):
        message = {
            "type": "chat",
            "sender": sender,
            "msg": msg,
            "timestamp": timestamp
        }
        self.send_message(message)