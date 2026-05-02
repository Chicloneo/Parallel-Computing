import time
from random import randint, gauss
from itertools import starmap
from multiprocessing import Pool


def zeta(s: float, cant_terms: int) -> float:
    # La serie solo converge y su valor es real para s>1 real, pero nos
    # da igual, porque nosotros solo usamos una cantidad finita de términos.
    return sum([1 / (n ** s) for n in range(1, cant_terms + 1)])


def azar_costoso(coste: int) -> float:
    return zeta(gauss(0, 1), coste)

def crear_archivo(numero_de_datos: int, numero: str):
        nombre_archivo = f'/Users/salillo/Desktop/Universidad/Universidad 4º/Segundo Cuatrimestre/PRPA/ej2_código_del_enunciado/Datos_{numero}'

        cant_datos_azar = randint(numero_de_datos // 2, 2 * numero_de_datos) 
        coste = 1_000
        coste_azar = randint(coste // 2, 2 * coste)

        #Aquí generamos los números. No podemos quitarlo
        numeros = [azar_costoso(coste_azar) for _ in range(cant_datos_azar)] #lista de longitud 5_000--20_000 (si quisiera 10_000) de números generados por la función zeta

        num_strings = [f'{num}' for num in numeros]  # Convierte los números a strings.
        str_total = ' '.join(num_strings)  # Une los strings separados por blancos.
        with open(nombre_archivo, 'w') as archivo:
            archivo.write(str_total)
    

#coste es la cantidad de términos que sumamos
#es más costoso porque añadimos la función gauss (no estoy seguro)

if __name__ == '__main__':
    cant_datos = 10_000
    cant_datos_azar = randint(cant_datos // 2, 2 * cant_datos) #entre 5_000 y 20_000
    # Cada ejecución produce distinta cantidad de datos.
    coste = 1_000
    coste_azar = randint(coste // 2, 2 * coste) #entre 500 y 2_000
    # En cada ejecución el coste es distinto.
    nombre_archivo = '/Users/salillo/Desktop/Universidad/Universidad 4º/Segundo Cuatrimestre/PRPA/Ejercicio 2/datos'

    t0 = time.perf_counter()

    numeros = [azar_costoso(coste_azar) for _ in range(cant_datos_azar)] #lista de longitud 5_000--20_000 de números generados por la función zeta
    num_strings = [f'{num}' for num in numeros]  # Convierte los números a strings.
    str_total = ' '.join(num_strings)  # Une los strings separados por blancos.
    with open(nombre_archivo, 'w') as archivo:
        archivo.write(str_total)

    t1 = time.perf_counter()
    print(f'tiempo: {t1 - t0:.4f} segundos')

    num_procesos = 10
    pool = Pool(num_procesos)
    pool.starmap(crear_archivo,[(200_000//num_procesos,i,num_procesos) for i in range(num_procesos)])