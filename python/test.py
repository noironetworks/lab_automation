import telnetlib

from raritan import rpc
from raritan.rpc import pdumodel

LEFT = 'Left'
RIGHT = 'Right'
MANUFACTURER = 'manufacturer'
USERNAME = 'username'
PASSWORD = 'password'
IP = 'ip'
MODEL = 'model'

# Raritan specific definitions
PX2_5464 = 'PX2-5464'
PX3_5464V = 'PX3-5464V'
PX2_5496 = 'PX2-5496'
RARITAN = 'raritan'
RARITAN_USERNAME = 'admin'
SJ15LABUSER = 'sj15labuser'
INSIEME = 'insieme'

# APC specific efinitions
AP7941 = 'AP7941'
AP8941 = 'AP8941'
AP8959NA3 = 'AP8959NA3'
APC = 'apc'
APC_USERNAME = 'apc'
APC_PASSWORD = 'apc'
APC_NOMINAL_VOLTAGE = '208'
APPCLI = "appcli"
CURRENT = "current"
POWER = "power"
APC_TIMEOUT=2

ONE = '1'
FOUR = '4'
ESC = "\x1B"

NO_MATCH = b'zzz'
USERNAME_MATCH = b"User Name :"
PASSWORD_MATCH = b" Password  :"
APC_PROMPT_MATCH=b"APC>"

# Schema here is:
#  [ Row: [ Rack: [ { Left PDU Dict}, {Right PDU Dict} ]]]
PDUS = {
        'DD': {
            '1': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: AP7941,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.14'},
                  RIGHT: {MANUFACTURER: APC,
                          MODEL: PX3_5464V,
                          USERNAME: APC_USERNAME,
                          PASSWORD: APC_PASSWORD,
                          IP: '172.20.79.11'}},
            '2': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX2_5464,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.12'}},
            '3': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX2_5464,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.13'}},
            '4': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX3_5464V,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.16'}},
            '5': {LEFT: {MANUFACTURER: APC,
                         MODEL: PX3_5464V,
                         USERNAME: APC_USERNAME,
                         PASSWORD: APC_PASSWORD,
                         IP: '172.20.79.15'},
                  RIGHT: {MANUFACTURER: RARITAN,
                          MODEL: AP7941,
                          USERNAME: RARITAN_USERNAME,
                          PASSWORD: SJ15LABUSER,
                          IP: '172.20.79.19'}},
            '6': {LEFT: {MANUFACTURER: APC,
                         MODEL: AP8959NA3,
                         USERNAME: APC_USERNAME,
                         PASSWORD: APC_PASSWORD,
                         IP: '172.20.79.17'}},
            '7': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX3_5464V,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.36'},
                  RIGHT: {MANUFACTURER: RARITAN,
                          MODEL: PX2_5496,
                          USERNAME: RARITAN_USERNAME,
                          PASSWORD: SJ15LABUSER,
                          IP: '172.20.79.18'}}
            },
        'II': {
            '1': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX3_5464V,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.20'},
                  RIGHT: {MANUFACTURER: RARITAN,
                          MODEL: PX2_5464, 
                          USERNAME: RARITAN_USERNAME,
                          PASSWORD: SJ15LABUSER,
                          IP: '172.20.79.21'}},
            '2': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX3_5464V,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.22'},
                  RIGHT: {MANUFACTURER: RARITAN,
                          MODEL: PX2_5496,
                          USERNAME: RARITAN_USERNAME,
                          PASSWORD: SJ15LABUSER,
                          IP: '172.20.79.23'}},
            '3': {LEFT: {MANUFACTURER: APC,
                         MODEL: AP8941,
                         USERNAME: APC_USERNAME,
                         PASSWORD: APC_PASSWORD,
                         IP: '172.20.79.24'},
                  RIGHT: {MANUFACTURER: APC,
                          MODEL: AP8941,
                          USERNAME: APC_USERNAME,
                          PASSWORD: APC_PASSWORD,
                          IP: '172.20.79.25'}},
            '4': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX2_5464,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.26'},
                  RIGHT: {MANUFACTURER: RARITAN,
                          MODEL: PX2_5464,
                          USERNAME: RARITAN_USERNAME,
                          PASSWORD: SJ15LABUSER,
                          IP: '172.20.79.27'}},
            '5': {LEFT: {MANUFACTURER: APC,
                         MODEL: AP8941,
                         USERNAME: APC_USERNAME,
                         PASSWORD: APC_PASSWORD,
                         IP: '172.20.79.28'},
                  RIGHT: {MANUFACTURER: RARITAN,
                          MODEL: PX3_5464V,
                          USERNAME: RARITAN_USERNAME,
                          PASSWORD: SJ15LABUSER,
                          IP: '172.20.79.29'}},
            '6': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX2_5464,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.30'},
                  RIGHT: {MANUFACTURER: RARITAN,
                          MODEL: PX2_5496,
                          USERNAME: RARITAN_USERNAME,
                          PASSWORD: SJ15LABUSER,
                          IP: '172.20.79.31'}},
            '7': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX3_5464V,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.30'}},
            '8': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX2_5464,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: SJ15LABUSER,
                         IP: '172.20.79.30'}},
            },
        'KK': {
            '1': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX3_5464V,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: INSIEME,
                         IP: '172.21.84.11'},
                  RIGHT: {MANUFACTURER: RARITAN,
                          MODEL: PX2_5464, 
                          USERNAME: RARITAN_USERNAME,
                          PASSWORD: INSIEME,
                          IP: '172.21.84.12'}},
            '2': {LEFT: {MANUFACTURER: RARITAN,
                         MODEL: PX3_5464V,
                         USERNAME: RARITAN_USERNAME,
                         PASSWORD: INSIEME,
                         IP: '172.21.84.9'} #,
                  #RIGHT: {MANUFACTURER: RARITAN,
                  #        MODEL: PX2_5464, 
                  #        USERNAME: RARITAN_USERNAME,
                  #        PASSWORD: INSIEME,
                  #        IP: '172.21.84.10'}
                  },
            '3': {#LEFT: {MANUFACTURER: RARITAN,
                  #       MODEL: PX3_5464V,
                  #       USERNAME: RARITAN_USERNAME,
                  #       PASSWORD: INSIEME,
                  #       IP: '172.21.84.7'},
                  RIGHT: {MANUFACTURER: RARITAN,
                          MODEL: PX2_5464, 
                          USERNAME: RARITAN_USERNAME,
                          PASSWORD: INSIEME,
                          IP: '172.21.84.8'}}
            }
        }




class SensorData(object):
    def __init__(self, voltage, current, power):
        self.voltage = voltage
        self.current = current
        self.power = power
    def get_current(self):
        return self.current
    def get_voltage(self):
        return self.voltage
    def get_power(self):
        return self.power
    def print_sensor_data(self):
        print("\t\t\tVoltage: %s" % self.voltage)
        print("\t\t\tCurrent: %s" % self.current)
        print("\t\t\tPower: %s" % self.power)


class ApcSensorData(SensorData):
    def __init__(self, voltage, current, power, current1, current2):
        self.current1 = current1
        self.current2 = current2
        super(ApcSensorData, self).__init__(voltage, current, power)
    def print_sensor_data(self):
        super(ApcSensorData, self).print_sensor_data()
        print("\t\t\tBank1 Current: %s" % self.current1)
        print("\t\t\tBank2 Current: %s" % self.current2)

class RaritanSensorData(SensorData):
    def __init__(self, voltage, current, active_power, apparent_power, active_energy):
        self.apparent_power = apparent_power
        self.active_energy = active_energy
        super(RaritanSensorData, self).__init__(voltage, current, active_power)
    def print_sensor_data(self):
        super(RaritanSensorData, self).print_sensor_data()
        print("\t\t\tApparent Power: %s" % self.apparent_power)
        print("\t\t\tAcitve Engergy: %s" % self.active_energy)

class PduManager(object):

    def __init__(self):
        self.pdus = PDUS
        self.all_rows = list(self.pdus.keys())

    def _get_raritan_sensor_data(self, pdu):
        agent = rpc.Agent("https", pdu[IP], pdu[USERNAME], pdu[PASSWORD])
        inlet = pdumodel.Inlet("/model/inlet/0", agent)
        sensors = inlet.getSensors()
        return RaritanSensorData(sensors.voltage.getReading().value,
                                 sensors.current.getReading().value,
                                 sensors.activePower.getReading().value,
                                 sensors.apparentPower.getReading().value,
                                 sensors.activeEnergy.getReading().value)

    def _write_apc(self, session, data):
        session.write(data.encode('ascii') + b"\r")

    def _get_apc_sensor_data(self, pdu):
        tn = telnetlib.Telnet(pdu[IP])
        #tn.set_debuglevel(100)
        tn.read_until(USERNAME_MATCH, timeout=APC_TIMEOUT)
        self._write_apc(tn, pdu[PASSWORD])
        tn.read_until(PASSWORD_MATCH, timeout=APC_TIMEOUT)
        self._write_apc(tn, pdu[PASSWORD])
        tn.read_until(NO_MATCH, timeout=APC_TIMEOUT)
        if pdu[MODEL] in [AP8959NA3, AP8941]:
            self._write_apc(tn, APPCLI)
            tn.read_until(APC_PROMPT_MATCH, timeout=APC_TIMEOUT)
            self._write_apc(tn, CURRENT)
            current_data = tn.read_until(APC_PROMPT_MATCH, timeout=APC_TIMEOUT)
            self._write_apc(tn, POWER)
            power_data = tn.read_until(APC_PROMPT_MATCH, timeout=APC_TIMEOUT)
            split_current_data = current_data.decode('ascii').split("\n")
            current = split_current_data[2].split()[2][:-1]
            split_power_data = power_data.decode('ascii').split("\n")
            power = split_power_data[3].split()[0]
            if float(current) <= 0.0:
                voltage = APC_NOMINAL_VOLTAGE
            else:
                voltage = str(float(power) / float(current))
            # Only voltage, current, and power for this one
            sensor = SensorData(voltage, current, power)
        else:
            self._write_apc(tn, ONE)
            tn.read_until(NO_MATCH, timeout=APC_TIMEOUT)
            self._write_apc(tn, ONE)
            current_data_string = tn.read_until(NO_MATCH, timeout=APC_TIMEOUT)
            self._write_apc(tn, ESC)
            menu_data = tn.read_until(NO_MATCH, timeout=APC_TIMEOUT)
            split_menu_data = menu_data.decode('ascii').split("\n")
            if '4' in split_menu_data[7]:
                self._write_apc(tn, FOUR)
                voltage_data_string = tn.read_until(NO_MATCH, timeout=APC_TIMEOUT)
                self._write_apc(tn, ESC)
                tn.read_until(NO_MATCH, timeout=APC_TIMEOUT)
                voltage_data = voltage_data_string.decode('ascii').split()
                voltage = voltage_data[9]
            else:
                voltage = APC_NOMINAL_VOLTAGE
            self._write_apc(tn, ESC)
            tn.read_until(NO_MATCH, timeout=APC_TIMEOUT)
            self._write_apc(tn, FOUR)
            tn.read_until(NO_MATCH, timeout=APC_TIMEOUT)
            current_data = current_data_string.decode('ascii').split("\n")
            current1 = current_data[7].split()[1]
            current2 = current_data[8].split()[1]
            total_current = current_data[9].split()[1]
            power = float(total_current)*float(voltage)
            sensor = ApcSensorData(voltage, total_current,
                                   power, current1, current2)
        tn.close()

        return sensor

    def get_sensor_data(self, row, rack, side):
        pdu = self.pdus[row][rack][side]
        if pdu[MANUFACTURER] == APC:
            return self._get_apc_sensor_data(pdu)
        elif pdu[MANUFACTURER] == RARITAN:
            return self._get_raritan_sensor_data(pdu)

    def print_pdu_sensors(self, rows=None, racks=None, sides=None):
        if not rows:
            rows_keys = self.all_rows
        else:
            rows_keys = rows
        if not isinstance(rows_keys, list):
            print("Error: rows must be of type list")
            return
        for row in rows_keys:
            row_power = 0.0
            print("Row %s:" % row)
            racks_keys = racks
            if not racks_keys:
                racks_keys = list(self.pdus[row].keys())
            else:
                racks_keys = racks
            if not isinstance(racks_keys, list):
                print("Error: racks must be of type list")
                return
            for rack in racks_keys:
                print("\tRack %s:" % rack)
                if not sides:
                    sides_keys = list(self.pdus[row][rack].keys())
                else:
                    sides_keys = sides
                if not isinstance(sides_keys, list):
                    print("Error: sides must be of type list")
                    return
                rack_power = 0.0
                for side in sides_keys:
                    print("\t\tSide: %s" % side)
                    sensor_data = self.get_sensor_data(row, rack, side)
                    if sensor_data:
                        sensor_data.print_sensor_data()
                        row_power += float(sensor_data.get_power())
                        rack_power += float(sensor_data.get_power())
                print("\tRack %s total power: %s" % (rack, rack_power))
            print("Row %s total power: %s" % (row, row_power))


pdu_manager = PduManager()
pdu_manager.print_pdu_sensors()


