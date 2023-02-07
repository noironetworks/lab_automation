import telnetlib

USERNAME = 'apc'
PASSWORD = 'apc'
ONE = '1'
FOUR = '4'
ESC = "\x1B"
APPCLI = "appcli"
CURRENT = "current"
POWER = "power"

NO_MATCH=b'zzz'
USERNAME_MATCH=b"User Name :"
PASSWORD_MATCH=b" Password  :"
PROMPT_MATCH=b"APC>"

#tn = telnetlib.Telnet('172.20.79.11')
#tn = telnetlib.Telnet('172.20.79.15')
tn = telnetlib.Telnet('172.20.79.17')
tn.set_debuglevel(100)
tn.read_until(USERNAME_MATCH, timeout=5)
tn.write(USERNAME.encode('ascii') + b"\r")
tn.read_until(PASSWORD_MATCH, timeout=5)
tn.write(PASSWORD.encode('ascii') + b"\r")
tn.read_until(NO_MATCH, timeout=5)
if True:
    tn.write(APPCLI.encode('ascii') + b"\r")
    tn.read_until(PROMPT_MATCH, timeout=5)
    tn.write(CURRENT.encode('ascii') + b"\r")
    current_data = tn.read_until(PROMPT_MATCH, timeout=5)
    tn.write(POWER.encode('ascii') + b"\r")
    power_data = tn.read_until(PROMPT_MATCH, timeout=5)
    split_current_data = current_data.decode('ascii').split("\n")
    current = split_current_data[2].split()[2][:-1]
    split_power_data = power_data.decode('ascii').split("\n")
    power = split_power_data[2].split()[0]
    voltage = str(float(power) / float(current))
else:
    tn.write(ONE.encode('ascii') + b"\r")
    tn.read_until(NO_MATCH, timeout=5)
    tn.write(ONE.encode('ascii') + b"\r")
    sensor_data_string = tn.read_until(NO_MATCH, timeout=5)
    tn.write(ESC.encode('ascii') + b"\r")
    menu_data = tn.read_until(NO_MATCH, timeout=5)
    split_menu_data = menu_data.decode('ascii').split("\n")
    if '4' in split_menu_data[7]:
        tn.write(FOUR.encode('ascii') + b"\r")
        voltage_data_string = tn.read_until(NO_MATCH, timeout=5)
        tn.write(ESC.encode('ascii') + b"\r")
        tn.read_until(NO_MATCH, timeout=5)
        voltage_data = voltage_data_string.decode('ascii').split()
        voltage = voltage_data[9]
    else:
        voltage = '208'
tn.write(ESC.encode('ascii') + b"\r")
tn.read_until(NO_MATCH, timeout=5)
tn.write(FOUR.encode('ascii') + b"\r")
tn.read_until(NO_MATCH, timeout=5)
tn.close()
split_data = sensor_data_string.decode('ascii').split("\n")
current1 = split_data[7].split()[1]
current2 = split_data[8].split()[1]
total_current = split_data[9].split()[1]
power = float(total_current)*float(voltage)
