import pandas as pd
from cores import bcolors
import netmiko
#relacaoLogin = ['ip','username','password','secret','privilege','modo','nome','modelo','serial','IOS']


def relacaoLogin(coletaDF, reportDF, ip, login, device, secret, dispositivo):
    contError = 0
    contRela = 0
    while contRela == 0 and contError < 3:
        try:
            #device._netmiko_device.send_command("terminal history")
            reportDF.report_relacaoLogin['ip'] = [ip[0]]
            reportDF.report_relacaoLogin['username'] = [
                login[0]]
            reportDF.report_relacaoLogin['password'] = [
                login[1]]
            reportDF.report_relacaoLogin['secret'] = [
                secret[0]]

            reportDF.report_relacaoLogin['privilege'] = [device._netmiko_device.send_command(
                'show privilege', read_timeout=30).replace('Current privilege level is ', '')]

            if (device.transport == 'telnet'):
                reportDF.report_relacaoLogin['modo'] = ['TELNET']
            else:
                reportDF.report_relacaoLogin['modo'] = ['SSH']

            reportDF.report_relacaoLogin['nome'] = [
                dispositivo['hostname']]
            reportDF.report_relacaoLogin['modelo'] = [
                dispositivo['model']]
            reportDF.report_relacaoLogin['serial'] = [
                dispositivo['serial_number']]
            reportDF.report_relacaoLogin['IOS'] = [
                dispositivo['os_version']]

            coletaDF.dfRelacaoLogin = pd.concat(
                [coletaDF.dfRelacaoLogin, reportDF.report_relacaoLogin], ignore_index=True)
            # device.close()
            contRela = 1
            break
        except (netmiko.ReadTimeout):
            contError += 1
            continue
        except Exception as err:
            print(f'{bcolors.WARNING}------ERRO relacaoLogin------')
            print(err)
            print(ip[0])
            print(device['transport'])
            print(f'------------------{bcolors.ENDC}')
            break
    return coletaDF.dfRelacaoLogin, contError
