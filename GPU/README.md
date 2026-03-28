# GPU simulation
Santiago Lillo Macías
2026-03-28

- [1. Introducción](#1-introducción)
- [2. Arquitectura de la GPU](#2-arquitectura-de-la-gpu)
- [3. Implementación del Paralelismo](#3-implementación-del-paralelismo)
  - [3.1. Memoria Global vs Memoria
    Local](#31-memoria-global-vs-memoria-local)
  - [3.2. ¿Qué hace cada kernel?](#32-qué-hace-cada-kernel)
- [4. Análisis de Flujo de Datos](#4-análisis-de-flujo-de-datos)
- [5. Tiempo de ejecución](#5-tiempo-de-ejecución)
- [6. Interacción con el usuario](#6-interacción-con-el-usuario)

## 1. Introducción

Este documento analiza el diseño y funcionamiento de un simulador de GPU
desarrollado en Python, cuyo objetivo es materializar los conceptos
teóricos de la arquitectura de computadores y la programación paralela.

El objetivo de esta práctica es realizar una simulación de una GPU.
Puesto que es, en efecto, una simulación, nos acercaremos lo máximo
posible a esta. Sin embargo, por el propio hardware, hay limitaciones
que nos impiden acercarnos fielmente a una GPU; por ejemplo, en el
tiempo de ejecución.

Para simular nuestra GPU, en pos de una mayor claridad, nos hemos basado
en dos conceptos:

1.- Separar el código en seis archivos `.py` (proporcionado por el
profesor).

2.- Programación Orientada a Objetos (POO)

De esta manera, hacemos el símil del hardware. Cada `.py`se refiere a un
componente físico distinto: memoria global, memoria local, streaming
multiprocessor, … También nos permite aislar mejor los errores. Por
supuesto, usamos POO ya que heredamos clases como `Process` o `Thread`,
y nos permite mantener la jerarquía existente; cada GPU tiene varios
SMs, cada SM tiene varios núcleos, etc.

------------------------------------------------------------------------

## 2. Arquitectura de la GPU

Vamos a explicar qué hace cada `.py`.

- **`GPU.py` (Graphic Processing Unit):** Actúa como el cerebro
  principal. Prepara los datos, define las dimensiones del problema (los
  bloques) y envía las tareas a la cola de la GPU.
- **`sm.py` (Streaming Multiprocessor):** Lo podemos imaginar como un
  capataz. Recibe tareas (bloques de trabajo de la cola de la GPU) que
  reparte a sus núcleos. Cada SM es un proceso independiente.
- **`nucleo.py` (Thread):** Representa un núcleo CUDA (hilo de
  ejecución). No usamos la librería CUDA. Son hebras, pues son una clase
  hija (subclase) de `Thread`.
- **`kernels.py` (Unidades de Cómputo):** Aquí suceden las operaciones
  matemáticas (sumar, escalar, …).
- **`gpu_memory.py` (Memoria Global):** Define la estructura de memoria
  accesible por todos los SMs. Es más lenta que la memoria local porque
  se necesita sincronización, y está “un nivel más por encima”.
- **`sm_memory.py` (Memoria Local):** Es la memoria privada para cada
  SM, utilizada como caché temporal. Está implementada simplemente como
  una lista. Esto es muy eficiente, ya que acceder a la posición de un
  vector es de coste O(1).

------------------------------------------------------------------------

## 3. Implementación del Paralelismo

El corazón de la simulación reside en la ejecución paralela de los
kernels y la correcta gestión de la sincronización y la memoria. A
continuación, se detallan las implementaciones principales.

### 3.1. Memoria Global vs Memoria Local

**Memoria Global (`GPUMemory`):**

``` python
# gpu_memory.py
from multiprocessing import Array, Value

class GPUMemory:
    def __init__(self, tam_max: int) -> None:
        self.tam_max = Value('i', tam_max)
        self.dato1 = Array('f', tam_max)
        self.dato2 = Array('f', tam_max)
        self.res = Array('f', tam_max)
        self.tam_datos = Value('i', 0)
        self.kernel = Value('i', 0)
```

\-`self.dato1` y `self.dato2` son vectores porque son un `Array` de
`tam_max`. En ellos se cargarán los datos iniciales.

\-`self.res` es el vector donde se escribe el resultado.

-Con `Value('i', 0)` estoy diciendo “voy a guardar un entero (‘i’ de
integer) en esta dirección de memoria y lo inicializo en 0”.

\-`self.tam_datos` es la cantidad de datos “reales” con lo sque vamos a
trabajar. Si el tamaño máximo es 1000, pero solo trabajamos con 50, no
tendremos que preocuparnos de los otros 950.

\-`self.kernel` es el número que hemos asociado a `INCR` (1), `SUMAR`
(2), etc.

Como indica el profesor, “Estamos suponiendo que la memoria de la GPU
está estructurada con los campos que me interesan. Es poco realista,
pero aceptable para esta simulación.” En una GPU real, la memoria no
está exactamente estructurada de esta manera.

**Memoria Local (`SMMemory`):**

``` python
# sm_memory.py
class SMMemory:
    def __init__(self, tam: int) -> None:
        self.datos = [0.0] * tam
        self.ini_bloque = 0
        self.tam_bloque = 0
```

Está implementada como una lista estándar de Python dentro del proceso
de cada SM, funcionando como una memoria de trabajo privada y mucho más
rápida para los núcleos que la memoria principal compartida. Como ya
hemos dicho, el acceso a una posición de memoria tiene coste constante.

\-`self.datos` crea el vector de tamaño `tam`.

\-`self.ini_bloque` indica la posición de la memoria global donde el SM
empieza a trabajar.

`self.tam_bloque` análogo. Nos sirve para que no haya núcleos trabajando
“de más” en caso de que queden pocas cosas por hacer y muchos núcleos
esperando.

### 3.2. ¿Qué hace cada kernel?

Analicemos los kernels. Aquí entran en juego los cálculos matemáticos

**Kernel Incremento (`INCR`):**

Realiza un cálculo directo sobre la memoria global sin requerir
sincronización de las hebras, ya que cada núcleo opera sobre un índice
independiente.

``` python
# kernels.py
def incr(core_id: int, gpu_mem: GPUMemory, sm_mem: SMMemory, _: Barrier) -> None:
    if core_id < sm_mem.tam_bloque:
        idx = sm_mem.ini_bloque + core_id
        # Acceso directo a memoria global
        gpu_mem.res[idx] = gpu_mem.dato1[idx] + 1
```

Cada núcleo tiene asignado un ID. El `if` verifica que trabajen tantos
núcleos como `sm_mem.tam_bloque` y no más. La línea
`idx = sm_mem.ini_bloque + core_id` hace que cada núcleo comience a
trabajar en la posición que le corresponde. Si prescindimos de esta
línea, todos los núcleos trabajarían sobre los mismos datos (mismas
posiciones de memoria, las iniciales).

Finalmente, tenemos `gpu_mem.res[idx] = gpu_mem.dato1[idx] + 1`. En la
memoria global, suman 1 al input `dato1`, en la posición del vector que
le corresponde.

**Kernel Suma de vectores (`SUMAR`):**

``` python
# kernels.py
def sumar(core_id: int, gpu_mem: GPUMemory, sm_mem: SMMemory, _: Barrier) -> None:
    if core_id < sm_mem.tam_bloque:
        # Calculamos el índice global
        idx_global = sm_mem.ini_bloque + core_id
        
        #Copia a memoria local
        sm_mem.datos[core_id] = gpu_mem.dato1[idx_global]
        sm_mem.datos[core_id + sm_mem.tam_bloque] = gpu_mem.dato2[idx_global]
        
        # Suma y copia a la memoria global
        resultado_local = sm_mem.datos[core_id] + sm_mem.datos[core_id + sm_mem.tam_bloque]
        gpu_mem.res[idx_global] = resultado_local
```

La condición del `if` y la primera línea es análogo a `INCR`. Después,
con `sm_mem.datos[core_id]` guardamos en la memoria local el bloque
sobre el que vamos a trabajar del primer vector y con
`sm_mem.datos[core_id + sm_mem.tam_bloque]` el bloque del segundo
vector. Por último, sumamos en nuestra memoria local y lo copiamos a la
global.

**Kernel Difuminar (`DIFUMINAR`):**

``` python
# kernels.py
def difuminar(core_id: int, gpu_mem: GPUMemory, sm_mem: SMMemory, barrera: Barrier) -> None:
    if core_id < sm_mem.tam_bloque:
        # Calculamos el índice global
        idx = sm_mem.ini_bloque + core_id
        sm_mem.datos[core_id] = gpu_mem.dato1[idx]
        
    # Nadie avanza hasta que todos han copiado sus datos
    barrera.wait()
    
    if core_id < sm_mem.tam_bloque:
        #Omitido por brevedad
        # ...
        gpu_mem.res[idx] = (izq + centro + der) / 3.0
```

La condición del `if` y la primera línea es análogo a los anteriores.
Después copiamos los datos a la memoria local.

¿Qué hace `barrera.wait()`? Cuando una hebra llega a esa línea de código
se queda esperando hasta que todas las hebras también lean esa línea. En
ese momento, la barrera “se levanta” y todos reanudan su trabajo a la
vez. ¿Para qué sirve? Para evitar la condición de carrera. Una hebra
copia su dato en la memoria local, pero después lee el de su izquierda y
el de su derecha. Si no ponemos esta barrera, los datos de izquierda y
derecha podrían aún no haberse copiado.

**Kernel Producto Escalar (`ESCALAR`):**

``` python
# kernels.py
def escalar(core_id: int, gpu_mem: GPUMemory, sm_mem: SMMemory, barrera: Barrier) -> None:
    if core_id < sm_mem.tam_bloque:
        # Calculamos el índice global
        idx = sm_mem.ini_bloque + core_id

        producto_local = gpu_mem.dato1[idx] * gpu_mem.dato2[idx]
        
        with gpu_mem.res.get_lock():
            gpu_mem.res[0] += producto_local
```

La condición del `if` y la primera línea es análogo a los anteriores.
Calculamos el producto de dos componentes de los vectores, guardándolo
en la memoria local. Pero para ello no necesitamos copiar todo el vector
a la memoria local. Con el `get_lock()`, aseguramos que solo un hilo a
la vez sume al resultado global (así no hay condición de carrera).

<!-- Creo que esto último es secuencial (ineficiente) -->

## 4. Análisis de Flujo de Datos

Analizamos la ruta que sigue un dato desde que ingresa al sistema como
input hasta que es procesado:

1.  Preparación: En `GPU.py`, la CPU crea las instancias de memoria
    (`GPUMemory`), define los vectores iniciales y los carga en los
    arrays compartidos.

2.  Distribución de Tareas: El Host (GPU) divide el trabajo total en
    fragmentos iterando con `block_start` y `block_size`, encolando
    estas tuplas en la `Queue` global.

3.  Recepción en SM: El multiprocesador (`sm.py`) consume tareas de la
    cola. Lee los límites del bloque y actualiza su memoria local
    (`SMMemory.ini_bloque` y `tam_bloque`).

4.  Ejecución (Núcleos): Los hilos (`nucleo.py`) avanzan la barrera,
    leen de la memoria global qué operación toca
    (`gpu_mem.kernel.value`) e invocan la función correspondiente en
    `kernels.py`.

5.  Recolección: Una vez que todos los procesos SM hacen `.join()`, el
    programa principal recupera e imprime los resultados directamente
    desde `gpu_mem.res`.

## 5. Tiempo de ejecución

Si ejecutamos

``` python
mem_gpu.tam_datos.value = 501
mem_gpu.dato1[:501] = [1.2] * 501
```

la terminal muestra

``` {text}
---> Iniciando tarea: INCR (Incremento +1) <---
incr             : [2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2]
rdo esperado     : [2.2, 2.2, 2.2, ...]
tiempo paralelo  : 0.085200 s
tiempo secuencial: 0.000057 s
```

En prácticas anteriores, la ventaja del paralelismo se reflejaba con una
cantidad de datos mayor. Por ejemplo, podemos probar con `500_000`

``` python
mem_gpu.tam_datos.value = 500_000
mem_gpu.dato1[:] = [1.2] * 500_000
```

a lo que la terminal muestra

``` {text}
---> Iniciando tarea: INCR (Incremento +1) <---
incr             : [2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2]
rdo esperado     : [2.2, 2.2, 2.2, ...]
tiempo paralelo  : 18.160339 s
tiempo secuencial: 0.046736 s
```

Observamos con estos 2 ejemplos que, sorprendentemente el tiempo de
ejecución secuencial es más rápido que el “paralelo” (el de la GPU). Sin
embargo, conviene recordar que estamos realizando una simulación de una
GPU. Por tanto, si estuviéramos operando sobre una GPU real, los tiempos
paralelos serían claramente inferiores.

## 6. Interacción con el usuario

Queremos que el usuario seleccione las distintas tareas (`INCR`,
`SUMAR`, `DIFUMINAR` o `ESCALAR`). Para ello, añadimos un `while True`
(mientras el usuario no diga lo contrario, esperamos a que nos de una
instrucción)

``` python
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
```

En la terminal se muestra

``` {text}
=======================================
    SIMULADOR GPU - MENÚ PRINCIPAL     
=======================================
Selecciona la tarea a ejecutar:
0) Salir del programa
1) Incremento (INCR)
2) Suma de dos vectores (SUMAR)
3) Difuminar (DIFUMINAR)
4) Producto Escalar (ESCALAR)
=======================================
```

El programa identifica Incremento con 1, Suma con 2, … porque
<span style="color: blue;">en</span> `GPU.py` hemos importado

``` python
from kernels import INCR, SUMAR, DIFUMINAR, ESCALAR
```

y en `kernels.py` definimos

``` python
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
```

Por ello, cada vez que ejecutamos una nueva “tarea”, damos una vuelta al
bucle, y por tanto habrá que “reiniciar” la GPU. Para ello, volvemos a
crear una cola y creamos de nuevo los objetos de tipo SM.

``` python
q_bloques = Queue()
sms = [SM(cant_nucleos_por_sm, mem_gpu, tam_mem_sm, q_bloques) for _ in range(cant_sms)]
for s in sms:
    s.start()
```

Cuando el usuario haya escogido una tarea específica, el bucle entra en
el `if` específico de cada tarea.

Al principio el ordenador dice a la GPU lo que debe ejecutar y prepara
los datos:

- `INCR`: rellenamos los primeros 501 elementos del vector con 1.2

``` python
mem_gpu.tam_datos.value = 501
mem_gpu.dato1[:501] = [1.2] * 501
```

- `SUMAR`: rellenamos los primeros 10 elementos de los dos vectores para
  hacer la suma.

``` python
mem_gpu.tam_datos.value = 10
mem_gpu.dato1[:10] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
mem_gpu.dato2[:10] = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5]
```

- `DIFUMINAR`: rellenamos los primeros 501 elementos del vector con
  múltiplos de 3 y limpiemos el vector de resultados.

``` python
tam_datos = 501
mem_gpu.tam_datos.value = tam_datos

for i in range(tam_datos):
    mem_gpu.dato1[i] = float(i * 3)
    mem_gpu.res[i] = 0.0 
```

- `ESCALAR`: rellenamos los primeros 10 elementos de los dos vectores
  con 1.0 y 2.0 y limpiemos el primer elemento del vector de resultados.

``` python
tam_datos_esc = 10
mem_gpu.tam_datos.value = tam_datos_esc
            
for i in range(tam_datos_esc):
    mem_gpu.dato1[i] = 1.0
    mem_gpu.dato2[i] = 2.0
mem_gpu.res[0] = 0.0 
```

Después el ordenador divide la tarea en bloques

``` python
for block_start in range(0, mem_gpu.tam_datos.value, cant_nucleos_por_sm):
    block_size = min(cant_nucleos_por_sm, mem_gpu.tam_datos.value - block_start)
    q_bloques.put((block_start, block_size))
```

Ponemos un `None` para cada `SM` para avisar cuando no hay nada.

``` python
for _ in range(cant_sms):
q_bloques.put(None)
```

y al final espera a que todos los `SM` acaben y imprime el resultado

``` python
for sm in sms:
sm.join()
```
