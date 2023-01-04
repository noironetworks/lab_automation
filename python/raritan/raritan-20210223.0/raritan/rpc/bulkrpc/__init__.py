# Do NOT edit this file!
# It was generated by IdlC class idl.json.python.ProxyAsnVisitor.

#
# Section generated from "/home/nb/builds/MEGA/px2-3.0.0-3.0.9-branch-20140613-none-release-none-pdu-raritan/fwcomponents/mkdist/tmp/px2_final/jsonrpcd/src/idl/BulkRequest.idl"
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
from raritan.rpc.opaque.bulkrpc import JsonObject

import raritan.rpc.bulkrpc


# structure
class Request(Structure):
    idlType = "bulkrpc.Request:1.0.0"
    elements = ["rid", "json"]

    def __init__(self, rid, json):
        typecheck.is_string(rid, AssertionError)
        typecheck.is_string(json, AssertionError)

        self.rid = rid
        self.json = json

    @classmethod
    def decode(cls, json, agent):
        obj = cls(
            rid=json["rid"],
            json=json["json"],
        )
        return obj

    def encode(self):
        json = {}
        json["rid"] = self.rid
        json["json"] = self.json
        return json


# structure
class Response(Structure):
    idlType = "bulkrpc.Response:1.0.0"
    elements = ["json", "statcode"]

    def __init__(self, json, statcode):
        typecheck.is_string(json, AssertionError)
        typecheck.is_int(statcode, AssertionError)

        self.json = json
        self.statcode = statcode

    @classmethod
    def decode(cls, json, agent):
        obj = cls(
            json=json["json"],
            statcode=json["statcode"],
        )
        return obj

    def encode(self):
        json = {}
        json["json"] = self.json
        json["statcode"] = self.statcode
        return json


# interface
class BulkRequest(Interface):
    idlType = "bulkrpc.BulkRequest:1.0.1"

    # structure
    class Request(Structure):
        idlType = "bulkrpc.BulkRequest.Request:1.0.0"
        elements = ["rid", "json"]

        def __init__(self, rid, json):
            typecheck.is_string(rid, AssertionError)

            self.rid = rid
            self.json = json

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                rid=json["rid"],
                json=raritan.rpc.bulkrpc.JsonObject.decode(json["json"], agent),
            )
            return obj

        def encode(self):
            json = {}
            json["rid"] = self.rid
            json["json"] = raritan.rpc.bulkrpc.JsonObject.encode(self.json)
            return json

    # structure
    class Response(Structure):
        idlType = "bulkrpc.BulkRequest.Response:1.0.0"
        elements = ["json", "statcode"]

        def __init__(self, json, statcode):
            typecheck.is_int(statcode, AssertionError)

            self.json = json
            self.statcode = statcode

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                json=raritan.rpc.bulkrpc.JsonObject.decode(json["json"], agent),
                statcode=json["statcode"],
            )
            return obj

        def encode(self):
            json = {}
            json["json"] = raritan.rpc.bulkrpc.JsonObject.encode(self.json)
            json["statcode"] = self.statcode
            return json

    def performRequest(self, requests):
        agent = self.agent
        for x0 in requests:
            typecheck.is_struct(x0, raritan.rpc.bulkrpc.Request, AssertionError)
        args = {}
        args["requests"] = [raritan.rpc.bulkrpc.Request.encode(x0) for x0 in requests]
        rsp = agent.json_rpc(self.target, "performRequest", args)
        responses = [
            raritan.rpc.bulkrpc.Response.decode(x0, agent) for x0 in rsp["responses"]
        ]
        for x0 in responses:
            typecheck.is_struct(x0, raritan.rpc.bulkrpc.Response, DecodeException)
        return responses

    def performBulk(self, requests):
        agent = self.agent
        for x0 in requests:
            typecheck.is_struct(
                x0, raritan.rpc.bulkrpc.BulkRequest.Request, AssertionError
            )
        args = {}
        args["requests"] = [
            raritan.rpc.bulkrpc.BulkRequest.Request.encode(x0) for x0 in requests
        ]
        rsp = agent.json_rpc(self.target, "performBulk", args)
        responses = [
            raritan.rpc.bulkrpc.BulkRequest.Response.decode(x0, agent)
            for x0 in rsp["responses"]
        ]
        for x0 in responses:
            typecheck.is_struct(
                x0, raritan.rpc.bulkrpc.BulkRequest.Response, DecodeException
            )
        return responses
