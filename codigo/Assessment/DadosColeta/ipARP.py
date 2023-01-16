#ipARP           = ['Hostname','ip','Protocol','Address','Age','Hardware Addr','Type','Interface']
import netmiko
import pandas as pd
from cores import bcolors


def ipARP(device, ip, reportDF, dispositivo, coletaDF):

    contError = 0
    contRela = 0
    while contRela == 0 and contError < 3:
        try:
            prompt_ipARP = device._netmiko_device.send_command(
                'show ip arp', read_timeout=30)
            if (prompt_ipARP.__contains__('% Ambiguous command') or prompt_ipARP.__contains__('% Invalid input detected at \'^\' marker')):
                print(f'{bcolors.WARNING}------ERRO ipARP------')
                print('Comando Invalido')
                print(ip[0])
                print(device['transport'])
                print(f'------------------{bcolors.ENDC}')
                break
            # print(prompt_ipARP)
            ipARPLines = prompt_ipARP.split('\n')
            for ipARPs in ipARPLines:

                if not ipARPs.__contains__('Protocol'):
                    reportDF.report_ipARP['Hostname'] = [
                        dispositivo['hostname']]
                    reportDF.report_ipARP['ip'] = [ip[0]]
                    reportDF.report_ipARP['Protocol'] = [ipARPs[ipARPLines[0].index(
                        'Protocol'):ipARPLines[0].index('Address')-1].strip()]
                    reportDF.report_ipARP['Address'] = [
                        ipARPs[ipARPLines[0].index('Address'):ipARPLines[0].index('Age')-1].strip()]
                    reportDF.report_ipARP['Age'] = [ipARPs[ipARPLines[0].index(
                        'Age'):ipARPLines[0].index('Hardware Addr')-1].strip()]
                    reportDF.report_ipARP['Hardware Addr'] = [ipARPs[ipARPLines[0].index(
                        'Hardware Addr'):ipARPLines[0].index('Type')-1].strip()]
                    reportDF.report_ipARP['Type'] = [ipARPs[ipARPLines[0].index(
                        'Type'):ipARPLines[0].index('Interface')-1].strip()]
                    reportDF.report_ipARP['Interface'] = [
                        ipARPs[ipARPLines[0].index('Interface'):len(ipARPs)].strip()]

                coletaDF.dfIpARP = pd.concat(
                    [coletaDF.dfIpARP, reportDF.report_ipARP], ignore_index=True)
            contRela = 1
            break
        except (netmiko.ReadTimeout):
            contError += 1
            continue
        except Exception as err:
            print(f'{bcolors.WARNING}------ERRO ipARP------')
            print(err)
            print(ip[0])
            print(device['transport'])
            print(f'------------------{bcolors.ENDC}')
            break
    return coletaDF.dfIpARP, contError
