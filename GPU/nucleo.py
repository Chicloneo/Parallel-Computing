from threading import Thread
from gpu_memory import GPUMemory
from sm_memory import SMMemory
from threading import Barrier
from multiprocessing import Queue
from kernels import KERNELS

class Nucleo(Thread):
    def __init__(self, core_id: int, gpu_mem: GPUMemory, sm_mem: SMMemory, barrera: Barrier) -> None:
        super().__init__()
        self.core_id = core_id
        self.gpu_mem = gpu_mem
        self.sm_mem = sm_mem
        self.barrera = barrera

    def run(self) -> None:
        while True:
            #Esperamos a que el SM asigne el bloque y dé el pistoletazo de salida
            self.barrera.wait()
            
            # Condición de parada: definimos una convención. 
            # Por ejemplo, si el SM pone el tamaño del bloque a -1, significa "fin del trabajo".
            if self.sm_mem.tam_bloque == -1:
                break
                
            # Sabemos qué operación toca hacer leyendo la memoria global de la GPU (sumar, difuminar, etc.)
            tipo_kernel = self.gpu_mem.kernel.value
            
            #Ejecutamos el kernel correspondiente
            KERNELS[tipo_kernel](self.core_id, self.gpu_mem, self.sm_mem, self.barrera)
            
            #Esperamos a que todos los núcleos terminen para no pisarnos en la siguiente vuelta
            self.barrera.wait()
