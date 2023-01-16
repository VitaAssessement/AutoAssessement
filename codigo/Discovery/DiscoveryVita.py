import datetime
import re
from tkinter import filedialog

import os
import napalm
import napalm.base.exceptions
import netmiko
import numpy as np
import pandas as pd
import PySimpleGUI as sg
import requests
from alive_progress import alive_bar

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def autoColetaVita():
    '''Vinicius Conti Sardinha
        Vivo Vita IT'''

    versao_atual = 0.3

    response = requests.get(
        "https://api.github.com/repos/VitaAssessment/AutoAssessment/releases/latest")
    versao_recente = float(response.json()["name"])

    if versao_atual < versao_recente:
        print(f'{bcolors.WARNING}-----------------------------------------------------------------------------------------\nfavor atualizar script em https://github.com/VitaAssessment/AutoAssessment.git\n-----------------------------------------------------------------------------------------{bcolors.ENDC}')
        return

    class dataFrames:
        def __init__(self,
                     dfSwtCDP=None,
                     dfSemConexao=None,
                     dfSemLogin=None):
            self.dfSwtCDP = dfSwtCDP if dfSwtCDP is not None else pd.DataFrame(
                [], index=None)
            self.dfSemConexao = dfSemConexao if dfSemConexao is not None else pd.DataFrame(
                [], columns=['ip','modo'], index=None)
            self.dfSemLogin = dfSemLogin if dfSemLogin is not None else pd.DataFrame(
                [], columns=['ip', 'falha'], index=None)

    class reports:
        def __init__(self,
                     report_swtCDP=None):
            self.report_swtCDP = report_swtCDP if report_swtCDP is not None else pd.DataFrame([
            ], index=None)

    coletaDF = dataFrames()

    modo_config = False

    # abrindo arquivo excel
#################################################################################################################################

    try:
        xl = pd.ExcelFile(filedialog.askopenfilename(
            title='por favor selecione o arquivo Excel'))
    except Exception:
        print(f'{bcolors.BOLD}nenhum arquivo foi selecionado{bcolors.ENDC}')
        return

    # lendo arquivo excel
    try:

        array_ips = selecSheet(
            'selecione o nome da planilha que contém os ips', xl, 0)
        if (array_ips == ['cancelado']).all():
            return
        array_login = selecSheet(
            'selecione o nome da planinha que contém os usernames e senhas', xl, 0)
        if (array_login == ['cancelado']).all():
            return
        array_secret = selecSheet(
            'selecione o nome da planinha que contém os enable secrets', xl, 0)
        if (array_secret == ['cancelado']).all():
            return
        xl.close()
    except Exception:
        print(f'{bcolors.BOLD}operação cancelada{bcolors.ENDC}')
        return

#################################################################################################################################
    try:
        sg.popup_ok(
            'Por Favor selecione a pasta onde serão salvos os logs')  # selecionando onde salvar os logs
        pastaLogs = filedialog.askdirectory(
            title='Por Favor selecione a pasta onde serão salvos os logs')
    except Exception as err:
        exception_type = type(err).__name__
        print(f'{bcolors.WARNING}-----ERRO 1------')
        print(exception_type)
        print(f'------------------{bcolors.ENDC}')


#################################################################################################################################

    print(f'{bcolors.BOLD}{bcolors.HEADER}iniciando assessment...{bcolors.ENDC}')
    cont = 0
    with alive_bar(len(array_ips)*2, force_tty=True,title=f'{bcolors.HEADER}{bcolors.BOLD}Assessment{bcolors.ENDC}',
elapsed=' em {elapsed}',enrich_print=False,dual_line=True,
elapsed_end=f'{bcolors.OKGREEN} execução finalizada em '+'{elapsed}'+f'{bcolors.ENDC}') as bar:
        while cont < len(array_ips):

            for neigCont in coletaDF.dfSwtCDP['IP Neig']:
                if not array_ips.__contains__(neigCont[0]):
                    array_ips = array_ips+neigCont
            
            print(array_ips)

            reportDF = reports()

            loopLogin = False
            cont2 = 0
            bar.text(f'{bcolors.OKBLUE}conectando via {bcolors.HEADER}SSH{bcolors.OKBLUE} a: {bcolors.ENDC}'+array_ips[cont][0])
            for cont2 in range(len(array_login)):
                if (loopLogin):
                    loopLogin = False
                    break
                else:
                    tempo_init = datetime.datetime.now()
                    driver = napalm.get_network_driver(array_ips[cont][1])
                    device = driver(hostname=array_ips[cont][0],
                                    username=array_login[cont2][0],
                                    password=array_login[cont2][1],
                                    timeout=120,
                                    optional_args={'transport': 'ssh',
                                                "session_log": pastaLogs+'/'+array_ips[cont][0]+'_SSH'+'.txt',
                                                'force_no_enable': 'True'})

                    try:
                        device.open()
                        coletaDF, reportDF = rodarColeta(tempo_init=tempo_init, cont=cont, cont2=cont2, array_ips=array_ips, array_login=array_login,
                                                        array_secret=array_secret, device=device, coletaDF=coletaDF, reportDF=reportDF)
                        break
                    except (netmiko.NetMikoTimeoutException, napalm.base.exceptions.ConnectionException):
                        print(f'{bcolors.FAIL}falha na conexão via SSH com IP: {bcolors.ENDC}' + array_ips[cont][0])
                        coletaDF.dfSemConexao = pd.concat([coletaDF.dfSemConexao, pd.DataFrame(
                            {'ip': [array_ips[cont][0]], 'modo': ['SSH']}, index=None)], ignore_index=True)
                        loopLogin = True
                        continue

                    except (netmiko.NetMikoAuthenticationException, netmiko.ReadException):
                        if (cont2 == len(array_login)-1):
                            print(f'{bcolors.FAIL}falha no login com IP: {bcolors.ENDC}' +
                                array_ips[cont][0])
                            coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                                {'ip': [array_ips[cont][0]], 'falha':['login']}, index=None)], ignore_index=True)
                        continue

                    except ConnectionRefusedError:
                        if (cont2 == len(array_login)-1):
                            print(f'{bcolors.FAIL}falha no login com IP: {bcolors.ENDC}' +
                                array_ips[cont][0])
                            coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                                {'ip': [array_ips[cont][0]], 'falha':['recusado - SSH']}, index=None)], ignore_index=True)
                        continue

                    except TimeoutError:
                        print(f'{bcolors.FAIL}falha na conexão via SSH com IP: {bcolors.ENDC}' + array_ips[cont][0])
                        coletaDF.dfSemConexao = pd.concat([coletaDF.dfSemConexao, pd.DataFrame(
                            {'ip': [array_ips[cont][0]], 'modo': ['SSH']}, index=None)], ignore_index=True)
                        loopLogin = True
                        continue
                    
                    except Exception as err:
                        exception_type = type(err)
                        print(f'{bcolors.WARNING}------ERRO 3------')
                        print(exception_type)
                        print(f'------------------{bcolors.ENDC}')

                    device.close()

            loopLogin = False
            cont2 = 0
            bar()
            bar.text(f'{bcolors.OKBLUE}conectando via {bcolors.HEADER}TELNET{bcolors.OKBLUE} a: {bcolors.ENDC}'+array_ips[cont][0])
            for cont2 in range(len(array_login)):
                if (loopLogin):
                    loopLogin = False
                    break
                else:
                    tempo_init = datetime.datetime.now()
                    device = driver(hostname=array_ips[cont][0],
                                    username=array_login[cont2][0],
                                    password=array_login[cont2][1],
                                    timeout=120,
                                    optional_args={'transport': 'telnet',
                                                "session_log": pastaLogs+'/'+array_ips[cont][0]+'_TELNET'+'.txt',
                                                'force_no_enable': 'True'})
                    try:
                        device.open()
                        coletaDF, reportDF = rodarColeta(tempo_init=tempo_init, cont=cont, cont2=cont2, array_ips=array_ips, array_login=array_login,
                                                        array_secret=array_secret, device=device, coletaDF=coletaDF, reportDF=reportDF)
                        break
                    except netmiko.NetmikoAuthenticationException:
                        if (cont2 == len(array_login)-1):
                            print(f'{bcolors.FAIL}falha no login com IP: {bcolors.ENDC}' +
                                array_ips[cont][0])
                            coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                                {'ip': [array_ips[cont][0]], 'falha':['login']}, index=None)], ignore_index=True)
                        continue

                    except ConnectionRefusedError:
                        if (cont2 == len(array_login)-1):
                            print(f'{bcolors.FAIL}falha no login com IP: {bcolors.ENDC}' +
                                array_ips[cont][0])
                            coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                                {'ip': [array_ips[cont][0]], 'falha':['recusado - TELNET']}, index=None)], ignore_index=True)
                        continue

                    except (netmiko.NetMikoTimeoutException, netmiko.ReadTimeout, napalm.base.exceptions.ConnectionException):
                        loopLogin = True
                        break

                    except TimeoutError:
                        print(f'{bcolors.FAIL}falha na conexão via TELNET com IP: {bcolors.ENDC}' + array_ips[cont][0])
                        coletaDF.dfSemConexao = pd.concat([coletaDF.dfSemConexao, pd.DataFrame(
                            {'ip': [array_ips[cont][0]],'modo':['TELNET']}, index=None)], ignore_index=True)
                        loopLogin = True
                        break

                    except Exception as err:
                        exception_type = type(err).__name__
                        print(f'{bcolors.WARNING}------ERRO 2------')
                        print(exception_type)
                        print(f'------------------{bcolors.ENDC}')

            if os.path.getsize(pastaLogs+'/'+array_ips[cont][0]+'_SSH'+'.txt') == 0:
                os.remove(pastaLogs+'/'+array_ips[cont][0]+'_SSH'+'.txt')
            if os.path.getsize(pastaLogs+'/'+array_ips[cont][0]+'_TELNET'+'.txt') == 0:
                os.remove(pastaLogs+'/'+array_ips[cont][0]+'_TELNET'+'.txt')
            bar()
            cont = cont+1

#################################################################################################################################

    try:
        print(f'\n{bcolors.HEADER}selecione onde salvar a relação de logins{bcolors.ENDC}')
        file_name = filedialog.asksaveasfilename(  # salvando arquivo de resultados
            filetypes=[('excel file', '*.xlsx')], defaultextension='.xlsx')
        if (file_name == ''):
            return

        with pd.ExcelWriter(file_name) as writer:
            escribaExcel(writer, 'swt-cdp', coletaDF.dfSwtCDP)
            escribaExcel(writer, 'falha login', coletaDF.dfSemLogin)
            escribaExcel(writer, 'falha conexão', coletaDF.dfSemConexao)

        return

    except Exception as err:
        exception_type = type(err).__name__
        print(f'{bcolors.WARNING}------ERRO 6------')
        print(exception_type)
        print(f'------------------{bcolors.ENDC}')

#################################################################################################################################


def selecSheet(texto, xl, cabecalho):  # função de escolher sheet, pra economizar linhas
    try:
        event, values = sg.Window(texto, [[sg.Text(texto), sg.Listbox(xl.sheet_names, size=(20, 3), key='LB')],
                                          [sg.Button('Ok'), sg.Button('Cancelar')]]).read(close=True)

        if event == 'Ok':
            return xl.parse(str(values["LB"][0]), header=cabecalho).to_numpy()
        else:
            sg.popup_cancel('Processo Cancelado')
            return ['cancelado']
    except Exception as err:
        exception_type = type(err).__name__
        print(f'{bcolors.WARNING}------ERRO 7------')
        print(exception_type)
        print(f'------------------{bcolors.ENDC}')

#################################################################################################################################


def escribaExcel(writer, sheetName, df):
    df.to_excel(writer, sheet_name=sheetName, index=False, na_rep='NaN')

# Auto-adjust columns' width
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets[sheetName].set_column(col_idx, col_idx, column_width+2)


def rodarColeta(tempo_init, cont, cont2, array_ips, array_login, array_secret, device, reportDF, coletaDF):
    if (len(array_secret)) > 1:
        range_secret = len(array_secret)
    else:
        range_secret = 1
    cont3 = 0
    for cont3 in range(range_secret):
        try:
            device.open()
            device._netmiko_device.secret = str(array_secret[cont3][0])
            #device._netmiko_device.global_delay_factor = 4
            if not (device._netmiko_device.check_enable_mode()):
                device._netmiko_device.enable()

    #################################################################################################################################
        #swtCDP = ['Hostname','ip','Neighbor','Local Interface','Holdtime','Capabilities','Platform','IP Neig','Port ID','Software','Versao','Release']
            if contError < 3:
                contError = 0
            contRela = 0
            while contRela == 0 and contError < 3:
                try:

                    prompt_swtCDP = device._netmiko_device.send_command(
                        'show cdp neighbors detail', read_timeout=30)
                    if (prompt_swtCDP.__contains__('% Ambiguous command') or prompt_swtCDP.__contains__('% Invalid input detected at \'^\' marker')):
                        print(f'{bcolors.WARNING}------ERRO swtCDP------')
                        print('Comando Invalido')
                        print(array_ips[cont][0])
                        print(device['transport'])
                        print(f'------------------{bcolors.ENDC}')
                        break
                    swtCDPNeighbors = prompt_swtCDP.split('(Device ID)')

                    dispositivo = device.get_facts()

                    for cdpCont in range(len(swtCDPNeighbors)):
                        swtCDP1 = swtCDPNeighbors[cdpCont].split('\n')
                        for sCDP in swtCDP1:
                            #hostname
                            reportDF.report_swtCDP['Hostname'] = [
                                dispositivo['hostname']]
                            reportDF.report_swtCDP['ip'] = [array_ips[cont][0]]
                            #neighbor name
                            if sCDP.__contains__('Device ID'):
                                cdpNeighbor = sCDP.replace('Device ID', '')
                                cdpNeighbor = cdpNeighbor.replace(':', '')
                                cdpNeighbor = cdpNeighbor.replace(' ', '')
                                reportDF.report_swtCDP['neighbor'] = [
                                    cdpNeighbor]
                            #interface local
                            if sCDP.__contains__('Interface'):
                                cdpInterface = sCDP.split()
                                reportDF.report_swtCDP['Local Interface'] = [
                                    cdpInterface[1].replace(',', '')]
                            #neighbor type
                            if sCDP.__contains__('Capabilities'):
                                cdpCapabilities = sCDP.split("Capabilities:")
                                reportDF.report_swtCDP['Capabilities'] = [
                                    cdpCapabilities[1].removeprefix(' ').replace(',', '')]
                            #neighbor IP
                            if sCDP.__contains__('IP address'):
                                cdpIP = sCDP.split(' ')
                                reportDF.report_swtCDP['IP Neig'] = [
                                    cdpIP[len(cdpIP)-1]]
                            #neighbor port
                            if sCDP.__contains__('Port ID'):
                                cdpPort = sCDP.split(' ')
                                reportDF.report_swtCDP['Port ID'] = [
                                    cdpPort[len(cdpPort)-1]]
                        coletaDF.dfSwtCDP = pd.concat(
                            [coletaDF.dfSwtCDP, reportDF.report_swtCDP], ignore_index=True)
                        reportDF.report_swtCDP = pd.DataFrame(index=None)

                    # device.close()
                    contRela = 1
                    break
                except (netmiko.ReadTimeout):
                    contError += 1
                    continue
                except Exception as err:
                    print(f'{bcolors.ENDC}------ERRO swtCDP------')
                    print(err)
                    print(array_ips[cont][0])
                    print(device['transport'])
                    print(f'------------------{bcolors.ENDC}')
                    break
            if (contError < 3):
                tempo_final = datetime.datetime.now()
                tempo_delta = tempo_final - tempo_init
                print(f'{bcolors.OKGREEN}Execução com Sucesso no IP: {bcolors.ENDC}' +
                      array_ips[cont][0]+f'{bcolors.OKGREEN} em '+str(tempo_delta.total_seconds())+f' segundos.{bcolors.ENDC}')
            else:
                print(
                    f'{bcolors.FAIL}Falha na requisição de informações devido a conexão instavel no IP: {bcolors.ENDC}'+array_ips[cont][0])
                coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                    {'ip': [array_ips[cont][0]], 'falha':['conexão instavel']}, index=None)], ignore_index=True)
            loopLogin = True
            break

        except (netmiko.ReadTimeout, netmiko.NetMikoAuthenticationException, napalm.base.exceptions.ConnectionException):
            device.close()
            if (cont3 == range_secret-1):
                print(f'{bcolors.FAIL}falha no enable com IP: {bcolors.ENDC}' +
                      array_ips[cont][0])
                coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                    {'ip': [array_ips[cont][0]], 'falha':['enable']}, index=None)], ignore_index=True)
                loopLogin = True
                break
            else:
                loopLogin = True
            continue

        except Exception as err:
                            exception_type = type(err)
                            print(f'{bcolors.WARNING}------ERRO 5------')
                            print(exception_type)
                            print(f'------------------{bcolors.ENDC}')
    return coletaDF, reportDF


autoColetaVita()