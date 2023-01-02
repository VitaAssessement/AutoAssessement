import napalm.base.exceptions
import netmiko
import napalm
import pandas as pd
from tkinter import filedialog
import PySimpleGUI as sg
import numpy as np
import re
import datetime

def autoColetaVita():

    '''Vinicius Conti Sardinha
        CPF: 509.514.378-01'''

    class dataFrames:
        def __init__(self,
        dfRelacaoLogin = None,
        dfShowVersion = None,
        dfSwtCDP = None,
        dfVTP = None,
        dfShowInventory = None,
        dfSwtInterfaces = None,
        dfInterfaceBrief = None,
        dfVlan = None,
        dfIpARP = None,
        dfMacAddr = None,
        dfMacCount = None,
        dfSemConexao = None,
        dfSemLogin = None):
            self.dfRelacaoLogin = dfRelacaoLogin if dfRelacaoLogin is not None else pd.DataFrame([], index=None)
            self.dfShowVersion = dfShowVersion if dfShowVersion is not None else pd.DataFrame([], index=None)
            self.dfSwtCDP = dfSwtCDP if dfSwtCDP is not None else pd.DataFrame([], index=None)
            self.dfVTP = dfVTP if dfVTP is not None else pd.DataFrame([], index=None)
            self.dfShowInventory = dfShowInventory if dfShowInventory is not None else pd.DataFrame([], index=None)
            self.dfSwtInterfaces = dfSwtInterfaces if dfSwtInterfaces is not None else pd.DataFrame([], index=None)
            self.dfInterfaceBrief = dfInterfaceBrief if dfInterfaceBrief is not None else pd.DataFrame([], index=None)
            self.dfVlan = dfVlan if dfVlan is not None else pd.DataFrame([], index=None)
            self.dfIpARP = dfIpARP if dfIpARP is not None else pd.DataFrame([], index=None)
            self.dfMacAddr = dfMacAddr if dfMacAddr is not None else pd.DataFrame([], index=None)
            self.dfMacCount = dfMacCount if dfMacCount is not None else pd.DataFrame([], index=None)
            self.dfSemConexao = dfSemConexao if dfSemConexao is not None else pd.DataFrame([], columns=['ip'], index=None)
            self.dfSemLogin = dfSemLogin  if dfSemLogin is not None else pd.DataFrame([], columns=['ip','falha'], index=None)

    class reports:
        def __init__(self,
        report_relacaoLogin = None,
        report_showVersion = None,
        report_swtCDP = None,
        report_vtp = None,
        report_showInventory = None,
        report_swtInterfaces = None,
        report_interfaceBrief = None,
        report_vlan = None,
        report_ipARP = None,
        report_macAddr = None,
        report_macCount = None):
            self.report_relacaoLogin     = report_relacaoLogin if report_relacaoLogin is not None else pd.DataFrame([], index=None)
            self.report_showVersion      = report_showVersion if report_showVersion is not None else pd.DataFrame([], index=None)
            self.report_swtCDP           = report_swtCDP if report_swtCDP is not None else pd.DataFrame([], index=None)
            self.report_vtp              = report_vtp if report_vtp is not None else pd.DataFrame([], index=None)
            self.report_showInventory    = report_showInventory if report_showInventory is not None else pd.DataFrame([], index=None)
            self.report_swtInterfaces    = report_swtInterfaces if report_swtInterfaces is not None else pd.DataFrame([], index=None)
            self.report_interfaceBrief   = report_interfaceBrief if report_interfaceBrief is not None else pd.DataFrame([], index=None)
            self.report_vlan             = report_vlan if report_vlan is not None else pd.DataFrame([], index=None)
            self.report_ipARP            = report_ipARP if report_ipARP is not None else pd.DataFrame([], index=None)
            self.report_macAddr          = report_macAddr if report_macAddr is not None else pd.DataFrame([], index=None)
            self.report_macCount         = report_macCount if report_macCount is not None else pd.DataFrame([], index=None)

    coletaDF = dataFrames()

    modo_config = False

    # abrindo arquivo excel
#################################################################################################################################

    try:
        xl = pd.ExcelFile(filedialog.askopenfilename(
            title='por favor selecione o arquivo Excel'))
    except Exception:
        print('nenhum arquivo foi selecionado')
        return

    # lendo arquivo excel
    try:

        event, values = sg.Window("Deseja rodar algum comando adicional?", [[sg.Text("Deseja rodar algum comando adicional?")],[sg.Button('Sim'), sg.Button('Não')] ]).read(close=True)

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
        if(modo_config):
            array_comandos = selecSheet(
                'selecione o nome da planilha que contém os comandos a serem executados', xl, None)
            if (array_comandos == ['cancelado']).all():
                return
        else:
            array_comandos = None
        xl.close()
    except Exception:
        print('operação cancelada')
        return

#################################################################################################################################
    try:
        sg.popup_ok(
        'Por Favor selecione a pasta onde serão salvos os logs')    #selecionando onde salvar os logs
        pastaLogs = filedialog.askdirectory(
        title='Por Favor selecione a pasta onde serão salvos os logs')  
    except Exception as err:
        exception_type = type(err).__name__
        print('-----ERRO 1------')
        print(exception_type)
        print('------------------')



#################################################################################################################################
    tempo_inicial = datetime.datetime.now()
    cont = 0
    for cont in range(len(array_ips)):
        
        reportDF = reports()

        loopLogin = False
        cont2 = 0
        print('conectando via ssh a: '+array_ips[cont][0])
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
                            optional_args={'transport':'ssh',
                            "session_log": pastaLogs+'/'+array_ips[cont][0]+'_SSH'+'.txt',
                            'force_no_enable':'True'})
                    
                try:
                    device.open()
                    coletaDF, reportDF = rodarColeta(tempo_init=tempo_init,cont=cont,cont2=cont2,array_ips=array_ips,array_login=array_login,array_secret=array_secret,modo_config=modo_config,array_comandos=array_comandos,device=device,coletaDF=coletaDF,reportDF=reportDF)
                    break
                except (netmiko.NetMikoTimeoutException, napalm.base.exceptions.ConnectionException):
                    loopLogin = True
                    continue

                except (netmiko.NetMikoAuthenticationException, netmiko.ReadException):
                    if (cont2 == len(array_login)-1):
                        print('falha no login com IP: ' +
                        array_ips[cont][0])
                        coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                        {'ip': [array_ips[cont][0]],'falha':['login']}, index=None)], ignore_index=True)
                    continue

                except ConnectionRefusedError:
                    if (cont2 == len(array_login)-1):
                        print('falha no login com IP: ' +
                        array_ips[cont][0])
                        coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                        {'ip': [array_ips[cont][0]],'falha':['recusado - SSH']}, index=None)], ignore_index=True)
                    continue

                '''except Exception as err:
                    exception_type = type(err)
                    print('------ERRO 3------')
                    print(exception_type)
                    print('------------------')'''

                device.close()
        
        loopLogin = False
        cont2 = 0
        print('conectando via telnet a: '+array_ips[cont][0])
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
                        optional_args={'transport':'telnet',
                        "session_log": pastaLogs+'/'+array_ips[cont][0]+'_TELNET'+'.txt',
                        'force_no_enable':'True'})
                try:
                    device.open()
                    coletaDF, reportDF = rodarColeta(tempo_init=tempo_init,cont=cont,cont2=cont2,array_ips=array_ips,array_login=array_login,array_secret=array_secret,modo_config=modo_config,array_comandos=array_comandos,device=device,coletaDF=coletaDF,reportDF=reportDF)
                    break
                except netmiko.NetmikoAuthenticationException:
                    if (cont2 == len(array_login)-1):
                        print('falha no login com IP: ' +
                        array_ips[cont][0])
                        coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                        {'ip': [array_ips[cont][0]],'falha':['login']}, index=None)], ignore_index=True)
                    continue

                except ConnectionRefusedError:
                    if (cont2 == len(array_login)-1):
                        print('falha no login com IP: ' +
                        array_ips[cont][0])
                        coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                        {'ip': [array_ips[cont][0]],'falha':['recusado - TELNET']}, index=None)], ignore_index=True)
                    continue

                except (netmiko.NetMikoTimeoutException, netmiko.ReadTimeout, napalm.base.exceptions.ConnectionException):
                    loopLogin = True
                    break

                except TimeoutError:
                    print('falha na conexão com IP: ' + array_ips[cont][0])
                    coletaDF.dfSemConexao = pd.concat([coletaDF.dfSemConexao, pd.DataFrame(
                    {'ip': [array_ips[cont][0]]}, index=None)], ignore_index=True)
                    loopLogin = True
                    break

                except Exception as err:
                    exception_type = type(err).__name__
                    print('------ERRO 2------')
                    print(exception_type)
                    print('------------------')


                
#################################################################################################################################

    try:
        tempo_fim = datetime.datetime.now()
        print('selecione onde salvar a relação de logins')
        file_name = filedialog.asksaveasfilename(  # salvando arquivo de resultados
            filetypes=[('excel file', '*.xlsx')], defaultextension='.xlsx')
        if (file_name == ''):
            return
        
        with pd.ExcelWriter(file_name) as writer:
            escribaExcel(writer,'Relação Logins',coletaDF.dfRelacaoLogin)
            escribaExcel(writer,'Show Version',coletaDF.dfShowVersion)
            escribaExcel(writer,'Show Inventory',coletaDF.dfShowInventory)
            escribaExcel(writer,'swt-Interfaces',coletaDF.dfSwtInterfaces)
            escribaExcel(writer,'Interface Brief',coletaDF.dfInterfaceBrief)
            escribaExcel(writer,'swt-cdp',coletaDF.dfSwtCDP)
            escribaExcel(writer,'vtp',coletaDF.dfVTP)
            escribaExcel(writer,'vlan',coletaDF.dfVlan)
            escribaExcel(writer,'IP ARP',coletaDF.dfIpARP)
            escribaExcel(writer,'MAC-Addr',coletaDF.dfMacAddr)
            escribaExcel(writer,'MAC-COUNT',coletaDF.dfMacCount)
            escribaExcel(writer,'falha login',coletaDF.dfSemLogin)
            escribaExcel(writer,'falha conexão',coletaDF.dfSemConexao)
    
        print('execução finalizada em '+str((tempo_fim-tempo_inicial).total_seconds())+' segundos.')
        return

    except Exception as err:
        exception_type = type(err).__name__
        print('------ERRO 6------')
        print(exception_type)
        print('------------------')

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
        print('------ERRO 7------')
        print(exception_type)
        print('------------------')

#################################################################################################################################

def escribaExcel(writer, sheetName, df):
    df.to_excel(writer, sheet_name=sheetName, index=False, na_rep='NaN')

# Auto-adjust columns' width
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets[sheetName].set_column(col_idx, col_idx, column_width+2)

def rodarColeta(tempo_init,cont,cont2,array_ips,array_login,array_secret,array_comandos,modo_config,device,reportDF,coletaDF):
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
                            if not(device._netmiko_device.check_enable_mode()):
                                device._netmiko_device.enable()

    #################################################################################################################################
                        #relacaoLogin = ['ip','username','password','secret','privilege','modo','nome','modelo','serial','IOS']
                            contError=0                            
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
                                    #device._netmiko_device.send_command("terminal history")
                                    reportDF.report_relacaoLogin['ip'] = [array_ips[cont][0]]
                                    reportDF.report_relacaoLogin['username'] = [array_login[cont2][0]]
                                    reportDF.report_relacaoLogin['password'] = [array_login[cont2][1]]
                                    reportDF.report_relacaoLogin['secret'] = [array_secret[cont3][0]]
                                    
                                    reportDF.report_relacaoLogin['privilege'] = [device._netmiko_device.send_command(
                                                'show privilege', read_timeout=30).replace('Current privilege level is ','')]
                                    
                                    if (device.transport == 'telnet'):
                                        reportDF.report_relacaoLogin['modo'] = ['TELNET']
                                    else:
                                        reportDF.report_relacaoLogin['modo'] = ['SSH']

                                    dispositivo = device.get_facts()

                                    reportDF.report_relacaoLogin['nome'] = [dispositivo['hostname']]
                                    reportDF.report_relacaoLogin['modelo'] = [dispositivo['model']]
                                    reportDF.report_relacaoLogin['serial'] = [dispositivo['serial_number']]
                                    reportDF.report_relacaoLogin['IOS'] = [dispositivo['os_version']]

                                    coletaDF.dfRelacaoLogin = pd.concat([coletaDF.dfRelacaoLogin, reportDF.report_relacaoLogin], ignore_index=True)
                                    #device.close()
                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO relacaoLogin------')
                                    print(err)
                                    print('------------------')
                                    break

    #################################################################################################################################
                        #showVersion = ['Hostname','ip','modelo','serial','IOS','Rom','uptime','license Level','Configuration Register']
                            if contError < 3:
                                contError=0                            
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
                                
                                    reportDF.report_showVersion['Hostname'] = [dispositivo['hostname']]
                                    reportDF.report_showVersion['ip'] = [array_ips[cont][0]]
                                    reportDF.report_showVersion['modelo'] = [dispositivo['model']]
                                    reportDF.report_showVersion['serial'] = [dispositivo['serial_number']]

                                    prompt_show_version = device._netmiko_device.send_command('show version', read_timeout=30,)
                                    if (prompt_show_version.__contains__('% Ambiguous command') or prompt_show_version.__contains__('% Invalid input detected at \'^\' marker')):
                                        print('------ERRO showVersion------')
                                        print('Comando Invalido')
                                        print('------------------')
                                        break
                                    show_version = prompt_show_version.split('\n')

                                    #def contemSVersionIOS(lista):
                                    #    return lista.__contains__('')
                                    #show_versionIOS1 = filter(contemSVersionIOS,show_version)
                                    #for show_versionIOS2 in show_versionIOS1:
                                    #    show_versionIOS += show_versionIOS2
                                    #show_versionIOS = show_versionIOS.replace(' ','')
                                    reportDF.report_showVersion['IOS'] = [show_version[0].split(',')[1]]
                                    reportDF.report_showVersion['Rom'] = [dispositivo['os_version'].replace('Version ','').split(',')[1]]
                                    reportDF.report_showVersion['uptime'] = [str(datetime.timedelta(seconds=dispositivo['uptime']))]
                                    
                                    for idShowVersion,SVersion in enumerate(show_version):
                                        if SVersion.__contains__('SW Image'):
                                            reportDF.report_showVersion['license level'] = [show_version[idShowVersion+2][SVersion.index('SW Image'):len(SVersion)].split()[0]]
                                        if SVersion.__contains__('Configuration register'):
                                            confReg = SVersion.replace('Configuration register is','')
                                            confReg = confReg.replace(' ','')
                                            reportDF.report_showVersion['Configuration Register'] = [confReg]

                                    #device.close()
                                    coletaDF.dfShowVersion = pd.concat([coletaDF.dfShowVersion, reportDF.report_showVersion], ignore_index=True)
                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO showVersion------')
                                    print(err)
                                    print('------------------')
                                    break
    #################################################################################################################################
                        #swtCDP = ['Hostname','ip','Neighbor','Local Interface','Holdtime','Capabilities','Platform','IP Neig','Port ID','Software','Versao','Release']
                            if contError < 3:
                                contError=0                        
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
                                    
                                    
                                    prompt_swtCDP = device._netmiko_device.send_command('show cdp neighbors detail', read_timeout=30)
                                    if (prompt_swtCDP.__contains__('% Ambiguous command') or prompt_swtCDP.__contains__('% Invalid input detected at \'^\' marker')):
                                        print('------ERRO swtCDP------')
                                        print('Comando Invalido')
                                        print('------------------')
                                        break
                                    swtCDPNeighbors = prompt_swtCDP.split('(Device ID)')
                                    

                                    for cdpCont in range(len(swtCDPNeighbors)):
                                        swtCDP1 = swtCDPNeighbors[cdpCont].split('\n')
                                        for sCDP in swtCDP1:
                                            reportDF.report_swtCDP['Hostname'] = [dispositivo['hostname']]
                                            reportDF.report_swtCDP['ip'] = [array_ips[cont][0]]
                                            if sCDP.__contains__('Device ID'):
                                                cdpNeighbor = sCDP.replace('Device ID','')
                                                cdpNeighbor = cdpNeighbor.replace(':','')
                                                cdpNeighbor = cdpNeighbor.replace(' ','')
                                                reportDF.report_swtCDP['neighbor'] = [cdpNeighbor]
                                            if sCDP.__contains__('Interface'):
                                                cdpInterface = sCDP.split()
                                                reportDF.report_swtCDP['Local Interface'] = [cdpInterface[1].replace(',','')]
                                            if sCDP.__contains__('Holdtime'):
                                                cdpHoldtime = sCDP.replace('Holdtime','')
                                                cdpHoldtime = cdpHoldtime.replace(':','')
                                                cdpHoldtime = cdpHoldtime.replace(' ','')
                                                cdpHoldtime = cdpHoldtime.replace('sec','')
                                                reportDF.report_swtCDP['Holdtime'] = [str(datetime.timedelta(seconds=int(cdpHoldtime)))]
                                            if sCDP.__contains__('Capabilities'):
                                                cdpCapabilities = sCDP.split("Capabilities:")
                                                reportDF.report_swtCDP['Capabilities'] = [cdpCapabilities[1].removeprefix(' ').replace(',','')]
                                            if sCDP.__contains__('Platform'):
                                                cdpPlatform = sCDP.split(' ')
                                                reportDF.report_swtCDP['Platform'] = [cdpPlatform[2].replace(',','')]
                                            if sCDP.__contains__('IP address'):
                                                cdpIP = sCDP.split(' ')
                                                reportDF.report_swtCDP['IP Neig'] = [cdpIP[len(cdpIP)-1]]
                                            if sCDP.__contains__('Port ID'):
                                                cdpPort = sCDP.split(' ')
                                                reportDF.report_swtCDP['Port ID'] = [cdpPort[len(cdpPort)-1]]
                                            if sCDP.__contains__(', Version'):
                                                cdpVersion = sCDP.split(',')
                                                reportDF.report_swtCDP['Software'] = [cdpVersion[1]]
                                                reportDF.report_swtCDP['Versao'] = [cdpVersion[2].replace('Version','').replace(' ','')]
                                                reportDF.report_swtCDP['Release'] = [cdpVersion[len(cdpVersion)-1]]
                                        coletaDF.dfSwtCDP = pd.concat([coletaDF.dfSwtCDP, reportDF.report_swtCDP], ignore_index=True)
                                        reportDF.report_swtCDP = pd.DataFrame(index=None)

                                    #device.close()
                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO swtCDP------')
                                    print(err)
                                    print('------------------')
                                    break
    #################################################################################################################################
                        #vtp = ['Hostname','ip','vtp Capable','vtp Running','vtp mode','domain name']
                            if contError < 3:
                                contError=0                        
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
                                    reportDF.report_vtp['Hostname'] = [dispositivo['hostname']]
                                    reportDF.report_vtp['ip'] = [array_ips[cont][0]]
                                    
                                    prompt_vtp = device._netmiko_device.send_command('show vtp status',read_timeout=30)
                                    if (prompt_vtp.__contains__('% Ambiguous command') or prompt_vtp.__contains__('% Invalid input detected at \'^\' marker')):
                                        print('------ERRO VTP------')
                                        print('Comando Invalido')
                                        print('------------------')
                                        break
                                    #print(prompt_vtp)
                                    vtp_status = prompt_vtp.split('\n')
                                    for vtp_line in vtp_status:
                                        if vtp_line.__contains__('capable'):
                                            reportDF.report_vtp['vtp capable'] = [vtp_line.split(':')[1].removeprefix(' ')]
                                        if vtp_line.__contains__('running'):
                                            reportDF.report_vtp['vtp Running'] = [vtp_line.split(':')[1].removeprefix(' ')]
                                        if vtp_line.__contains__('Operating Mode'):
                                            reportDF.report_vtp['vtp mode'] = [vtp_line.split(':')[1].removeprefix(' ')]
                                        if vtp_line.__contains__('Domain Name'):
                                            reportDF.report_vtp['domain name'] = [vtp_line.split(':')[1].removeprefix(' ')]
                                        
                                    #device.close()
                                    coletaDF.dfVTP = pd.concat([coletaDF.dfVTP, reportDF.report_vtp], ignore_index=True)
                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO VTP------')
                                    print(err)
                                    print('------------------')
                                    break
    #################################################################################################################################
                        #showInventory   = ['Hostname','ip','NAME','DESC','PID','VID','SN']
                            if contError < 3:
                                contError=0                        
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
        
                                    prompt_show_inventory = device._netmiko_device.send_command('show inventory',read_timeout=30)
                                    if (prompt_show_inventory.__contains__('% Ambiguous command') or prompt_show_inventory.__contains__('% Invalid input detected at \'^\' marker')):
                                        print('------ERRO showInventory------')
                                        print('Comando Invalido')
                                        print('------------------')
                                        break
                                    #print(prompt_show_inventory)
                                    showInventorySect = ['NAME'+x for x in prompt_show_inventory.split('NAME') if x]
                                    
                                    for inventoryCont in range(len(showInventorySect)):
                                        #print(showInventorySect[inventoryCont])
                                        showInventory1 = showInventorySect[inventoryCont].split('\n')
                                        for sInv in showInventory1:
                                            reportDF.report_showInventory['Hostname'] = [dispositivo['hostname']]
                                            reportDF.report_showInventory['ip'] = [array_ips[cont][0]]
                                            if sInv.__contains__('NAME'):
                                                sInvNameDesc = sInv.split('\"')
                                                #print(sInvNameDesc[1])
                                                reportDF.report_showInventory['NAME'] = [sInvNameDesc[1]]
                                                #print(sInvNameDesc[3])
                                                reportDF.report_showInventory['DESC'] = [sInvNameDesc[3]]
                                            if sInv.__contains__('PID'):
                                                sInvPIDVIDSN = sInv.split(',')
                                                reportDF.report_showInventory['PID'] = [sInvPIDVIDSN[0].replace('PID:','').strip()]
                                                reportDF.report_showInventory['VID'] = [sInvPIDVIDSN[1].replace('VID:','').strip()]
                                                reportDF.report_showInventory['SN'] = [sInvPIDVIDSN[2].replace('SN:','').strip()]
                                        #print(report_showInventory)        
                                        coletaDF.dfShowInventory = pd.concat([coletaDF.dfShowInventory, reportDF.report_showInventory], ignore_index=True)
                                    #device.close()
                                    #print(dfShowInventory)
                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO showInventory------')
                                    print(err)
                                    print('------------------')
                                    break
    #################################################################################################################################
                        #swtInterfaces   = ['Hostname','ip','Port','Name','Status','Vlan','Duplex','Speed','Type']
                            if contError < 3:
                                contError=0                        
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
                                    prompt_swtInterfaces = device._netmiko_device.send_command('show interfaces status',read_timeout=30)
                                    if (prompt_swtInterfaces.__contains__('% Ambiguous command') or prompt_swtInterfaces.__contains__('% Invalid input detected at \'^\' marker')):
                                        print('------ERRO swtInterfaces------')
                                        print('Comando Invalido')
                                        print('------------------')
                                        break
                                    if (prompt_swtInterfaces == ''):
                                        reportDF.report_swtInterfaces['Hostname'] = [dispositivo['hostname']]
                                        reportDF.report_swtInterfaces['ip'] = [array_ips[cont][0]]
                                        break
                                    swtInterfacesLines = prompt_swtInterfaces.split('\n')
                                    if swtInterfacesLines[0] == '':
                                        del swtInterfacesLines[0]
                                    for swtInterface in swtInterfacesLines:
                                        if not swtInterface.__contains__('Port'):
                                            reportDF.report_swtInterfaces['Hostname'] = [dispositivo['hostname']]
                                            reportDF.report_swtInterfaces['ip'] = [array_ips[cont][0]]
                                            reportDF.report_swtInterfaces['Port'] = [swtInterface[swtInterfacesLines[0].index('Port'):swtInterfacesLines[0].index('Name')-1].strip()]
                                            reportDF.report_swtInterfaces['Name'] = [swtInterface[swtInterfacesLines[0].index('Name'):swtInterfacesLines[0].index('Status')-1].strip()]
                                            reportDF.report_swtInterfaces['Status'] = [swtInterface[swtInterfacesLines[0].index('Status'):swtInterfacesLines[0].index('Vlan')-1].strip()]
                                            reportDF.report_swtInterfaces['Vlan'] = [swtInterface[swtInterfacesLines[0].index('Vlan'):swtInterfacesLines[0].index('Duplex')-1].strip()]
                                            reportDF.report_swtInterfaces['Duplex'] = [swtInterface[swtInterfacesLines[0].index('Duplex'):swtInterfacesLines[0].index('Speed')-1].strip()]
                                            reportDF.report_swtInterfaces['Speed'] = [swtInterface[swtInterfacesLines[0].index('Speed')-1:swtInterfacesLines[0].index('Type')-1].strip()]
                                            reportDF.report_swtInterfaces['Type'] = [swtInterface[swtInterfacesLines[0].index('Type'):len(swtInterface)].strip()]
                                            
                                        coletaDF.dfSwtInterfaces = pd.concat([coletaDF.dfSwtInterfaces, reportDF.report_swtInterfaces], ignore_index=True)
                                    #device.close()

                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO swtInterfaces------')
                                    print(err)
                                    print('------------------')
                                    break
    #################################################################################################################################
                        #interfaceBrief  = ['Hostname','ip','Interface','IP-Address','OK?','Method','Status','Protocol']
                            if contError < 3:
                                contError=0                        
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
                                    prompt_interfaceBrief = device._netmiko_device.send_command('show ip int brief',read_timeout=30)
                                    if (prompt_interfaceBrief.__contains__('% Ambiguous command') or prompt_interfaceBrief.__contains__('% Invalid input detected at \'^\' marker')):
                                        print('------ERRO interfaceBrief------')
                                        print('Comando Invalido')
                                        print('------------------')
                                        break
                                    #print('prompt_interfaceBrief')
                                    #print([prompt_interfaceBrief])
                                    
                                    interfaceBriefLines = prompt_interfaceBrief.split('\n')
                                    for interfaceBriefs in interfaceBriefLines:
                                        
                                        if not interfaceBriefs.__contains__('Interface'):
                                            reportDF.report_interfaceBrief['Hostname'] = [dispositivo['hostname']]
                                            reportDF.report_interfaceBrief['ip'] = [array_ips[cont][0]]
                                            reportDF.report_interfaceBrief['Interface'] = [interfaceBriefs[interfaceBriefLines[0].index('Interface'):interfaceBriefLines[0].index('IP-Address')-1].strip()]
                                            reportDF.report_interfaceBrief['IP-Address'] = [interfaceBriefs[interfaceBriefLines[0].index('IP-Address'):interfaceBriefLines[0].index('OK?')-1].strip()]
                                            reportDF.report_interfaceBrief['OK?'] = [interfaceBriefs[interfaceBriefLines[0].index('OK?'):interfaceBriefLines[0].index('Method')-1].strip()]
                                            reportDF.report_interfaceBrief['Method'] = [interfaceBriefs[interfaceBriefLines[0].index('Method'):interfaceBriefLines[0].index('Status')-1].strip()]
                                            reportDF.report_interfaceBrief['Status'] = [interfaceBriefs[interfaceBriefLines[0].index('Status'):interfaceBriefLines[0].index('Protocol')-1].strip()]
                                            reportDF.report_interfaceBrief['Protocol'] = [interfaceBriefs[interfaceBriefLines[0].index('Protocol'):len(interfaceBriefs)].strip()]
                                            
                                        coletaDF.dfInterfaceBrief = pd.concat([coletaDF.dfInterfaceBrief, reportDF.report_interfaceBrief], ignore_index=True)
                                    #device.close()
                                    
                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO interfaceBrief------')
                                    print(err)
                                    print('------------------')
                                    break
    #################################################################################################################################
                        #vlan            = ['Hostname','ip','Vlan ID','Vlan Name','Status','Ports']
                            if contError < 3:
                                contError=0                        
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
                                    #report_['Hostname'] = [dispositivo['hostname']]
                                    #report_['ip'] = [array_ips[cont][0]]
                                    
                                    prompt_vlans = device._netmiko_device.send_command('show vlan',read_timeout=30)
                                    if (prompt_vlans.__contains__('% Ambiguous command') or prompt_vlans.__contains__('% Invalid input detected at \'^\' marker')):
                                        prompt_vlans = device._netmiko_device.send_command('show vlans',read_timeout=30)
                                        if (prompt_vlans.__contains__('% Ambiguous command') or prompt_vlans.__contains__('% Invalid input detected at \'^\' marker')):
                                            print('------ERRO VLAN------')
                                            print('Comando Invalido')
                                            print('------------------')
                                            break
                                    if (prompt_vlans.__contains__('No Virtual LANs configured.')):
                                        reportDF.report_vlan['Hostname'] = [dispositivo['hostname']]
                                        reportDF.report_vlan['ip'] = [array_ips[cont][0]]
                                        reportDF.report_vlan['Vlan ID'] = ['No Virtual LANs configured.']
                                        coletaDF.dfVlan = pd.concat([coletaDF.dfVlan, reportDF.report_vlan], ignore_index=True)
                                        break
                                    vlanLines = prompt_vlans.split('\n')
                                    
                                    #for vcont in range(len(vlanLines)):
                                    #    print(vlanLines[vcont])
                                    #    print('-------')

                                    vlanN = ''
                                    vlanName = ''
                                    vlanStatus = ''
                                    vlanPorts = ''
                                    
                                    for vlans in vlanLines:
                                        if vlans == '' or vlans == ' ':
                                            continue
                                        if vlans.__contains__('Type  SAID'):
                                            break
                                        if not (vlans.__contains__('VLAN Name') or vlans.__contains__('----')):
                                            vlanN = vlans[vlanLines[1].index('VLAN'):vlanLines[1].index('Name')-1].strip()
                                            vlanName = vlans[vlanLines[1].index('Name'):vlanLines[1].index('Status')-1].strip()
                                            vlanStatus = vlans[vlanLines[1].index('Status'):vlanLines[1].index('Ports')-1].strip()
                                            vlanPorts = vlans[vlanLines[1].index('Ports'):len(vlans)].strip()
                                            reportDF.report_vlan['Hostname'] = [dispositivo['hostname']]
                                            reportDF.report_vlan['ip'] = [array_ips[cont][0]]      
                                            reportDF.report_vlan['Vlan ID'] = [vlanN]
                                            reportDF.report_vlan['Vlan Name'] = [vlanName]
                                            reportDF.report_vlan['Status'] = [vlanStatus]
                                            reportDF.report_vlan['Ports'] = [vlanPorts]
                                            coletaDF.dfVlan = pd.concat([coletaDF.dfVlan, reportDF.report_vlan], ignore_index=True)

                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO vlan------')
                                    print(err)
                                    print('------------------')
                                    break
    #################################################################################################################################
                        #ipARP           = ['Hostname','ip','Protocol','Address','Age','Hardware Addr','Type','Interface']
                            if contError < 3:
                                contError=0                        
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
                                    prompt_ipARP = device._netmiko_device.send_command('show ip ar',read_timeout=30)
                                    if (prompt_ipARP.__contains__('% Ambiguous command') or prompt_ipARP.__contains__('% Invalid input detected at \'^\' marker')):
                                        print('------ERRO ipARP------')
                                        print('Comando Invalido')
                                        print('------------------')
                                        break
                                    #print(prompt_ipARP)
                                    ipARPLines = prompt_ipARP.split('\n')
                                    for ipARPs in ipARPLines:
                                        
                                        if not ipARPs.__contains__('Protocol'):
                                            reportDF.report_ipARP['Hostname'] = [dispositivo['hostname']]
                                            reportDF.report_ipARP['ip'] = [array_ips[cont][0]]
                                            reportDF.report_ipARP['Protocol'] = [ipARPs[ipARPLines[0].index('Protocol'):ipARPLines[0].index('Address')-1].strip()]
                                            reportDF.report_ipARP['Address'] = [ipARPs[ipARPLines[0].index('Address'):ipARPLines[0].index('Age')-1].strip()]
                                            reportDF.report_ipARP['Age'] = [ipARPs[ipARPLines[0].index('Age'):ipARPLines[0].index('Hardware Addr')-1].strip()]
                                            reportDF.report_ipARP['Hardware Addr'] = [ipARPs[ipARPLines[0].index('Hardware Addr'):ipARPLines[0].index('Type')-1].strip()]
                                            reportDF.report_ipARP['Type'] = [ipARPs[ipARPLines[0].index('Type'):ipARPLines[0].index('Interface')-1].strip()]
                                            reportDF.report_ipARP['Interface'] = [ipARPs[ipARPLines[0].index('Interface'):len(ipARPs)].strip()]
                                            
                                        coletaDF.dfIpARP = pd.concat([coletaDF.dfIpARP, reportDF.report_ipARP], ignore_index=True)
                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO ipARP------')
                                    print(err)
                                    print('------------------')
                                    break
    #################################################################################################################################
                        #macAddr         = ['Hostname','ip','vlan','mac address','Type','protocols','port']
                            if contError < 3:
                                contError=0                        
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
                                    #report_['Hostname'] = [dispositivo['hostname']]
                                    #report_['ip'] = [array_ips[cont][0]]
                                    prompt_macAddr = device._netmiko_device.send_command('show mac address-table',read_timeout=30)
                                    if (prompt_macAddr.__contains__('% Ambiguous command') or prompt_macAddr.__contains__('% Invalid input detected at \'^\' marker')):
                                        prompt_macAddr = device._netmiko_device.send_command('show mac-address-table',read_timeout=30)
                                        if (prompt_macAddr.__contains__('% Ambiguous command') or prompt_macAddr.__contains__('% Invalid input detected at \'^\' marker')):
                                            print('------ERRO MacAddr------')
                                            print('Comando Invalido')
                                            print('------------------')
                                            break
                                    #print(prompt_macAddr)
                                    macAddrLines = prompt_macAddr.split('\n')
                                    if macAddrLines[0] == '':
                                        del macAddrLines[0]
                                    for macAddrs in macAddrLines:
                                        
                                        if not (macAddrs.__contains__('vlan') or macAddrs.__contains__('----') or macAddrs.__contains__('Unicast Entries') or macAddrs.__contains__('Destination Address  Address Type  VLAN  Destination Por') or macAddrs == '' or macAddrs.__contains__('Mac Address Tabl') or macAddrs.__contains__('Vlan    Mac Address       Type        Port') or macAddrs.__contains__('Total Mac Addresses for this criterion:')):
                                            if (prompt_macAddr.__contains__('-+-')):
                                                reportDF.report_macAddr['Hostname'] = [dispositivo['hostname']]
                                                reportDF.report_macAddr['ip'] = [array_ips[cont][0]]
                                                reportDF.report_macAddr['vlan'] = [macAddrs[0:macAddrLines[2].find('+')].strip()]
                                                macAddrMarker = macAddrLines[2].find('+')
                                                reportDF.report_macAddr['mac address'] = [macAddrs[macAddrMarker:macAddrLines[2].find('+',macAddrMarker+1)].strip()]
                                                macAddrMarker = macAddrLines[2].find('+',macAddrMarker+1)
                                                reportDF.report_macAddr['Type'] = [macAddrs[macAddrMarker:macAddrLines[2].find('+',macAddrMarker+1)].strip()]
                                                macAddrMarker = macAddrLines[2].find('+',macAddrMarker+1)
                                                reportDF.report_macAddr['protocols'] = [macAddrs[macAddrMarker:macAddrLines[2].find('+',macAddrMarker+1)].strip()]
                                                macAddrMarker = macAddrLines[2].find('+',macAddrMarker+1)
                                                reportDF.report_macAddr['port'] = [macAddrs[macAddrMarker:len(macAddrs)].strip()]
                                            else:
                                                reportDF.report_macAddr['Hostname'] = [dispositivo['hostname']]
                                                reportDF.report_macAddr['ip'] = [array_ips[cont][0]]
                                                reportDF.report_macAddr['vlan'] = [macAddrs[macAddrLines[3].index('Vlan'):macAddrLines[3].index('Mac')-1].strip()]
                                                reportDF.report_macAddr['mac address'] = [macAddrs[macAddrLines[3].index('Mac'):macAddrLines[3].index('Type')-1].strip()]
                                                reportDF.report_macAddr['Type'] = [macAddrs[macAddrLines[3].index('Type'):macAddrLines[3].index('Ports')-1].strip()]
                                                reportDF.report_macAddr['port'] = [macAddrs[macAddrLines[3].index('Ports'):len(macAddrs)].strip()]
                                        coletaDF.dfMacAddr = pd.concat([coletaDF.dfMacAddr, reportDF.report_macAddr], ignore_index=True)
                                        
                                    #device.close()
                                    #df = pd.concat([df, report_], ignore_index=True)
                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO MacAddr------')
                                    print(err)
                                    print('------------------')
                                    break
    #################################################################################################################################
                        #MacCount        = ['Hostname','ip','Vlan','Dynamic Count','Statis Count','Total']
                            if contError < 3:
                                contError=0
                            contRela =0    
                            while contRela == 0 and contError <3:
                                try:
                                    prompt_macCount = device._netmiko_device.send_command('show mac address-table count')
                                    if (prompt_macCount.__contains__('% Ambiguous command') or prompt_macCount.__contains__('% Invalid input detected at \'^\' marker')):
                                        prompt_macCount = device._netmiko_device.send_command('show mac-address-table count')
                                        if (prompt_macCount.__contains__('% Ambiguous command') or prompt_macCount.__contains__('% Invalid input detected at \'^\' marker')):
                                            print('------ERRO MacCount------')
                                            print('Comando Invalido')
                                            print('------------------')
                                            break
                                    if not any(letra_macCount.isalpha() for letra_macCount in prompt_macCount):
                                        reportDF.report_macCount['Hostname'] = [dispositivo['hostname']]
                                        reportDF.report_macCount['ip'] = [array_ips[cont][0]]
                                        coletaDF.dfMacCount = pd.concat([coletaDF.dfMacCount, reportDF.report_macCount], ignore_index=True)
                                        break
                                    #print(prompt_macCount)
                                    macCountSect = prompt_macCount.split('(Mac Entries)')
                                    
                                    for macCountCont in range(len(macCountSect)):
                                        mCount = macCountSect[macCountCont].split('\n')
                                        
                                        reportDF.report_macCount['Hostname'] = [dispositivo['hostname']]
                                        reportDF.report_macCount['ip'] = [array_ips[cont][0]]
                                        reportDF.report_macCount['Vlan'] = [re.sub(r"\D+", "", mCount[1])]
                                        reportDF.report_macCount['Dynamic Count'] = [re.sub(r"\D+", "", mCount[3])]
                                        reportDF.report_macCount['Static Count'] = [re.sub(r"\D+", "", mCount[4])]
                                        reportDF.report_macCount['Total'] = [re.sub(r"\D+", "", mCount[5])]
                                        coletaDF.dfMacCount = pd.concat([coletaDF.dfMacCount, reportDF.report_macCount], ignore_index=True)
                                            
                                            
                                    #device.close()
                                    
                                    contRela = 1
                                    break
                                except(netmiko.ReadTimeout):
                                    contError+=1
                                    continue
                                except Exception as err:
                                    print('------ERRO MacCount------')
                                    print(err)
                                    print('------------------')
                                    break
    #################################################################################################################################
                                # convertendo array bidimensional em array de string
                            if(modo_config):
                                array_comandos2 = [None]*len(array_comandos)
                                for cont4 in range(len(array_comandos)):
                                    array_comandos2[cont4] = str(array_comandos[cont4][0])
                            if (modo_config):
                                for cont4 in range(len(array_comandos)):    #executando comandos(se houver)
                                    print('executando comando: ' +
                                        array_comandos2[cont4])
                                    # executando comandos
                                    device._netmiko_device.send_command_timing(
                                        array_comandos2[cont4], strip_command=False)
                            if(contError < 3):
                                tempo_final = datetime.datetime.now()
                                tempo_delta = tempo_final - tempo_init
                                print('Execução com Sucesso no IP: '+array_ips[cont][0]+' em '+str(tempo_delta.total_seconds())+' segundos.')
                            else:
                                print('Falha na requisição de informações devido a conexão instavel no IP: '+array_ips[cont][0])
                                coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                                {'ip': [array_ips[cont][0]],'falha':['conexão instavel']}, index=None)], ignore_index=True)
                            loopLogin = True
                            break

                        except (netmiko.ReadTimeout, netmiko.NetMikoAuthenticationException, napalm.base.exceptions.ConnectionException):
                            device.close()
                            if (cont3 == range_secret-1):
                                print('falha no enable com IP: ' +
                                array_ips[cont][0])
                                coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                                {'ip': [array_ips[cont][0]],'falha':['enable']}, index=None)], ignore_index=True)
                                loopLogin = True
                                break
                            else:
                                loopLogin = True
                            continue

                        '''except Exception as err:
                            exception_type = type(err)
                            print('------ERRO 5------')
                            print(exception_type)
                            print('------------------')'''
                    return coletaDF,reportDF

autoColetaVita()
