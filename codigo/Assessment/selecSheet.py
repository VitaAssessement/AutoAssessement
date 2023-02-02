from cores import bcolors
import PySimpleGUI as sg

'''
cria uma janela com uma lista dinamica e retorna um dos valores dessa lista
'''


# recebe o texto, o arquivo excel de escolha e o cabeçalho do prompt
def selecSheet(texto, xl, cabecalho):
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
