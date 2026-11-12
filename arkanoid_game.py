"""Plantilla del juego Arkanoid para el hito M2.

Completa los métodos marcados con TODO respetando las anotaciones de tipo y la
estructura de la clase. El objetivo es construir un prototipo jugable usando
pygame que cargue bloques desde un fichero de nivel basado en caracteres.
"""
from arkanoid_core import *
# --------------------------------------------------------------------- #
# Métodos a completar por el alumnado
# --------------------------------------------------------------------- #

@arkanoid_method

def cargar_nivel(self) -> list[str]:
    """Lee el fichero de nivel y devuelve la cuadrícula como lista de filas."""
    # - Comprueba que `self.level_path` existe y es fichero.
    if self.level_path is None or not self.level_path.is_file():
        raise FileNotFoundError(f"El fichero de nivel {self.level_path} no existe.")
    
    # - Lee su contenido, filtra líneas vacías y valida que todas tienen el mismo ancho.
    lineas = []
    for i in self.level_path.read_text().splitlines():
        if i.strip(): # Revisa si la linea tiene contenido
            lineas.append(i)
    
    ancho = len(lineas[0])
    for i in lineas:
        if len(i) != ancho:
            raise ValueError("No tienen el mismo ancho")

    # - Guarda el resultado en `self.layout` y devuélvelo.
    self.layout = lineas
    return lineas

@arkanoid_method
def preparar_entidades(self) -> None:
    """Posiciona paleta y bola, y reinicia puntuación y vidas."""
    # - Ajusta el tamaño de `self.paddle` y céntrala usando `midbottom`.
    self.paddle = self.crear_rect(0, 0, 120, 18)
    self.paddle.midbottom = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 25)

    # - Reinicia `self.score`, `self.lives` y `self.end_message`.
    self.score = 0
    self.lives = 3
    self.end_message = ""
    
    # - Llama a `self.reiniciar_bola()` para colocar la bola sobre la paleta.
    self.reiniciar_bola()

@arkanoid_method
def crear_bloques(self) -> None:
    """Genera los rectángulos de los bloques en base a la cuadrícula."""
    # - Limpia `self.blocks`, `self.block_colors` y `self.block_symbols`.
    self.blocks = []
    self.block_colors = []
    self.block_symbols = []

    # - Recorre `self.layout` para detectar símbolos de bloque.
    # - Usa `self.calcular_posicion_bloque` y rellena las listas paralelas.
    for f in range(len(self.layout)):
        for c in range(len(self.layout[f])):
            simbolo = self.layout[f][c]
            if simbolo in self.BLOCK_COLORS:
                self.block_symbols.append(simbolo)
                self.block_colors.append(self.BLOCK_COLORS[simbolo])
                self.blocks.append(self.calcular_posicion_bloque(f, c))

@arkanoid_method
def procesar_input(self) -> None:
    """Gestiona la entrada de teclado para mover la paleta."""
    # - Obtén el estado de teclas con `self.obtener_estado_teclas()`.
    teclas = self.obtener_estado_teclas()

    # - Desplaza la paleta con `self.PADDLE_SPEED` si se pulsan las teclas izquierda/derecha.
    izquierda = teclas[self.KEY_LEFT] or teclas[self.KEY_A]
    derecha = teclas[self.KEY_RIGHT] or teclas[self.KEY_D]

    desplazamiento = (int(bool(derecha)) - int(bool(izquierda))) * self.PADDLE_SPEED
    
    # - Limita la posición para que no salga de la pantalla.
    self.paddle.x += desplazamiento
    self.paddle.left = max(0, self.paddle.left)
    self.paddle.right = min(self.SCREEN_WIDTH, self.paddle.right)

@arkanoid_method
def actualizar_bola(self) -> None:
    """Actualiza la posición de la bola y resuelve colisiones."""
    # - Suma `self.ball_velocity` a `self.ball_pos` y genera `ball_rect` con `self.obtener_rect_bola()`.
    self.ball_pos += self.ball_velocity
    ball_rect = self.obtener_rect_bola()

    # - Gestiona rebotes con paredes, paleta y bloques, modificando velocidad y puntuación.
    
    # Rebote con techo
    if ball_rect.top <= 0:
        # Evitar colision infinita
        ball_rect.top = 0

        self.ball_velocity.y *= -1

    # Rebote con paredes izquierda y derecha
    if ball_rect.left <= 0:
        # Evitar colision infinita
        ball_rect.left = 0
        
        self.ball_velocity.x *= -1
    elif ball_rect.right >= self.SCREEN_WIDTH:
        # Evitar colision infinita
        ball_rect.right = self.SCREEN_WIDTH
        
        self.ball_velocity.x *= -1
    
    # Rebote con paddle (paleta)
    if ball_rect.colliderect(self.paddle) and self.ball_velocity.y > 0:
        desplazamiento = (self.ball_pos.x - self.paddle.centerx) / (self.paddle.width / 2)
        desplazamiento = max(-1.0, min(1.0, desplazamiento))

        self.ball_velocity = Vector2(desplazamiento, -1).normalize() * self.BALL_SPEED
        self.ball_pos.y = self.paddle.top - self.BALL_RADIUS

    # Colisión con bloques
    for i in range(len(self.blocks)):
        block = self.blocks[i]
        if ball_rect.colliderect(block):
            # > El solapamiento lo he hecho con ayuda de IA
            # 1. Calcular el solapamiento en ambos ejes antes de borrar el bloque
            overlap_x = min(ball_rect.right, block.right) - max(ball_rect.left, block.left)
            overlap_y = min(ball_rect.bottom, block.bottom) - max(ball_rect.top, block.top)

            # 2. Invertir velocidad y corregir posición según el eje de impacto
            if overlap_x < overlap_y:
                self.ball_velocity.x *= -1
                if ball_rect.centerx < block.centerx:
                    ball_rect.right = block.left
                else:
                    ball_rect.left = block.right
            else:
                self.ball_velocity.y *= -1
                if ball_rect.centery < block.centery:
                    ball_rect.bottom = block.top
                else:
                    ball_rect.top = block.bottom

            self.blocks.pop(i)
            self.block_colors.pop(i)
            simbolo = self.block_symbols.pop(i)

            puntos = self.BLOCK_POINTS.get(simbolo, 0)
            self.score += puntos

            if len(self.blocks) == 1:
                self.BALL_SPEED *= 2
                self.ball_velocity *= 2

            break
    
    # - Controla fin de nivel cuando no queden bloques y resta vidas si la bola cae.
    if ball_rect.top >= self.SCREEN_HEIGHT:
        self.lives -= 1
        if self.lives <= 0:
            self.end_message = "GAME OVER"
            self.ball_velocity = Vector2(0, 0)
        else:
            self.reiniciar_bola()

    if not self.blocks and not self.end_message:
        self.end_message = "¡GG!"
        self.score += 100

@arkanoid_method
def dibujar_escena(self) -> None:
    """Renderiza fondo, bloques, paleta, bola y HUD."""
    # - Rellena el fondo y dibuja cada bloque con `self.dibujar_rectangulo`.
    self.screen.fill(self.BACKGROUND_COLOR)
    pygame.draw.rect(self.screen, self.BACKGROUND_COLOR2, (10, 10, self.SCREEN_WIDTH - 20, self.SCREEN_HEIGHT - 20), width=3)

    for i in range(len(self.blocks)):
        self.dibujar_rectangulo(self.blocks[i], self.block_colors[i])

    # - Pinta la paleta y la bola con las utilidades proporcionadas.
    self.dibujar_rectangulo(self.paddle, self.PADDLE_COLOR)
    centro_bola = (int(self.ball_pos.x), int(self.ball_pos.y))
    self.dibujar_circulo(centro_bola, self.BALL_RADIUS, self.BALL_COLOR)
    
    # - Muestra puntuación, vidas y mensajes usando `self.dibujar_texto`.
    self.dibujar_texto(f"PUNTOS: {self.score}", (20, 10))
    self.dibujar_texto(f"VIDAS: {self.lives}", (self.SCREEN_WIDTH - 120, 10))
    if self.end_message:
        self.dibujar_texto(
            self.end_message,
            (self.SCREEN_WIDTH // 2 - 120, self.SCREEN_HEIGHT // 2),
                grande=True)

@arkanoid_method
def run(self) -> None:
    """Ejecuta el bucle principal del juego."""
    # - Inicializa recursos (`self.inicializar_pygame`, `self.cargar_nivel`, etc.).
    self.inicializar_pygame()
    self.cargar_nivel()
    self.preparar_entidades()
    self.crear_bloques()
    
    off = False
    while off == False:
        # - Procesa eventos de `self.iterar_eventos()` y llama a los métodos de actualización/dibujo.
        for evento in self.iterar_eventos():
            if evento.type == self.EVENT_QUIT:
                off = True
            elif evento.type == self.EVENT_KEYDOWN:
                if evento.key == self.KEY_ESCAPE:
                    off = True

        if not self.end_message:
            self.procesar_input()
            self.actualizar_bola()

        self.dibujar_escena()

        # - Refresca la pantalla con `self.actualizar_pantalla()` y cierra con `self.finalizar_pygame()`.
        self.actualizar_pantalla()
        self.clock.tick(self.FPS)

    self.finalizar_pygame()

def main() -> None:
    """Permite ejecutar el juego desde la línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Plantilla del hito M2: Arkanoid con pygame.",
    )
    parser.add_argument(
        "level",
        type=str,
        help="Ruta al fichero de nivel (texto con # para bloques y . para huecos).",
    )
    args = parser.parse_args()

    game = ArkanoidGame(args.level)
    game.run()

if __name__ == "__main__":
    main()

    # > test_cargar_nivel()
    # juego = ArkanoidGame("niveles/demo.txt")
    # juego = ArkanoidGame("niveles/null.txt")
    # juego = ArkanoidGame("niveles/noEquidistante.txt")
    # try:
    #     resultado = juego.cargar_nivel()
    #     print("Nivel cargado correctamente:")
    #     print(resultado)
    # except Exception as e:
    #     print(f"Error: {e}")