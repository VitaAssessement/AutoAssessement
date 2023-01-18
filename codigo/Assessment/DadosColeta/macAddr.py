#macAddr         = ['Hostname','ip','vlan','mac address','Type','protocols','port']
import netmiko
import pandas as pd
from cores import bcolors


def macAddr(device, ip, reportDF, dispositivo, coletaDF):

    contError = 0
    contRela = 0
    while contRela == 0 and contError < 3:
        try:

            prompt_macAddr = device._netmiko_device.send_command(
                'show mac address-table', read_timeout=30)
            if (prompt_macAddr.__contains__('% Ambiguous command') or prompt_macAddr.__contains__('% Invalid input detected at \'^\' marker')):
                prompt_macAddr = device._netmiko_device.send_command(
                    'show mac-address-table', read_timeout=30)
                if (prompt_macAddr.__contains__('% Ambiguous command') or prompt_macAddr.__contains__('% Invalid input detected at \'^\' marker')):
                    print(f'{bcolors.WARNING}------ERRO MacAddr------')
                    print('Comando Invalido')
                    print(ip[0])
                    print(device['transport'])
                    print(f'------------------{bcolors.ENDC}')
                    break

            macAddrLines = prompt_macAddr.split('\n')
            if macAddrLines[0] == '':
                del macAddrLines[0]
            for macAddrs in macAddrLines:

                if not (macAddrs.__contains__('vlan') or macAddrs.__contains__('----') or macAddrs.__contains__('Unicast Entries') or macAddrs.__contains__('Destination Address  Address Type  VLAN  Destination Por') or macAddrs == '' or macAddrs.__contains__('Mac Address Tabl') or macAddrs.__contains__('Vlan    Mac Address       Type        Port') or macAddrs.__contains__('Total Mac Addresses for this criterion:')):
                    if (prompt_macAddr.__contains__('-+-')):
                        reportDF.report_macAddr['Hostname'] = [
                            dispositivo['hostname']]
                        reportDF.report_macAddr['ip'] = [
                            ip[0]]
                        reportDF.report_macAddr['vlan'] = [
                            macAddrs[0:macAddrLines[2].find('+')].strip()]
                        macAddrMarker = macAddrLines[2].find('+')
                        reportDF.report_macAddr['mac address'] = [
                            macAddrs[macAddrMarker:macAddrLines[2].find('+', macAddrMarker+1)].strip()]
                        macAddrMarker = macAddrLines[2].find(
                            '+', macAddrMarker+1)
                        reportDF.report_macAddr['Type'] = [
                            macAddrs[macAddrMarker:macAddrLines[2].find('+', macAddrMarker+1)].strip()]
                        macAddrMarker = macAddrLines[2].find(
                            '+', macAddrMarker+1)
                        reportDF.report_macAddr['protocols'] = [
                            macAddrs[macAddrMarker:macAddrLines[2].find('+', macAddrMarker+1)].strip()]
                        macAddrMarker = macAddrLines[2].find(
                            '+', macAddrMarker+1)
                        reportDF.report_macAddr['port'] = [
                            macAddrs[macAddrMarker:len(macAddrs)].strip()]
                    else:
                        reportDF.report_macAddr['Hostname'] = [
                            dispositivo['hostname']]
                        reportDF.report_macAddr['ip'] = [
                            ip[0]]
                        reportDF.report_macAddr['vlan'] = [
                            macAddrs[macAddrLines[3].index('Vlan'):macAddrLines[3].index('Mac')-1].strip()]
                        reportDF.report_macAddr['mac address'] = [
                            macAddrs[macAddrLines[3].index('Mac'):macAddrLines[3].index('Type')-1].strip()]
                        reportDF.report_macAddr['Type'] = [macAddrs[macAddrLines[3].index(
                            'Type'):macAddrLines[3].index('Ports')-1].strip()]
                        reportDF.report_macAddr['port'] = [
                            macAddrs[macAddrLines[3].index('Ports'):len(macAddrs)].strip()]
                coletaDF.dfMacAddr = pd.concat(
                    [coletaDF.dfMacAddr, reportDF.report_macAddr], ignore_index=True)

            contRela = 1
            break
        except (netmiko.ReadTimeout):
            contError += 1
            continue
        except Exception as err:
            print(f'{bcolors.WARNING}------ERRO MacAddr------')
            print(err)
            print(ip[0])
            print(device['transport'])
            print(f'------------------{bcolors.ENDC}')
            break
    return coletaDF.dfMacAddr, contError
