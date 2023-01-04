# Do NOT edit this file!
# It was generated by IdlC class idl.json.python.ProxyAsnVisitor.

#
# Section generated from "/home/nb/builds/MEGA/px2-3.0.0-3.0.9-branch-20140613-none-release-none-pdu-raritan/fwcomponents/mkdist/tmp/px2_final/libidl_client/fitness/idl/Fitness.idl"
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
import raritan.rpc.fitness


# interface
class Fitness(Interface):
    idlType = "fitness.Fitness:1.0.0"

    FLAG_VALUE_INVALID = 0x1

    FLAG_VALUE_OLD = 0x2

    FLAG_ENTRY_CRITICAL = 0x4

    # structure
    class DataEntry(Structure):
        idlType = "fitness.Fitness.DataEntry:1.0.0"
        elements = [
            "id",
            "value",
            "maxValue",
            "worstValue",
            "thresholdValue",
            "rawValue",
            "flags",
        ]

        def __init__(
            self, id, value, maxValue, worstValue, thresholdValue, rawValue, flags
        ):
            typecheck.is_string(id, AssertionError)
            typecheck.is_int(value, AssertionError)
            typecheck.is_int(maxValue, AssertionError)
            typecheck.is_int(worstValue, AssertionError)
            typecheck.is_int(thresholdValue, AssertionError)
            typecheck.is_long(rawValue, AssertionError)
            typecheck.is_int(flags, AssertionError)

            self.id = id
            self.value = value
            self.maxValue = maxValue
            self.worstValue = worstValue
            self.thresholdValue = thresholdValue
            self.rawValue = rawValue
            self.flags = flags

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                id=json["id"],
                value=json["value"],
                maxValue=json["maxValue"],
                worstValue=json["worstValue"],
                thresholdValue=json["thresholdValue"],
                rawValue=int(json["rawValue"]),
                flags=json["flags"],
            )
            return obj

        def encode(self):
            json = {}
            json["id"] = self.id
            json["value"] = self.value
            json["maxValue"] = self.maxValue
            json["worstValue"] = self.worstValue
            json["thresholdValue"] = self.thresholdValue
            json["rawValue"] = self.rawValue
            json["flags"] = self.flags
            return json

    # structure
    class ErrorLogEntry(Structure):
        idlType = "fitness.Fitness.ErrorLogEntry:1.0.0"
        elements = [
            "id",
            "value",
            "thresholdValue",
            "rawValue",
            "powerOnHours",
            "timeStampUTC",
        ]

        def __init__(
            self, id, value, thresholdValue, rawValue, powerOnHours, timeStampUTC
        ):
            typecheck.is_string(id, AssertionError)
            typecheck.is_int(value, AssertionError)
            typecheck.is_int(thresholdValue, AssertionError)
            typecheck.is_long(rawValue, AssertionError)
            typecheck.is_int(powerOnHours, AssertionError)
            typecheck.is_time(timeStampUTC, AssertionError)

            self.id = id
            self.value = value
            self.thresholdValue = thresholdValue
            self.rawValue = rawValue
            self.powerOnHours = powerOnHours
            self.timeStampUTC = timeStampUTC

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                id=json["id"],
                value=json["value"],
                thresholdValue=json["thresholdValue"],
                rawValue=int(json["rawValue"]),
                powerOnHours=json["powerOnHours"],
                timeStampUTC=raritan.rpc.Time.decode(json["timeStampUTC"]),
            )
            return obj

        def encode(self):
            json = {}
            json["id"] = self.id
            json["value"] = self.value
            json["thresholdValue"] = self.thresholdValue
            json["rawValue"] = self.rawValue
            json["powerOnHours"] = self.powerOnHours
            json["timeStampUTC"] = raritan.rpc.Time.encode(self.timeStampUTC)
            return json

    def getDataEntries(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getDataEntries", args)
        _ret_ = [
            raritan.rpc.fitness.Fitness.DataEntry.decode(x0, agent)
            for x0 in rsp["_ret_"]
        ]
        for x0 in _ret_:
            typecheck.is_struct(
                x0, raritan.rpc.fitness.Fitness.DataEntry, DecodeException
            )
        return _ret_

    def getErrorLogIndexRange(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getErrorLogIndexRange", args)
        firstIndex = rsp["firstIndex"]
        entryCount = rsp["entryCount"]
        typecheck.is_int(firstIndex, DecodeException)
        typecheck.is_int(entryCount, DecodeException)
        return (firstIndex, entryCount)

    def getErrorLogEntries(self, startIndex, count):
        agent = self.agent
        typecheck.is_int(startIndex, AssertionError)
        typecheck.is_int(count, AssertionError)
        args = {}
        args["startIndex"] = startIndex
        args["count"] = count
        rsp = agent.json_rpc(self.target, "getErrorLogEntries", args)
        _ret_ = [
            raritan.rpc.fitness.Fitness.ErrorLogEntry.decode(x0, agent)
            for x0 in rsp["_ret_"]
        ]
        for x0 in _ret_:
            typecheck.is_struct(
                x0, raritan.rpc.fitness.Fitness.ErrorLogEntry, DecodeException
            )
        return _ret_
