#swtInterfaces   = ['Hostname','ip','Port','Name','Status','Vlan','Duplex','Speed','Type']
import pandas as pd
import netmiko
from cores import bcolors


def swtInterfaces(device, ip, reportDF, dispositivo, coletaDF):

    contError = 0
    contRela = 0
    while contRela == 0 and contError < 3:
        try:
            prompt_swtInterfaces = device._netmiko_device.send_command(
                'show interfaces status', read_timeout=30)
            if (prompt_swtInterfaces.__contains__('% Ambiguous command') or prompt_swtInterfaces.__contains__('% Invalid input detected at \'^\' marker')):
                print(f'{bcolors.WARNING}------ERRO swtInterfaces------')
                print('Comando Invalido')
                print(ip[0])
                print(device['transport'])
                print(f'------------------{bcolors.ENDC}')
                break
            if (prompt_swtInterfaces == ''):
                reportDF.report_swtInterfaces['Hostname'] = [
                    dispositivo['hostname']]
                reportDF.report_swtInterfaces['ip'] = [
                    ip[0]]
                break
            swtInterfacesLines = prompt_swtInterfaces.split('\n')
            if swtInterfacesLines[0] == '':
                del swtInterfacesLines[0]
            for swtInterface in swtInterfacesLines:
                if not swtInterface.__contains__('Port'):
                    reportDF.report_swtInterfaces['Hostname'] = [
                        dispositivo['hostname']]
                    reportDF.report_swtInterfaces['ip'] = [
                        ip[0]]
                    reportDF.report_swtInterfaces['Port'] = [swtInterface[swtInterfacesLines[0].index(
                        'Port'):swtInterfacesLines[0].index('Name')-1].strip()]
                    reportDF.report_swtInterfaces['Name'] = [swtInterface[swtInterfacesLines[0].index(
                        'Name'):swtInterfacesLines[0].index('Status')-1].strip()]
                    reportDF.report_swtInterfaces['Status'] = [swtInterface[swtInterfacesLines[0].index(
                        'Status'):swtInterfacesLines[0].index('Vlan')-1].strip()]
                    reportDF.report_swtInterfaces['Vlan'] = [swtInterface[swtInterfacesLines[0].index(
                        'Vlan'):swtInterfacesLines[0].index('Duplex')-1].strip()]
                    reportDF.report_swtInterfaces['Duplex'] = [swtInterface[swtInterfacesLines[0].index(
                        'Duplex'):swtInterfacesLines[0].index('Speed')-1].strip()]
                    reportDF.report_swtInterfaces['Speed'] = [swtInterface[swtInterfacesLines[0].index(
                        'Speed')-1:swtInterfacesLines[0].index('Type')-1].strip()]
                    reportDF.report_swtInterfaces['Type'] = [
                        swtInterface[swtInterfacesLines[0].index('Type'):len(swtInterface)].strip()]

                coletaDF.dfSwtInterfaces = pd.concat(
                    [coletaDF.dfSwtInterfaces, reportDF.report_swtInterfaces], ignore_index=True)

            contRela = 1
            break
        except (netmiko.ReadTimeout):
            contError += 1
            continue
        except Exception as err:
            print(f'{bcolors.WARNING}------ERRO swtInterfaces------')
            print(err)
            print(ip[0])
            print(device['transport'])
            print(f'------------------{bcolors.ENDC}')
            break
    return coletaDF.dfSwtInterfaces, contError
