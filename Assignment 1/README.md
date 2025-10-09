# Airline Server Simulation

##### Copilot auto-completes were used
##### I also used chatgpt to get some help error fixing
##### https://devdocs.io/python~3.13/ for researching standard library things

1) How to run your program? Please state your assumptions clearly.

    Assignemnt was tested and written with Python 3.13 in mind
    run ```python -m src.main``` from Assignment folder
    logs all will be created within logs folder, console also shows all flights
    airport and route yaml required

    Assumptions:
    Each airport acts as both server and client
    ANC SEA hubs else spokes
    Small airports must go through a hub to reach elsewhere
    One Layover Max, FAI >> ANC >> BRW

2) Do you see parallels with systems such as Internet eXchange Points and the
Internet traffic, and how did we simulate the traffic with a hub-and-spoke
topology here? Explain.

    Airports are acting as routers, Payload as packets, flights as links
    Hubs acting as IXP

3) Please state your assumptions and your thoughts inspired by this exercise in
the context of Computer Networks.

    Each message contains metadata and payload like IP packet header and data.
    Hubs read header to determine whether to forward or "deliver locally"
    Using TCP is more reliable but, less scalable. UDP would be faster but less reliable.
    A thought of mine is that reading documentation and seeing that something will be deprecated in the following version is terrible. (Thread related stuff)

###### first/last-name JSONs sourced from: 
https://github.com/terryweiss/ink-collector/tree/master/tests/nottests
