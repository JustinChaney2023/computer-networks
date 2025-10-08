'''
System Overview:
Peers = Airports: each airport is a process that can both accept and initiate socket connections. Run them through multiple terminals
Messages = Passengers: message includes from, to, layover(opt), payload (name or cargo)
Routing: at most one layover (e.g., FAI -> ANC -> BRW), direct flights to hubs (e.g., BRW -> ANC, SEA -> SIT). No spoke to spoke must go via hub
Scale: Have more than 5 nodes, simlate a reasonable number or airports.
Addressing: use host:port or setup a lookup table (mapping code -> host:port)
Logs: every node writes clear logs (send/recv/route/arrival/termination) goes into logs folder


'''

# Client Socket

''' 
Assignment is simplified
anc->seattle
nearby->anc nearby->sea
focus is on how to run multiple client-server tcp sockets
should be able to handle concurrency # not opening/closing sockets 1 by 1 should be a few
grading on a sliding scale / check grading matrix (reasonable assumptions dont oversimplify)
only 1 layover
bi directional fai->anc # anc->fai

500 messages in 6 minutes

departure is client
server is arrival

check msg / if u are dest end connection if u are a layover then send to dest 
each client generates random flights
or
make a scheduler that makes random flights and sends to origin

mininet.org
---------------------
This is a Airport Network Emulator not simulator
---------------------

'''

