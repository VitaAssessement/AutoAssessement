import pandas as pd
import datetime
import re
import os
import napalm.base.exceptions
import napalm
import netmiko
import numpy as np
from cores import bcolors
from DadosColeta.relacaoLogin import relacaoLogin
from DadosColeta.showVersion import showVersion
from DadosColeta.interfaceBrief import interfaceBrief
from DadosColeta.ipARP import ipARP
from DadosColeta.macAddr import macAddr
from DadosColeta.MacCount import MacCount
from DadosColeta.showInventory import showInventory
from DadosColeta.swtCDP import swtCDP
from DadosColeta.swtInterfaces import swtInterfaces
from DadosColeta.vlan import vlan
from DadosColeta.vtp import vtp

def rodarColeta(tempo_init, cont2, ip, array_login, array_secret, array_comandos, modo_config, device, reportDF, coletaDF):
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

            dispositivo = device.get_facts()

        #relacaoLogin = ['ip','username','password','secret','privilege','modo','nome','modelo','serial','IOS']
            coletaDF.dfRelacaoLogin, contError = relacaoLogin(coletaDF,reportDF,ip,array_login[cont2],device,array_secret[cont3],dispositivo)

        #showVersion = ['Hostname','ip','modelo','serial','IOS','Rom','uptime','license Level','Configuration Register']
            coletaDF.dfShowVersion, contError = showVersion(reportDF,dispositivo,ip,device,coletaDF)
            
        #swtCDP = ['Hostname','ip','Neighbor','Local Interface','Holdtime','Capabilities','Platform','IP Neig','Port ID','Software','Versao','Release']
            coletaDF.dfSwtCDP, contError = swtCDP(device,reportDF,dispositivo,coletaDF,ip)
            
        #vtp = ['Hostname','ip','vtp Capable','vtp Running','vtp mode','domain name']
            coletaDF.dfVTP, contError = vtp(reportDF,dispositivo,device,coletaDF,ip)
            
        #showInventory   = ['Hostname','ip','NAME','DESC','PID','VID','SN']
            coletaDF.dfShowInventory, contError = showInventory(device,reportDF,dispositivo,ip,coletaDF)
            
        #swtInterfaces   = ['Hostname','ip','Port','Name','Status','Vlan','Duplex','Speed','Type']
            coletaDF.dfSwtInterfaces, contError = swtInterfaces(device,ip,reportDF,dispositivo,coletaDF)

        #interfaceBrief  = ['Hostname','ip','Interface','IP-Address','OK?','Method','Status','Protocol']
            coletaDF.dfInterfaceBrief, contError = interfaceBrief(device,ip,reportDF,dispositivo,coletaDF)

        #vlan            = ['Hostname','ip','Vlan ID','Vlan Name','Status','Ports']
            coletaDF.dfVlan, contError = vlan(device,reportDF,coletaDF,dispositivo,ip)

        #ipARP           = ['Hostname','ip','Protocol','Address','Age','Hardware Addr','Type','Interface']
            coletaDF.dfIpARP, contError = ipARP(device,ip,reportDF,dispositivo,coletaDF)

        #macAddr         = ['Hostname','ip','vlan','mac address','Type','protocols','port']
            coletaDF.dfMacAddr, contError = macAddr(device,ip,reportDF,dispositivo,coletaDF)

        #MacCount        = ['Hostname','ip','Vlan','Dynamic Count','Statis Count','Total']
            coletaDF.dfMacCount, contError = MacCount(device,ip,reportDF,dispositivo,coletaDF)
    #################################################################################################################################
                # convertendo array bidimensional em array de string
            if (modo_config):
                array_comandos2 = [None]*len(array_comandos)
                for cont4 in range(len(array_comandos)):
                    array_comandos2[cont4] = str(array_comandos[cont4][0])
                # executando comandos(se houver)
                for cont4 in range(len(array_comandos)):
                    print(f'{bcolors.OKCYAN}executando comando: {bcolors.ENDC}' +
                          array_comandos2[cont4])
                    # executando comandos
                    device._netmiko_device.send_command_timing(
                        array_comandos2[cont4], strip_command=False)
            if (contError < 3):
                tempo_final = datetime.datetime.now()
                tempo_delta = tempo_final - tempo_init
                print(f'{bcolors.OKGREEN}Execução com Sucesso no IP: {bcolors.ENDC}' +
                      ip[0]+f'{bcolors.OKGREEN} em '+str(tempo_delta.total_seconds())+f' segundos.{bcolors.ENDC}')
            else:
                print(
                    f'{bcolors.FAIL}Falha na requisição de informações devido a conexão instavel no IP: {bcolors.ENDC}'+ip[0])
                coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                    {'ip': [ip[0]], 'falha':['conexão instavel']}, index=None)], ignore_index=True)
            loopLogin = True
            break

        except (netmiko.ReadTimeout, netmiko.NetMikoAuthenticationException, napalm.base.exceptions.ConnectionException):
            device.close()
            if (cont3 == range_secret-1):
                print(f'{bcolors.FAIL}falha no enable com IP: {bcolors.ENDC}' +
                      ip[0])
                coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                    {'ip': [ip[0]], 'falha':['enable']}, index=None)], ignore_index=True)
                loopLogin = True
                break
            else:
                loopLogin = True
            continue

        #except UnboundLocalError:
        #    print('')

        except Exception as err:
                            exception_type = type(err)
                            print(f'{bcolors.WARNING}------ERRO 5------')
                            print(exception_type)
                            print(f'------------------{bcolors.ENDC}')
    return coletaDF, reportDF
