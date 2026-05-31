#importamos la libreria de pygame porque es la libreria que posee las herramientas a utilizar en este codigo
import pygame
#le da a Python acceso directo a interactuar con el sistema operativo
import sys
#con esta libreria permitimos que otros tenga mas accesibilidad a la hora de usar el codigo porque daba un problema al compartirlo
import os

#activamos pygame.init() porque es el motor del juego, lo que se encarga de activar la libreria
pygame.init()

#config
ruta_base   = os.path.dirname(os.path.abspath(__file__))
ruta_assets = os.path.join(ruta_base, "assets")
#objetos a usar
ruta_character  = os.path.join(ruta_assets, "я.png")
ruta_snail      = os.path.join(ruta_assets, "snail_image.png")
ruta_goal       = os.path.join(ruta_assets, "pablo.png")
ruta_fire_up    = os.path.join(ruta_assets, "fuego_hacia_arriba.png")
ruta_fire_right = os.path.join(ruta_assets, "fugo_hacia_el_lado.png")
ruta_musica     = os.path.join(ruta_assets, "Street Fighter II Arcade Music - Balrog Stage - CPS1 - Lamar Johnson.mp3")
ruta_text       = os.path.join(ruta_assets, "karmatic-arcade/ka1.ttf")

#musica
pygame.mixer.music.load(ruta_musica)
pygame.mixer.music.set_volume(0.5)#Ajusta el volumen al 50% para que no suene tan alto
pygame.mixer.music.play(-1)# El parametro -1 hace que la música se repita infinitamente

icono = pygame.image.load(ruta_snail) #copia la direccion de la imagen y se pega
pygame.display.set_icon(icono)#lo coloca como el icono de la ventana

#vidas
VIDAS_GLOBALES = 3
tiempo_invulnerable = 0#esto es para que el personaje vuelva a recibir daño
#esto con pygame.time.get_ticks() se ajusta a un tiempo de invulnerabilidad 
#esto para que no muera al momento de aparecer

# estos son los datos para generar la ventana del interfaz
screen_x, screen_y = 800, 600
pantalla = pygame.display.set_mode((screen_x, screen_y))
#esto es para que en la ventana aparezca con este nombre
pygame.display.set_caption("snail")

#datos de colores
white = (255, 255, 255)
black = (0, 0, 0)
red   = (255, 0, 0)
grey  = (128, 128, 128)

#fuente que se utilizara
#se le coloca el nombre de una variable para llamarlo mas facil
fuente_path = ruta_text
#definimos como sera las "instrucciones" y el "titulo"
try:
    fuente_titulo       = pygame.font.Font(fuente_path, 70)
    fuente_instrucciones = pygame.font.Font(fuente_path, 25)
#en el caso de que no se encuentre usamos estos datos
except FileNotFoundError:
    fuente_titulo       = pygame.font.SysFont("Arial", 70, bold=True)
    fuente_instrucciones = pygame.font.SysFont("Arial", 25, bold=True)

#se comienzan a crear los objetos que entran en la interfaz
#definimos la clase mundo donde se va a jugar
class Mundo:
    def __init__(self): self.objetos = []#se le coloca una lista de objetos que se le agregaran de las otras clases
    def draw(self, screen): screen.fill(grey)#rendriza la pantalla y lo dibuja, de paso dibuja pantalla a gris
#cuando se gane o pierda cargara esta pantalla se cargara una nueva pantalla para dibujar lo que sigue
class pantalla_final:
    # Cuando se gane o pierda, se cargará esta escena para dibujar el contenido final
    def __init__(self): self.objetos = []
    def draw(self, screen): screen.fill(white)# Limpia la pantalla con fondo blanco para el texto fina

#se crea la clase caracol para sacar al enemigo del que se debe escapar
class Caracol:
    def __init__(self, x, y, imagen_path=None):#le creamos un paramentro para la imagen para despues cambiarsela
        # Guardamos la posición actual y la inicial para los reinicios
        self.x = x; self.y = y
        self.inicio_x = x; self.inicio_y = y
        self.size = 60#le creamos sus medidas

        # esto sera para un estado inicial
        self.modo = "normal"

        #si no se pasa imagen_path usamos la imagen del caracol por defecto
        if imagen_path is None:
            imagen_path = ruta_snail

        #se crea un try para que coloque la imagen base, en este caso es la del caracol
        try:
            self.imagen = pygame.image.load(imagen_path).convert_alpha()#el convert_alpa es para que pygame 
            #procese el canal Alpha (las transparencias de la imagen png) de forma nativa
            self.imagen = pygame.transform.scale(self.imagen, (self.size, self.size))
        #si no llega a encontrar la imagen no colocara una imagen
        except FileNotFoundError:
            self.imagen = None

    #creamos un metodo para que se dibuje en la pantalla
    def draw(self, screen):
        if self.imagen:
            screen.blit(self.imagen, (self.x, self.y))
        #si no encuentra la imagen pone un cuadrado rojo
        else:
            pygame.draw.rect(screen, red, (self.x, self.y, self.size, self.size))

    #con este metodo se reinicia la posicion del caracol al reiniciar partida
    #Almacena las coordenadas de origen (inicio_x, inicio_y), tambien si el jugador pierde una vida, el objeto 
    # puede ser reposicionado inmediatamente a su punto de partida 
    def resetear(self):
        self.x = self.inicio_x; self.y = self.inicio_y
        self.modo = "normal"

    #creamos un metodo en el cual con una velocidad la cual podremos cambiar, haremos siga a un objeto(osea nosotros)
    #la distancia no cosidera objtos distintos
    def perseguir(self, objetivo_x, objetivo_y, velocidad=1):
        if self.x < objetivo_x: 
            self.x += velocidad
        if self.x > objetivo_x: 
            self.x -= velocidad
        if self.y < objetivo_y: 
            self.y += velocidad
        if self.y > objetivo_y: 
            self.y -= velocidad
    
    # Algoritmo avanzado de persecución con control de colisiones y límites de pantalla
    def perseguir_con_colision(self, objetivo_x, objetivo_y, objetos, velocidad=1):
        # Determina la dirección del movimiento en los ejes X e Y
        dx = velocidad if self.x < objetivo_x else -velocidad if self.x > objetivo_x else 0
        dy = velocidad if self.y < objetivo_y else -velocidad if self.y > objetivo_y else 0

        # Movimiento y colisión en el eje X (se mantiene adentro de la ventana en los lados x(izquierda y derecha)
        self.x += dx
        self.x = max(0, min(self.x, screen_x - self.size))#esto se hace para poner limites en la pantalla
        #Compara la posición del caracol con el límite derecho de la pantalla (restando su tamaño para que no se salga)
        #con el max si el caracol se mueve a la izquierda y su posición cae a -10, max(-10, 0) devolverá 0
        # bloqueando al personaje en el origen.

        for obj in objetos: self._resolver_colision_x(obj)
        #lo mismo para y(arriba y abajo)
        self.y += dy
        self.y = max(0, min(self.y, screen_y - self.size))
        for obj in objetos: self._resolver_colision_y(obj)


    def perseguir_nivel3(self, objetivo_x, objetivo_y, objetos, velocidad=1):
        #se determina la dirección del movimiento en base a la posición del jugador
        dx = velocidad if self.x < objetivo_x else -velocidad if self.x > objetivo_x else 0
        dy = velocidad if self.y < objetivo_y else -velocidad if self.y > objetivo_y else 0

        #en el nivel 3 si el caracol se sale completamente por el borde derecho (self.x > screen_x)
        # se teletransporta instantáneamente al lado izquierdo. Y si se sale por abajo, aparece arriba.
        self.x += dx
        if self.x < -self.size:  self.x = screen_x#aca evaluamos las cordenadas, si llega a un punto lo mueve al punto opuesto
        elif self.x > screen_x:  self.x = -self.size
        for obj in objetos: self._resolver_colision_x(obj)

        self.y += dy
        if self.y < -self.size:  self.y = screen_y
        elif self.y > screen_y:  self.y = -self.size
        for obj in objetos: self._resolver_colision_y(obj)

    #evitan que el caracol atraviese las paredes u obstáculos del mapa
    #este es el de x
    def _resolver_colision_x(self, obj):
        rect_p = pygame.Rect(self.x, self.y, self.size, self.size)
        rect_o = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        if rect_p.colliderect(rect_o):
            if self.x + self.size//2 < obj.x + obj.width//2: self.x = obj.x - self.size
            else: self.x = obj.x + obj.width
    #este es el de y
    def _resolver_colision_y(self, obj):
        rect_p = pygame.Rect(self.x, self.y, self.size, self.size)
        rect_o = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        if rect_p.colliderect(rect_o):
            if self.y + self.size//2 < obj.y + obj.height//2: self.y = obj.y - self.size
            else: self.y = obj.y + obj.height

#vidas
#Esta función es la que se ejecuta cuando el caracol alcanza al personaje
#Su objetivo es restar una vida, reiniciar las posiciones y
#dar una pequeña ventana de tiempo para que se pueda recuperar sin morir de golpe otra vez.
def procesar_golpe(miguel, inicio_miguel, caracol_asesino = None):
    #para no crear variables nuevas se ocupa global y ocupar las que ya estan
    global VIDAS_GLOBALES, tiempo_invulnerable
    tiempo_actual = pygame.time.get_ticks()#busca el tiempo en que va el juego(los ticks)
    #Si el juego determina que todavía estás en el tiempo de protección
    if tiempo_actual < tiempo_invulnerable:#esto es un cronometro, cuando el tiempo actual, el del juego, alcanze el objetivo de 
        #3 segundos a futuro hara lo siguiente:
        return True#la función se detiene inmediatamente usando return True
    VIDAS_GLOBALES -= 1#Si no eras invulnerable, se te resta una vida de la caja global
    #Si las vidas llegan a cero
    if VIDAS_GLOBALES <= 0:
        #la función restablece el contador a 3 para la próxima partida
        VIDAS_GLOBALES = 3
        #devuelve False (un aviso para que el bucle principal sepa que el jugador perdió y debe cargar la pantalla_final).
        return False
    #Si aún quedan vidas, teletransporta al personaje y al caracol a sus puntos de partida iniciales para limpiar el mapa.
    miguel.x, miguel.y = inicio_miguel
    #si existe la variable caracol en el nivel
    if caracol_asesino:
        #lo resetea
        caracol_asesino.resetear()
    tiempo_invulnerable = tiempo_actual + 3000#para tener el tiempo de invulnerabilidad le sumara al tiempo jugado 3 sugundos
    return True

#la función principal es pintar en la pantalla el texto que le dice al usuario cuántas vidas le quedan
def dibujar_vidas():
    #para no crear variables nuevas se ocupa global y ocupar las que ya estan
    global VIDAS_GLOBALES, tiempo_invulnerable
    tiempo_actual = pygame.time.get_ticks()#se saca el tiempo actual jugado
    if tiempo_actual < tiempo_invulnerable:#ocupa el mismo cronometro que procesar_golpe
        if (tiempo_actual // 200) % 2 == 0: #se dividi si entre 2 segundos, si el tiempo es par:
            #se salta el dibujo de las vidas en ese fotograma
            return#esto genera el efecto de parpadeo
    #Si el tiempo no es par o si no eres invulnerable, dibuja el texto de forma normal en la esquina superior izquierda de la pantalla.
    texto = fuente_instrucciones.render(f"VIDAS: {VIDAS_GLOBALES}", True, white)
    #dibuja la pantalla
    pantalla.blit(texto, (20, 20))

#se crea la funcion para la pantalla de inicio
def pantalla_inicio():
    esperando = True#se crea una variable para que el bucle corra
    while esperando:
        # Pinta el fondo de la pantalla de un color (en este caso azul)
        pantalla.fill((30,30,60))
        #con fuente_titulo (variable qu ya habiamos creado) ocupamos render para que muestre el texto
        #(el texto que podremos, , el color)
        titulo = fuente_titulo.render("Snail", True, white)
        #ocupamos la fuente_instrucciones y le colocamos lo mismo que a fuente_titulo
        inst1  = fuente_instrucciones.render("ESPACIO para jugar", True, (200,200,200))
        inst2  = fuente_instrucciones.render("ESC para salir", True, (200,200,200))
        #colocamos el texto en la pantalla
        #(se coloca en la mitad de x, pero se le resta la mitad de su ancho para que queden justamente en la mitad, posicion en y)
        pantalla.blit(titulo, (screen_x//2 - titulo.get_width()//2, 200))
        pantalla.blit(inst1,  (screen_x//2 - inst1.get_width()//2,  350))
        pantalla.blit(inst2,  (screen_x//2 - inst2.get_width()//2,  420))
        #que se dibuje la pantalla
        pygame.display.flip()
        #creamos un condicional pra las siguiente situaciones:
        for evento in pygame.event.get():
            # Si el usuario hace clic en la "X" de cerrar la ventana, se apaga el motor y el sistema
            if evento.type == pygame.QUIT: 
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:#si detecta que una tecla es presiona
                #esto se hace para delitimar y que solo funcionen las teclas que queremos que funcionen
                #con key pygame estara al tanto de las teclas que se presiones
                #si se presiona space volvera false la variable y rompera el bucle para avanzar al siguiente bucle
                if evento.key == pygame.K_SPACE:  
                    esperando = False
                #con scape se saldra del interfaz directamente
                if evento.key == pygame.K_ESCAPE: 
                    pygame.quit(); sys.exit()

#clase personaje
class Personaje:
    #estructura basica de __init__ con una parametro de imagen para poder cambiarlo despues
    def __init__(self, x, y, imagen_path=None):
        self.x = x; 
        self.y = y; 
        self.size = 60#las medidas

        #si no se pasa imagen_path usamos la imagen del personaje por defecto
        if imagen_path is None:
            imagen_path = ruta_character

        #esto es para que busque la imagen
        try:
            #si se encuentra:
            self.imagen = pygame.image.load(imagen_path).convert_alpha()
            self.imagen = pygame.transform.scale(self.imagen, (self.size, self.size))
        #si no:
        except FileNotFoundError:
            self.imagen = None#no tendra imagen
        #de esta manera se evitan errores de crasheo del interfaz

    #metodo para que el personaje se dibuje en la pantalla
    def draw(self, screen):
        if self.imagen: 
            screen.blit(self.imagen, (self.x, self.y))
        else: 
            pygame.draw.rect(screen, red, (self.x, self.y, self.size, self.size))

    #metodo para que el personaje se mueva:
    def move(self, dx, dy, objetos=None):
        self.x += dx
        #si sale 1px de un borde, se teletransporta al opuesto
        if self.x < -self.size:  
            self.x = screen_x
        elif self.x > screen_x:  
            self.x = -self.size
        if objetos:#si al moverse interactua con un objeto
            for obj in objetos:#para cada objeto que este en objetos
                #llaara a la funcion _resolver_colision_x
                self._resolver_colision_x(obj)

        self.y += dy
        #si sale 1px de un borde, se teletransporta al opuesto
        if self.y < -self.size:  
            self.y = screen_y
        elif self.y > screen_y:  
            self.y = -self.size
        #lo mismo para y
        if objetos:
            for obj in objetos: self._resolver_colision_y(obj)

    #detecta impactos horizontales y empuja al personaje fuera de las paredes
    def _resolver_colision_x(self, obj):
        #Se crea en la posición actual de Miguel (self.x, self.y)
        rect_p = pygame.Rect(self.x, self.y, self.size, self.size)#toma los datos de tus objetos y crea dos rectángulos
        #Se crea en la posición de la pared y toma las medidas exactas que tenga esa pared en específico (obj.width, obj.height)
        rect_o = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        # Si las cajas de colisión se superponen, calcula el punto medio algebraico
        if rect_p.colliderect(rect_o):
            # Si el centro del personaje está a la izquierda del centro del bloque, se frena a la izquierda
            if self.x + self.size//2 < obj.x + obj.width//2: 
                self.x = obj.x - self.size
            # Si viene del lado derecho, se clava justo donde termina el bloque
            else: 
                self.x = obj.x + obj.width

    #lo mismo en y
    def _resolver_colision_y(self, obj):
        rect_p = pygame.Rect(self.x, self.y, self.size, self.size)
        rect_o = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        if rect_p.colliderect(rect_o):
            if self.y + self.size//2 < obj.y + obj.height//2: 
                self.y = obj.y - self.size
            else: 
                self.y = obj.y + obj.height

#fuego
# El fuego hacia la derecha va a la derecha, sale, regresa, espera 4s.
class Fuegito_hacia_la_derecha:
    def __init__(self, x, y):
        #datos del objeto
        self.inicio_x = x; self.inicio_y = y
        self.x = x; self.y = y
        self.size = 45
        #Declaramos ancho y alto explícitamente para que la funcion de colisiones lo reconozca como obstaculo
        self.width = self.size# para que funcione como obstáculo en la lista
        self.height = self.size

        self.estado = "moverse"#"moverse" o "esperar"
        self.tiempo_espera = 0

        #lo mismo de siempre con try para la imagen y except para que no crashee
        try:
            self.imagen = pygame.image.load(ruta_fire_right).convert_alpha()
            self.imagen = pygame.transform.scale(self.imagen, (self.size, self.size))
        except FileNotFoundError:
            self.imagen = None

    def actualizar(self):
        #si esta en estado de moverse
        if self.estado == "moverse":
            #+= en x para que mueva su posicion a la derecha
            self.x += 5#la velocidad a la que se movera
            # cuando cruzó completamente el borde derecho

            #si se cruza el limite del borde derecho de la pantalla
            if self.x > screen_x:
                #regresar a su posicion inicial en x, tambien en y
                self.x = self.inicio_x#regresa en x
                self.y = self.inicio_y#es para evitar un posible bug o error
                self.estado = "esperar"# Cambia de fase para pausar el objeto
                #Registra el milisegundo actual en que inicio la pausa
                self.tiempo_espera = pygame.time.get_ticks()
        #Pausa antes de volver a salir
        elif self.estado == "esperar":
            #Resta el tiempo actual menos el tiempo guardado. Si ya pasaron 4 segundos
            if pygame.time.get_ticks() - self.tiempo_espera >= 4000:
                self.estado = "moverse"#vuelve a cambiar de estado

    #se dibujan en pantalla
    def draw(self, screen):
        if self.imagen: 
            screen.blit(self.imagen, (self.x, self.y))
        else: pygame.draw.rect(screen, (255, 100, 0), (self.x, self.y, self.size, self.size))

# El fuego hacia arriba sube, sale por arriba, regresa al inicio, espera 4s.
#aca funciona igual que la clase x, pero en y
class Fuegito_hacia_arriba:
    def __init__(self, x, y, tiempo_espera_ms=4000, velocidad=5):
        self.inicio_x = x; self.inicio_y = y
        self.x = x; self.y = y
        self.velocidad = velocidad
        self.size = 45
        self.width = self.size
        self.height = self.size
        self.estado = "moverse"
        self.tiempo_espera = 0
        # tiempo de espera configurable: nivel 2 usa 4000ms, nivel 3_1 usa 3000ms
        self.tiempo_espera_ms = tiempo_espera_ms
        try:
            self.imagen = pygame.image.load(ruta_fire_up).convert_alpha()
            self.imagen = pygame.transform.scale(self.imagen, (self.size, self.size))
        except FileNotFoundError:
            self.imagen = None

    def actualizar(self):
        if self.estado == "moverse":
            self.y -= self.velocidad         
            # cuando cruzó completamente el borde superior
            if self.y < -self.size:
                self.x = self.inicio_x
                self.y = self.inicio_y       
                self.estado = "esperar"
                self.tiempo_espera = pygame.time.get_ticks()
        elif self.estado == "esperar":
            if pygame.time.get_ticks() - self.tiempo_espera >= self.tiempo_espera_ms:
                self.estado = "moverse"

    def draw(self, screen):
        if self.imagen: 
            screen.blit(self.imagen, (self.x, self.y))
        else: pygame.draw.rect(screen, (255, 50, 0), (self.x, self.y, self.size, self.size))


#meta especial
# Cuando Miguel se acerca verticalmente, la meta se activa, huye por la derecha y desaparece.
class meta3_escape:
    def __init__(self, x, y, imagen_path=None):#imagen path para hacer su imagen una variable que se pueda cambiar
        #le asignamos sus valores
        self.x = x; self.y = y
        self.size = 45
        
        self.width = self.size
        self.height = self.size
        # Bandera para saber si la meta debe correr hacia la derecha
        self.escapando = False
        #se vuelve True cuando ya cruzó el borde, no regresa más
        self.escapo = False  

        #si no se pasa imagen_path usamos la imagen del caracol por defecto
        if imagen_path is None:
            imagen_path = ruta_snail

        #siempre se hara esto al colocarles una imagen para que no vaya a dar un posible error en la terminal y crashee
        try:
            self.imagen = pygame.image.load(imagen_path).convert_alpha()
            self.imagen = pygame.transform.scale(self.imagen, (self.size, self.size))
        except FileNotFoundError:
            self.imagen = None

    def actualizar(self, miguel_y):
        # si ya escapó no hace nada
        if self.escapo:
            return
        # Calcula la distancia vertical absoluta entre la meta y el personaje
        distancia_y = abs(self.y - miguel_y)#la distancia de la meta con el personaje
        # Si Miguel se acerca a menos de 80 pixeles en el eje Y, la meta empieza a escapar
        if distancia_y < 80:            
            self.escapando = True#cambia el valor de false a true

        # Si la meta esta en estado de escape, se mueve hacia la derecha
        if self.escapando:
            self.x += 4#se le suman 4 por frame
            # Si su posicion es mayor al limite derecho de la ventana del juego
            if self.x > screen_x:
                # Bloquea el estado para que desaparezca definitivamente
                self.escapo = True

    #se dibuja en pantalla
    def draw(self, screen):
        # solo se dibuja si no escapó
        if not self.escapo:
            if self.imagen: screen.blit(self.imagen, (self.x, self.y))
            else: pygame.draw.rect(screen, (0, 200, 0), (self.x, self.y, self.size, self.size))

#mapa nivel 1
#para el mapa solo creamos varios objetos y los dibujamos en el bucle del nivel que corresponde
class cuadro01:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=270;self.height=220
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro02:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=290;self.height=120
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro03:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=100;self.height=320
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro04:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=100;self.height=100
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro05:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=40;self.height=600
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro001:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=365;self.height=220
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro002:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=130;self.height=360
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro003:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=290;self.height=220
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro_extra:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=5;self.height=160
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))




#mapa nivel 2
#igual que con el nivel 2 creamos los objetos y los colocamos en el bucle que corresponden
class Cuadro_01:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=35;self.height=600
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_02:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=765;self.height=80
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_03:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=70;self.height=520
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_04:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=695;self.height=75
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_001:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=575;self.height=75
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_002:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=360;self.height=100
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_003:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=110;self.height=230
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_0001:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=50;self.height=135
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_0002:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=110;self.height=50
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_0003:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=25;self.height=75
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_0004:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=75;self.height=80
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class Cuadro_extra:
    def __init__(self,x,y): self.x=x;self.y=y;self.width=40;self.height=15
    def draw(self,s): pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))



#nivel 3
class cuadro100:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 70; self.height = 600
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height)) 

class cuadro200:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 175; self.height = 70
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro300:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 175; self.height = 90
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))  

class cuadro700:#245
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 60; self.height = 250
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadrobeta:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 200; self.height = 260
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro400:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 100; self.height = 40
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro500:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 100; self.height = 450
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadrogamma:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 70; self.height = 150
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadro600:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 170; self.height = 350
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadrodseta:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 170; self.height = 50
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadrodelta:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 240; self.height = 15
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class cuadroeta:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 50; self.height = 435
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))




#nivel 3.1
class sideon:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 800; self.height = 200
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class sidedown:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 800; self.height = 200
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class bloque_objeto:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 20; self.height = 600
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))

class bloque_2:
    def __init__(self, x, y):  self.x = x; self.y = y; self.width = 20; self.height = 600
    def draw(self, s):  pygame.draw.rect(s,black,(self.x,self.y,self.width,self.height))



#bloque de metas
class meta1:
    def __init__(self,x,y):
        self.x=x;self.y=y;self.size=45
        try:
            self.imagen=pygame.image.load(ruta_goal).convert_alpha()
            self.imagen=pygame.transform.scale(self.imagen,(self.size,self.size))
        except FileNotFoundError: self.imagen=None
    def draw(self,s):
        if self.imagen: s.blit(self.imagen,(self.x,self.y))

class meta2:
    def __init__(self,x,y):
        self.x=x;self.y=y;self.size=30
        try:
            self.imagen=pygame.image.load(ruta_goal).convert_alpha()
            self.imagen=pygame.transform.scale(self.imagen,(self.size,self.size))
        except FileNotFoundError: self.imagen=None
    def draw(self,s):
        if self.imagen: s.blit(self.imagen,(self.x,self.y))

class meta3:
    def __init__(self, x, y):
        self.x=x;self.y=y;self.size=45
        try:
            self.imagen=pygame.image.load(ruta_goal).convert_alpha()
            self.imagen=pygame.transform.scale(self.imagen,(self.size,self.size))
        except FileNotFoundError: self.imagen=None
    def draw(self,s):
        if self.imagen: s.blit(self.imagen,(self.x,self.y))

#nievl 1
def main():
    #se llama el valor de las vida y el tiempo de invulnerabilidad
    global VIDAS_GLOBALES, tiempo_invulnerable#con global se encarga de no crear otra variable
    clock = pygame.time.Clock()#creamos una variable reloj para controlar los fps
    
    #aca se comenzaran a llamar a todos los objetos y variable creados anteriormente para
    #que el bucle haga uso de ellos
    world = Mundo()#llamamos a la clase mundo como worl
    #le damos una posicion inicial a miguel en una variable (x es la horizontal y y la vertical) 
    INICIO_MIGUEL  = (125, screen_y // 2)#el //2 es para que los coloque en medio de la pantalla
    INICIO_CARACOL = (10,  screen_y // 2)
    #creamos las variables de los personajes y colocamos la variable de la posicion en sus coordenadas
    miguel         = Personaje(*INICIO_MIGUEL)#el * es para que python no tome el valor como un solo valor en x
    caracol_asesino = Caracol(*INICIO_CARACOL)#al ocupar * python ocupa el valor completo como 2 valores distintos
    #creamos la variable para la meta
    primer_nivel   = meta1(700, 200)

    #colocamos todos los objetos del mapa
    objeto1 = cuadro01(0,0);   objeto2 = cuadro02(270,0); objeto3 = cuadro03(560,0)
    objeto4 = cuadro04(660,0); objeto5 = cuadro05(760,0)
    objeto6 = cuadro001(0,380);objeto7 = cuadro002(355,240);objeto8 = cuadro003(480,380)
    objeto9 = cuadro_extra(0,220)

    #creams una lista de objetos del nivel 1, pra luego limital el movimiento y que no los atraviese
    objetos_nivel1 = [objeto1,objeto2,objeto3,objeto4,objeto5,
                      objeto6,objeto7,objeto8,objeto9]

    #creams el bucle respectivo
    while True:#mientras sea verdad
        clock.tick(60)#el tiempo ira a 60 frames
        #va a estar pendiente por si se presiona la x del interfaz salirse
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit(); sys.exit()

        #con key y get_pressed esta pendiente de obtener todos los movimientos del personaje en caso de que 
        #se presione una de lassiguiente teclas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  
            #si es izquierda le restara 5 a su posicion para moverse a la izquierda
            miguel.move(-5,0,objetos_nivel1)
        if keys[pygame.K_RIGHT]: 
            #si es derecha se la sumara pra moverse a la derecha
            miguel.move(5,0,objetos_nivel1)
        if keys[pygame.K_UP]:
            #si es hacia arriba se le restara a su posicion en y para moverse hacia arriba
            miguel.move(0,-5,objetos_nivel1)
        if keys[pygame.K_DOWN]:  
            #si es abajo se sumara a su posicion en y para bajar
            miguel.move(0,5,objetos_nivel1)

        #se define: cada que vez que nos movamos se movera con nosotros/ no atravesara objetos/ y su velocidad
        caracol_asesino.perseguir_con_colision(miguel.x, miguel.y, objetos_nivel1, velocidad= 3)

        # Genera hitboxes para evaluar colisiones de daño o victoria
        rect_miguel  = pygame.Rect(miguel.x, miguel.y, miguel.size, miguel.size)
        rect_caracol = pygame.Rect(caracol_asesino.x, caracol_asesino.y, caracol_asesino.size, caracol_asesino.size)
        rect_meta    = pygame.Rect(primer_nivel.x, primer_nivel.y, primer_nivel.size, primer_nivel.size)

        #si el caracol toca a Miguel
        if rect_miguel.colliderect(rect_caracol):
            # Llama a procesar_golpe. 
            if not procesar_golpe(miguel, INICIO_MIGUEL, caracol_asesino): 
                #da el aviso  la funcion procesar golpe para decir que heos perdido
                return False

        # Evaluacion de victoria: si Miguel toca la meta, el nivel termina con éxito devolviendo True
        if rect_miguel.colliderect(rect_meta): 
            return True

        #dibujamo los objetos en la pantalla
        #ca se debe dibujar en orden, ya que si se dibuja antes el personaje y despues el mundo, mundo se superpondra al personaje
        #ocultando el personaj
        world.draw(pantalla)
        miguel.draw(pantalla); caracol_asesino.draw(pantalla); primer_nivel.draw(pantalla)
        objeto1.draw(pantalla); objeto2.draw(pantalla); objeto3.draw(pantalla)
        objeto4.draw(pantalla); objeto5.draw(pantalla); objeto6.draw(pantalla)
        objeto7.draw(pantalla); objeto8.draw(pantalla); objeto9.draw(pantalla)
        #dibujamos las vidas para que las vean
        dibujar_vidas()
        #actualizamos la pantalla
        pygame.display.flip()


#funcion del nivel 2
#repetimos el proceso con algunas exepciones
def nivel2():
    global VIDAS_GLOBALES, tiempo_invulnerable
    clock = pygame.time.Clock()
    world = Mundo()

    #creamos nuevamente otro punto de inicio
    INICIO_MIGUEL  = (50, screen_y // 2)
    INICIO_CARACOL = (250, 360)

    miguel          = Personaje(*INICIO_MIGUEL)
    caracol_asesino = Caracol(*INICIO_CARACOL)
    meta            = meta2(50, 100)#cambiamos la posicion de la meta 2

    objeto01 = Cuadro_01(0,0);    objeto02 = Cuadro_02(35,0)
    objeto03 = Cuadro_03(730,80); objeto04 = Cuadro_04(35,530)
    objeto05 = Cuadro_001(35,145);objeto06 = Cuadro_002(35,485)
    objeto07 = Cuadro_003(500,210)
    objeto08 = Cuadro_0001(300,280); objeto09 = Cuadro_0002(190,280)
    objeto010= Cuadro_0003(190,320); objeto011= Cuadro_0004(350,280)
    objeto012= Cuadro_extra(460,425)

    #colocamos unas variables para ubicar el objeto fuego para que el personaje las esquive
    posicion_x = 550
    posicion_y = 140

    #veremos de simplificar la generacion de objetos
    #para que se dupliquen y se vayan creando copias por cada dupe ocupas un for
    fuegos_derecha = []#creamos un lista para que se vayan guardando los objetos
    for i in range(3):#en un rango de 3
        #posicionamos en x fija pero con un y cambiante para que se creen hacia abajo y luego los agregamos
        fuegos_derecha.append(Fuegito_hacia_la_derecha(550, posicion_y))
        posicion_y += 130#cambiamos el valor a usar

    fuegos_arriba = []
    for i in range(6):#en un rango de 6
        fuegos_arriba.append(Fuegito_hacia_arriba(posicion_x, 140))#hacemos lo mismo pero en x para qe sea hacia la izquierda
        posicion_x -= 80

    # solo los bloques estáticos para colisión del caracol y del personaje con los muros
    objetos_nivel2 = [objeto01,objeto02,objeto03,objeto04,
                      objeto05,objeto06,objeto07,
                      objeto08,objeto09,objeto010,objeto011,objeto012]

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  
            miguel.move(-5,0,objetos_nivel2)
        if keys[pygame.K_RIGHT]: 
            miguel.move(5,0,objetos_nivel2)
        if keys[pygame.K_UP]:    
            miguel.move(0,-5,objetos_nivel2)
        if keys[pygame.K_DOWN]:  
            miguel.move(0,5,objetos_nivel2)

        caracol_asesino.perseguir_con_colision(miguel.x, miguel.y, objetos_nivel2, velocidad=3.5)

        #llamamos a sus funciones actualizar para cada fuego que se cree en las listas
        for f in fuegos_derecha: 
            f.actualizar()
        for f in fuegos_arriba:  
            f.actualizar()

        rect_miguel  = pygame.Rect(miguel.x, miguel.y, miguel.size, miguel.size)
        rect_caracol = pygame.Rect(caracol_asesino.x, caracol_asesino.y, caracol_asesino.size, caracol_asesino.size)
        rect_meta    = pygame.Rect(meta.x, meta.y, meta.size, meta.size)

        if rect_miguel.colliderect(rect_caracol):
            if not procesar_golpe(miguel, INICIO_MIGUEL, caracol_asesino): 
                return False

        #ocupamos otro for para simplificar las colisiones de los fuegos
        for f in fuegos_derecha:
            rect_f = pygame.Rect(f.x, f.y, f.size, f.size)
            #si esta en el estado de moverse y choca con el personaje:
            if f.estado == "moverse" and rect_miguel.colliderect(rect_f):#practicamente lo mismo que con el caracol pero con el fuego
                #llama a la funcion procesal golpe
                if not procesar_golpe(miguel, INICIO_MIGUEL, caracol_asesino): 
                    return False
        #hacemos lo mismo con el fuego que va hacia arriba
        for f in fuegos_arriba:
            rect_f = pygame.Rect(f.x, f.y, f.size, f.size)
            if f.estado == "moverse" and rect_miguel.colliderect(rect_f):
                if not procesar_golpe(miguel, INICIO_MIGUEL, caracol_asesino): 
                    return False

        if rect_miguel.colliderect(rect_meta): return True

        world.draw(pantalla)
        miguel.draw(pantalla); caracol_asesino.draw(pantalla); meta.draw(pantalla)

        #se debe dibujar el fuego antes que los objetos para que no se dibujen enfrente de los muros
        #bucle for para que cada fuego se dibuje en la pantalla
        for f in fuegos_derecha: 
            f.draw(pantalla)
        for f in fuegos_arriba:  
            f.draw(pantalla)

        objeto01.draw(pantalla); objeto02.draw(pantalla); objeto03.draw(pantalla)
        objeto04.draw(pantalla); objeto05.draw(pantalla); objeto06.draw(pantalla)
        objeto07.draw(pantalla); objeto08.draw(pantalla); objeto09.draw(pantalla)
        objeto010.draw(pantalla); objeto011.draw(pantalla); objeto012.draw(pantalla)
        dibujar_vidas()
        pygame.display.flip()


#creamos la funcin para el nivel 3
#repetimos el proceso con nuevas variables y unos cambios
def nivel3():
    global VIDAS_GLOBALES, tiempo_invulnerable
    clock = pygame.time.Clock()
    world = Mundo()

    #volvemos a cambiar la posicion del persoanaje y el caracol
    INICIO_MIGUEL  = (100, 200)
    INICIO_CARACOL = (100, 425)

    #aparte de llamar a las variables de las posiciones iniciales le cambiamos la imagen con image_path
    miguel          = Personaje(*INICIO_MIGUEL, imagen_path=ruta_goal)#imagen de la meta para el personaje
    caracol_asesino = Caracol(*INICIO_CARACOL,  imagen_path=ruta_character)#imagen del personaje para el caracol
    meta = meta3_escape(700, 500, imagen_path=ruta_snail)#imagen del caracol para la meta

    objeto_1 = cuadro100(0, 0)
    objeto_2 = cuadro200(70, 0)
    objeto_3 = cuadro300(70, 510)
    objeto_7 = cuadro700(185, 260)
    beta = cuadrobeta(245, 190)
    objeto_4 = cuadro400(360, 560)
    objeto_5 = cuadro500(360, 0)
    gamma = cuadrogamma(560, 450)
    objeto_6 = cuadro600(460, 100)
    dseta = cuadrodseta(630, 550)
    delta = cuadrodelta(560, 0)
    eta = cuadroeta(750, 15)

    objetos_nivel3 = [objeto_1, objeto_2, objeto_3, objeto_7, beta,
                      objeto_4, objeto_5, gamma, dseta,
                      objeto_6, delta, eta]

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  
            miguel.move(-5,0, objetos_nivel3)
        if keys[pygame.K_RIGHT]: 
            miguel.move(5,0, objetos_nivel3)
        if keys[pygame.K_UP]:    
            miguel.move(0,-5, objetos_nivel3)
        if keys[pygame.K_DOWN]:  
            miguel.move(0,5, objetos_nivel3)

        #le vamos cambiando la velocidad al caracol para que vaya mas rapido
        caracol_asesino.perseguir_nivel3(miguel.x, miguel.y, objetos_nivel3, velocidad=4.5)

        #llamamos a la funcion de la meta para que se mueva al cumplir la condicion
        meta.actualizar(miguel.y)

        #creamos los cuadros de colisiones de los objetos
        rect_miguel  = pygame.Rect(miguel.x, miguel.y, miguel.size, miguel.size)
        rect_caracol = pygame.Rect(caracol_asesino.x, caracol_asesino.y, caracol_asesino.size, caracol_asesino.size)

        #colision entre el personaje y el caracol
        if rect_miguel.colliderect(rect_caracol):
            if not procesar_golpe(miguel, INICIO_MIGUEL, caracol_asesino): 
                return False

        #si miguel llega a estas coordenadas avanza al siguiente bucle
        if miguel.x >= 750 and miguel.y >= 450:
            return True

        world.draw(pantalla)
        miguel.draw(pantalla); caracol_asesino.draw(pantalla); meta.draw(pantalla)
        objeto_1.draw(pantalla); objeto_2.draw(pantalla); objeto_3.draw(pantalla); objeto_7.draw(pantalla); beta.draw(pantalla)
        objeto_4.draw(pantalla); objeto_5.draw(pantalla); gamma.draw(pantalla); dseta.draw(pantalla)
        objeto_6.draw(pantalla); delta.draw(pantalla); eta.draw(pantalla)
        dibujar_vidas()
        pygame.display.flip()

#nivel 3.1
#repetimos el proceso con distintos elementos
def nivel3_1():
    global VIDAS_GLOBALES, tiempo_invulnerable
    clock = pygame.time.Clock()
    world = Mundo()

    #en este nivel solo aparecera el personaje
    INICIO_MIGUEL  = (75, 280)
    #le ponemos la imagen del caracol al personaje
    miguel = Personaje(*INICIO_MIGUEL, imagen_path=ruta_snail)
    # meta final del nivel 3_1
    meta_final = meta3(700, 280)#aca no le cambiamos imagen

    sidea = sideon(0, 0)
    sideb = sidedown(0, 400)
    bloque = bloque_objeto(0, 0)
    bloque_segundo = bloque_2(780, 0)

    #usamos la misma mecanica para los fuegos que la nivel 2
    posicion_fx = 175
    fuegos_arriba_31 = []
    for i in range(7):#en un rango de 7
        #le cambiamos la velocidad de aparecion y le aumentamos la velocidad
        fuegos_arriba_31.append(Fuegito_hacia_arriba(posicion_fx, 400, tiempo_espera_ms=2500, velocidad = 7))
        #cada uno aumentara en 75 hasta 7(en x/horizontal a la derecha)
        posicion_fx += 75

    nivel3_1_objetos = [sidea, sideb]

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  
            #le cambiamos los controles para engañar al jugador
            #si presiona izquierda ira hacia arriba
            miguel.move(0, -5, nivel3_1_objetos)
        if keys[pygame.K_RIGHT]: 
            #si presiona derecha ira hacia abajo
            miguel.move(0, 5, nivel3_1_objetos)
        if keys[pygame.K_UP]:  
            #si presiona arriba ira hacia la izquierda  
            miguel.move(-5, 0, nivel3_1_objetos)
        if keys[pygame.K_DOWN]:  
            #si presiona hacia abajo ira a la derecha
            miguel.move(5, 0, nivel3_1_objetos)

        #para cada fuego en la lista de fuegos se va a activar el comando actualizar
        for f in fuegos_arriba_31: 
            f.actualizar()

        rect_miguel = pygame.Rect(miguel.x, miguel.y, miguel.size, miguel.size)
        rect_meta   = pygame.Rect(meta_final.x, meta_final.y, meta_final.size, meta_final.size)

        
        for f in fuegos_arriba_31:#a cada fuego en la lista se le pone la hitbox
            rect_f = pygame.Rect(f.x, f.y, f.size, f.size)
            #para que el personaje reciba daño el fuego debe moverse y debe chocar con el personaje
            if f.estado == "moverse" and rect_miguel.colliderect(rect_f):
                #llama a la funcion procesal golpe
                if not procesar_golpe(miguel, INICIO_MIGUEL):#como en este nivel no hay caracol solo colocamos estos paremetros
                    return False


        # al tocar la meta pasa a agradecimientos
        if rect_miguel.colliderect(rect_meta): 
            return True

        world.draw(pantalla)
        miguel.draw(pantalla)
        meta_final.draw(pantalla)
        for f in fuegos_arriba_31: 
            f.draw(pantalla)
        sidea.draw(pantalla)
        sideb.draw(pantalla)
        bloque.draw(pantalla)
        bloque_segundo.draw(pantalla)
        dibujar_vidas()

        pygame.display.flip()

#bucle de agradecimientos y muestra de los integrantes
def agradecimientos():
    # los textos arrancan fuera de pantalla y bajan hasta su posición final
    # donde termina el primer elemento
    pos_final_base = 80#El punto de partida en el eje Y donde se dibujará el título Integrantes en la pantalla.
    velocidad_bajada = 3#definimos la velocidad con la que bajara

    # posición de todo el bloque
    offset_y = -500#variable para hacer un empuje hacia arriba.
    destino_y = 0#hacemos una variable para que el desfase llegue a 0 para que el texto quede en su posición original.

    # se activa solo cuando el texto ya bajó
    esperando_input = False 

    while True:
        pantalla.fill((30,30,60))

        #si la variable donde se ubican (offset_y) es menor que el destino que es a donde el texto ira
        if offset_y < destino_y:#esto se reproduce hasta sean iguales
            offset_y += velocidad_bajada#sumamos a su posicion en y para que vaya bajando
            #si la posicion es mayor al destino osea esta mas abajo
            if offset_y > destino_y: 
                offset_y = destino_y#obliga a que ambos sean iguales
        else:
            esperando_input = True
        #dibujamos en la pantalla
        titulo_surf = fuente_titulo.render("Fin del juego:", True, (200,200,200))
        pantalla.blit(titulo_surf, (screen_x//2 - titulo_surf.get_width()//2, pos_final_base + offset_y))
        felic = fuente_instrucciones.render("Juego completado Bv", True, (200,200,200))
        inst1 = fuente_instrucciones.render("ESPACIO para volver a jugar", True, (200,200,200))
        inst2 = fuente_instrucciones.render("ESC para salir", True, (200,200,200))
        pantalla.blit(felic, (screen_x//2 - felic.get_width()//2, pos_final_base + 310 + offset_y))
        pantalla.blit(inst1, (screen_x//2 - inst1.get_width()//2, pos_final_base + 360 + offset_y))
        pantalla.blit(inst2, (screen_x//2 - inst2.get_width()//2, pos_final_base + 400 + offset_y))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN and esperando_input:#si presionamos alguna tecla y termino de bajar
                if evento.key == pygame.K_SPACE:#regresamos al menu
                    return
                if evento.key == pygame.K_ESCAPE: #cerramos todo
                    pygame.quit(); sys.exit()

        pygame.time.Clock().tick(60)

#este es el inicio, y al mismo tiempo el fin del juego, todo el juego comienza al iniciar esta funcion
#bucle de conector, conecta todo con esto
#si se abre la terminal ejecuta
if __name__ == "__main__":# Esta condicion asegura que el juego solo arranque si ejecutamos este archivo directamente
    while True:
        #aca ira llamando a las funciones que usamos
        pantalla_inicio()#todo lo que este despues de aca, si se pierde regresara aca
        VIDAS_GLOBALES = 3
        tiempo_invulnerable = 0
        
        if not main():#al ser un true, no sigue con el continuo y va al siguiente if/es un caso de if sin else
            continue#con continue nos saltamos todo si perdemos y nos manda a la primera lin
        if not nivel2():  
            continue
        if not nivel3():  
            continue
        if not nivel3_1():  
            continue
        agradecimientos()