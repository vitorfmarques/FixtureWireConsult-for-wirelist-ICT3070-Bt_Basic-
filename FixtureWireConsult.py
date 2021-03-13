import json, os, re
from PySimpleGUI import PySimpleGUI as sg
from time import sleep

version = 'v1.0.1'


def ConfigureConfig():
    '''
        Checks config file at root;
        If a file does not exist, it creates a standard version of the file automatically;
        '''
    Default = {
        'Version' : '1.0',
        'SystemRef' : 
        {
            'Name' : 'ICT 001',
            'SystemName' : 'brbelict001'
        }
    }
    
    DefaultContent = json.dumps(Default, indent = True)

    with open(r'config\config.json', 'w+') as file:
        file.write(DefaultContent)

def checkwirelist(ref) -> bool:
    '''
        Check condition of wireless files in the reference folder
        -> 'ref' = Reference name
        -> Return flag check (bool)
        '''
    try:
        file = open(refroot + '\\' + ref + '\\wirelist', 'r')

    except (FileExistsError,PermissionError,FileNotFoundError) as erro:
        print(f'Load erro ref >> {erro} <<')
        return False
        
    else:
        file.close()
        return True

def LabelValidation(label):
    '''
        Valid test label Expression
        '''
    exp_reg = re.compile(r'^[1-2]{1}%{1}\w')
    match = re.match(exp_reg, label)
    if match:
        return True
    else:
        return False


class Wiredata:

    def __init__(self, board, label):
        self.board = board
        self.label = label
        self.BoardWirelist = self.LoadBoardWirelist(board)
        self.LabelWirelist = self.LoadLabelWirelist()
        if not self.LabelWirelist == None:
            self.TestType = self.GetTestType()
            self.Module = self.GetModule()
            self.SubExist = self.SubCheck()

    def LoadBoardWirelist(self, board):
        with open(refroot + '\\' + board + '\\wirelist') as file:
            BoardWirelist = file.read()
            return BoardWirelist  

    def LoadLabelWirelist(self):
        # LabelWire = re.findall(fr'test \w+ "' + self.label + '\"' + r'.+end test', self.BoardWirelist, flags=re.M | re.DOTALL)
        LabelWire = re.findall(fr'test \w+ \"{self.label}\".+end test', self.BoardWirelist, flags=re.M | re.DOTALL)
        if LabelWire:
            LabelWire = LabelWire[0]
            cut_end = LabelWire.find('end test')
            LabelWire = LabelWire[:cut_end]  
            return LabelWire
        else:
            return None

    def GetTestType(self):
        testtype = re.findall(r'\w+', self.LabelWirelist)
        return testtype[1]

    def GetModule(self):
        if self.TestType == 'analog':   # Module info not present in analog test's wire list
            return None
        else:
            module = re.findall(r'\w+', self.LabelWirelist)
            return module[7]

    def SubCheck(self):
        if 'subtest' in self.LabelWirelist:
            return True
        else:
            return False

class Interface:

    sg.theme('DarkGreen')    

    def main_window(self):
        # Main Window
        # sg.theme('Reddit')
        # Main Layout
        main_layout = [
            [sg.Text('Fixture Reference: ')],
            [sg.Listbox(RefListAvl, size=(20,len(RefListAvl)), key='-SelectRef-', enable_events=True)],
            [sg.Text('Label Search: ')],
            [sg.Input(key='-SearchLabel-', focus=True)],
            [sg.Button('Show', key='-Show-', bind_return_key=True)],
        ]

        # Main Window
        return sg.Window('Fixture Wirelist Consult ' + version, main_layout,icon='appdata/icon.ico', finalize=True)

    def LoadErro(self):
        '''
            Window load, check files in folders error
            '''
        layout_column = [
                [sg.Text('Erro ao realizar leitura de referência.\n Verique a pasta de referências na raiz.',justification='center')],
        ]
        layout = [
            [sg.Column(layout_column, element_justification='center')],
            [sg.Button('OK', bind_return_key=True, focus=True)]
        ]

        window = sg.Window('Erro', layout, icon='appdata/icon.ico', grab_anywhere=True)

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit' or event == 'OK':
                break
        window.close()

    def ErroMsg(self, msg):
        '''
            Print erro msg. <msg>
            -> msg = string(msg print)
            '''
        layout_column = [
                [sg.Text(msg, justification='center')],
        ]

        layout = [
            [sg.Column(layout_column, element_justification='center')],
            [sg.Button('OK', bind_return_key=True, focus=True)]
        ]

        window = sg.Window('Erro', layout, icon='appdata/icon.ico', grab_anywhere=True)
        
        while True:
            event, value = window.read()
            if event == sg.WINDOW_CLOSED or value == 'OK' or event == 'OK':
                break
        window.close()


    def WireWindow(self, data):
        layout = [
            [sg.Text(data.label, justification='center')],
            [sg.Multiline(data.LabelWirelist, autoscroll=True, size=(45,15))],
            [sg.Button('Close', key='-close-', bind_return_key=True)]
        ]
        return sg.Window(data.label, layout, icon='appdata/icon.ico', location=(0,0), finalize=True)
# ===========================================================================

if __name__ == "__main__":

    main = Interface()
    # Check COnfig File Exist
    try:
        ConfigFile = open(r'config\config.json', 'r')
    except (FileExistsError, FileNotFoundError) as error:
        ConfigureConfig()
    else:
        ConfigFile.close()

    # Scanning the root folder of recerences
        # Walk files in paste 
    refroot = r'refs'
    RefList = []
    for Folder in os.listdir(refroot):
        RefList.append(Folder)

    # Check and lists correct wirelist files available
    RefListAvl = []
    fErro = False
    for ref in RefList:
        if checkwirelist(ref):
            RefListAvl.append(ref.lower())  # References available list
        else:
            fErro = True
            
    if fErro:
        main.LoadErro()
 
    main_window = main.main_window()        # main window create
    WindowListObjects = {}     # Window objects open list

    while True:

        InputErro = False
        window, event, value = sg.read_all_windows()

        if window == main_window and event == sg.WINDOW_CLOSED:
            break

        # Main Window Event
        if window == main_window and event == '-Show-':
            # Select Board 
            SelectBoard =  value['-SelectRef-']
            if len(SelectBoard) == 0 or not SelectBoard[0] in RefListAvl:
                print('Referência selecionada não encontrada\n')
                main.ErroMsg('Referência selecionada não encontrada')
                InputErro = True
            else:
                SelectBoard =  value['-SelectRef-'][0]

            # Search label
            SearchLabel = value['-SearchLabel-']

            if not LabelValidation(SearchLabel):
                print('Pesquisa no formato incorreto (1/2%nome')
                main.ErroMsg('Pesquisa no formato incorreto (1/2%nome)')
                InputErro = True

            if not InputErro:   # Create window list
                Selection = SelectBoard + SearchLabel                       # Permite abrir janela de mesma label em referencia diferente
                if Selection not in WindowListObjects.keys():
                    WirelistData = Wiredata(SelectBoard, SearchLabel)
                    NewWindow = Interface()
                    if WirelistData.LabelWirelist == None:
                        main.ErroMsg('Label não encontrada')
                        # WindowListObjects.update({SearchLabel: WindowObjet})
                    else:
                        WindowObjet = NewWindow.WireWindow(WirelistData)
                        WindowListObjects.update({Selection: WindowObjet})
                else:
                    print('ja foi aberto')
                    pass
        
        # Second Windows - OtherWindows monitor (Read)
        for LabelWindow_Selection, Object in WindowListObjects.items():
            if window == Object and event == '-close-':
                print('Event Detect in:', Object, '/', window)
                Object.Close()
                del WindowListObjects[LabelWindow_Selection]
                break
        
