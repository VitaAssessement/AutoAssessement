#vlan            = ['Hostname','ip','Vlan ID','Vlan Name','Status','Ports']
import netmiko
import pandas as pd
from cores import bcolors


def vlan(device, reportDF, coletaDF, dispositivo, ip):
    contError = 0
    contRela = 0
    while contRela == 0 and contError < 3:
        try:

            prompt_vlans = device._netmiko_device.send_command(
                'show vlan', read_timeout=30)
            if (prompt_vlans.__contains__('% Ambiguous command') or prompt_vlans.__contains__('% Invalid input detected at \'^\' marker')):
                prompt_vlans = device._netmiko_device.send_command(
                    'show vlans', read_timeout=30)
                if (prompt_vlans.__contains__('% Ambiguous command') or prompt_vlans.__contains__('% Invalid input detected at \'^\' marker')):
                    print(f'{bcolors.WARNING}------ERRO VLAN------')
                    print('Comando Invalido')
                    print(ip[0])
                    print(device['transport'])
                    print(f'------------------{bcolors.ENDC}')
                    break
            if (prompt_vlans.__contains__('No Virtual LANs configured.')):
                reportDF.report_vlan['Hostname'] = [
                    dispositivo['hostname']]
                reportDF.report_vlan['ip'] = [ip[0]]
                reportDF.report_vlan['Vlan ID'] = [
                    'No Virtual LANs configured.']
                coletaDF.dfVlan = pd.concat(
                    [coletaDF.dfVlan, reportDF.report_vlan], ignore_index=True)
                break
            vlanLines = prompt_vlans.split('\n')

            vlanN = ''
            vlanName = ''
            vlanStatus = ''
            vlanPorts = ''

            for vlans in vlanLines:
                if vlans == '' or vlans == ' ':
                    continue
                if vlans.__contains__('Type  SAID'):
                    break
                if not (vlans.__contains__('VLAN Name') or vlans.__contains__('----')):
                    vlanN = vlans[vlanLines[1].index(
                        'VLAN'):vlanLines[1].index('Name')-1].strip()
                    vlanName = vlans[vlanLines[1].index(
                        'Name'):vlanLines[1].index('Status')-1].strip()
                    vlanStatus = vlans[vlanLines[1].index(
                        'Status'):vlanLines[1].index('Ports')-1].strip()
                    vlanPorts = vlans[vlanLines[1].index(
                        'Ports'):len(vlans)].strip()
                    reportDF.report_vlan['Hostname'] = [
                        dispositivo['hostname']]
                    reportDF.report_vlan['ip'] = [ip[0]]
                    reportDF.report_vlan['Vlan ID'] = [vlanN]
                    reportDF.report_vlan['Vlan Name'] = [vlanName]
                    reportDF.report_vlan['Status'] = [vlanStatus]
                    reportDF.report_vlan['Ports'] = [vlanPorts]
                    coletaDF.dfVlan = pd.concat(
                        [coletaDF.dfVlan, reportDF.report_vlan], ignore_index=True)

            contRela = 1
            break
        except (netmiko.ReadTimeout):
            contError += 1
            continue
        except Exception as err:
            print(f'{bcolors.WARNING}------ERRO vlan------')
            print(err)
            print(ip[0])
            print(device['transport'])
            print(f'------------------{bcolors.ENDC}')
            break
    return coletaDF.dfVlan, contError
