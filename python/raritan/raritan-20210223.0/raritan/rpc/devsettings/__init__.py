# Do NOT edit this file!
# It was generated by IdlC class idl.json.python.ProxyAsnVisitor.

#
# Section generated from "/home/nb/builds/MEGA/px2-3.0.0-3.0.9-branch-20140613-none-release-none-pdu-raritan/fwcomponents/mkdist/tmp/px2_final/libisys/src/idl/Snmp.idl"
#

import raritan.rpc
from raritan.rpc import (
    Interface,
    Structure,
    ValueObject,
    Enumeration,
    typecheck,
    DecodeException,
)
import raritan.rpc.devsettings

import raritan.rpc.idl


# interface
class Snmp(Interface):
    idlType = "devsettings.Snmp:1.0.2"

    ERR_INVALID_PARAMS = 1

    # structure
    class Configuration(Structure):
        idlType = "devsettings.Snmp.Configuration:1.0.0"
        elements = [
            "v2enable",
            "v3enable",
            "readComm",
            "writeComm",
            "sysContact",
            "sysName",
            "sysLocation",
        ]

        def __init__(
            self,
            v2enable,
            v3enable,
            readComm,
            writeComm,
            sysContact,
            sysName,
            sysLocation,
        ):
            typecheck.is_bool(v2enable, AssertionError)
            typecheck.is_bool(v3enable, AssertionError)
            typecheck.is_string(readComm, AssertionError)
            typecheck.is_string(writeComm, AssertionError)
            typecheck.is_string(sysContact, AssertionError)
            typecheck.is_string(sysName, AssertionError)
            typecheck.is_string(sysLocation, AssertionError)

            self.v2enable = v2enable
            self.v3enable = v3enable
            self.readComm = readComm
            self.writeComm = writeComm
            self.sysContact = sysContact
            self.sysName = sysName
            self.sysLocation = sysLocation

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                v2enable=json["v2enable"],
                v3enable=json["v3enable"],
                readComm=json["readComm"],
                writeComm=json["writeComm"],
                sysContact=json["sysContact"],
                sysName=json["sysName"],
                sysLocation=json["sysLocation"],
            )
            return obj

        def encode(self):
            json = {}
            json["v2enable"] = self.v2enable
            json["v3enable"] = self.v3enable
            json["readComm"] = self.readComm
            json["writeComm"] = self.writeComm
            json["sysContact"] = self.sysContact
            json["sysName"] = self.sysName
            json["sysLocation"] = self.sysLocation
            return json

    # value object
    class ConfigurationChangedEvent(raritan.rpc.idl.Event):
        idlType = "devsettings.Snmp.ConfigurationChangedEvent:1.0.0"

        def __init__(self, userName, ipAddr, oldConfig, newConfig, source):
            super(
                raritan.rpc.devsettings.Snmp.ConfigurationChangedEvent, self
            ).__init__(source)
            typecheck.is_string(userName, AssertionError)
            typecheck.is_string(ipAddr, AssertionError)
            typecheck.is_struct(
                oldConfig, raritan.rpc.devsettings.Snmp.Configuration, AssertionError
            )
            typecheck.is_struct(
                newConfig, raritan.rpc.devsettings.Snmp.Configuration, AssertionError
            )

            self.userName = userName
            self.ipAddr = ipAddr
            self.oldConfig = oldConfig
            self.newConfig = newConfig

        def encode(self):
            json = super(
                raritan.rpc.devsettings.Snmp.ConfigurationChangedEvent, self
            ).encode()
            json["userName"] = self.userName
            json["ipAddr"] = self.ipAddr
            json["oldConfig"] = raritan.rpc.devsettings.Snmp.Configuration.encode(
                self.oldConfig
            )
            json["newConfig"] = raritan.rpc.devsettings.Snmp.Configuration.encode(
                self.newConfig
            )
            return json

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                userName=json["userName"],
                ipAddr=json["ipAddr"],
                oldConfig=raritan.rpc.devsettings.Snmp.Configuration.decode(
                    json["oldConfig"], agent
                ),
                newConfig=raritan.rpc.devsettings.Snmp.Configuration.decode(
                    json["newConfig"], agent
                ),
                # for idl.Event
                source=Interface.decode(json["source"], agent),
            )
            return obj

        def listElements(self):
            elements = ["userName", "ipAddr", "oldConfig", "newConfig"]
            elements = (
                elements
                + super(
                    raritan.rpc.devsettings.Snmp.ConfigurationChangedEvent, self
                ).listElements()
            )
            return elements

    def getConfiguration(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getConfiguration", args)
        _ret_ = raritan.rpc.devsettings.Snmp.Configuration.decode(rsp["_ret_"], agent)
        typecheck.is_struct(
            _ret_, raritan.rpc.devsettings.Snmp.Configuration, DecodeException
        )
        return _ret_

    def setConfiguration(self, cfg):
        agent = self.agent
        typecheck.is_struct(
            cfg, raritan.rpc.devsettings.Snmp.Configuration, AssertionError
        )
        args = {}
        args["cfg"] = raritan.rpc.devsettings.Snmp.Configuration.encode(cfg)
        rsp = agent.json_rpc(self.target, "setConfiguration", args)
        _ret_ = rsp["_ret_"]
        typecheck.is_int(_ret_, DecodeException)
        return _ret_

    def getV3EngineId(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getV3EngineId", args)
        _ret_ = rsp["_ret_"]
        typecheck.is_string(_ret_, DecodeException)
        return _ret_


# Do NOT edit this file!
# It was generated by IdlC class idl.json.python.ProxyAsnVisitor.

#
# Section generated from "/home/nb/builds/MEGA/px2-3.0.0-3.0.9-branch-20140613-none-release-none-pdu-raritan/fwcomponents/mkdist/tmp/px2_final/libisys/src/idl/Modbus.idl"
#

import raritan.rpc
from raritan.rpc import (
    Interface,
    Structure,
    ValueObject,
    Enumeration,
    typecheck,
    DecodeException,
)
import raritan.rpc.devsettings


# interface
class Modbus(Interface):
    idlType = "devsettings.Modbus:1.0.0"

    # structure
    class TcpSettings(Structure):
        idlType = "devsettings.Modbus.TcpSettings:1.0.0"
        elements = ["readonly"]

        def __init__(self, readonly):
            typecheck.is_bool(readonly, AssertionError)

            self.readonly = readonly

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                readonly=json["readonly"],
            )
            return obj

        def encode(self):
            json = {}
            json["readonly"] = self.readonly
            return json

    # structure
    class Settings(Structure):
        idlType = "devsettings.Modbus.Settings:1.0.0"
        elements = ["tcp"]

        def __init__(self, tcp):
            typecheck.is_struct(
                tcp, raritan.rpc.devsettings.Modbus.TcpSettings, AssertionError
            )

            self.tcp = tcp

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                tcp=raritan.rpc.devsettings.Modbus.TcpSettings.decode(
                    json["tcp"], agent
                ),
            )
            return obj

        def encode(self):
            json = {}
            json["tcp"] = raritan.rpc.devsettings.Modbus.TcpSettings.encode(self.tcp)
            return json

    def getSettings(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getSettings", args)
        _ret_ = raritan.rpc.devsettings.Modbus.Settings.decode(rsp["_ret_"], agent)
        typecheck.is_struct(
            _ret_, raritan.rpc.devsettings.Modbus.Settings, DecodeException
        )
        return _ret_

    def setSettings(self, settings):
        agent = self.agent
        typecheck.is_struct(
            settings, raritan.rpc.devsettings.Modbus.Settings, AssertionError
        )
        args = {}
        args["settings"] = raritan.rpc.devsettings.Modbus.Settings.encode(settings)
        rsp = agent.json_rpc(self.target, "setSettings", args)


# Do NOT edit this file!
# It was generated by IdlC class idl.json.python.ProxyAsnVisitor.

#
# Section generated from "/home/nb/builds/MEGA/px2-3.0.0-3.0.9-branch-20140613-none-release-none-pdu-raritan/fwcomponents/mkdist/tmp/px2_final/libisys/src/idl/Zeroconf.idl"
#

import raritan.rpc
from raritan.rpc import (
    Interface,
    Structure,
    ValueObject,
    Enumeration,
    typecheck,
    DecodeException,
)
import raritan.rpc.devsettings

import raritan.rpc.idl


# interface
class Zeroconf(Interface):
    idlType = "devsettings.Zeroconf:1.0.0"

    # structure
    class Settings(Structure):
        idlType = "devsettings.Zeroconf.Settings:1.0.0"
        elements = ["mdnsEnabled"]

        def __init__(self, mdnsEnabled):
            typecheck.is_bool(mdnsEnabled, AssertionError)

            self.mdnsEnabled = mdnsEnabled

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                mdnsEnabled=json["mdnsEnabled"],
            )
            return obj

        def encode(self):
            json = {}
            json["mdnsEnabled"] = self.mdnsEnabled
            return json

    # value object
    class SettingsChangedEvent(raritan.rpc.idl.Event):
        idlType = "devsettings.Zeroconf.SettingsChangedEvent:1.0.0"

        def __init__(self, oldSettings, newSettings, source):
            super(raritan.rpc.devsettings.Zeroconf.SettingsChangedEvent, self).__init__(
                source
            )
            typecheck.is_struct(
                oldSettings, raritan.rpc.devsettings.Zeroconf.Settings, AssertionError
            )
            typecheck.is_struct(
                newSettings, raritan.rpc.devsettings.Zeroconf.Settings, AssertionError
            )

            self.oldSettings = oldSettings
            self.newSettings = newSettings

        def encode(self):
            json = super(
                raritan.rpc.devsettings.Zeroconf.SettingsChangedEvent, self
            ).encode()
            json["oldSettings"] = raritan.rpc.devsettings.Zeroconf.Settings.encode(
                self.oldSettings
            )
            json["newSettings"] = raritan.rpc.devsettings.Zeroconf.Settings.encode(
                self.newSettings
            )
            return json

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                oldSettings=raritan.rpc.devsettings.Zeroconf.Settings.decode(
                    json["oldSettings"], agent
                ),
                newSettings=raritan.rpc.devsettings.Zeroconf.Settings.decode(
                    json["newSettings"], agent
                ),
                # for idl.Event
                source=Interface.decode(json["source"], agent),
            )
            return obj

        def listElements(self):
            elements = ["oldSettings", "newSettings"]
            elements = (
                elements
                + super(
                    raritan.rpc.devsettings.Zeroconf.SettingsChangedEvent, self
                ).listElements()
            )
            return elements

    def getSettings(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getSettings", args)
        _ret_ = raritan.rpc.devsettings.Zeroconf.Settings.decode(rsp["_ret_"], agent)
        typecheck.is_struct(
            _ret_, raritan.rpc.devsettings.Zeroconf.Settings, DecodeException
        )
        return _ret_

    def setSettings(self, settings):
        agent = self.agent
        typecheck.is_struct(
            settings, raritan.rpc.devsettings.Zeroconf.Settings, AssertionError
        )
        args = {}
        args["settings"] = raritan.rpc.devsettings.Zeroconf.Settings.encode(settings)
        rsp = agent.json_rpc(self.target, "setSettings", args)


# Do NOT edit this file!
# It was generated by IdlC class idl.json.python.ProxyAsnVisitor.

#
# Section generated from "/home/nb/builds/MEGA/px2-3.0.0-3.0.9-branch-20140613-none-release-none-pdu-raritan/fwcomponents/mkdist/tmp/px2_final/libisys/src/idl/Smtp.idl"
#

import raritan.rpc
from raritan.rpc import (
    Interface,
    Structure,
    ValueObject,
    Enumeration,
    typecheck,
    DecodeException,
)
import raritan.rpc.devsettings


# interface
class Smtp(Interface):
    idlType = "devsettings.Smtp:1.0.1"

    ERR_INVALID_PARAMS = 1

    # structure
    class Configuration(Structure):
        idlType = "devsettings.Smtp.Configuration:1.0.0"
        elements = [
            "host",
            "port",
            "sender",
            "useAuth",
            "username",
            "password",
            "retryCount",
            "retryInterval",
        ]

        def __init__(
            self,
            host,
            port,
            sender,
            useAuth,
            username,
            password,
            retryCount,
            retryInterval,
        ):
            typecheck.is_string(host, AssertionError)
            typecheck.is_int(port, AssertionError)
            typecheck.is_string(sender, AssertionError)
            typecheck.is_bool(useAuth, AssertionError)
            typecheck.is_string(username, AssertionError)
            typecheck.is_string(password, AssertionError)
            typecheck.is_int(retryCount, AssertionError)
            typecheck.is_int(retryInterval, AssertionError)

            self.host = host
            self.port = port
            self.sender = sender
            self.useAuth = useAuth
            self.username = username
            self.password = password
            self.retryCount = retryCount
            self.retryInterval = retryInterval

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                host=json["host"],
                port=json["port"],
                sender=json["sender"],
                useAuth=json["useAuth"],
                username=json["username"],
                password=json["password"],
                retryCount=json["retryCount"],
                retryInterval=json["retryInterval"],
            )
            return obj

        def encode(self):
            json = {}
            json["host"] = self.host
            json["port"] = self.port
            json["sender"] = self.sender
            json["useAuth"] = self.useAuth
            json["username"] = self.username
            json["password"] = self.password
            json["retryCount"] = self.retryCount
            json["retryInterval"] = self.retryInterval
            return json

    def getConfiguration(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getConfiguration", args)
        _ret_ = raritan.rpc.devsettings.Smtp.Configuration.decode(rsp["_ret_"], agent)
        typecheck.is_struct(
            _ret_, raritan.rpc.devsettings.Smtp.Configuration, DecodeException
        )
        return _ret_

    def setConfiguration(self, cfg):
        agent = self.agent
        typecheck.is_struct(
            cfg, raritan.rpc.devsettings.Smtp.Configuration, AssertionError
        )
        args = {}
        args["cfg"] = raritan.rpc.devsettings.Smtp.Configuration.encode(cfg)
        rsp = agent.json_rpc(self.target, "setConfiguration", args)
        _ret_ = rsp["_ret_"]
        typecheck.is_int(_ret_, DecodeException)
        return _ret_

    # structure
    class TestResult(Structure):
        idlType = "devsettings.Smtp.TestResult:1.0.0"
        elements = ["status", "message"]

        def __init__(self, status, message):
            typecheck.is_int(status, AssertionError)
            typecheck.is_string(message, AssertionError)

            self.status = status
            self.message = message

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                status=json["status"],
                message=json["message"],
            )
            return obj

        def encode(self):
            json = {}
            json["status"] = self.status
            json["message"] = self.message
            return json

    def testConfiguration(self, cfg, recipients):
        agent = self.agent
        typecheck.is_struct(
            cfg, raritan.rpc.devsettings.Smtp.Configuration, AssertionError
        )
        for x0 in recipients:
            typecheck.is_string(x0, AssertionError)
        args = {}
        args["cfg"] = raritan.rpc.devsettings.Smtp.Configuration.encode(cfg)
        args["recipients"] = [x0 for x0 in recipients]
        rsp = agent.json_rpc(self.target, "testConfiguration", args)
        _ret_ = raritan.rpc.devsettings.Smtp.TestResult.decode(rsp["_ret_"], agent)
        typecheck.is_struct(
            _ret_, raritan.rpc.devsettings.Smtp.TestResult, DecodeException
        )
        return _ret_