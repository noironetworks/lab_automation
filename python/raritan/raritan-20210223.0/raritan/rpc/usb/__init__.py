# Do NOT edit this file!
# It was generated by IdlC class idl.json.python.ProxyAsnVisitor.

#
# Section generated from "/home/nb/builds/MEGA/px2-3.0.0-3.0.9-branch-20140613-none-release-none-pdu-raritan/fwcomponents/mkdist/tmp/px2_final/libisys/src/idl/Usb.idl"
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
import raritan.rpc.usb


# structure
class UsbDevice(Structure):
    idlType = "usb.UsbDevice:1.0.0"
    elements = ["bus", "device", "vendorId", "productId"]

    def __init__(self, bus, device, vendorId, productId):
        typecheck.is_int(bus, AssertionError)
        typecheck.is_int(device, AssertionError)
        typecheck.is_int(vendorId, AssertionError)
        typecheck.is_int(productId, AssertionError)

        self.bus = bus
        self.device = device
        self.vendorId = vendorId
        self.productId = productId

    @classmethod
    def decode(cls, json, agent):
        obj = cls(
            bus=json["bus"],
            device=json["device"],
            vendorId=json["vendorId"],
            productId=json["productId"],
        )
        return obj

    def encode(self):
        json = {}
        json["bus"] = self.bus
        json["device"] = self.device
        json["vendorId"] = self.vendorId
        json["productId"] = self.productId
        return json


# interface
class Usb(Interface):
    idlType = "usb.Usb:1.0.0"

    def getDevices(self):
        agent = self.agent
        args = {}
        rsp = agent.json_rpc(self.target, "getDevices", args)
        usbDevices = [
            raritan.rpc.usb.UsbDevice.decode(x0, agent) for x0 in rsp["usbDevices"]
        ]
        for x0 in usbDevices:
            typecheck.is_struct(x0, raritan.rpc.usb.UsbDevice, DecodeException)
        return usbDevices
