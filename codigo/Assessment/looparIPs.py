from cores import bcolors
import pandas as pd
import datetime
import os
import napalm.base.exceptions
import napalm
import netmiko
from rodarColeta import rodarColeta

def looparIPs (ip,reports,bar,array_login,pastaLogs,array_secret,modo_config,array_comandos,coletaDF):
    try:

            reportDF = reports()

            loopLogin = False
            cont2 = 0
            bar.text(f'{bcolors.OKBLUE}conectando via {bcolors.HEADER}SSH{bcolors.OKBLUE} a: {bcolors.ENDC}'+ip[0])
            for cont2 in range(len(array_login)):
                if (loopLogin):
                    loopLogin = False
                    break
                else:
                    tempo_init = datetime.datetime.now()
                    driver = napalm.get_network_driver(ip[1])
                    device = driver(hostname=ip[0],
                                    username=array_login[cont2][0],
                                    password=array_login[cont2][1],
                                    timeout=120,
                                    optional_args={'transport': 'ssh',
                                                "session_log": pastaLogs+'/'+ip[0]+'_SSH'+'.txt',
                                                'force_no_enable': 'True'})

                    try:
                        device.open()
                        coletaDF, reportDF,loopLogin = rodarColeta(tempo_init=tempo_init, cont2=cont2, ip=ip, array_login=array_login,
                                                        array_secret=array_secret, modo_config=modo_config, array_comandos=array_comandos, device=device, coletaDF=coletaDF, reportDF=reportDF,loopLogin=loopLogin)
                        break
                    except (netmiko.NetMikoTimeoutException, napalm.base.exceptions.ConnectionException):
                        print(f'{bcolors.FAIL}falha na conexão via SSH com IP: {bcolors.ENDC}' + ip[0])
                        coletaDF.dfSemConexao = pd.concat([coletaDF.dfSemConexao, pd.DataFrame(
                            {'ip': [ip[0]], 'modo': ['SSH']}, index=None)], ignore_index=True)
                        loopLogin = True
                        continue

                    except (netmiko.NetMikoAuthenticationException, netmiko.ReadException):
                        if (cont2 == len(array_login)-1):
                            print(f'{bcolors.FAIL}falha no login com IP: {bcolors.ENDC}' +
                                ip[0])
                            coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                                {'ip': [ip[0]], 'falha':['login']}, index=None)], ignore_index=True)
                        continue

                    except ConnectionRefusedError:
                        if (cont2 == len(array_login)-1):
                            print(f'{bcolors.FAIL}falha no login com IP: {bcolors.ENDC}' +
                                ip[0])
                            coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                                {'ip': [ip[0]], 'falha':['recusado - SSH']}, index=None)], ignore_index=True)
                        continue

                    except TimeoutError:
                        print(f'{bcolors.FAIL}falha na conexão via SSH com IP: {bcolors.ENDC}' + ip[0])
                        coletaDF.dfSemConexao = pd.concat([coletaDF.dfSemConexao, pd.DataFrame(
                            {'ip': [ip[0]], 'modo': ['SSH']}, index=None)], ignore_index=True)
                        loopLogin = True
                        continue
                    
                    except UnboundLocalError:
                        print('')

                    except Exception as err:
                        exception_type = type(err)
                        print(f'{bcolors.WARNING}------ERRO 3------')
                        print(exception_type)
                        print(f'------------------{bcolors.ENDC}')

                    device.close()

            loopLogin = False
            cont2 = 0
            bar()
            bar.text(f'{bcolors.OKBLUE}conectando via {bcolors.HEADER}TELNET{bcolors.OKBLUE} a: {bcolors.ENDC}'+ip[0])
            for cont2 in range(len(array_login)):
                if (loopLogin):
                    loopLogin = False
                    break
                else:
                    tempo_init = datetime.datetime.now()
                    device = driver(hostname=ip[0],
                                    username=array_login[cont2][0],
                                    password=array_login[cont2][1],
                                    timeout=120,
                                    optional_args={'transport': 'telnet',
                                                "session_log": pastaLogs+'/'+ip[0]+'_TELNET'+'.txt',
                                                'force_no_enable': 'True'})
                    try:
                        device.open()
                        coletaDF, reportDF,loopLogin = rodarColeta(tempo_init=tempo_init, cont2=cont2, ip=ip, array_login=array_login,
                                                        array_secret=array_secret, modo_config=modo_config, array_comandos=array_comandos, device=device, coletaDF=coletaDF, reportDF=reportDF,loopLogin=loopLogin)
                        break
                    except netmiko.NetmikoAuthenticationException:
                        if (cont2 == len(array_login)-1):
                            print(f'{bcolors.FAIL}falha no login com IP: {bcolors.ENDC}' +
                                ip[0])
                            coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                                {'ip': [ip[0]], 'falha':['login']}, index=None)], ignore_index=True)
                        continue

                    except ConnectionRefusedError:
                        if (cont2 == len(array_login)-1):
                            print(f'{bcolors.FAIL}falha no login com IP: {bcolors.ENDC}' +
                                ip[0])
                            coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                                {'ip': [ip[0]], 'falha':['recusado - TELNET']}, index=None)], ignore_index=True)
                        continue

                    except (netmiko.NetMikoTimeoutException, netmiko.ReadTimeout, napalm.base.exceptions.ConnectionException):
                        loopLogin = True
                        break

                    except TimeoutError:
                        print(f'{bcolors.FAIL}falha na conexão via TELNET com IP: {bcolors.ENDC}' + ip[0])
                        coletaDF.dfSemConexao = pd.concat([coletaDF.dfSemConexao, pd.DataFrame(
                            {'ip': [ip[0]],'modo':['TELNET']}, index=None)], ignore_index=True)
                        loopLogin = True
                        break

                    except Exception as err:
                        exception_type = type(err).__name__
                        print(f'{bcolors.WARNING}------ERRO 2------')
                        print(exception_type)
                        print(f'------------------{bcolors.ENDC}')

            if os.path.getsize(pastaLogs+'/'+ip[0]+'_SSH'+'.txt') == 0:
                os.remove(pastaLogs+'/'+ip[0]+'_SSH'+'.txt')
            if os.path.getsize(pastaLogs+'/'+ip[0]+'_TELNET'+'.txt') == 0:
                os.remove(pastaLogs+'/'+ip[0]+'_TELNET'+'.txt')
            bar()

    except UnboundLocalError:
        print('')

    except Exception as err:
                        exception_type = type(err).__name__
                        print(f'{bcolors.WARNING}------ERRO 10------')
                        print(exception_type)
                        print(f'------------------{bcolors.ENDC}')
