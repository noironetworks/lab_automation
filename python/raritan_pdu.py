from raritan import rpc
from raritan.rpc import pdumodel

agent = rpc.Agent("https", "172.20.79.14", "admin", "sj15labuser")
pdu = pdumodel.Pdu("/model/pdu/0", agent)
metadata = pdu.getMetaData()
print metadata
