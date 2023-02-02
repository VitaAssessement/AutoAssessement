#interfaceBrief  = ['Hostname','ip','Interface','IP-Address','OK?','Method','Status','Protocol']
import netmiko
import pandas as pd
from cores import bcolors


def interfaceBrief(device, ip, reportDF, dispositivo, coletaDF):
    contError = 0
    contRela = 0
    while contRela == 0 and contError < 3:
        try:
            prompt_interfaceBrief = device._netmiko_device.send_command(
                'show ip int brief', read_timeout=30)
            if (prompt_interfaceBrief.__contains__('% Ambiguous command') or prompt_interfaceBrief.__contains__('% Invalid input detected at \'^\' marker')):
                print(f'{bcolors.WARNING}------ERRO interfaceBrief------')
                print('Comando Invalido')
                print(ip[0])
                print(device['transport'])
                print(f'------------------{bcolors.ENDC}')
                break

            interfaceBriefLines = prompt_interfaceBrief.split('\n')
            for interfaceBriefs in interfaceBriefLines:

                if not interfaceBriefs.__contains__('Interface'):
                    reportDF.report_interfaceBrief['Hostname'] = [
                        dispositivo['hostname']]
                    reportDF.report_interfaceBrief['ip'] = [
                        ip[0]]
                    reportDF.report_interfaceBrief['Interface'] = [interfaceBriefs[interfaceBriefLines[0].index(
                        'Interface'):interfaceBriefLines[0].index('IP-Address')-1].strip()]
                    reportDF.report_interfaceBrief['IP-Address'] = [interfaceBriefs[interfaceBriefLines[0].index(
                        'IP-Address'):interfaceBriefLines[0].index('OK?')-1].strip()]
                    reportDF.report_interfaceBrief['OK?'] = [interfaceBriefs[interfaceBriefLines[0].index(
                        'OK?'):interfaceBriefLines[0].index('Method')-1].strip()]
                    reportDF.report_interfaceBrief['Method'] = [interfaceBriefs[interfaceBriefLines[0].index(
                        'Method'):interfaceBriefLines[0].index('Status')-1].strip()]
                    reportDF.report_interfaceBrief['Status'] = [interfaceBriefs[interfaceBriefLines[0].index(
                        'Status'):interfaceBriefLines[0].index('Protocol')-1].strip()]
                    reportDF.report_interfaceBrief['Protocol'] = [
                        interfaceBriefs[interfaceBriefLines[0].index('Protocol'):len(interfaceBriefs)].strip()]

                coletaDF.dfInterfaceBrief = pd.concat(
                    [coletaDF.dfInterfaceBrief, reportDF.report_interfaceBrief], ignore_index=True)

            contRela = 1
            break
        except (netmiko.ReadTimeout):
            contError += 1
            continue
        except Exception as err:
            print(f'{bcolors.WARNING}------ERRO interfaceBrief------')
            print(err)
            print(ip[0])
            print(device['transport'])
            print(f'------------------{bcolors.ENDC}')
            break
    return coletaDF.dfInterfaceBrief, contError
