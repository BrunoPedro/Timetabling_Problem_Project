import csv
import os
import pandas as pd
from horario import horario
from salas import salas


class score:

    def __init__(self, horario: horario, salas: salas, criteriosPath):
        self.horarioEx = horario
        
        colunaLotacao = self.horarioEx.getListaParametros().loc[self.horarioEx.getListaParametros()[0] == "C12", 1]
        colunaLotacao = int(colunaLotacao.iloc[0]) - 1
        self.horarioEx.getListaHorarios().iloc[:, colunaLotacao].fillna(0, inplace=True)

        self.listaSalas = salas.getListaSalas()
        self.listaCriterios = []

        try:
            self.listaCriterios = pd.read_csv(criteriosPath, sep=';', header=None, encoding='utf-8-sig')
        except FileNotFoundError:
            print(f"File '{criteriosPath}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def gerarScores(self, nomeOutput):
        avaliacao = []

        for i in range(len(self.listaCriterios)):
            scoresLine = (str(self.listaCriterios.iloc[i, 1])).split(" ")
            
            avaliacaoLine = []

            for j in range(len(scoresLine)):
                if scoresLine[j] and scoresLine[j][0] == 'C':  
                    coluna = int(self.horarioEx.getListaParametros().loc[self.horarioEx.getListaParametros()[0] == scoresLine[j], 1])-1
                    avaliacaoLine.append(f'coluna_{coluna}')
                elif scoresLine[j] and scoresLine[j] in ['+', '-', '*', '/', '<', '>', '<=', '>=', 'in', 'and', 'or', 'vazio']:
                    avaliacaoLine.append(scoresLine[j])
                elif scoresLine[j] and scoresLine[j] == 'notin':
                    avaliacaoLine.append('not in')
                elif scoresLine[j] and scoresLine[j] == 'equal':
                    avaliacaoLine.append('==')
                elif scoresLine[j] and scoresLine[j] == 'notequal':
                    avaliacaoLine.append('!=')
                elif scoresLine[j] and str(scoresLine[j]).isdigit():
                    avaliacaoLine.append(scoresLine[j])
                elif scoresLine[j] and scoresLine[j][0] == '#':
                    avaliacaoLine.append(str(scoresLine[j]).replace('_', ' '))

            avaliacao.append([self.listaCriterios.iloc[i, 0], self.avaliacaoScore(avaliacaoLine)])

        csv_file_path = os.path.join('output', f'{nomeOutput}.csv')

        
        with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as fileObject:
            csv_writer = csv.writer(fileObject, delimiter=';')

            header = ['Critério', 'Avaliação']
            csv_writer.writerow(header)

            for row in avaliacao:
                csv_writer.writerow(row)

        print(f'The scores have been written to {csv_file_path}')

    def avaliacaoScore(self, avaliacaoLine):
        avaliacao = 0
        

        for i in range(1, len(self.horarioEx.getListaHorarios())):
            scoreLine = ''

            for j in range(len(avaliacaoLine)):
                if 'coluna_' in avaliacaoLine[j]:
                    coluna = str(avaliacaoLine[j]).split('_')[1]
                    value = self.horarioEx.getListaHorarios().iloc[i, int(coluna)]
                    value = value if pd.notna(value) else ""
                    result = int(value) if isinstance(value, float) else value
                    result = str(result)
                    if result != "" and result[-1] == "]":
                        result = result[:len(result) - 2]
                    if isinstance(result, str) and result.isdigit():
                        result = int(result)
                        scoreLine = ' '.join([scoreLine, str(result)])
                    else:
                        scoreLine = ' '.join([scoreLine, f'"{result}"'])
                elif '#' in avaliacaoLine[j]:
                    scoreLine = ' '.join([scoreLine, f'"{avaliacaoLine[j][1:]}"'])
                elif avaliacaoLine[j] == 'vazio':
                    scoreLine = ' '.join([scoreLine, '""'])
                else:
                    scoreLine = ' '.join([scoreLine, avaliacaoLine[j]])

            if eval(scoreLine):
                avaliacao += 1

        return avaliacao
