import time
from math import sqrt #así no importa toda la librería
from itertools import starmap
from multiprocessing import Pool
import pathlib
import os


nombre_de_archivo = 'datos'

t0 = time.perf_counter()

with open(nombre_de_archivo, 'r') as archivo:
    texto = archivo.read()  # por ejemplo: texto = '1.0 2.0 3.0 4.0 5.0'
datos_str = texto.split()  # datos_str = ['1.0', '2.0', '3.0', '4.0', '5.0']
datos = list(map(float, datos_str))  # datos = [1.0, 2.0, 3.0, 4.0, 5.0]
cant_datos = len(datos)  # cant_datos = 5
suma = sum(datos)  # suma = 15.0
suma_cuadrados = sum([dato ** 2 for dato in datos])  # suma_cuadrados = 55.0

media = suma / cant_datos
varianza = (suma_cuadrados / cant_datos) - (media ** 2)
desviacion_tipica = sqrt(varianza)
# aunque, en general, no sabemos si la distribución es normal

t1 = time.perf_counter()

print(f'media: {media:.4f}')
print(f'desviación típica: {desviacion_tipica:.4f}')
print(f'tiempo: {t1 - t0:.4f} segundos')

"""
def suma_sumacuadr_cant(nombre_de_archivo: str) -> tuple[int, int, int]: 

    #Lee un archivo y devuelve su media, varianza y desviación típica (en ese orden).

    with open(nombre_de_archivo, 'r') as archivo:
        texto = archivo.read()  # por ejemplo: texto = '1.0 2.0 3.0 4.0 5.0'

    datos_str = texto.split()  # datos_str = ['1.0', '2.0', '3.0', '4.0', '5.0']
    datos = list(map(float, datos_str))  # datos = [1.0, 2.0, 3.0, 4.0, 5.0]
    cant_datos = len(datos)  # cant_datos = 5
    suma = sum(datos)  # suma = 15.0
    suma_cuadrados = sum([dato ** 2 for dato in datos])  # suma_cuadrados = 55.0

    media = suma / cant_datos
    varianza = (suma_cuadrados / cant_datos) - (media ** 2)
    desviacion_tipica = sqrt(varianza)

    return [media, varianza, desviacion_tipica]
"""

def aux_media(nombre_de_archivo:str) -> list[float,int, float]:
    """
    Lee un archivo y devuelve su suma parcial, número de elementos, y suma de cuadrados
    """
    with open(nombre_de_archivo, 'r') as archivo:
        texto = archivo.read()  # por ejemplo: texto = '1.0 2.0 3.0 4.0 5.0'

    datos_str = texto.split()  # datos_str = ['1.0', '2.0', '3.0', '4.0', '5.0']
    datos = list(map(float, datos_str))  # datos = [1.0, 2.0, 3.0, 4.0, 5.0]
    conteo = len(datos)  # cant_datos = 5
    suma_parcial = sum(datos)  # suma = 15.0
    suma_cuadrados = sum([dato ** 2 for dato in datos])
    return [suma_parcial, conteo, suma_cuadrados]


if __name__ == '__main__':

    pool = Pool()
    print('-------------')
                                                
    ruta_carpeta = "datos_analizar"
    archivos = [os.path.join(ruta_carpeta, f) for f in os.listdir(ruta_carpeta)]

    print('---------------------------------------------------------')

    sumas_y_conteos = pool.map(aux_media,[archivo for archivo in archivos])
    sumas_parciales = [suma_parcial[0] for suma_parcial in sumas_y_conteos]
    conteos = [conteo[1] for conteo in sumas_y_conteos] #conteo es la cantidad de números que hay en cada archivo
    media_total = sum(sumas_parciales)/sum(conteos)
    sumas_cuadrados_parciales = [suma_cuadrados_parcial[2] for suma_cuadrados_parcial in sumas_y_conteos]
    varianza_total = (sum(sumas_cuadrados_parciales)/sum(conteos)) - media_total**2
    desviacion_tipica_total = sqrt(varianza_total)

    """
    No se puede hacer la media de las medias (5+4+0), ni la media de las varianzas ...
    Usámos la fórmula media total = (suma_del_archivo_1 + ... suma_del_archivo_n) / (conteo_1 + ... conteo_n)
    Análogo (con su correspondiente fórmula) para la varianza
    Para la desviación típica total basta con calcular la raíz cuadrada de la varianza total
    """

    print("Media total: ", media_total)
    print("Varianza total: ", varianza_total)
    print("Desviación típica total: ", desviacion_tipica_total)