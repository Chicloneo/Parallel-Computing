#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 12:13:42 2026

@author: salillo
"""

"""
PRPA
Santiago Lillo Macías
Ejercicio 1
"""

"""
from time import perf_counter
to = perf_counter()
... código ...
t1 = perf_counter()

perf counter cuenta el tiempo que tarda el código en ejecutarse

pool = Pool() divide los procesos (Python por defecto lo hace a su manera)
pool = Pool(3) fivide en 3 procesos
"""

from itertools import starmap
from multiprocessing import Pool
from time import perf_counter
from typing import Callable
import math

def sucesor(x:int) -> int:
    return x+1

def suma(x:int, y:int) -> int:
    return x+y

def area_rect(una_funcion: Callable[[float], float],inf: float, sup: float) -> float:
    return (sup - inf) * una_funcion((inf + sup) / 2)

#En las prácticas de PRPA es obligatorio indicar los tipos (inf:float)
#Importante poner comentarios
def integral_sec(la_funcion: Callable[[float], float], inf: float, sup: float, cant_interv: int) -> float:
    tareas = [(la_funcion, inf + i * (sup - inf) / cant_interv, inf + (i + 1) * (sup - inf) / cant_interv) for i in range(cant_interv)]
    resultados = starmap(area_rect, tareas)
    return sum(resultados)



if __name__ == '__main__': #para que el Pool no haga cosas raras

    pool = Pool() #Le estoy diciendo al ordenador: "Vamos a crear X procesos" #no tengo claro esto

    to = perf_counter()
    map(sucesor, [2,5,9]) #no hace "nada"
    print('suma map = ', list(map(sucesor, [2,5,9])))
    starmap(suma,[(1,1),(3,5),(9,3)]) #no hace "nada"
    print('suma starmap = ', list(starmap(suma,[(1,1),(3,5),(9,3)])))
    #starmap hace que suma((x,y)) -> suma(x,y)
    t1 = perf_counter()
    print('Tiempo sumas sin pool = ', t1-to)
    
    to = perf_counter()
    resultados1 = pool.map(sucesor, [2,5,9])
    print('suma pool map = ', resultados1)
    resultados2 = pool.starmap(suma,[(1,1),(3,5),(9,3)])
    print('suma pool starmap = ',resultados2)
    t1 = perf_counter()
    print('Tiempo sumas con pool = ', t1-to)
    #Para intervalos pocos o pocas tareas, tarda más el pool
    
    print(' ')
    
    def integral_paral_0(una_funcion: Callable[[float], float], inf: float, sup: float, cant_interv: int, cant_proc = None) -> float:
        pool = Pool(cant_proc) #Por defecto es None (los disponibles que haya) pero le podemos especificar cuántos procesos queremos, en la medida de lo posible.
        tareas = [(una_funcion, inf + i * (sup - inf) / cant_interv, inf + (i + 1) * (sup - inf) / cant_interv) for i in range(cant_interv)]
        resultados = pool.starmap(area_rect, tareas)
        return sum(resultados)
    
    to = perf_counter()
    res_integral_sec = integral_sec(math.sin, 0, math.pi, 10**6)
    t1 = perf_counter()
    print('Resultado de integral secuencial: ', res_integral_sec)
    print('Tiempo integral secuencial sin pool = ', t1-to)

    print(' ')
    to = perf_counter()
    res_integral_paralela = integral_paral_0(math.sin, 0, math.pi, 10**6)
    t1 = perf_counter()
    print('Resutado integral paralela = ', res_integral_paralela)
    print('Tiempo integral con pool = ', t1-to)
    
    """
    assert condición, "Mensaje de error si la condición no se cumple"
    Es útil para depurar errores.
    Es como un if pero más eficiente (creo).
    """
    
    print(' ')
    def integral_paral(una_funcion: Callable[[float], float], inf: float, sup: float, cant_interv: int, cant_tareas: int, cant_proc: int= None) -> float:
        tareas_subintervalos = [(una_funcion, inf + i * (sup - inf) / cant_tareas, inf + (i + 1) * (sup - inf) / cant_tareas, cant_interv//cant_tareas) for i in range(cant_tareas)]
        pool = Pool(cant_proc)
        resultados = pool.starmap(integral_sec, tareas_subintervalos)
        #print(resultados)
        return sum(resultados)
    
    to = perf_counter()
    res_integral_paralela_nueva = integral_paral(math.sin, 0, math.pi, 10**6, 50, 20)
    t1 = perf_counter()
    print('Resutado integral paralela nueva= ', res_integral_paralela_nueva)
    print('Tiempo integral nueva con pool = ', t1-to)
    #el resultado debe aproximarse lo máximo a 2














