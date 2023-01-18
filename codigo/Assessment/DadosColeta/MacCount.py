#MacCount        = ['Hostname','ip','Vlan','Dynamic Count','Statis Count','Total']
import netmiko
import pandas as pd
from cores import bcolors
import re


def MacCount(device, ip, reportDF, dispositivo, coletaDF):
    contError = 0
    contRela = 0
    while contRela == 0 and contError < 3:
        try:
            prompt_macCount = device._netmiko_device.send_command(
                'show mac address-table count')
            if (prompt_macCount.__contains__('% Ambiguous command') or prompt_macCount.__contains__('% Invalid input detected at \'^\' marker')):
                prompt_macCount = device._netmiko_device.send_command(
                    'show mac-address-table count')
                if (prompt_macCount.__contains__('% Ambiguous command') or prompt_macCount.__contains__('% Invalid input detected at \'^\' marker')):
                    print(f'{bcolors.WARNING}------ERRO MacCount------')
                    print('Comando Invalido')
                    print(ip[0])
                    print(device['transport'])
                    print(f'------------------{bcolors.ENDC}')
                    break
            if not any(letra_macCount.isalpha() for letra_macCount in prompt_macCount):
                reportDF.report_macCount['Hostname'] = [
                    dispositivo['hostname']]
                reportDF.report_macCount['ip'] = [ip[0]]
                coletaDF.dfMacCount = pd.concat(
                    [coletaDF.dfMacCount, reportDF.report_macCount], ignore_index=True)
                break

            macCountSect = prompt_macCount.split('(Mac Entries)')

            for macCountCont in range(len(macCountSect)):
                mCount = macCountSect[macCountCont].split('\n')

                reportDF.report_macCount['Hostname'] = [
                    dispositivo['hostname']]
                reportDF.report_macCount['ip'] = [ip[0]]
                reportDF.report_macCount['Vlan'] = [
                    re.sub(r"\D+", "", mCount[1])]
                reportDF.report_macCount['Dynamic Count'] = [
                    re.sub(r"\D+", "", mCount[3])]
                reportDF.report_macCount['Static Count'] = [
                    re.sub(r"\D+", "", mCount[4])]
                reportDF.report_macCount['Total'] = [
                    re.sub(r"\D+", "", mCount[5])]
                coletaDF.dfMacCount = pd.concat(
                    [coletaDF.dfMacCount, reportDF.report_macCount], ignore_index=True)

            contRela = 1
            break
        except (netmiko.ReadTimeout):
            contError += 1
            continue
        except Exception as err:
            print(f'{bcolors.WARNING}------ERRO MacCount------')
            print(err)
            print(ip[0])
            print(device['transport'])
            print(f'------------------{bcolors.ENDC}')
            break
    return coletaDF.dfMacCount, contError
