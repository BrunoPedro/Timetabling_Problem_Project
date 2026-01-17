import pandas as pd
import os


class salas:
     
    def __init__(self, paramPath):

        self.listaParametros = pd.DataFrame()
        self.listaSalas = pd.DataFrame()
        
        try:
            self.listaParametros = pd.read_csv(paramPath, sep=";", encoding="utf-8", header=None)
        except FileNotFoundError:
            print(f"File '{paramPath}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        salasPath = os.path.join(self.listaParametros.iloc[0, 1], self.listaParametros.iloc[1, 1])
        
        try:
            self.listaSalas = pd.read_csv(salasPath, sep=";", encoding="utf-8-sig")
        except FileNotFoundError:
            print(f"File '{salasPath}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        
    def getCaracteristicas(self, linha):
        listaCaracteristicas = []
        for columnName, cellValue in self.listaSalas.iloc[linha].items():
            if cellValue == 'X':
                listaCaracteristicas.append(columnName)
        return ';'.join(listaCaracteristicas)

    def getRaridadeCaracteristicas(self, linha, caracteristica):
        listaRaridade = []
        listaCaractRaridades = []

        for column in self.listaSalas.columns[5:]:
            counts = self.listaSalas[column].count()
            listaRaridade.append([column, counts])

        listaCaracteristicas = self.getCaracteristicas(linha).split(';')
        if caracteristica in listaCaracteristicas:
            listaCaracteristicas.remove(caracteristica)

        for caracteristica in listaCaracteristicas:
            for raridade in listaRaridade:
                if raridade[0] == caracteristica:
                    listaCaractRaridades.append(raridade[1])
        return listaCaractRaridades
    

            
            
    def obterDados(self, coluna, linha):
        return self.listaSalas.iloc[linha, coluna]
    
    
    def getLotacao(self, linha):
        return self.obterDados(2, linha) 
    
    def getNome(self, linha):
        return self.obterDados(1, linha)
    
    
    def getListaParametros(self):
        return self.listaParametros
    
    
    def getListaSalas(self):
        return self.listaSalas
    
    def setListaSalas(self, novaLista: pd.DataFrame):
        self.listaSalas = novaLista
