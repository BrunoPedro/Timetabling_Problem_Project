import pandas as pd
import os

class horario:

    def __init__(self, paramPath, horarioPath=None):

        self.listaParametros = pd.DataFrame()
        self.listaHorarios = pd.DataFrame()
        self.paramPath = paramPath
        
        
        try:
            self.listaParametros = pd.read_csv(paramPath, sep=";", encoding="utf-8-sig", header=None)
        except FileNotFoundError:
            print(f"File '{paramPath}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        if horarioPath is None:
            self.horarioPath = os.path.join(self.listaParametros.iloc[0, 1], self.listaParametros.iloc[1, 1])
        else:
            self.horarioPath = horarioPath
        try:
            self.listaHorarios = pd.read_csv(self.horarioPath, sep=";", encoding="utf-8")
        except FileNotFoundError:
            print(f"File '{horarioPath}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    
    def getListaParametros(self):
        return self.listaParametros
    
    def getListaHorarios(self):
        return self.listaHorarios
    
    def setListaHorarios(self, novaLista: pd.DataFrame):
        self.listaHorarios = novaLista
    
    def eliminarColunasParaAlgoritmo(self):
        algParam = self.listaParametros

        for i in range(len(algParam)):
            if algParam.iloc[i, 0] in ['C11', 'C12', 'C13']:
                columnToDrop = int(algParam.iloc[i, 1]) - 1
                self.listaHorarios = self.listaHorarios.drop(self.listaHorarios.columns[columnToDrop], axis=1)

                for j in range(4, len(algParam)):
                    if int(algParam.iloc[j, 1]) > columnToDrop:
                        algParam.iloc[j, 1] = int(algParam.iloc[j, 1]) - 1

                algParam.iloc[i, 1] = len(algParam) - 4

        self.listaParametros = algParam

    
    def obterDados(self, c, linha):
        for _, row in self.listaParametros.iterrows():
            if row[0] == c:
                return self.listaHorarios.iloc[linha, int(row[1])-1]
            
    def getCaracteristicaPedida(self, linha):
        return self.obterDados('C10', linha)
            

    def getInscritos(self, linha):
        return self.obterDados('C05', linha)
    
    def getDataHora(self, linha):
        return [self.obterDados(char, linha) for char in ['C07', 'C08', 'C09']]

    def getPath(self):
        return self.paramPath


