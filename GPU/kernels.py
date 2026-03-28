from threading import Barrier
from gpu_memory import GPUMemory
from sm_memory import SMMemory


def incr(core_id: int, gpu_mem: GPUMemory, sm_mem: SMMemory, _: Barrier) -> None:
    if core_id < sm_mem.tam_bloque:
        idx = sm_mem.ini_bloque + core_id
        #Acceso directo a la memoria global.
        gpu_mem.res[idx] = gpu_mem.dato1[idx] + 1

def sumar(core_id: int, gpu_mem: GPUMemory, sm_mem: SMMemory, _: Barrier) -> None:
    if core_id < sm_mem.tam_bloque:
        # Calculamos el índice global
        idx_global = sm_mem.ini_bloque + core_id
        
        #Copia a memoria local
        sm_mem.datos[core_id] = gpu_mem.dato1[idx_global]
        sm_mem.datos[core_id + sm_mem.tam_bloque] = gpu_mem.dato2[idx_global]
        
        #Suma y copia a la memoria global
        resultado_local = sm_mem.datos[core_id] + sm_mem.datos[core_id + sm_mem.tam_bloque]
        gpu_mem.res[idx_global] = resultado_local


def difuminar(core_id: int, gpu_mem: GPUMemory, sm_mem: SMMemory, barrera: Barrier) -> None:
    if core_id < sm_mem.tam_bloque:
        # Calculamos el índice global
        idx = sm_mem.ini_bloque + core_id
        sm_mem.datos[core_id] = gpu_mem.dato1[idx]
    
    # Nadie avanza hasta que todos han copiado sus datos
    barrera.wait()
    
    #Cálculo de la media
    if core_id < sm_mem.tam_bloque:
        idx = sm_mem.ini_bloque + core_id
        
        # Valor central (siempre en memoria local)
        centro = sm_mem.datos[core_id]
        
        # Vecino Izquierdo
        if core_id > 0:
            izq = sm_mem.datos[core_id - 1] # Está en mi bloque (local)
        elif idx > 0:
            izq = gpu_mem.dato1[idx - 1]    # Está fuera de mi bloque (global)
        else:
            izq = centro                   #Caso de los extremos
            
        # Vecino Derecho
        if core_id < sm_mem.tam_bloque - 1:
            der = sm_mem.datos[core_id + 1] # Está en mi bloque (local)
        elif idx < gpu_mem.tam_datos.value - 1:
            der = gpu_mem.dato1[idx + 1]    # Está fuera de mi bloque (global)
        else:
            der = centro                   #Caso de los extremos
            
        #Guardamos el resultado
        gpu_mem.res[idx] = (izq + centro + der) / 3.0



def escalar(core_id: int, gpu_mem: GPUMemory, sm_mem: SMMemory, barrera: Barrier) -> None:
    if core_id < sm_mem.tam_bloque:
        idx = sm_mem.ini_bloque + core_id

        producto_local = gpu_mem.dato1[idx] * gpu_mem.dato2[idx]

        with gpu_mem.res.get_lock():
            gpu_mem.res[0] += producto_local

            


INCR = 1
SUMAR = 2
DIFUMINAR = 3
ESCALAR = 4

KERNELS = {
    INCR: incr,
    SUMAR: sumar,
    DIFUMINAR: difuminar,
    ESCALAR: escalar,
}
