REQ:
Logs: Each node must log actions (send, receive, forward, terminate).
README: How to run it, parallels with networking (IXPs, Internet), your assumptions/reflections.
Submission: A .zip with code + logs + README (optionally a screencast).

message format

**origin** >> destination >> layover >> payload

origin = from airport
destination = to airport
layover = intermediary node (optional)
payload = passenger name or cargo

Hubs = [
    ANC,    # Anchorage
    SEA     # Seattle
]

Nodes = [
    FAI,    # Fairbanks
    BRW,    # Barrow
    OTZ,    # Kotzebue
    JNU,    # Juneau
    BET,    # Bethel
    ADQ,    # Kodiak
    SIT,    # Sitka
    PSG,    # Petersburg
    OME,    # Nome
    KTN,    # Ketchikan
]
