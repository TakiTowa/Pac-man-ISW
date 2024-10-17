import pygame
import sys
import json
from PyQt5 import QtWidgets, QtGui

pygame.init()

# Inicializar joystick
pygame.joystick.init()

# Colores
NEGRO = (0, 0, 0)
AMARILLO = (255, 255, 0)
AZUL = (0, 0, 255)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
ROSADO = (255, 105, 180)
CIAN = (0, 255, 255)

# Dimensiones de la ventana
ANCHO_VENTANA = 1000
ALTO_VENTANA = 700
ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Pacman con Laberinto, Puntos y Fantasmas")

# Reloj para controlar la velocidad de actualización
reloj = pygame.time.Clock()

# Tamaño de cada bloque en el laberinto
TAM_BLOQUE = 40

# Laberinto (1 = muro, 0 = camino)
laberinto = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Crear una lista de puntos en posiciones iniciales (matriz paralela a laberinto)
puntos = [[1 if laberinto[fila][columna] == 0 else 0 for columna in range(len(laberinto[0]))] for fila in range(len(laberinto))]

# Posición inicial del Pacman
x_pacman = TAM_BLOQUE + TAM_BLOQUE // 2
y_pacman = TAM_BLOQUE + TAM_BLOQUE // 2
velocidad = 5
radio_pacman = 15

# Contador de puntos
puntos_recolectados = 0

# Direcciones del Pacman
direccion_x = 0
direccion_y = 0

# Fuente para mostrar texto
fuente = pygame.font.Font(None, 36)

# Clase para los fantasmas
class Fantasma:
    def __init__(self, x, y, color, velocidad):
        self.x = x
        self.y = y
        self.color = color
        self.velocidad = velocidad
        self.radio = 15

    def mover(self, pacman_x, pacman_y):
        # Movimiento sencillo hacia Pacman
        if self.x < pacman_x:
            nueva_direccion_x = self.velocidad
        elif self.x > pacman_x:
            nueva_direccion_x = -self.velocidad
        else:
            nueva_direccion_x = 0

        if self.y < pacman_y:
            nueva_direccion_y = self.velocidad
        elif self.y > pacman_y:
            nueva_direccion_y = -self.velocidad
        else:
            nueva_direccion_y = 0

        # Proponer nuevas posiciones
        propuesta_x = self.x + nueva_direccion_x
        propuesta_y = self.y + nueva_direccion_y

        # Verificar colisiones con el laberinto
        if not colision_laberinto(propuesta_x, self.y):
            self.x = propuesta_x
        if not colision_laberinto(self.x, propuesta_y):
            self.y = propuesta_y

    def dibujar(self, ventana):
        pygame.draw.circle(ventana, self.color, (int(self.x), int(self.y)), self.radio)

# Inicializar fantasmas con diferentes colores y posiciones
fantasmas = [
    Fantasma(TAM_BLOQUE * 13 + TAM_BLOQUE // 2, TAM_BLOQUE * 3 + TAM_BLOQUE // 2, ROJO, 3),
    Fantasma(TAM_BLOQUE * 13 + TAM_BLOQUE // 2, TAM_BLOQUE * 6 + TAM_BLOQUE // 2, ROSADO, 2),
    Fantasma(TAM_BLOQUE * 13 + TAM_BLOQUE // 2, TAM_BLOQUE * 5 + TAM_BLOQUE // 2, CIAN, 2.5)
]

# Función para dibujar el laberinto
def dibujar_laberinto():
    for fila in range(len(laberinto)):
        for columna in range(len(laberinto[fila])):
            if laberinto[fila][columna] == 1:
                pygame.draw.rect(ventana, AZUL, (columna * TAM_BLOQUE, fila * TAM_BLOQUE, TAM_BLOQUE, TAM_BLOQUE))

# Función para dibujar los puntos
def dibujar_puntos():
    for fila in range(len(puntos)):
        for columna in range(len(puntos[fila])):
            if puntos[fila][columna] == 1:
                pygame.draw.circle(ventana, BLANCO, (columna * TAM_BLOQUE + TAM_BLOQUE // 2, fila * TAM_BLOQUE + TAM_BLOQUE // 2), 5)

# Función para dibujar al Pacman
def dibujar_pacman(x, y):
    pygame.draw.circle(ventana, AMARILLO, (int(x), int(y)), radio_pacman)

# Función para comprobar colisiones con el laberinto
def colision_laberinto(x, y):
    columna = int(x) // TAM_BLOQUE
    fila = int(y) // TAM_BLOQUE
    if fila < 0 or fila >= len(laberinto) or columna < 0 or columna >= len(laberinto[0]):
        return True
    return laberinto[fila][columna] == 1

# Función para comprobar la colisión con puntos
def colision_punto(x, y):
    global puntos_recolectados
    columna = int(x) // TAM_BLOQUE
    fila = int(y) // TAM_BLOQUE
    if 0 <= fila < len(puntos) and 0 <= columna < len(puntos[0]) and puntos[fila][columna] == 1:
        puntos[fila][columna] = 0
        puntos_recolectados += 1

# Función para mostrar puntaje
def score_display(score):
    value = fuente.render("Puntos: " + str(score), True, BLANCO)
    ventana.blit(value, [10, 10])

# Guardar puntaje en JSON
def save_score(name, score):
    try:
        with open("score.json", "r") as file:
            data = json.load(file)
        if 'scores' not in data:
            data['scores'] = []
        new_data = {
            "name": name,
            "score": score
        }
        data['scores'].append(new_data)
        with open("score.json", 'w') as file:
            json.dump(data, file, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"scores": []}
        new_data = {
            "name": name,
            "score": score
        }
        data['scores'].append(new_data)
        with open("score.json", 'w') as file:
            json.dump(data, file, indent=4)

# Obtener las puntuaciones más altas desde JSON
def get_high_scores():
    try:
        with open("score.json", "r") as file:
            data = json.load(file)
            return data.get('scores', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Mostrar las puntuaciones más altas
def show_scores(scores):
    x_offset = ANCHO_VENTANA // 2 + 140  # Mueve la tabla hacia la derecha
    y_offset = 80  # Mantiene el desplazamiento vertical
    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    for index, entry in enumerate(sorted_scores):
        if index > 9:
            break
        name = entry["name"]
        score = entry["score"]
        score_text = f"{index + 1}. {name}: {score}"
        score_surface = fuente.render(score_text, True, BLANCO)
        ventana.blit(score_surface, [x_offset, y_offset + index * 30])

# Función para obtener el nombre del jugador
def get_high_score():
    app = QtWidgets.QApplication(sys.argv)
    name, ok = QtWidgets.QInputDialog.getText(None, "Puntaje:", "Escribe tu nombre", QtWidgets.QLineEdit.Normal)
    return name if ok else None

# Reiniciar el juego
def reiniciar_juego():
    global x_pacman, y_pacman, puntos_recolectados, game_over, puntos
    x_pacman = TAM_BLOQUE + TAM_BLOQUE // 2
    y_pacman = TAM_BLOQUE + TAM_BLOQUE // 2
    puntos_recolectados = 0
    game_over = False
    puntos = [[1 if laberinto[fila][columna] == 0 else 0 for columna in range(len(laberinto[0]))] for fila in range(len(laberinto))]

# Botón de reinicio
def dibujar_boton_reinicio():
    boton_rect = pygame.Rect(ANCHO_VENTANA // 2 + 140, ALTO_VENTANA // 2 + 50, 100, 40)
    pygame.draw.rect(ventana, ROSADO, boton_rect)
    texto_boton = fuente.render("Reiniciar", True, NEGRO)
    ventana.blit(texto_boton, (boton_rect.x + 10, boton_rect.y + 5))

# Función para detectar colisión entre dos círculos
def detectar_colision(x1, y1, r1, x2, y2, r2):
    distancia = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    return distancia < (r1 + r2)

# Bucle principal del juego
# Bucle principal del juego
game_over = False
joystick = False

# Comprobar si hay joysticks conectados
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()


while True:
    # Manejar eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_over:
            # Comprobar clics en el botón de reinicio
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Botón izquierdo del ratón
                    mouse_pos = pygame.mouse.get_pos()
                    boton_rect = pygame.Rect(ANCHO_VENTANA // 2 - 50, ALTO_VENTANA // 2 + 50, 100, 40)
                    if boton_rect.collidepoint(mouse_pos):
                        reiniciar_juego()
            
            if evento.type == pygame.JOYBUTTONDOWN:
                 if evento.button == 1:  # Botón izquierdo del ratón
                    boton_rect = pygame.Rect(ANCHO_VENTANA // 2 - 50, ALTO_VENTANA // 2 + 50, 100, 40)
                    reiniciar_juego()
                    
            
            continue
        
         # Verificar si hay joystick conectado
        if joystick:
            if evento.type == pygame.JOYAXISMOTION:
                # Eje izquierdo (izquierda/derecha y arriba/abajo)
                if joystick.get_axis(0) < -0.5:  # Eje X
                    direccion_x = -velocidad
                    direccion_y = 0
                elif joystick.get_axis(0) > 0.5:  # Eje X
                    direccion_x = velocidad
                    direccion_y = 0
                elif joystick.get_axis(1) < -0.5:  # Eje Y
                    direccion_y = -velocidad
                    direccion_x = 0
                elif joystick.get_axis(1) > 0.5:  # Eje Y
                    direccion_y = velocidad
                    direccion_x = 0
                else:
                    direccion_x = 0
                    direccion_y = 0
            
            # Botones de acción (ej. cruz, cuadrado, círculo)
            if evento.type == pygame.JOYBUTTONDOWN:
                if evento.button == 0:  # Cruz (X)
                    direccion_x = -velocidad
                    direccion_y = 0
                elif evento.button == 1:  # Círculo (O)
                    direccion_x = velocidad
                    direccion_y = 0
                elif evento.button == 2:  # Cuadrado (□)
                    direccion_y = -velocidad
                    direccion_x = 0
                elif evento.button == 3:  # Triángulo (△)
                    direccion_y = velocidad
                    direccion_x = 0

        # Detectar las teclas presionadas
        if evento.type == pygame.KEYDOWN and not game_over:
            if evento.key == pygame.K_LEFT:
                direccion_x = -velocidad
                direccion_y = 0
            elif evento.key == pygame.K_RIGHT:
                direccion_x = velocidad
                direccion_y = 0
            elif evento.key == pygame.K_UP:
                direccion_y = -velocidad
                direccion_x = 0
            elif evento.key == pygame.K_DOWN:
                direccion_y = velocidad
                direccion_x = 0

        # Detectar cuando se sueltan las teclas
        if evento.type == pygame.KEYUP and not game_over:
            if evento.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                direccion_x = 0
                direccion_y = 0

    if not game_over:
        nueva_x_pacman = x_pacman + direccion_x
        nueva_y_pacman = y_pacman + direccion_y

        if not colision_laberinto(nueva_x_pacman - radio_pacman, y_pacman):
            x_pacman = nueva_x_pacman
        if not colision_laberinto(x_pacman, nueva_y_pacman - radio_pacman):
            y_pacman = nueva_y_pacman

        colision_punto(x_pacman, y_pacman)

        # Mover y dibujar fantasmas
        for fantasma in fantasmas:
            fantasma.mover(x_pacman, y_pacman)

        for fantasma in fantasmas:
            if detectar_colision(x_pacman, y_pacman, radio_pacman, fantasma.x, fantasma.y, fantasma.radio):
                game_over = True
                name = get_high_score()
                if name:
                    save_score(name, puntos_recolectados)
                break

    # Dibujar todo
    ventana.fill(NEGRO)
    dibujar_laberinto()
    dibujar_puntos()
    dibujar_pacman(x_pacman, y_pacman)

    if not game_over:
        for fantasma in fantasmas:
            fantasma.dibujar(ventana)
    else:
        dibujar_boton_reinicio()
        # Mostrar las puntuaciones más altas
        scores = get_high_scores()
        show_scores(scores)

    # Mostrar puntaje
    score_display(puntos_recolectados)

    # Actualizar pantalla
    pygame.display.flip()
    reloj.tick(30)
