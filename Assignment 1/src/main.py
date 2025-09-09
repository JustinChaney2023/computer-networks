import socket

'''
System Overview:
Peers = Airports: each airport is a process that can both accept and initiate socket connections. Run them through multiple terminals
Messages = Passengers: message includes from, to, layover(opt), payload (name or cargo)
Routing: at most one layover (e.g., FAI -> ANC -> BRW), direct flights to hubs (e.g., BRW -> ANC, SEA -> SIT). No spoke to spoke must go via hub
Scale: Have more than 5 nodes, simlate a reasonable number or airports.
Addressing: use host:port or setup a lookup table (mapping code -> host:port)
Logs: every node writes clear logs (send/recv/route/arrival/termination) goes into logs folder


'''