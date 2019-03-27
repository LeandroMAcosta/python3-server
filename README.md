# Aplicación Servidor
# Indice
1. ¿Cómo funciona un servidor?
2. Proyecto
    2.1 Funciones
    2.2 Excepciones
    2.3 Errores

3. Servidor Multicliente
    2.2 Selectors
    2.3 Threads

4. Bibliografía

5. Integrantes del grupo

## ¿Cómo funciona un servidor?

![Servido Cliente](https://files.realpython.com/media/sockets-tcp-flow.1da426797e37.jpg)

Veamos las funciones que llama el servidor para crear un **listening** socket:
    * socket()
    * bind()
    * listen()
    * accept()

El socket espera a que los clientes se conecten, cuando esto sucede el servidor hace
una llamada a la función `accept()` para poder completar la conección.

Por otra parte el cliente llama a la función `connect()` para poder establecer
la conección con el servidor e iniciar lo que se conoce como *three-way handshake*, que no
es nada más que una forma de asegurarse que el cliente se pueda comunicar con el servidor
en la network y vice-versa.

Para comunicarse entre ellos tanto el servido como el cliente utilizan las funciones.
    * send()
    * recv()

Por último una vez que el cliente no necesita comunicarse más con el servidor , envia 
un mensaje para indicarle que no va enviar más mensajes y cierra su respectivo 
socket usand `close()`.

## Proyecto
-------------------------------
Cuando el cliente o el servidor usan la funcion `send()` pueden surgir complicaciones. ¿Cuál es el problema?. Muy simple send() devuelve la cantidad de bytes enviados, pero puede llegar a pasar que esa cantidad es menor al tamaño de la información que se quiere enviar.
> Las aplicaciones son responsables de verificar que toda la información haya sido enviada ; si sólo se envió una oarta , la aplicación tiene que enviar la información que resta.

Podemos evitar este inconveniente utilizando la función `sendall()`
> A diferencia de send(), este metodo continua enviando la información hasta que se envia todo u ocurre un error. En caso de exito se devuelve cero.
------------------------------

## Servidor Multicliente
Volviendo a como funciona un servidor cabe destacar que el método descripto sólo funciona para un cliente. Entonces ¿Cómo hacemos para manejar multiples clientes al mismo tiempo?. Existen varias formas de implementar un servidor multicliente:

###Selectors 

Va a ser una breve descripción de como funciona porque no es el método que optamos nosotros para realizar un servidor multicliente. 

Si usamos la **systemcall** `select()` podemos fijarnos que socket's tiene la E/S para leer/escribir, dependiendo del caso. Para ello se puede utilizar la librería *Selectors*. 
``` python
    import selectors
    selector = selectors.DefaultSelector()
    
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind((host, port))
    socket.listen()
    
    print('listening on', (host, port))
    
    socket.setblocking(False)
    sel.register(socket, selectors.EVENT_READ, data=None)
```
La mayor diferencia con el servidor que sólo puede manejar un cliente a la vez es que tenemos es la llamada a la función 
socket.setblocking(False) que sirve para configurar el socken en un modo *non-blocking*.
> Una función o método que temporalmente suspende tu aplicacion se llama *blocking call*, por ejemplo accept() o send() no retornan inmediatamente.Las "Blocking calls" tienen que esperar a systemcall's para terminar antes que devuelvan un valor.

Sel.register() como lo dice el nombre registra el socket para que sea monitoreado con `sel.select()` 
para eventos en los que estamos interesados. La información es recivida cuando la llamada a `sel.select()` termina.

### Threads   


## Bibliografía
1. [Servidor Multicliente (Ejemplo)](https://www.geeksforgeeks.org/socket-programming-multi-threading-python/)

2. [Servidor Multicliente usando Selectors](https://realpython.com/python-sockets/#multi-connection-client-and-server)

3. [Libreria Selectors](https://docs.python.org/3/library/selectors.html)

4. [Libreria Thread](htthttps://docs.python.org/2/library/thread.html)

## Integrantes del Grupo
- Gonzalo Gigena
- Leanro Acosta
- Joaquin de Francesca