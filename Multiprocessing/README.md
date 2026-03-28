# Multiprocessing example
Santiago Lillo Macías
2026-03-28

We will compute an integral with two different methods: sequential and
parallel computing. The simplicity of this example does not allow us to
show the eficiency of parallel computing. For now, we will just focus on
this new kind of computing, commonñy unkown for junior developers.

Let the function be

``` python
def sucesor(x:int) -> int:
    return x+1
```

We may want to know the sucesor of `[2,5,9]`.

-Option one: `for i in ...`

-Option two (Good!): use `map`. Of course the `for` loop is easier to
implement and better if you have a small input, but we are thinking of
big inputs, such as vectors with a large size.

``` python
resultados1 = pool.map(sucesor, [2,5,9])
print('suma pool map = ', resultados1)
```

`map` calculates sucesor(2), sucesor(5) and sucesor(9) at the same time.
The first line does a lazy evaluation, so it won’t show the result
unless we ask for it. We do so on the second line.

``` text
suma pool map =  [3, 6, 10]
```

Let the function be

``` python
def suma(x:int, y:int) -> int:
    return x+y
```

Remark this function takes two arguments. We cannot use
`map(suma,[(1,1),(3,5),(9,3)])`, because it will take the `(1,1)` input
as a whole, and not as two arguments. `starmap` converts `suma((x,y))`
into `suma(x,y)`.

``` python
from itertools import starmap
resultados2 = pool.starmap(suma,[(1,1),(3,5),(9,3)])
print('suma pool starmap = ',resultados2)
```

We do the same as before.

``` text
suma pool starmap =  [2, 8, 12]
```

But what is this `pool` thing? Before using it, we have to create a
Pool:

``` python
from multiprocessing import Pool
pool = Pool()
```

Imagine you have 10 workers and you are the boss. Then, with that line
you are saying “Hey, workers, get ready to start. You will have to do a
job separately”. By default, the system will create whatever number of
phisically avaliable kernels on your computer. Usually it will be 8. You
can chek that with `cpu.count()`. If you want a specific number N of
processes, you shall write

``` python
pool = Pool(N)
```

and depending on your hardware, and if it’s working on some other
things, you could possibly get N processes, but not always.
