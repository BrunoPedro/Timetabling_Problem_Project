import ast
import csv
import datetime
import os
import time
from horario import horario
from salas import salas
import random
import pandas as pd

class algoritmo:

    def __init__(self, horario:horario, salas:salas):
        self.horarioInicial =  horario
        self.salasAtribuir = salas
        self.listaSalasUtilizadas = []
        self.listaGeradores = pd.DataFrame()
        
    
    def iniciarNovoHorario(self):
        novoHorario = pd.DataFrame(columns=self.horarioInicial.getListaHorarios().iloc[0].index)
        novoHorario['Nome sala'] = None
        novoHorario['Capacidade Normal'] = None
        novoHorario['Características reais da sala'] = None
        return novoHorario

    def gerarHorarioNovoFifo(self):

        novoHorario = self.iniciarNovoHorario()

        for i, _ in self.horarioInicial.getListaHorarios().iterrows():
            if self.horarioInicial.getCaracteristicaPedida(i) == "Não necessita de sala":
               novoHorario = novoHorario._append(self.aulaAtribuidaSemSala(i, None), ignore_index=True)
            else:              
                novoHorario = novoHorario._append(self.fifo(i), ignore_index=True)
            print('Nº Salas Atribuidas = ',i)
        path = r'output\G23_F_Horario.csv'
        self.output(novoHorario, path)
       
    def fifo(self, linha):
        for j, sala_row in self.salasAtribuir.getListaSalas().iterrows():
            if (
                self.horarioInicial.getInscritos(linha) <= sala_row['Capacidade Normal']
                and str(self.horarioInicial.getCaracteristicaPedida(linha)) in self.salasAtribuir.getCaracteristicas(j)
            ):
                if not self.salaJaAtribuida(linha, j, None, None):
                    self.salaAtribuida(linha, j, None, None)
                    return self.aulaAtribuida(linha, j, None, None)
        for j, sala_row in self.salasAtribuir.getListaSalas().iterrows():
            if  (
                self.horarioInicial.getInscritos(linha) <= sala_row['Capacidade Normal']
                or str(self.horarioInicial.getCaracteristicaPedida(linha)) in self.salasAtribuir.getCaracteristicas(j)
            ):
                if not self.salaJaAtribuida(linha, j, None, None):
                    self.salaAtribuida(linha, j, None, None)
                    return self.aulaAtribuida(linha, j, None, None)
        return self.AtribuirRandom(linha, None)


    def gerarHorarioNovoDespLugares(self):
        
        novoHorario = self.iniciarNovoHorario()

        colunaInscritos = int(self.horarioInicial.getListaParametros().loc[self.horarioInicial.getListaParametros()[0] == "C05", 1]) - 1
        colunaInscritosNome = self.horarioInicial.getListaHorarios().columns[colunaInscritos]
        horarioOrdenado = self.horarioInicial
        newListaHorario = self.horarioInicial.getListaHorarios().sort_values(by=colunaInscritosNome, ascending=True, ignore_index=True)
        horarioOrdenado.setListaHorarios(newListaHorario)

        ListaAulasPorAtribuir = []
        counter = 0
        
        for i, _ in horarioOrdenado.getListaHorarios().iterrows():
            caracteristicaPedida = horarioOrdenado.getCaracteristicaPedida(i)
            if caracteristicaPedida == "Não necessita de sala":
                novoHorario = novoHorario._append(self.aulaAtribuidaSemSala(i, horarioOrdenado), ignore_index=True)
                counter +=1
                print('Nº Salas Atribuidas = ',counter)
            else:    
                linhaNovoHorario, atribuida = self.despLugares(i, horarioOrdenado)
                if atribuida:
                    novoHorario = novoHorario._append(linhaNovoHorario, ignore_index=True)
                    counter +=1
                    print('Nº Salas Atribuidas = ',counter)
                else:
                    ListaAulasPorAtribuir.append(linhaNovoHorario)      
        
        for i in range(len(ListaAulasPorAtribuir)):

            novoHorario = novoHorario._append(self.AtribuirRandom(ListaAulasPorAtribuir[i], horarioOrdenado), ignore_index=True)
            counter +=1
            print('Nº Salas Atribuidas = ',counter)

        path = r'output\G23_DL_Horario.csv'
        return self.output(novoHorario, path)
    
    def despLugares(self, linha, horarioOrdenado: horario):

        salasOrdenadas = self.salasAtribuir
        newListaSalas = self.salasAtribuir.getListaSalas().sort_values(by='Capacidade Normal', ascending=True, ignore_index=True)
        salasOrdenadas.setListaSalas(newListaSalas)

        incritos = horarioOrdenado.getInscritos(linha)

        for j, _ in salasOrdenadas.getListaSalas().iterrows():
            lotacao = salasOrdenadas.getLotacao(j)
            if incritos <= lotacao:
                if not self.salaJaAtribuida(linha, j, horarioOrdenado, salasOrdenadas):
                    self.salaAtribuida(linha, j, horarioOrdenado, salasOrdenadas)
                    return self.aulaAtribuida(linha, j, horarioOrdenado, salasOrdenadas), True
        return linha, False


    def gerarHorarioNovoDespCaract(self):
        
        novoHorario = self.iniciarNovoHorario()

        ListaAulasPorAtribuir = []
        counter = 0

        for i, _ in self.horarioInicial.getListaHorarios().iterrows():
            if self.horarioInicial.getCaracteristicaPedida(i) == "Não necessita de sala":
               novoHorario = novoHorario._append(self.aulaAtribuidaSemSala(i, None), ignore_index=True)
            else:    
                linhaNovoHorario, atribuida = self.despCaract(i)
                if atribuida:
                    novoHorario = novoHorario._append(linhaNovoHorario, ignore_index=True)
                    counter +=1
                    print('Nº Salas Atribuidas = ',counter)
                else:
                    ListaAulasPorAtribuir.append(linhaNovoHorario)      
    
        for i in range(len(ListaAulasPorAtribuir)):

            novoHorario = novoHorario._append(self.AtribuirRandom(ListaAulasPorAtribuir[i], self.horarioInicial), ignore_index=True)
            counter +=1
            print('Nº Salas Atribuidas = ',counter)

        path = r'output\G23_DC_Horario.csv'
        return self.output(novoHorario, path)

    def despCaract(self, linha):

        salasOrdenadas = self.salasAtribuir
        newListaSalas = self.salasAtribuir.getListaSalas().sort_values(by='Nº características', ascending=True, ignore_index=True)
        salasOrdenadas.setListaSalas(newListaSalas)

        for j, _ in salasOrdenadas.getListaSalas().iterrows():
            if str(self.horarioInicial.getCaracteristicaPedida(linha)) in salasOrdenadas.getCaracteristicas(j):
                if not self.salaJaAtribuida(linha, j, None, salasOrdenadas):
                    self.salaAtribuida(linha, j, None, salasOrdenadas)
                    return self.aulaAtribuida(linha, j, None, salasOrdenadas), True
        
        return linha, False
    

    def gerarHorarioNovoDespValor(self):
        
        novoHorario = self.iniciarNovoHorario()

        ListaAulasPorAtribuir = []
        counter = 0

        for i, _ in self.horarioInicial.getListaHorarios().iterrows():
            if self.horarioInicial.getCaracteristicaPedida(i) == "Não necessita de sala":
               novoHorario = novoHorario._append(self.aulaAtribuidaSemSala(i, None), ignore_index=True)
            else:    
                linhaNovoHorario, atribuida = self.despValor(i)
                if atribuida:
                    novoHorario = novoHorario._append(linhaNovoHorario, ignore_index=True)
                    counter +=1
                    print('Nº Salas Atribuidas = ',counter)
                else:
                    ListaAulasPorAtribuir.append(linhaNovoHorario)      
    
        for i in range(len(ListaAulasPorAtribuir)):

            novoHorario = novoHorario._append(self.AtribuirRandom(ListaAulasPorAtribuir[i], self.horarioInicial), ignore_index=True)
            counter +=1
            print('Nº Salas Atribuidas = ',counter)

        path = r'output\G23_DV_Horario.csv'
        return self.output(novoHorario, path)

    def despValor(self, linha):
        
        salasOrdenadas = self.salasAtribuir
        newListaSalas = self.salasAtribuir.getListaSalas().sort_values(by='Nº características', ascending=True, ignore_index=True)
        salasOrdenadas.setListaSalas(newListaSalas)
        listaSalasPossiveis = []
        salaPossivel= None
        caracteristicaPedida = self.horarioInicial.getCaracteristicaPedida(linha)

        for j, _ in salasOrdenadas.getListaSalas().iterrows():
            if str(caracteristicaPedida) in salasOrdenadas.getCaracteristicas(j):
                if not self.salaJaAtribuida(linha, j, None, salasOrdenadas):
                    listaSalasPossiveis.append(j)
                    if len(listaSalasPossiveis)==5:
                        break
        
        for linhaDaSala in listaSalasPossiveis:
            raridadesDaSala = salasOrdenadas.getRaridadeCaracteristicas(linhaDaSala, caracteristicaPedida)
            if len(raridadesDaSala) <= 1:
                self.salaAtribuida(linha, linhaDaSala, None, salasOrdenadas)
                return self.aulaAtribuida(linha, linhaDaSala, None, salasOrdenadas), True
            else:
                if salaPossivel is None:
                    salaPossivel = linhaDaSala
                elif min(raridadesDaSala) > min(salasOrdenadas.getRaridadeCaracteristicas(salaPossivel, caracteristicaPedida)):
                    salaPossivel = linhaDaSala   
        if salaPossivel is None:
            return linha, False
        else:
            self.salaAtribuida(linha, salaPossivel, None, salasOrdenadas)
            return self.aulaAtribuida(linha, salaPossivel, None, salasOrdenadas), True

    def gerarHorarioNovoRandom(self):
        
        novoHorario = self.iniciarNovoHorario()

        for i, _ in self.horarioInicial.getListaHorarios().iterrows():
            novoHorario = novoHorario._append(self.AtribuirRandom(i, None), ignore_index=True)
            print('Nº Salas Atribuidas = ',i)
        path = r'output\G23_R_Horario.csv'
        return self.output(novoHorario, path)
    
    def AtribuirRandom(self, linha, horarioIn: horario):
        horarioIn = horarioIn or self.horarioInicial
        salaRandom = random.choice(range(len(self.salasAtribuir.getListaSalas())))
        self.salaAtribuida(linha, salaRandom, horarioIn, None)
        return self.aulaAtribuida(linha, salaRandom, horarioIn, None)



    def salaJaAtribuida(self, linha, sala, horarioIn: horario, salaIn:salas):
        horarioIn = horarioIn or self.horarioInicial
        salaIn = salaIn or self.salasAtribuir
        novaAula = horarioIn.getDataHora(linha)
        novaAula.append(salaIn.getNome(sala))
        return novaAula in self.listaSalasUtilizadas

    def salaAtribuida(self, linha, sala, horarioIn: horario, salaIn:salas):
        horarioIn = horarioIn or self.horarioInicial
        salaIn = salaIn or self.salasAtribuir
        novaAula = horarioIn.getDataHora(linha)
        novaAula.append(salaIn.getNome(sala))
        self.listaSalasUtilizadas.append(novaAula) 
    
    def aulaAtribuida(self, linha, sala, horarioIn: horario, salaIn:salas):
        horarioIn = horarioIn or self.horarioInicial
        salaIn = salaIn or self.salasAtribuir
        horarioLine = horarioIn.getListaHorarios().iloc[linha]
        salaLine = salaIn.getListaSalas().iloc[sala]
        result  = pd.concat([horarioLine, salaLine[['Nome sala', 'Capacidade Normal']]])
        result['Características reais da sala'] = salaIn.getCaracteristicas(sala)
        return result
    
    def aulaAtribuidaSemSala(self, linha, horarioIn):
        horarioIn = horarioIn or self.horarioInicial
        result = horarioIn.getListaHorarios().iloc[linha].copy()
        result['Nome sala'] = None
        result['Capacidade Normal'] = None
        result['Características reais da sala'] = None
        return result

    def output(self, novoHorario, path):
        originalHorario = horario(self.horarioInicial.getPath())
        originalOrder = originalHorario.getListaHorarios().columns

        novoHorario = novoHorario[originalOrder]
        
        while True:
            try:
                novoHorario.to_csv(path, sep=";", encoding="utf-8-sig", index=False)
                print(f'Schedule has been written to {path}')
                break
            except PermissionError:
                print("Error: File is open. Retrying in 5 seconds...")
                time.sleep(5)

        return path

