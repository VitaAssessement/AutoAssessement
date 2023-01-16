import pandas as pd
from cores import bcolors
from tkinter import filedialog
import PySimpleGUI as sg
import requests
from alive_progress import alive_bar
from multiprocessing.pool import ThreadPool as Pool
from selecSheet import selecSheet
from looparIPs import looparIPs
from escribaExcel import escribaExcel

pool_size = 5 #quantidade de processamentos simultaneos no multithread

def autoColeta():
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
                     dfRelacaoLogin=None,
                     dfShowVersion=None,
                     dfSwtCDP=None,
                     dfVTP=None,
                     dfShowInventory=None,
                     dfSwtInterfaces=None,
                     dfInterfaceBrief=None,
                     dfVlan=None,
                     dfIpARP=None,
                     dfMacAddr=None,
                     dfMacCount=None,
                     dfSemConexao=None,
                     dfSemLogin=None):
            self.dfRelacaoLogin = dfRelacaoLogin if dfRelacaoLogin is not None else pd.DataFrame([
            ], index=None)
            self.dfShowVersion = dfShowVersion if dfShowVersion is not None else pd.DataFrame([
            ], index=None)
            self.dfSwtCDP = dfSwtCDP if dfSwtCDP is not None else pd.DataFrame(
                [], index=None)
            self.dfVTP = dfVTP if dfVTP is not None else pd.DataFrame(
                [], index=None)
            self.dfShowInventory = dfShowInventory if dfShowInventory is not None else pd.DataFrame([
            ], index=None)
            self.dfSwtInterfaces = dfSwtInterfaces if dfSwtInterfaces is not None else pd.DataFrame([
            ], index=None)
            self.dfInterfaceBrief = dfInterfaceBrief if dfInterfaceBrief is not None else pd.DataFrame([
            ], index=None)
            self.dfVlan = dfVlan if dfVlan is not None else pd.DataFrame(
                [], index=None)
            self.dfIpARP = dfIpARP if dfIpARP is not None else pd.DataFrame(
                [], index=None)
            self.dfMacAddr = dfMacAddr if dfMacAddr is not None else pd.DataFrame(
                [], index=None)
            self.dfMacCount = dfMacCount if dfMacCount is not None else pd.DataFrame([
            ], index=None)
            self.dfSemConexao = dfSemConexao if dfSemConexao is not None else pd.DataFrame(
                [], columns=['ip','modo'], index=None)
            self.dfSemLogin = dfSemLogin if dfSemLogin is not None else pd.DataFrame(
                [], columns=['ip', 'falha'], index=None)

    class reports:
        def __init__(self,
                     report_relacaoLogin=None,
                     report_showVersion=None,
                     report_swtCDP=None,
                     report_vtp=None,
                     report_showInventory=None,
                     report_swtInterfaces=None,
                     report_interfaceBrief=None,
                     report_vlan=None,
                     report_ipARP=None,
                     report_macAddr=None,
                     report_macCount=None):
            self.report_relacaoLogin = report_relacaoLogin if report_relacaoLogin is not None else pd.DataFrame([
            ], index=None)
            self.report_showVersion = report_showVersion if report_showVersion is not None else pd.DataFrame([
            ], index=None)
            self.report_swtCDP = report_swtCDP if report_swtCDP is not None else pd.DataFrame([
            ], index=None)
            self.report_vtp = report_vtp if report_vtp is not None else pd.DataFrame([
            ], index=None)
            self.report_showInventory = report_showInventory if report_showInventory is not None else pd.DataFrame([
            ], index=None)
            self.report_swtInterfaces = report_swtInterfaces if report_swtInterfaces is not None else pd.DataFrame([
            ], index=None)
            self.report_interfaceBrief = report_interfaceBrief if report_interfaceBrief is not None else pd.DataFrame([
            ], index=None)
            self.report_vlan = report_vlan if report_vlan is not None else pd.DataFrame([
            ], index=None)
            self.report_ipARP = report_ipARP if report_ipARP is not None else pd.DataFrame([
            ], index=None)
            self.report_macAddr = report_macAddr if report_macAddr is not None else pd.DataFrame([
            ], index=None)
            self.report_macCount = report_macCount if report_macCount is not None else pd.DataFrame([
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

        event, values = sg.Window("Deseja rodar algum comando adicional?", [[sg.Text(
            "Deseja rodar algum comando adicional?")], [sg.Button('Sim'), sg.Button('Não')]]).read(close=True)

        if event == 'Sim':
            modo_config = True
        else:
            modo_config = False

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
        if (modo_config):
            array_comandos = selecSheet(
                'selecione o nome da planilha que contém os comandos a serem executados', xl, None)
            if (array_comandos == ['cancelado']).all():
                return
        else:
            array_comandos = None
        xl.close()
    except TimeoutError:
        print('blabla')
    '''except Exception:
        print(f'{bcolors.BOLD}operação cancelada{bcolors.ENDC}')
        return'''

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
        
        pool = Pool(pool_size)

        for ip in array_ips:
            pool.apply_async(looparIPs, (ip,reports,bar,array_login,pastaLogs,array_secret,modo_config,array_comandos,coletaDF))
            #looparIPs(ip,reports,bar,array_login,pastaLogs,array_secret,modo_config,array_comandos,coletaDF)
        pool.close()
        pool.join()
#################################################################################################################################

    try:
        print(f'\n{bcolors.HEADER}selecione onde salvar a relação de logins{bcolors.ENDC}')
        file_name = filedialog.asksaveasfilename(  # salvando arquivo de resultados
            filetypes=[('excel file', '*.xlsx')], defaultextension='.xlsx')
        if (file_name == ''):
            return

        with pd.ExcelWriter(file_name) as writer:
            escribaExcel(writer, 'Relação Logins', coletaDF.dfRelacaoLogin)
            escribaExcel(writer, 'Show Version', coletaDF.dfShowVersion)
            escribaExcel(writer, 'Show Inventory', coletaDF.dfShowInventory)
            escribaExcel(writer, 'swt-Interfaces', coletaDF.dfSwtInterfaces)
            escribaExcel(writer, 'Interface Brief', coletaDF.dfInterfaceBrief)
            escribaExcel(writer, 'swt-cdp', coletaDF.dfSwtCDP)
            escribaExcel(writer, 'vtp', coletaDF.dfVTP)
            escribaExcel(writer, 'vlan', coletaDF.dfVlan)
            escribaExcel(writer, 'IP ARP', coletaDF.dfIpARP)
            escribaExcel(writer, 'MAC-Addr', coletaDF.dfMacAddr)
            escribaExcel(writer, 'MAC-COUNT', coletaDF.dfMacCount)
            escribaExcel(writer, 'falha login', coletaDF.dfSemLogin)
            escribaExcel(writer, 'falha conexão', coletaDF.dfSemConexao)

        return

    except Exception as err:
        exception_type = type(err).__name__
        print(f'{bcolors.WARNING}------ERRO 6------')
        print(exception_type)
        print(f'------------------{bcolors.ENDC}')
