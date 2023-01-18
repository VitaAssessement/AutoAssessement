#showVersion = ['Hostname','ip','modelo','serial','IOS','Rom','uptime','license Level','Configuration Register']
from cores import bcolors
import datetime
import pandas as pd
import netmiko


def showVersion(reportDF, dispositivo, ip, device, coletaDF):
    contError = 0
    contRela = 0
    while contRela == 0 and contError < 3:
        try:

            reportDF.report_showVersion['Hostname'] = [
                dispositivo['hostname']]
            reportDF.report_showVersion['ip'] = [ip[0]]
            reportDF.report_showVersion['modelo'] = [
                dispositivo['model']]
            reportDF.report_showVersion['serial'] = [
                dispositivo['serial_number']]

            prompt_show_version = device._netmiko_device.send_command(
                'show version', read_timeout=30,)
            if (prompt_show_version.__contains__('% Ambiguous command') or prompt_show_version.__contains__('% Invalid input detected at \'^\' marker')):
                print(f'{bcolors.WARNING}------ERRO showVersion------')
                print('Comando Invalido')
                print(ip[0])
                print(device['transport'])
                print(f'------------------{bcolors.ENDC}')
                break
            show_version = prompt_show_version.split('\n')

            reportDF.report_showVersion['IOS'] = [
                show_version[0].split(',')[1]]
            reportDF.report_showVersion['Rom'] = [
                dispositivo['os_version'].replace('Version ', '').split(',')[1]]
            reportDF.report_showVersion['uptime'] = [
                str(datetime.timedelta(seconds=dispositivo['uptime']))]

            for idShowVersion, SVersion in enumerate(show_version):
                if SVersion.__contains__('SW Image'):
                    reportDF.report_showVersion['license level'] = [
                        show_version[idShowVersion+2][SVersion.index('SW Image'):len(SVersion)].split()[0]]
                if SVersion.__contains__('Configuration register'):
                    confReg = SVersion.replace(
                        'Configuration register is', '')
                    confReg = confReg.replace(' ', '')
                    reportDF.report_showVersion['Configuration Register'] = [
                        confReg]

            coletaDF.dfShowVersion = pd.concat(
                [coletaDF.dfShowVersion, reportDF.report_showVersion], ignore_index=True)
            contRela = 1
            break
        except (netmiko.ReadTimeout):
            contError += 1
            continue
        except Exception as err:
            print(f'{bcolors.WARNING}------ERRO showVersion------')
            print(err)
            print(ip[0])
            print(device['transport'])
            print(f'------------------{bcolors.ENDC}')
            break

    return coletaDF.dfShowVersion, contError
