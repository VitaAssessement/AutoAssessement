#swtCDP = ['Hostname','ip','Neighbor','Local Interface','Holdtime','Capabilities','Platform','IP Neig','Port ID','Software','Versao','Release']
from cores import bcolors
import netmiko
import datetime
import pandas as pd


def swtCDP(device, reportDF, dispositivo, coletaDF, ip):
    contError = 0
    contRela = 0
    while contRela == 0 and contError < 3:
        try:

            prompt_swtCDP = device._netmiko_device.send_command(
                'show cdp neighbors detail', read_timeout=30)
            if (prompt_swtCDP.__contains__('% Ambiguous command') or prompt_swtCDP.__contains__('% Invalid input detected at \'^\' marker')):
                print(f'{bcolors.WARNING}------ERRO swtCDP------')
                print('Comando Invalido')
                print(ip[0])
                print(device['transport'])
                print(f'------------------{bcolors.ENDC}')
                break
            swtCDPNeighbors = prompt_swtCDP.split('(Device ID)')

            for cdpCont in range(len(swtCDPNeighbors)):
                swtCDP1 = swtCDPNeighbors[cdpCont].split('\n')
                for sCDP in swtCDP1:
                    reportDF.report_swtCDP['Hostname'] = [
                        dispositivo['hostname']]
                    reportDF.report_swtCDP['ip'] = [ip[0]]
                    if sCDP.__contains__('Device ID'):
                        cdpNeighbor = sCDP.replace('Device ID', '')
                        cdpNeighbor = cdpNeighbor.replace(':', '')
                        cdpNeighbor = cdpNeighbor.replace(' ', '')
                        reportDF.report_swtCDP['neighbor'] = [
                            cdpNeighbor]
                    if sCDP.__contains__('Interface'):
                        cdpInterface = sCDP.split()
                        reportDF.report_swtCDP['Local Interface'] = [
                            cdpInterface[1].replace(',', '')]
                    if sCDP.__contains__('Holdtime'):
                        cdpHoldtime = sCDP.replace('Holdtime', '')
                        cdpHoldtime = cdpHoldtime.replace(':', '')
                        cdpHoldtime = cdpHoldtime.replace(' ', '')
                        cdpHoldtime = cdpHoldtime.replace('sec', '')
                        reportDF.report_swtCDP['Holdtime'] = [
                            str(datetime.timedelta(seconds=int(cdpHoldtime)))]
                    if sCDP.__contains__('Capabilities'):
                        cdpCapabilities = sCDP.split("Capabilities:")
                        reportDF.report_swtCDP['Capabilities'] = [
                            cdpCapabilities[1].removeprefix(' ').replace(',', '')]
                    if sCDP.__contains__('Platform'):
                        cdpPlatform = sCDP.split(' ')
                        reportDF.report_swtCDP['Platform'] = [
                            cdpPlatform[2].replace(',', '')]
                    if sCDP.__contains__('IP address'):
                        cdpIP = sCDP.split(' ')
                        reportDF.report_swtCDP['IP Neig'] = [
                            cdpIP[len(cdpIP)-1]]
                    if sCDP.__contains__('Port ID'):
                        cdpPort = sCDP.split(' ')
                        reportDF.report_swtCDP['Port ID'] = [
                            cdpPort[len(cdpPort)-1]]
                    if sCDP.__contains__(', Version'):
                        cdpVersion = sCDP.split(',')
                        reportDF.report_swtCDP['Software'] = [
                            cdpVersion[1]]
                        reportDF.report_swtCDP['Versao'] = [
                            cdpVersion[2].replace('Version', '').replace(' ', '')]
                        reportDF.report_swtCDP['Release'] = [
                            cdpVersion[len(cdpVersion)-1]]
                coletaDF.dfSwtCDP = pd.concat(
                    [coletaDF.dfSwtCDP, reportDF.report_swtCDP], ignore_index=True)
                reportDF.report_swtCDP = pd.DataFrame(index=None)

            contRela = 1
            break
        except (netmiko.ReadTimeout):
            contError += 1
            continue
        except Exception as err:
            print(f'{bcolors.ENDC}------ERRO swtCDP------')
            print(err)
            print(ip[0])
            print(device['transport'])
            print(f'------------------{bcolors.ENDC}')
            break
    return coletaDF.dfSwtCDP, contError
