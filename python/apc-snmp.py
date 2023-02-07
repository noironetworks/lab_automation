import snmp
from snmp.engine import Engine
from snmp.security.usm.auth import *
from snmp.security.usm.priv import *
from snmp.types import *

sysDescr = OID.parse("1.3.6.1.2.1.1.1")
ifDescr = OID.parse("1.3.6.1.2.1.2.2.1.2")

# autowait=False will cause each request to return a handle rather than blocking
with Engine(autowait=False) as engine:
    engine.addUser(
        "apc",
        authProtocol=HmacSha256,
        authSecret=b"apc",
        privProtocol=Aes128Cfb,
        privSecret=b"apc",
    )

    # you can use autowait=True/False when creating a Manager
    hostA = engine.Manager("1172.20.79.11")
    #hostB = engine.Manager("192.168.0.2", autowait=True)

    # you can use wait=True/False on any single request as well
    requestA = hostA.get(sysDescr.extend(0))
    #requestB = hostB.getBulk(ifDescr, maxRepetitions=4, wait=False)

    responseA = requestA.wait()
    varbind = responseA.variableBindings[0]
    print("varbind A = %s" % varbind)
    #print(f"{varbind.name} = \"{varbind.value.data.decode()}\"")

    #responseB = requestB.wait()

    # quasi-infinite loop with a safety valve
    #for i in range(100):
    #    for varbind in responseB.variableBindings:
    #        oid, value = varbind

    #        try:
    #            ifIndex = oid.extractIndex(ifDescr, Integer)
    #        except OID.BadPrefix:
    #            break

    #        print(f"ifDescr.{ifIndex.value} = \"{value.data.decode()}\"")
    #    else:
    #        responseB = hostB.getBulk(oid, maxRepetitions=4)
    #        continue

    #    break
