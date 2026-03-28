from multiprocessing import Queue
from kernels import INCR, SUMAR, DIFUMINAR, ESCALAR
from sm import SM
from gpu_memory import GPUMemory
from time import perf_counter
import sys

if __name__ == '__main__':
    # parámetros de construcción de la GPU y puesta en marcha -----------
    cant_sms = 4
    cant_nucleos_por_sm = 5
    tam_mem_gpu = 500_000
    mem_gpu = GPUMemory(tam_mem_gpu)
    tam_mem_sm = 100

    # --- BUCLE PRINCIPAL ---
    while True:
        print("\n=======================================")
        print("    SIMULADOR GPU - MENÚ PRINCIPAL     ")
        print("=======================================")
        print("Selecciona la tarea a ejecutar:")
        print("0) Salir del programa")
        print(f"{INCR}) Incremento (INCR)")
        print(f"{SUMAR}) Suma de dos vectores (SUMAR)")
        print(f"{DIFUMINAR}) Difuminar (DIFUMINAR)")
        print(f"{ESCALAR}) Producto Escalar (ESCALAR)")
        print("=======================================")
        
        try:
            scelta = int(input("Escribe el número de la operación y pulsa Intro: "))
            
            # Condición de salida
            if scelta == 0:
                print("\nSaliendo del simulador. ¡Hasta pronto!\n")
                break
                
            mem_gpu.kernel.value = scelta
        except ValueError:
            print("\nError: debes introducir un número válido. Inténtalo de nuevo.")
            continue

        nome_tarea = ""

        if mem_gpu.kernel.value == INCR:
            nome_tarea = "INCR (Incremento +1)"
        elif mem_gpu.kernel.value == SUMAR:
            nome_tarea = "SUMAR (Suma de Vectores)"
        elif mem_gpu.kernel.value == DIFUMINAR:
            nome_tarea = "DIFUMINAR (Media de adyacentes)"
        elif mem_gpu.kernel.value == ESCALAR:
            nome_tarea = "ESCALAR (Producto Escalar)"
        else:
            print("\nOpción no válida. Inténtalo de nuevo.")
            continue

        print(f"\n---> Iniciando tarea: {nome_tarea} <---")
        
        #Creamos una nueva cola y reclutamos nuevos SMs para esta tarea específica
        q_bloques = Queue()
        sms = [SM(cant_nucleos_por_sm, mem_gpu, tam_mem_sm, q_bloques) for _ in range(cant_sms)]
        for s in sms:
            s.start()

        # ==================================================================
        # EJECUCIÓN DE LA TAREA SELECCIONADA
        # ==================================================================
        
        # tarea: incr ------------------------------------------------------
        if mem_gpu.kernel.value == INCR:

            # El ordenador dice a la GPU lo que debe ejecutar.
            mem_gpu.tam_datos.value = 500_000
            mem_gpu.dato1[:] = [1.2] * 500_000
            t1 = perf_counter()

            # La GPU divide el trabajo en bloques y los encola.
            for block_start in range(0, mem_gpu.tam_datos.value, cant_nucleos_por_sm):
                block_size = min(cant_nucleos_por_sm, mem_gpu.tam_datos.value - block_start)
                q_bloques.put((block_start, block_size))
            for _ in range(cant_sms):  
                q_bloques.put(None)

            # Espera a que todos los SMs acaben e imprime el resultado.
            for sm in sms:
                sm.join()
            t0 = perf_counter()
            
            print('incr             :', [round(x, 2) for x in mem_gpu.res[:10]])
            print('rdo esperado     : [2.2, 2.2, 2.2, ...]')
            print(f'tiempo paralelo  : {t0 - t1:.6f} s')

            # Calculo del tiempo secuencial
            t1 = perf_counter()
            [(dato + 1) for dato in mem_gpu.dato1[:]]
            t0 = perf_counter()
            print(f'tiempo secuencial: {t0 - t1:.6f} s')

        # tarea: sumar -----------------------------------------------------
        elif mem_gpu.kernel.value == SUMAR:
            # El ordenador dice a la GPU lo que debe ejecutar.
            mem_gpu.tam_datos.value = 10
            mem_gpu.dato1[:10] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
            mem_gpu.dato2[:10] = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5]

            # La GPU divide el trabajo en bloques y los encola.
            t1 = perf_counter()
            for block_start in range(0, mem_gpu.tam_datos.value, cant_nucleos_por_sm):
                block_size = min(cant_nucleos_por_sm, mem_gpu.tam_datos.value - block_start)
                q_bloques.put((block_start, block_size))
            for _ in range(cant_sms):  # un None por SM
                q_bloques.put(None)

            # Espera a que todos los SMs acaben e imprime el resultado.
            for sm in sms:
                sm.join()
            t0 = perf_counter()
            
            print('sumar            :', [round(x, 2) for x in mem_gpu.res[:10]])
            print('rdo esperado     : [1.5, 3.5, 5.5, 7.5, 9.5, 11.5, 13.5, 15.5, 17.5, 19.5]')
            print(f'tiempo paralelo  : {t0 - t1:.6f} s')

            # Calculo del tiempo secuencial
            t1 = perf_counter()
            [(dato1 + dato2) for dato1, dato2 in zip(mem_gpu.dato1[:10], mem_gpu.dato2[:10])]
            t0 = perf_counter()
            print(f'tiempo secuencial: {t0 - t1:.6f} s')

        # tarea: difuminar -----------------------------------------------------  
        elif mem_gpu.kernel.value == DIFUMINAR:
            tam_datos = 501
            mem_gpu.tam_datos.value = tam_datos

            # Rellenamos el vector con datos progresivos para que la media se note.
            # Usaremos los múltiplos de 3: [0.0, 3.0, 6.0, 9.0, 12.0, ...]
            for i in range(tam_datos):
                mem_gpu.dato1[i] = float(i * 3)
                mem_gpu.res[i] = 0.0  # Limpiamos el resultado por si acaso
                
            t1 = perf_counter()
            # La GPU divide el trabajo y lo mete en la nueva cola
            for block_start in range(0, mem_gpu.tam_datos.value, cant_nucleos_por_sm):
                block_size = min(cant_nucleos_por_sm, mem_gpu.tam_datos.value - block_start)
                q_bloques.put((block_start, block_size))

            # Señal de finalización (píldora venenosa)
            for _ in range(cant_sms):
                q_bloques.put(None)

            # Esperamos a que terminen
            for sm in sms:
                sm.join()
            t0 = perf_counter()
            
            print('Vector orig      :', list(mem_gpu.dato1[:10]))
            print('difuminar  :', [round(x, 1) for x in mem_gpu.res[:10]])
            print(f'tiempo paralelo  : {t0 - t1:.6f} s')

            # Calculo tiempo secuencial
            datos = mem_gpu.dato1[:tam_datos]
            t1 = perf_counter() 
            res_secuencial = [(datos[i-1] + datos[i] + datos[i+1]) / 3.0 for i in range(1, len(datos)-1)]
            res_secuencial.insert(0, (datos[0] + datos[0] + datos[1]) / 3.0)
            res_secuencial.append((datos[-2] + datos[-1] + datos[-1]) / 3.0)
            t0 = perf_counter()
            print(f'tiempo secuencial: {t0 - t1:.6f} s')


        # tarea: escalar -----------------------------------------------------  
        elif mem_gpu.kernel.value == ESCALAR:
            tam_datos_esc = 10
            mem_gpu.tam_datos.value = tam_datos_esc
            
            # Rellenamos los vectores: dato1 todo a 1.0 y dato2 todo a 2.0
            for i in range(tam_datos_esc):
                mem_gpu.dato1[i] = 1.0
                mem_gpu.dato2[i] = 2.0

            # IMPORTANTE: Inicializamos el acumulador (posición 0) a 0.0
            mem_gpu.res[0] = 0.0
            
            t1 = perf_counter()
            # Repartimos el trabajo
            for block_start in range(0, mem_gpu.tam_datos.value, cant_nucleos_por_sm):
                block_size = min(cant_nucleos_por_sm, mem_gpu.tam_datos.value - block_start)
                q_bloques.put((block_start, block_size))
            
            for _ in range(cant_sms):
                q_bloques.put(None)
            
            for sm in sms:
                sm.join()
            t0 = perf_counter()

            # Imprimimos el resultado (si hay 10 elementos de 1.0 * 2.0, la suma debe ser 20.0)
            print('Vector 1         :', list(mem_gpu.dato1[:tam_datos_esc]))
            print('Vector 2         :', list(mem_gpu.dato2[:tam_datos_esc]))
            print('Prod. Escalar:', mem_gpu.res[0])
            print(f'tiempo paralelo  : {t0 - t1:.6f} s')

            # calculo tiempo secuencial
            t1 = perf_counter()
            res_secuencial = sum(a * b for a, b in zip(mem_gpu.dato1[:tam_datos_esc], mem_gpu.dato2[:tam_datos_esc]))
            t0 = perf_counter()
            print(f'tiempo secuencial: {t0 - t1:.6f} s')
