#vtp = ['Hostname','ip','vtp Capable','vtp Running','vtp mode','domain name']
from cores import bcolors
import netmiko
import pandas as pd


def vtp(reportDF, dispositivo, device, coletaDF, ip):

    contError = 0
    contRela = 0
    while contRela == 0 and contError < 3:
        try:
            reportDF.report_vtp['Hostname'] = [dispositivo['hostname']]
            reportDF.report_vtp['ip'] = [ip[0]]

            prompt_vtp = device._netmiko_device.send_command(
                'show vtp status', read_timeout=30)
            if (prompt_vtp.__contains__('% Ambiguous command') or prompt_vtp.__contains__('% Invalid input detected at \'^\' marker')):
                print(f'{bcolors.WARNING}------ERRO VTP------')
                print('Comando Invalido')
                print(ip[0])
                print(device['transport'])
                print(f'------------------{bcolors.ENDC}')
                break

            vtp_status = prompt_vtp.split('\n')
            for vtp_line in vtp_status:
                if vtp_line.__contains__('capable'):
                    reportDF.report_vtp['vtp capable'] = [
                        vtp_line.split(':')[1].removeprefix(' ')]
                if vtp_line.__contains__('running'):
                    reportDF.report_vtp['vtp Running'] = [
                        vtp_line.split(':')[1].removeprefix(' ')]
                if vtp_line.__contains__('Operating Mode'):
                    reportDF.report_vtp['vtp mode'] = [
                        vtp_line.split(':')[1].removeprefix(' ')]
                if vtp_line.__contains__('Domain Name'):
                    reportDF.report_vtp['domain name'] = [
                        vtp_line.split(':')[1].removeprefix(' ')]

            coletaDF.dfVTP = pd.concat(
                [coletaDF.dfVTP, reportDF.report_vtp], ignore_index=True)
            contRela = 1
            break
        except (netmiko.ReadTimeout):
            contError += 1
            continue
        except Exception as err:
            print(f'{bcolors.WARNING}------ERRO VTP------')
            print(err)
            print(ip[0])
            print(device['transport'])
            print(f'------------------{bcolors.ENDC}')
            break
    return coletaDF.dfVTP, contError
