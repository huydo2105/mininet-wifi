from scapy.all import *
from scapy.fields import *

# Define the EpidemicHeader
class EpidemicHeader(Packet):
    name = "EpidemicHeader"
    fields_desc = [
        StrFixedLenField("packetId", "", length=36),  # UUID length
        IntField("hopCount", 0),
        IntField("timestamp", 0)
    ]

# Define the SummaryVectorHeader
class SummaryVectorHeader(Packet):
    name = "SummaryVectorHeader"
    fields_desc = [
        IntField("summaryVectorSize", 0)
    ]

# Register the layers so Scapy can recognize them
bind_layers(IP, EpidemicHeader)
bind_layers(IP, SummaryVectorHeader)