from cores import bcolors
import pandas as pd
import datetime
import os
import napalm.base.exceptions
import napalm
import netmiko
from rodarColeta import rodarColeta

'''
script responsavel por loopar por todos os logins, registrar os logs e deletar logs vazios
'''


def looparIPs(ip, reports, bar, array_login, pastaLogs, array_secret, modo_config, array_comandos, coletaDF):
    try:
        # criando objeto de report
        reportDF = reports()

        loopLogin = False
        cont2 = 0

        # atualizando barra de loading
        bar.text(
            f'{bcolors.OKBLUE}conectando via {bcolors.HEADER}SSH{bcolors.OKBLUE} a: {bcolors.ENDC}'+ip[0])

        # iniciando loop de logins
        for cont2 in range(len(array_login)):
            if (loopLogin):  # caso não seja mais necessario loopar esse login
                loopLogin = False
                break
            else:
                # pegando tempo de inicio da operação no ip
                tempo_init = datetime.datetime.now()

                # iniciando driver de conexão via SSH
                driver = napalm.get_network_driver(ip[1])
                device = driver(hostname=ip[0],
                                username=array_login[cont2][0],
                                password=array_login[cont2][1],
                                timeout=120,
                                optional_args={'transport': 'ssh',
                                               "session_log": pastaLogs+'/'+ip[0]+'_SSH'+'.txt',
                                               'force_no_enable': 'True'})

                try:
                    # iniciando driver e rodando programa de coleta de dados
                    device.open()
                    coletaDF, reportDF, loopLogin = rodarColeta(tempo_init=tempo_init, cont2=cont2, ip=ip, array_login=array_login,
                                                                array_secret=array_secret, modo_config=modo_config, array_comandos=array_comandos, device=device, coletaDF=coletaDF, reportDF=reportDF, loopLogin=loopLogin)
                    break
                except (netmiko.NetMikoTimeoutException, napalm.base.exceptions.ConnectionException):
                    # caso não conecte
                    print(
                        f'{bcolors.FAIL}falha na conexão via SSH com IP: {bcolors.ENDC}' + ip[0])
                    coletaDF.dfSemConexao = pd.concat([coletaDF.dfSemConexao, pd.DataFrame(
                        {'ip': [ip[0]], 'modo': ['SSH']}, index=None)], ignore_index=True)
                    # não insistir na conexão SSH
                    loopLogin = True
                    continue

                except (netmiko.NetMikoAuthenticationException, netmiko.ReadException):
                    # caso de falha no login
                    if (cont2 == len(array_login)-1):
                        print(f'{bcolors.FAIL}falha no login com IP: {bcolors.ENDC}' +
                              ip[0])
                        coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                            {'ip': [ip[0]], 'falha':['login']}, index=None)], ignore_index=True)
                    # tentar proximo login
                    continue

                except ConnectionRefusedError:
                    # em alguns dispositivos ele responde com ssh recusado ao inves de falha no login
                    if (cont2 == len(array_login)-1):
                        print(f'{bcolors.FAIL}falha no login com IP: {bcolors.ENDC}' +
                              ip[0])
                        coletaDF.dfSemLogin = pd.concat([coletaDF.dfSemLogin, pd.DataFrame(  # salvando informações de falha de login
                            {'ip': [ip[0]], 'falha':['recusado - SSH']}, index=None)], ignore_index=True)
                    # tentar proximo login
                    continue

                except TimeoutError:
                    # sem resposta
                    print(
                        f'{bcolors.FAIL}falha na conexão via SSH com IP: {bcolors.ENDC}' + ip[0])
                    coletaDF.dfSemConexao = pd.concat([coletaDF.dfSemConexao, pd.DataFrame(
                        {'ip': [ip[0]], 'modo': ['SSH']}, index=None)], ignore_index=True)
                    # não insistir
                    loopLogin = True
                    continue

                except UnboundLocalError:
                    # de vez em quando ele cria um warning no casting de variaveis, essa exceção suprime esse warning
                    print('')

                except Exception as err:
                    # encompassar qualquer outra exceção não prevista
                    exception_type = type(err)
                    print(f'{bcolors.WARNING}------ERRO 3------')
                    print(exception_type)
                    print(f'------------------{bcolors.ENDC}')

                device.close()

        # setar infos pra conexão telnet
        loopLogin = False
        cont2 = 0

        # atualizar progresso da barra de loading
        bar()

        # atualizar texto da barra de loading
        bar.text(
            f'{bcolors.OKBLUE}conectando via {bcolors.HEADER}TELNET{bcolors.OKBLUE} a: {bcolors.ENDC}'+ip[0])

        # iniciar loop de login TELNET, segue a mesma lógica do outro mas para telnet
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
                    coletaDF, reportDF, loopLogin = rodarColeta(tempo_init=tempo_init, cont2=cont2, ip=ip, array_login=array_login,
                                                                array_secret=array_secret, modo_config=modo_config, array_comandos=array_comandos, device=device, coletaDF=coletaDF, reportDF=reportDF, loopLogin=loopLogin)
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
                    print(
                        f'{bcolors.FAIL}falha na conexão via TELNET com IP: {bcolors.ENDC}' + ip[0])
                    coletaDF.dfSemConexao = pd.concat([coletaDF.dfSemConexao, pd.DataFrame(
                        {'ip': [ip[0]], 'modo':['TELNET']}, index=None)], ignore_index=True)
                    loopLogin = True
                    break

                except Exception as err:
                    exception_type = type(err).__name__
                    print(f'{bcolors.WARNING}------ERRO 2------')
                    print(exception_type)
                    print(f'------------------{bcolors.ENDC}')

        # deletar arquivos de log vazios, ocorre quando não é possivel conectar a um device
        if os.path.getsize(pastaLogs+'/'+ip[0]+'_SSH'+'.txt') == 0:
            os.remove(pastaLogs+'/'+ip[0]+'_SSH'+'.txt')
        if os.path.getsize(pastaLogs+'/'+ip[0]+'_TELNET'+'.txt') == 0:
            os.remove(pastaLogs+'/'+ip[0]+'_TELNET'+'.txt')
        # atualiza a barra de loading
        bar()

    except UnboundLocalError:
        print('')

    except Exception as err:
        exception_type = type(err).__name__
        print(f'{bcolors.WARNING}------ERRO 10------')
        print(exception_type)
        print(f'------------------{bcolors.ENDC}')
