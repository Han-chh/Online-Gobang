# Message Format

## General Format

| Field   | Type   | Description
|-------|------|-----------
| type| str|type of the message|
|message|json|main message| 

## Different Types of Messages

- join_room
  
  {"type": "join_room",
            "room_id": room_id,
            "ip": self.__get_local_ip(),
            "port": self.local_port}
- room_response
  {"type":"room_host_response", "host_side":black or white, "step_time": step_time, ip":host_ip,"port":host_port}
- existing_room_detection
  {"type":"existing_room_detection","room_id":room_id,"ip":ip}
- existing_room_response
  {"type":"existing_room_response"}

Handled by handle_msg:
- lost_ping
  {"type": "lost_ping"}
- chat_msg
  {"type": "chat_msg", "msg": msg, "timestamp": timestamp,"sender": black or white}
- move
  {"type":"move", "x":x:int,"y": y:int,"sender":black or white}
- win
  {"type":"win","winner":black or white}