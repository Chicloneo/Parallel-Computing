# Data generation and analysis
Santiago Lillo Macías
2026-03-28

We want to generate data. Thousands of numbers. Instead of generating one only file with all of them, we use our parallelism knowledge to fasten it and create multiple text files. For simplicity, our data are numbers.

A procedure to generate a random number is the following

```{python}
def zeta(s: float, cant_terms: int) -> float:
    return sum([1 / (n ** s) for n in range(1, cant_terms + 1)])

def azar_costoso(coste: int) -> float:
    return zeta(gauss(0, 1), coste)
```

The Riemann zeta function only converges for $s > 1, s \in \mathbb{R}$, but we are working with a finite number of terms, so we are OK with that.

## How to write them on a txt file?

```{python}
def crear_archivo(numero_de_datos: int, nombre: str):
        nombre_archivo = f'Datos_{nombre}'

        cant_datos_azar = randint(numero_de_datos // 2, 2 * numero_de_datos) # add more randomness
        coste = 1_000
        coste_azar = randint(coste // 2, 2 * coste) 

        numeros = [azar_costoso(coste_azar) for _ in range(cant_datos_azar)] 

        num_strings = [f'{num}' for num in numeros]  # Convert numbers into strings
        str_total = ' '.join(num_strings) 
        with open(nombre_archivo, 'w') as archivo:
            archivo.write(str_total)
```

This function creates a file named "Datos_1" (or Datos_2, ...)

## How to generate MORE numbers?

We will create multiple `.txt`, as promised

```{python}
if __name__ == '__main__':
    cant_datos = 10_000
    cant_datos_azar = randint(cant_datos // 2, 2 * cant_datos) #between 5_000 and 20_000
    coste = 1_000
    coste_azar = randint(coste // 2, 2 * coste) #entre 500 y 2_000

    nombre_archivo = 'datos'

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
```

Each execution produces a different quantity of numbers. Also cost is different each time.

10 txt files are created on the same folder as your `.py`.

# Data analysis

Suppose you have a folder named `datos_analizar`. It contains many files of many many numbers, and we want to do some math on them:

- Mean
- Standard deviation

## Mean auxiliary function

- Input: file name
- Output: Partial sum, number of elements, sum of squares

```{python}
def aux_media(nombre_de_archivo:str) -> list[float,int, float]:
    with open(nombre_de_archivo, 'r') as archivo:
        texto = archivo.read() 

    datos_str = texto.split()  
    datos = list(map(float, datos_str))  
    conteo = len(datos)  
    suma_parcial = sum(datos) 
    suma_cuadrados = sum([dato ** 2 for dato in datos])

    return [suma_parcial, conteo, suma_cuadrados]
``` 

Example:

```{text}
Texto = '1.0 2.0 3.0 4.0 5.0'
datos_str = ['1.0', '2.0', '3.0', '4.0', '5.0']
datos = [1.0, 2.0, 3.0, 4.0, 5.0]
cant_datos = 5
suma = 15.0
```

First of all, create a Pool of processes (_Get ready workers!_)

Then, give the folder path.

Finally, do the math.

## Some math theory

Be careful not to do the following: compute the total mean as the mean of means. Neither for the variance.

Example: mean1 = 0, mean2 = 4, mean3 = 5

total mean: 4.5 , not 3 $ = \frac{0+4+5}{3} $ !!!

Thus, if we want to compute the total mean of $n$ files, the formula is, given partial sums $s_i$ of $k_i$ numbers, the total mean is $$\mu = \frac{s_1 + \dots + s_n}{k_1 + \dots + k_n}$$ where the partial sum of numbers $\{x_1, \dots, x_{k_i}\}$ is $\sum_{j=1}^{k_i} x_j$

The variance formula is $$\frac{\sum s'_i}{\sum k_i} - \mu^2$$ where $s'_i$ is the partial sum of squares.

```{python}
if __name__ == '__main__':
    pool = Pool()
    print('-------------')
                                                
    ruta_carpeta = "datos_analizar"
    archivos = [os.path.join(ruta_carpeta, f) for f in os.listdir(ruta_carpeta)]

    print('---------------------------------------------------------')

    sumas_y_conteos = pool.map(aux_media,[archivo for archivo in archivos])
    sumas_parciales = [suma_parcial[0] for suma_parcial in sumas_y_conteos]
    conteos = [conteo[1] for conteo in sumas_y_conteos] # how many numbers are there on each file
    media_total = sum(sumas_parciales)/sum(conteos)

    sumas_cuadrados_parciales = [suma_cuadrados_parcial[2] for suma_cuadrados_parcial in sumas_y_conteos]
    varianza_total = (sum(sumas_cuadrados_parciales)/sum(conteos)) - media_total**2
    desviacion_tipica_total = sqrt(varianza_total)

    print("Media total: ", media_total)
    print("Varianza total: ", varianza_total)
    print("Desviación típica total: ", desviacion_tipica_total)
```
