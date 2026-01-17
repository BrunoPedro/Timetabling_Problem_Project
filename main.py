import re
from horario import horario
from salas import salas
from score import score
from algoritmo import algoritmo
import pandas as pd
import warnings

if __name__ == '__main__':

    warnings.filterwarnings("ignore")
    
    novaSala = salas(r'input\ISCTE_parametrização salas.csv')

    horarioISCTE = horario(r'input\ISCTE_parametrização horarios.csv', None)
    scoreISCTE = score(horarioISCTE, novaSala, r'input\criteriosqualidade.csv')
    scoreISCTE.gerarScores('ISCTE_Horario_score')

    horarioG23 = horario(r'input\G23_parametrização horarios.csv')
    horarioG23.eliminarColunasParaAlgoritmo()
    algo_instance = algoritmo(horarioG23, novaSala)

    novosHorariosOuputs = []
        
    novosHorariosOuputs.append(algo_instance.gerarHorarioNovoFifo())

    novosHorariosOuputs.append(algo_instance.gerarHorarioNovoDespLugares())

    novosHorariosOuputs.append(algo_instance.gerarHorarioNovoDespCaract())

    novosHorariosOuputs.append(algo_instance.gerarHorarioNovoDespValor())

    novosHorariosOuputs.append(algo_instance.gerarHorarioNovoRandom())

    novosHorariosOuputs = [r'output\G23_F_Horario.csv', r'output\G23_DL_Horario.csv', r'output\G23_DC_Horario.csv', r'output\G23_DV_Horario.csv', r'output\G23_R_Horario.csv']

    for lines in novosHorariosOuputs:
        match = re.search(r'\\(.*?)\.', lines)
        result = match.group(1)
        horarioGerado = horario(r'input\G23_parametrização horarios.csv', rf'output\{result}.csv')
        scoreHorarioGerado = score(horarioGerado, novaSala, r'input\criteriosqualidade.csv')
        scoreHorarioGerado.gerarScores(f'{result}_score')

   
    listaGeradoresPath = r'input\G23_metodopercent.csv'
    listaGeradores = pd.DataFrame()

    try:
        listaGeradores = pd.read_csv(listaGeradoresPath, sep=";", encoding="utf-8-sig", header=None)
    except FileNotFoundError:
        print(f"File '{listaGeradoresPath}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    def gerarParteDoHorario(parteDoHorario, j, novosHorariosOuputsElement, percentagem, last_row_index):
        
        if j < 1:
            return geradorNovo(novosHorariosOuputs[novosHorariosOuputsElement], percentagem, 0)
        else:
            horario_part = geradorNovo(novosHorariosOuputs[novosHorariosOuputsElement], percentagem, last_row_index)
            return pd.concat([parteDoHorario, horario_part], ignore_index=True)
        


    def geradorNovo(path, percentagem, last_row_index):
        try:
            horarioGerado = pd.read_csv(path, sep=";", encoding="utf-8-sig", header=0)
            
        except FileNotFoundError:
            print(f"File '{listaGeradoresPath}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        horarioGerado = horarioGerado.sort_values(by=['Início', 'Fim', 'Dia'], ascending=[True, True, True])
        if 0 <= percentagem <= 100:
        
            num_rows_to_select = int(round(len(horarioGerado) * (percentagem / 100.0), 0))

        
            selected_rows = horarioGerado.iloc[last_row_index:num_rows_to_select+last_row_index, :13]
        
        return selected_rows


    for i, _ in listaGeradores.iterrows():

        last_row_index = 0
        geradores = listaGeradores.iloc[i, 0].split("+")
        percentagens = listaGeradores.iloc[i, 1].split("+")
        parteDoHorario = pd.DataFrame()
        
        for j in range(len(geradores)):
            gerador = geradores[j]
            if gerador == 'F':
                parteDoHorario = gerarParteDoHorario(parteDoHorario, j, 0, int(percentagens[j]), last_row_index)
                last_row_index = len(parteDoHorario)
            
            elif gerador == 'DL':
                parteDoHorario = gerarParteDoHorario(parteDoHorario, j, 1, int(percentagens[j]), last_row_index)
                last_row_index = len(parteDoHorario)
                
            elif gerador == 'DC':
                parteDoHorario = gerarParteDoHorario(parteDoHorario, j, 2, int(percentagens[j]), last_row_index)
                last_row_index = len(parteDoHorario)
                
            elif gerador == 'DV':
                parteDoHorario = gerarParteDoHorario(parteDoHorario, j, 3, int(percentagens[j]), last_row_index)
                last_row_index = len(parteDoHorario)
                
            else:
                parteDoHorario = gerarParteDoHorario(parteDoHorario, j, 4, int(percentagens[j]), last_row_index)
                last_row_index = len(parteDoHorario)
                

        parteDoHorario['Capacidade Normal'] = parteDoHorario['Capacidade Normal'].fillna(0).astype(int)
        parteDoHorario['Capacidade Normal'] = parteDoHorario['Capacidade Normal'].replace(0, pd.NA)

        outputPath = rf'output\G23_{"".join(geradores)}_Horario.csv'
        parteDoHorario.to_csv(outputPath, sep=";", encoding="utf-8-sig", index=False)
        print(f'File "{outputPath}" created successfully.')

        horarioCruzado = horario(r'input\G23_parametrização horarios.csv', outputPath)
        scoreHorarioCruzado= score(horarioCruzado, novaSala, r'input\criteriosqualidade.csv')
        scoreHorarioCruzado.gerarScores(f'G23_{"".join(geradores)}_Horario_score')
                               

            
            
    
    


    

    


