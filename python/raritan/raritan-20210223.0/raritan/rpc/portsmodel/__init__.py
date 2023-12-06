# Do NOT edit this file!
# It was generated by IdlC class idl.json.python.ProxyAsnVisitor.

#
# Section generated from "/home/nb/builds/MEGA/px2-3.0.0-3.0.9-branch-20140613-none-release-none-pdu-raritan/fwcomponents/mkdist/tmp/px2_final/libidl_client/topofw/ports/idl/Port.idl"
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
import raritan.rpc.idl

import raritan.rpc.portsmodel


# interface
class Port(Interface):
    idlType = "portsmodel.Port:2.0.1"

    NO_ERROR = 0

    ERR_INVALID_PARAM = 1

    ERR_DEVICE_BUSY = 2

    # enumeration
    class DetectionType(Enumeration):
        idlType = "portsmodel.Port.DetectionType:1.0.0"
        values = ["AUTO", "PINNED", "DISABLED"]

    DetectionType.AUTO = DetectionType(0)
    DetectionType.PINNED = DetectionType(1)
    DetectionType.DISABLED = DetectionType(2)

    # structure
    class DetectionMode(Structure):
        idlType = "portsmodel.Port.DetectionMode:1.0.0"
        elements = ["type", "pinnedDeviceType"]

        def __init__(self, type, pinnedDeviceType):
            typecheck.is_enum(
                type, raritan.rpc.portsmodel.Port.DetectionType, AssertionError
            )
            typecheck.is_string(pinnedDeviceType, AssertionError)

            self.type = type
            self.pinnedDeviceType = pinnedDeviceType

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                type=raritan.rpc.portsmodel.Port.DetectionType.decode(json["type"]),
                pinnedDeviceType=json["pinnedDeviceType"],
            )
            return obj

        def encode(self):
            json = {}
            json["type"] = raritan.rpc.portsmodel.Port.DetectionType.encode(self.type)
            json["pinnedDeviceType"] = self.pinnedDeviceType
            return json

    # structure
    class Properties(Structure):
        idlType = "portsmodel.Port.Properties:1.0.0"
        elements = ["name", "label", "mode", "detectedDeviceType", "detectedDeviceName"]

        def __init__(self, name, label, mode, detectedDeviceType, detectedDeviceName):
            typecheck.is_string(name, AssertionError)
            typecheck.is_string(label, AssertionError)
            typecheck.is_struct(
                mode, raritan.rpc.portsmodel.Port.DetectionMode, AssertionError
            )
            typecheck.is_string(detectedDeviceType, AssertionError)
            typecheck.is_string(detectedDeviceName, AssertionError)

            self.name = name
            self.label = label
            self.mode = mode
            self.detectedDeviceType = detectedDeviceType
            self.detectedDeviceName = detectedDeviceName

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                name=json["name"],
                label=json["label"],
                mode=raritan.rpc.portsmodel.Port.DetectionMode.decode(
                    json["mode"], agent
                ),
                detectedDeviceType=json["detectedDeviceType"],
                detectedDeviceName=json["detectedDeviceName"],
            )
            return obj

        def encode(self):
            json = {}
            json["name"] = self.name
            json["label"] = self.label
            json["mode"] = raritan.rpc.portsmodel.Port.DetectionMode.encode(self.mode)
            json["detectedDeviceType"] = self.detectedDeviceType
            json["detectedDeviceName"] = self.detectedDeviceName
            return json

    # value object
    class PropertiesChangedEvent(raritan.rpc.idl.Event):
        idlType = "portsmodel.Port.PropertiesChangedEvent:1.0.0"

        def __init__(self, oldProperties, newProperties, source):
            super(raritan.rpc.portsmodel.Port.PropertiesChangedEvent, self).__init__(
                source
            )
            typecheck.is_struct(
                oldProperties, raritan.rpc.portsmodel.Port.Properties, AssertionError
            )
            typecheck.is_struct(
                newProperties, raritan.rpc.portsmodel.Port.Properties, AssertionError
            )

            self.oldProperties = oldProperties
            self.newProperties = newProperties

        def encode(self):
            json = super(
                raritan.rpc.portsmodel.Port.PropertiesChangedEvent, self
            ).encode()
            json["oldProperties"] = raritan.rpc.portsmodel.Port.Properties.encode(
                self.oldProperties
            )
            json["newProperties"] = raritan.rpc.portsmodel.Port.Properties.encode(
                self.newProperties
            )
            return json

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                oldProperties=raritan.rpc.portsmodel.Port.Properties.decode(
                    json["oldProperties"], agent
                ),
                newProperties=raritan.rpc.portsmodel.Port.Properties.decode(
                    json["newProperties"], agent
                ),
                # for idl.Event
                source=Interface.decode(json["source"], agent),
            )
            return obj

        def listElements(self):
            elements = ["oldProperties", "newProperties"]
            elements = (
                elements
                + super(
                    raritan.rpc.portsmodel.Port.PropertiesChangedEvent, self
                ).listElements()
            )
            return elements

    # value object
    class DeviceChangedEvent(raritan.rpc.idl.Event):
        idlType = "portsmodel.Port.DeviceChangedEvent:1.0.0"

        def __init__(self, oldDevice, newDevice, source):
            super(raritan.rpc.portsmodel.Port.DeviceChangedEvent, self).__init__(source)
            typecheck.is_remote_obj(oldDevice, AssertionError)
            typecheck.is_remote_obj(newDevice, AssertionError)

            self.oldDevice = oldDevice
            self.newDevice = newDevice

        def encode(self):
            json = super(raritan.rpc.portsmodel.Port.DeviceChangedEvent, self).encode()
            json["oldDevice"] = Interface.encode(self.oldDevice)
            json["newDevice"] = Interface.encode(self.newDevice)
            return json

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                oldDevice=Interface.decode(json["oldDevice"], agent),
                newDevice=Interface.decode(json["newDevice"], agent),
                # for idl.Event
                source=Interface.decode(json["source"], agent),
            )
            return obj

        def listElements(self):
            elements = ["oldDevice", "newDevice"]
            elements = (
                elements
                + super(
                    raritan.rpc.portsmodel.Port.DeviceChangedEvent, self
                ).listElements()
            )
            return elements

    def getProperties(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getProperties", args)
        _ret_ = raritan.rpc.portsmodel.Port.Properties.decode(rsp["_ret_"], agent)
        typecheck.is_struct(
            _ret_, raritan.rpc.portsmodel.Port.Properties, DecodeException
        )
        return _ret_

    def setName(self, name):
        agent = self.agent
        typecheck.is_string(name, AssertionError)
        args = {}
        args["name"] = name
        rsp = agent.json_rpc(self.target, "setName", args)

    def setDetectionMode(self, mode):
        agent = self.agent
        typecheck.is_struct(
            mode, raritan.rpc.portsmodel.Port.DetectionMode, AssertionError
        )
        args = {}
        args["mode"] = raritan.rpc.portsmodel.Port.DetectionMode.encode(mode)
        rsp = agent.json_rpc(self.target, "setDetectionMode", args)
        _ret_ = rsp["_ret_"]
        typecheck.is_int(_ret_, DecodeException)
        return _ret_

    def getDetectableDevices(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getDetectableDevices", args)
        _ret_ = [x0 for x0 in rsp["_ret_"]]
        for x0 in _ret_:
            typecheck.is_string(x0, DecodeException)
        return _ret_

    def getDevice(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getDevice", args)
        _ret_ = Interface.decode(rsp["_ret_"], agent)
        typecheck.is_remote_obj(_ret_, DecodeException)
        return _ret_

    def getDeviceConfig(self, deviceType):
        agent = self.agent
        typecheck.is_string(deviceType, AssertionError)
        args = {}
        args["deviceType"] = deviceType
        rsp = agent.json_rpc(self.target, "getDeviceConfig", args)
        _ret_ = Interface.decode(rsp["_ret_"], agent)
        typecheck.is_remote_obj(_ret_, DecodeException)
        return _ret_