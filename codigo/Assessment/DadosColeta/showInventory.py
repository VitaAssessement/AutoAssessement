#showInventory   = ['Hostname','ip','NAME','DESC','PID','VID','SN']
from cores import bcolors
import netmiko
import pandas as pd

def showInventory(device,reportDF,dispositivo,ip,coletaDF):            
            
            contError = 0
            contRela = 0
            while contRela == 0 and contError < 3:
                try:

                    prompt_show_inventory = device._netmiko_device.send_command(
                        'show inventory', read_timeout=30)
                    if (prompt_show_inventory.__contains__('% Ambiguous command') or prompt_show_inventory.__contains__('% Invalid input detected at \'^\' marker')):
                        print(f'{bcolors.WARNING}------ERRO showInventory------')
                        print('Comando Invalido')
                        print(ip[0])
                        print(device['transport'])
                        print(f'------------------{bcolors.ENDC}')
                        break
                    # print(prompt_show_inventory)
                    showInventorySect = [
                        'NAME'+x for x in prompt_show_inventory.split('NAME') if x]

                    for inventoryCont in range(len(showInventorySect)):
                        # print(showInventorySect[inventoryCont])
                        showInventory1 = showInventorySect[inventoryCont].split(
                            '\n')
                        for sInv in showInventory1:
                            reportDF.report_showInventory['Hostname'] = [
                                dispositivo['hostname']]
                            reportDF.report_showInventory['ip'] = [
                                ip[0]]
                            if sInv.__contains__('NAME'):
                                sInvNameDesc = sInv.split('\"')
                                # print(sInvNameDesc[1])
                                reportDF.report_showInventory['NAME'] = [
                                    sInvNameDesc[1]]
                                # print(sInvNameDesc[3])
                                reportDF.report_showInventory['DESC'] = [
                                    sInvNameDesc[3]]
                            if sInv.__contains__('PID'):
                                sInvPIDVIDSN = sInv.split(',')
                                reportDF.report_showInventory['PID'] = [
                                    sInvPIDVIDSN[0].replace('PID:', '').strip()]
                                reportDF.report_showInventory['VID'] = [
                                    sInvPIDVIDSN[1].replace('VID:', '').strip()]
                                reportDF.report_showInventory['SN'] = [
                                    sInvPIDVIDSN[2].replace('SN:', '').strip()]
                        # print(report_showInventory)
                        coletaDF.dfShowInventory = pd.concat(
                            [coletaDF.dfShowInventory, reportDF.report_showInventory], ignore_index=True)
                    # device.close()
                    # print(dfShowInventory)
                    contRela = 1
                    break
                except (netmiko.ReadTimeout):
                    contError += 1
                    continue
                except Exception as err:
                    print(f'{bcolors.WARNING}------ERRO showInventory------')
                    print(err)
                    print(ip[0])
                    print(device['transport'])
                    print(f'------------------{bcolors.ENDC}')
                    break
            return coletaDF.dfShowInventory, contError