from multiprocessing import Process
from nucleo import Nucleo
from gpu_memory import GPUMemory
from sm_memory import SMMemory
from threading import Barrier
from multiprocessing import Queue
from kernels import DIFUMINAR


class SM(Process):
    def __init__(self, cant_nucleos: int, gpu_mem: GPUMemory, tam_mem_sm: int, q_bloques: Queue) -> None:
        super().__init__()
        self.cant_nucleos = cant_nucleos
        self.gpu_mem = gpu_mem
        self.q_bloques = q_bloques
        self.tam_mem_sm = tam_mem_sm 

    def run(self) -> None:
        # Aquí es donde el proceso hijo empieza a vivir. 
        # Todo lo que creamos aquí es local y privado de este SM.
        
        #Creamos la memoria local del SM
        self.sm_mem = SMMemory(self.tam_mem_sm)
        
        #Creamos la barrera
        self.barrera = Barrier(self.cant_nucleos + 1)
        
        #Creamos los núcleos (hebras)
        nucleos = [Nucleo(i, self.gpu_mem, self.sm_mem, self.barrera) 
                   for i in range(self.cant_nucleos)]
        
        for n in nucleos:
            n.start()

        while True:
            # Sacamos un bloque de trabajo de la cola
            tarea = self.q_bloques.get()
            
            if tarea is None:
                self.sm_mem.tam_bloque = -1
                self.barrera.wait() #Todos esperan aquí
                for n in nucleos:
                    n.join()
                break
            
            ini, tam = tarea
            self.sm_mem.ini_bloque = ini
            self.sm_mem.tam_bloque = tam

            self.barrera.wait() # Todos a trabajar a la vez

            # Si el kernel es DIFUMINAR, el SM debe "ayudar" a desbloquear la barrera 
            # interna que los núcleos tienen en mitad de su función matemática.
            if self.gpu_mem.kernel.value == DIFUMINAR:
                self.barrera.wait()
            
            self.barrera.wait() # Esperamos: "Avisadme cuando todos terminéis"
