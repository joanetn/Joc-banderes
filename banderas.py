import os
import random
import sys
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel

pygame.init()

AZUL_OSCURO = (16, 26, 52)
BLANCO = (255, 255, 255)
CIAN = (0, 255, 255)
ROJO = (255, 0, 0)

ANCHO, ALTO = 600, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de Banderas")

manager = pygame_gui.UIManager((ANCHO, ALTO))

fuente = pygame.font.Font(None, 32)

DIRECTORIO_BANDERAS = "banderas"
banderas = os.listdir(DIRECTORIO_BANDERAS)
bandera_actual = None
nombre_bandera_actual = ""

partes_reveladas = set()

input_text = ""
color = CIAN
rectangulo_entrada = pygame.Rect(200, 10, 500, 35)
activa = False

banderas_resueltas = 0
racha_banderas_resueltas = 0

temporizador_notificacion = 0
etiqueta_notificacion = None

def cargar_bandera():
    global bandera_actual, partes_reveladas, nombre_bandera_actual
    bandera_path = os.path.join(DIRECTORIO_BANDERAS, random.choice(banderas))
    try:
        bandera_actual = pygame.image.load(bandera_path)
        if not isinstance(bandera_actual, pygame.Surface):
            raise ValueError("La imagen de la bandera no se cargó correctamente.")
        bandera_actual = pygame.transform.scale(bandera_actual, (bandera_actual.get_width(), bandera_actual.get_height()))
        nombre_bandera_actual = os.path.splitext(os.path.basename(bandera_path))[0].lower()
        partes_reveladas = {random.randint(0, 5) for _ in range(1)}
    except Exception as e:
        print("Error al cargar la bandera:", e)

def dividir_bandera(bandera):
    partes = []
    ancho_parte = bandera.get_width() // 3
    alto_parte = bandera.get_height() // 2
    for fila in range(2):
        for columna in range(3):
            parte = bandera.subsurface((columna * ancho_parte, fila * alto_parte, ancho_parte, alto_parte))
            partes.append(parte)
    return partes

def barra(evento):
    global input_text, activa, color
    if evento.type == pygame.MOUSEBUTTONDOWN:
        if rectangulo_entrada.collidepoint(evento.pos):
            activa = not activa
        else:
            activa = False
        color = CIAN if activa else BLANCO
    if evento.type == pygame.KEYDOWN:
        if activa:
            if evento.key == pygame.K_RETURN:
                verificar_pais(input_text.lower())
                input_text = ""
            elif evento.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += evento.unicode

def filtrar_paises(texto):
    return [bandera.split('.')[0] for bandera in banderas if bandera.split('.')[0].lower().startswith(texto)]

def verificar_pais(pais_ingresado):
    global partes_reveladas, banderas_resueltas, temporizador_notificacion, racha_banderas_resueltas
    if bandera_actual is not None:
        if pais_ingresado == nombre_bandera_actual:
            partes_reveladas = set(range(6))
            banderas_resueltas += 1
            racha_banderas_resueltas += 1
            actualizar_marcador()
            mostrar_notificacion("¡Has acertado!", color=BLANCO)
            cargar_bandera()
        else:
            if len(partes_reveladas) == 6:
                resetear_banderas_marcador()
                cargar_bandera()
            partes_reveladas.add(random.choice([p for p in range(6) if p not in partes_reveladas]))
            mostrar_notificacion("¡Esa no es!", color=ROJO)

def mostrar_notificacion(mensaje, color):
    global etiqueta_notificacion, temporizador_notificacion
    etiqueta_notificacion = UILabel(relative_rect=pygame.Rect(200, rectangulo_entrada.y + rectangulo_entrada.height + 10, 200, 30),
                                  text=mensaje, manager=manager, object_id="#etiqueta_notificacion")
    temporizador_notificacion = 200

def cargar_nueva_bandera():
    cargar_bandera()

def actualizar_marcador():
    global banderas_resueltas_text, racha_banderas_resueltas
    banderas_resueltas_text.set_text(f"Racha de aciertos: {racha_banderas_resueltas} | Banderas acertadas: {banderas_resueltas}")

def resetear_banderas_marcador():
    global racha_banderas_resueltas
    racha_banderas_resueltas = 0
    actualizar_marcador()

def main():
    cargar_bandera()

    margen_vertical = (ALTO - (bandera_actual.get_height() + 100)) // 2
    rectangulo_entrada.y += margen_vertical

    margen_vertical_imagen = (ALTO - bandera_actual.get_height()) // 2

    global banderas_resueltas_text
    banderas_resueltas_text = UILabel(relative_rect=pygame.Rect((ANCHO - 400) // 2, ALTO - 140, 400, 30),
                                      text=f"Racha de aciertos: {racha_banderas_resueltas} | Banderas acertadas: {banderas_resueltas}",
                                      manager=manager, object_id="#banderas_resueltas_text")

    while True:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            barra(evento)

        pantalla.fill(AZUL_OSCURO)

        if bandera_actual is not None:
            partes_bandera = dividir_bandera(bandera_actual)
            for i, parte in enumerate(partes_bandera):
                if i in partes_reveladas:
                    posicion_x = (ANCHO - bandera_actual.get_width()) // 2
                    posicion_y = (i // 3) * parte.get_height() + margen_vertical_imagen
                    pantalla.blit(parte, (posicion_x + (i % 3) * parte.get_width(), posicion_y))

        superficie_texto = fuente.render(input_text, True, color)
        ancho = max(200, superficie_texto.get_width() + 10)
        rectangulo_entrada.w = ancho
        pygame.draw.rect(pantalla, color, rectangulo_entrada, 2)
        pantalla.blit(superficie_texto, (rectangulo_entrada.x + 5, rectangulo_entrada.y + 5))
        pygame.draw.line(pantalla, color, (rectangulo_entrada.x + ancho, rectangulo_entrada.y), (rectangulo_entrada.x + ancho, rectangulo_entrada.y + rectangulo_entrada.height), 2)

        paises_filtrados = filtrar_paises(input_text.lower())

        if activa:
            y = rectangulo_entrada.y - 30
            for i, pais in enumerate(paises_filtrados):
                superficie_texto = fuente.render(pais, True, BLANCO)
                pantalla.blit(superficie_texto, (rectangulo_entrada.x + 5, y - i * 30))

        manager.update(0.01)
        manager.draw_ui(pantalla)

        global temporizador_notificacion, etiqueta_notificacion
        if temporizador_notificacion > 0:
            temporizador_notificacion -= 1
            if temporizador_notificacion == 0:
                if etiqueta_notificacion is not None:
                    etiqueta_notificacion.kill()

        pygame.display.flip()

if __name__ == "__main__":
    main()
