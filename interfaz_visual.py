import pygame
import sys
import math
from typing import List, Tuple
from simulador import SimuladorAtencion, ClienteEstado
import cv2
import numpy as np

class InterfazVisual:
    def __init__(self, simulador: SimuladorAtencion, velocidad: int = 1):
        pygame.init()
        
        # Configuración de pantalla (aumentar altura para evitar superposiciones)
        self.ANCHO = 1200
        self.ALTO = 850
        self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption("Simulador de Atención al Público")
        
        # Colores
        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.AZUL = (0, 100, 200)
        self.VERDE = (0, 200, 0)
        self.ROJO = (200, 0, 0)
        self.AMARILLO = (255, 255, 0)
        self.GRIS = (128, 128, 128)
        self.GRIS_CLARO = (200, 200, 200)
        self.NARANJA = (255, 165, 0)
        self.MORADO = (128, 0, 128)  # Color más contrastante para tiempo extra
        
        # Fuentes
        self.fuente_grande = pygame.font.Font(None, 42)
        self.fuente_mediana = pygame.font.Font(None, 28)
        self.fuente_pequena = pygame.font.Font(None, 22)
        
        self.simulador = simulador
        self.velocidad = velocidad
        self.tiempo_actual = 0
        self.indice_evento = 0
        
        # Para grabar video
        self.grabando = False
        self.frames = []
        self.frame_counter = 0  # Contador para limitar frames capturados
        
        # Posiciones de elementos
        self.setup_posiciones()
        
        self.simulador = simulador
        self.velocidad = velocidad
        self.tiempo_actual = 0
        self.indice_evento = 0
        
        # Para grabar video
        self.grabando = False
        self.frames = []
        self.frame_counter = 0  # Contador para limitar frames capturados
        
        # Posiciones de elementos
        self.setup_posiciones()
        
    def setup_posiciones(self):
        """Configura las posiciones de los elementos visuales"""
        # Área de boxes (más grande para mejor visualización)
        self.boxes_area = pygame.Rect(50, 120, 700, 220)
        self.box_width = 110
        self.box_height = 100
        
        # Área de cola (debajo de los boxes)
        self.cola_area = pygame.Rect(50, 360, 700, 140)
        
        # Área de estadísticas (parte inferior)
        self.stats_area = pygame.Rect(50, 520, 700, 300)
        
        # Área de controles (panel derecho superior) - más estrecho y corto
        self.controles_area = pygame.Rect(770, 80, 400, 280)
        
        # Área de estado (panel derecho inferior) - ajustado para no superponerse
        self.estado_area = pygame.Rect(770, 380, 400, 440)
        
    def dibujar_boxes(self):
        """Dibuja los boxes de atención"""
        # Título
        texto = self.fuente_mediana.render("BOXES DE ATENCIÓN", True, self.NEGRO)
        self.pantalla.blit(texto, (self.boxes_area.x, self.boxes_area.y - 40))  # Más separación
        
        # Calcular posiciones de boxes (máximo 6 por fila para mejor visualización)
        boxes_por_fila = min(6, self.simulador.num_boxes)
        filas = (self.simulador.num_boxes + boxes_por_fila - 1) // boxes_por_fila
        
        for i, box in enumerate(self.simulador.boxes):
            fila = i // boxes_por_fila
            col = i % boxes_por_fila
            
            x = self.boxes_area.x + col * (self.box_width + 10)
            y = self.boxes_area.y + fila * (self.box_height + 10)
            
            # Color del box según estado
            if box.ocupado:
                color = self.VERDE
                color_texto = self.BLANCO
            else:
                color = self.GRIS_CLARO
                color_texto = self.NEGRO
            
            # Dibujar box
            pygame.draw.rect(self.pantalla, color, (x, y, self.box_width, self.box_height))
            pygame.draw.rect(self.pantalla, self.NEGRO, (x, y, self.box_width, self.box_height), 2)
            
            # Número del box
            texto = self.fuente_pequena.render(f"Box {i+1}", True, color_texto)
            text_rect = texto.get_rect(center=(x + self.box_width//2, y + 20))
            self.pantalla.blit(texto, text_rect)
            
            # Cliente siendo atendido
            if box.ocupado and box.cliente_actual:
                texto = self.fuente_pequena.render(f"Cliente {box.cliente_actual.id}", True, color_texto)
                text_rect = texto.get_rect(center=(x + self.box_width//2, y + 45))
                self.pantalla.blit(texto, text_rect)
                
                # Tiempo restante aproximado
                if box.tiempo_fin_atencion:
                    tiempo_restante = max(0, box.tiempo_fin_atencion - self.tiempo_actual)
                    minutos_restantes = tiempo_restante // 60
                    texto = self.fuente_pequena.render(f"{minutos_restantes}min", True, color_texto)
                    text_rect = texto.get_rect(center=(x + self.box_width//2, y + 70))
                    self.pantalla.blit(texto, text_rect)
    
    def dibujar_cola(self):
        """Dibuja la cola de espera"""
        # Título
        texto = self.fuente_mediana.render(f"COLA DE ESPERA ({len(self.simulador.cola_espera)} clientes)", True, self.NEGRO)
        self.pantalla.blit(texto, (self.cola_area.x, self.cola_area.y - 40))  # Más separación
        
        # Dibujar clientes en cola
        cliente_size = 25
        clientes_por_fila = 7
        
        for i, cliente in enumerate(self.simulador.cola_espera[:35]):  # Mostrar máximo 35 clientes
            fila = i // clientes_por_fila
            col = i % clientes_por_fila
            
            x = self.cola_area.x + col * (cliente_size + 5)
            y = self.cola_area.y + fila * (cliente_size + 5)
            
            # Color según tiempo de espera
            tiempo_espera = self.tiempo_actual - cliente.tiempo_llegada
            if tiempo_espera > 25 * 60:  # Más de 25 minutos
                color = self.ROJO
            elif tiempo_espera > 15 * 60:  # Más de 15 minutos
                color = self.AMARILLO
            else:
                color = self.AZUL
            
            # Dibujar cliente
            pygame.draw.circle(self.pantalla, color, 
                             (x + cliente_size//2, y + cliente_size//2), 
                             cliente_size//2)
            pygame.draw.circle(self.pantalla, self.NEGRO, 
                             (x + cliente_size//2, y + cliente_size//2), 
                             cliente_size//2, 2)
            
            # ID del cliente
            if cliente_size >= 25:
                texto = self.fuente_pequena.render(str(cliente.id), True, self.BLANCO)
                text_rect = texto.get_rect(center=(x + cliente_size//2, y + cliente_size//2))
                self.pantalla.blit(texto, text_rect)
        
        # Indicar si hay más clientes
        if len(self.simulador.cola_espera) > 35:
            texto = self.fuente_pequena.render(f"...y {len(self.simulador.cola_espera) - 35} más", True, self.NEGRO)
            self.pantalla.blit(texto, (self.cola_area.x, self.cola_area.y + 180))
    
    def dibujar_estadisticas(self):
        """Dibuja las estadísticas en tiempo real"""
        pygame.draw.rect(self.pantalla, self.GRIS_CLARO, self.stats_area)
        pygame.draw.rect(self.pantalla, self.NEGRO, self.stats_area, 2)
        
        # Título con estado
        if self.tiempo_actual < self.simulador.DURACION_SIMULACION:
            titulo = "ESTADÍSTICAS EN TIEMPO REAL"
            color_titulo = self.NEGRO
        else:
            titulo = "ESTADÍSTICAS - PROCESANDO CLIENTES RESTANTES"
            color_titulo = self.MORADO  # Color más visible que naranja
            
        texto = self.fuente_mediana.render(titulo, True, color_titulo)
        self.pantalla.blit(texto, (self.stats_area.x + 10, self.stats_area.y + 10))
        
        # Tiempo actual
        horas = (self.tiempo_actual // 3600) + 8
        minutos = (self.tiempo_actual % 3600) // 60
        segundos = self.tiempo_actual % 60
        tiempo_str = f"Hora actual: {horas:02d}:{minutos:02d}:{segundos:02d}"
        texto = self.fuente_pequena.render(tiempo_str, True, self.NEGRO)
        self.pantalla.blit(texto, (self.stats_area.x + 10, self.stats_area.y + 40))
        
        # Estadísticas actuales
        stats = [
            f"Clientes que ingresaron: {len(self.simulador.todos_los_clientes)}",
            f"Clientes atendidos: {len(self.simulador.clientes_atendidos)}",
            f"Clientes abandonaron: {len(self.simulador.clientes_abandonaron)}",
            f"Clientes en cola: {len(self.simulador.cola_espera)}",
            f"Boxes ocupados: {sum(1 for box in self.simulador.boxes if box.ocupado)}",
            f"Boxes libres: {sum(1 for box in self.simulador.boxes if not box.ocupado)}"
        ]
        
        x_col1 = self.stats_area.x + 10
        x_col2 = self.stats_area.x + 250
        x_col3 = self.stats_area.x + 500
        
        for i, stat in enumerate(stats):
            y = self.stats_area.y + 70 + (i % 3) * 25
            if i < 3:
                x = x_col1
            elif i < 6:
                x = x_col2
            else:
                x = x_col3
            
            texto = self.fuente_pequena.render(stat, True, self.NEGRO)
            self.pantalla.blit(texto, (x, y))
        
        # Costos estimados
        costo_boxes = self.simulador.num_boxes * self.simulador.COSTO_BOX
        costo_perdidas = len(self.simulador.clientes_abandonaron) * self.simulador.PERDIDA_CLIENTE
        costo_total = costo_boxes + costo_perdidas
        
        y_costos = self.stats_area.y + 180
        costos = [
            f"Costo boxes: ${costo_boxes:,}",
            f"Pérdidas: ${costo_perdidas:,}",
            f"Costo total: ${costo_total:,}"
        ]
        
        for i, costo in enumerate(costos):
            texto = self.fuente_pequena.render(costo, True, self.NEGRO)
            self.pantalla.blit(texto, (self.stats_area.x + 10 + i * 200, y_costos))
    
    def dibujar_leyenda(self):
        """Dibuja la leyenda de colores"""
        leyenda_y = 50
        elementos = [
            ("Box libre", self.GRIS_CLARO),
            ("Box ocupado", self.VERDE),
            ("Cliente recién llegado", self.AZUL),
            ("Esperando 15+ min", self.AMARILLO),  # Texto más corto
            ("Esperando 25+ min", self.ROJO)      # Texto más corto
        ]
        
        for i, (texto, color) in enumerate(elementos):
            x = 50 + i * 200  # Aumentado espaciado de 180 a 200
            pygame.draw.circle(self.pantalla, color, (x, leyenda_y), 10)
            pygame.draw.circle(self.pantalla, self.NEGRO, (x, leyenda_y), 10, 2)
            
            texto_render = self.fuente_pequena.render(texto, True, self.NEGRO)
            self.pantalla.blit(texto_render, (x + 20, leyenda_y - 8))
    
    def capturar_frame(self, velocidad_animacion):
        """Captura el frame actual para el video a 15 FPS"""
        if self.grabando:
            # Calcular intervalo de captura basado en la velocidad de animación
            # Para 15 FPS constante en el video final, independiente de la velocidad de simulación
            frames_por_captura = max(1, velocidad_animacion // 15)
            
            self.frame_counter += 1
            if self.frame_counter % frames_por_captura == 0:
                try:
                    # Convertir superficie de pygame a array numpy
                    frame = pygame.surfarray.array3d(self.pantalla)
                    frame = np.rot90(frame)
                    frame = np.flipud(frame)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    self.frames.append(frame)
                    
                    # Limitar cantidad de frames en memoria (aprox 10 minutos a 15fps)
                    max_frames = 9000
                    if len(self.frames) > max_frames:
                        # Eliminar frames más antiguos
                        self.frames = self.frames[-max_frames:]
                        
                except Exception as e:
                    print(f"Error capturando frame: {e}")
                    self.grabando = False
    
    def guardar_video(self, nombre_archivo: str = "simulacion.avi"):
        """Guarda los frames capturados como video AVI"""
        if not self.frames:
            print("No hay frames para guardar")
            return
        
        try:
            print(f"Guardando video con {len(self.frames)} frames...")
            height, width, layers = self.frames[0].shape
            
            # Usar codec más compatible
            fourcc = cv2.VideoWriter.fourcc(*'MJPG')  # Motion JPEG, más compatible
            fps = 15.0  # Reducido de 30 a 15 fps para mejor rendimiento
            
            video = cv2.VideoWriter(nombre_archivo, fourcc, fps, (width, height))
            
            if not video.isOpened():
                print("Error: No se pudo abrir el escritor de video")
                return
            
            for i, frame in enumerate(self.frames):
                video.write(frame)
                # Mostrar progreso cada 100 frames
                if i % 100 == 0:
                    print(f"Procesando frame {i}/{len(self.frames)}")
            
            video.release()
            print(f"Video guardado exitosamente como {nombre_archivo}")
            
            # Limpiar frames de memoria
            self.frames.clear()
            
        except Exception as e:
            print(f"Error al guardar video: {e}")
            print("Intentando guardar con codec alternativo...")
            try:
                # Asegurar que tenemos las dimensiones
                if self.frames:
                    height, width, layers = self.frames[0].shape
                    # Intentar con codec sin compresión
                    fourcc = 0  # Sin compresión
                    video = cv2.VideoWriter(nombre_archivo.replace('.avi', '_raw.avi'), 
                                          fourcc, 15.0, (width, height))
                    
                    for frame in self.frames:
                        video.write(frame)
                    
                    video.release()
                    print(f"Video guardado sin compresión como {nombre_archivo.replace('.avi', '_raw.avi')}")
                else:
                    print("No hay frames disponibles para el codec alternativo")
                
            except Exception as e2:
                print(f"Error con codec alternativo: {e2}")
                print("La funcionalidad de video podría requerir codecs adicionales")
    
    def animar_simulacion(self, grabar_video: bool = False, velocidad_inicial: float = 1.0):
        """Anima la simulación paso a paso"""
        self.grabando = grabar_video
        clock = pygame.time.Clock()
        
        # NO ejecutar la simulación completa primero
        # self.simulador.simular()  # REMOVIDO
        
        print("Iniciando simulación en tiempo real...")
        print("Controles:")
        print("- ESPACIO: Pausar/Reanudar")
        print("- +/-: Cambiar velocidad (1x, 2x, 4x, 8x, 16x, 32x)")
        print("- ESC: Salir")
        print("- V: Activar/desactivar grabación de video")
        
        pausado = False
        velocidades_disponibles = [15, 30, 60, 120, 240, 480, 960, 1920]  # 0.25x, 0.5x, 1x, 2x, 4x, 8x, 16x, 32x
        velocidades_factor = [0.25, 0.5, 1, 2, 4, 8, 16, 32]
        
        # Encontrar el índice de velocidad inicial más cercano
        indice_velocidad = 2  # Default 1x
        if velocidad_inicial in velocidades_factor:
            indice_velocidad = velocidades_factor.index(velocidad_inicial)
        else:
            # Encontrar el más cercano
            diferencias = [abs(v - velocidad_inicial) for v in velocidades_factor]
            indice_velocidad = diferencias.index(min(diferencias))
        
        velocidad_animacion = velocidades_disponibles[indice_velocidad]
        print(f"Velocidad inicial: {velocidades_factor[indice_velocidad]}x")
        
        # Inicializar simulador para animación
        print(f"Iniciando simulación con {self.simulador.num_boxes} boxes...")
        
        # Continuar hasta que no haya más clientes por procesar
        simulacion_activa = True
        
        while simulacion_activa:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Cerrando simulación...")
                    self.cleanup()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("Simulación interrumpida por el usuario")
                        self.cleanup()
                        return
                    elif event.key == pygame.K_SPACE:
                        pausado = not pausado
                        print("PAUSADO" if pausado else "REANUDADO")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        if indice_velocidad < len(velocidades_disponibles) - 1:
                            indice_velocidad += 1
                            velocidad_animacion = velocidades_disponibles[indice_velocidad]
                            factor_velocidad = velocidades_factor[indice_velocidad]
                            print(f"Velocidad: {factor_velocidad}x ({velocidad_animacion} FPS)")
                    elif event.key == pygame.K_MINUS:
                        if indice_velocidad > 0:
                            indice_velocidad -= 1
                            velocidad_animacion = velocidades_disponibles[indice_velocidad]
                            factor_velocidad = velocidades_factor[indice_velocidad]
                            print(f"Velocidad: {factor_velocidad}x ({velocidad_animacion} FPS)")
                    elif event.key == pygame.K_v:
                        self.grabando = not self.grabando
                        if self.grabando:
                            print("Iniciando grabación de video...")
                            self.frame_counter = 0  # Reiniciar contador
                        else:
                            print("Deteniendo grabación de video...")
                            if self.frames:
                                nombre_video = f"simulacion_manual_{self.simulador.num_boxes}_boxes.avi"
                                self.guardar_video(nombre_video)
            
            if not pausado:
                # Ejecutar un paso de la simulación
                self.ejecutar_paso_simulacion()
                self.tiempo_actual += 1
                
                # Verificar si la simulación debe continuar
                hay_clientes_en_cola = len(self.simulador.cola_espera) > 0
                hay_boxes_ocupados = any(box.ocupado for box in self.simulador.boxes)
                
                # Durante horario normal o si aún hay clientes siendo procesados
                if (self.tiempo_actual < self.simulador.DURACION_SIMULACION or 
                    hay_clientes_en_cola or hay_boxes_ocupados):
                    simulacion_activa = True
                    
                    # Mostrar mensaje cuando termine el horario pero aún haya clientes
                    if (self.tiempo_actual == self.simulador.DURACION_SIMULACION and 
                        (hay_clientes_en_cola or hay_boxes_ocupados)):
                        print("🕐 Horario de atención terminado, procesando clientes restantes...")
                        print(f"   Clientes en cola: {len(self.simulador.cola_espera)}")
                        print(f"   Boxes ocupados: {sum(1 for box in self.simulador.boxes if box.ocupado)}")
                else:
                    simulacion_activa = False
                    print("✅ Todos los clientes han sido procesados")
                
                # Prevenir simulaciones infinitas (máximo 3 horas extra)
                if self.tiempo_actual > self.simulador.DURACION_SIMULACION + 10800:
                    print("⚠️  Tiempo límite alcanzado, finalizando simulación...")
                    simulacion_activa = False
            
            # Dibujar todo
            self.pantalla.fill(self.BLANCO)
            self.dibujar_leyenda()
            self.dibujar_boxes()
            self.dibujar_cola()
            self.dibujar_estadisticas()
            self.dibujar_controles()
            self.dibujar_estado(pausado, velocidad_animacion)
            
            pygame.display.flip()
            self.capturar_frame(velocidad_animacion)
            clock.tick(velocidad_animacion)
        
        # Mostrar estadísticas finales
        print("Simulación completada!")
        
        # Si estaba grabando, guardar el video
        if self.grabando and self.frames:
            print("Guardando video de la simulación...")
            nombre_video = f"simulacion_{self.simulador.num_boxes}_boxes.avi"
            self.guardar_video(nombre_video)
        
        self.mostrar_estadisticas_finales()
        
        if self.grabando:
            self.guardar_video()
    
    def ejecutar_paso_simulacion(self):
        """Ejecuta un paso de la simulación (un segundo)"""
        # Actualizar tiempo del simulador
        self.simulador.tiempo_actual = self.tiempo_actual
        
        # Solo durante horario de atención (8-12h)
        if self.tiempo_actual < self.simulador.DURACION_SIMULACION:
            if self.simulador.llega_cliente():
                self.simulador.agregar_cliente()
        
        # Procesar eventos
        self.simulador.procesar_finalizacion_atencion()
        self.simulador.procesar_abandonos(durante_horario_normal=(self.tiempo_actual < self.simulador.DURACION_SIMULACION))
        
        # Progreso cada 10%
        if self.tiempo_actual % (self.simulador.DURACION_SIMULACION // 10) == 0:
            progreso = (self.tiempo_actual / self.simulador.DURACION_SIMULACION) * 100
            print(f"Progreso: {progreso:.0f}%")
    
    def mostrar_estadisticas_finales(self):
        """Muestra las estadísticas finales y espera input del usuario"""
        esperando = True
        clock = pygame.time.Clock()
        
        while esperando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    esperando = False
            
            self.pantalla.fill(self.BLANCO)
            
            # Título
            texto = self.fuente_grande.render("SIMULACIÓN COMPLETADA", True, self.NEGRO)
            text_rect = texto.get_rect(center=(self.ANCHO//2, 100))
            self.pantalla.blit(texto, text_rect)
            
            # Estadísticas finales
            stats = self.simulador.obtener_estadisticas()
            y_pos = 200
            
            estadisticas = [
                f"Clientes que ingresaron: {stats['clientes_ingresaron']}",
                f"Clientes atendidos: {stats['clientes_atendidos']}",
                f"Clientes no atendidos: {stats['clientes_no_atendidos']}",
                f"Tiempo mínimo de atención: {stats['tiempo_min_atencion_min']} minutos",
                f"Tiempo máximo de atención: {stats['tiempo_max_atencion_min']} minutos",
                f"Tiempo mínimo de espera: {stats['tiempo_min_espera_min']} minutos",
                f"Tiempo máximo de espera: {stats['tiempo_max_espera_min']} minutos",
                f"Costo total: ${stats['costo_total']:,}",
                f"Costo de boxes: ${stats['costo_boxes']:,}",
                f"Pérdidas por abandono: ${stats['costo_perdidas']:,}"
            ]
            
            for stat in estadisticas:
                texto = self.fuente_mediana.render(stat, True, self.NEGRO)
                text_rect = texto.get_rect(center=(self.ANCHO//2, y_pos))
                self.pantalla.blit(texto, text_rect)
                y_pos += 40
            
            # Instrucciones
            texto = self.fuente_pequena.render("Presiona ESC para salir", True, self.GRIS)
            text_rect = texto.get_rect(center=(self.ANCHO//2, self.ALTO - 50))
            self.pantalla.blit(texto, text_rect)
            
            pygame.display.flip()
            clock.tick(60)
        
        # Usar cleanup en lugar de pygame.quit() directo
        self.cleanup()
    
    def dibujar_controles(self):
        """Dibuja el panel de controles"""
        pygame.draw.rect(self.pantalla, self.GRIS_CLARO, self.controles_area)
        pygame.draw.rect(self.pantalla, self.NEGRO, self.controles_area, 2)
        
        # Título
        texto = self.fuente_mediana.render("CONTROLES", True, self.NEGRO)
        self.pantalla.blit(texto, (self.controles_area.x + 10, self.controles_area.y + 10))
        
        # Lista de controles (texto más corto para evitar desbordamiento)
        controles = [
            "ESPACIO - Pausar/Reanudar",
            "+ - Aumentar velocidad",
            "- - Disminuir velocidad",
            "V - Activar/desactivar video",
            "ESC - Salir simulación",
            "",
            "VELOCIDADES DISPONIBLES:",
            "0.25x, 0.5x, 1x, 2x,",
            "4x, 8x, 16x, 32x",
            "",
            "INFORMACIÓN:",
            "• Simulación: 8:00 a 12:00",
            "• Abandono tras 30 min",
        ]
        
        y_pos = self.controles_area.y + 45
        for control in controles:
            if control == "":
                y_pos += 10  # Reducido espaciado
                continue
            elif control.startswith("VELOCIDADES DISPONIBLES:"):
                texto = self.fuente_pequena.render(control, True, self.AZUL)
            elif control.startswith("INFORMACIÓN:"):
                texto = self.fuente_pequena.render(control, True, self.AZUL)
            elif control.startswith("•") or control in ["0.25x, 0.5x, 1x, 2x,", "4x, 8x, 16x, 32x"]:
                texto = self.fuente_pequena.render(control, True, self.GRIS)
            else:
                texto = self.fuente_pequena.render(control, True, self.NEGRO)
            
            self.pantalla.blit(texto, (self.controles_area.x + 10, y_pos))
            y_pos += 20  # Reducido espaciado entre líneas
    
    def dibujar_estado(self, pausado: bool, velocidad_animacion: int):
        """Dibuja el estado actual de la simulación"""
        pygame.draw.rect(self.pantalla, self.GRIS_CLARO, self.estado_area)
        pygame.draw.rect(self.pantalla, self.NEGRO, self.estado_area, 2)
        
        # Título
        texto = self.fuente_mediana.render("ESTADO DE SIMULACIÓN", True, self.NEGRO)
        self.pantalla.blit(texto, (self.estado_area.x + 10, self.estado_area.y + 10))
        
        # Estado de pausa
        estado_pausa = "PAUSADO" if pausado else "EJECUTÁNDOSE"
        color_estado = self.ROJO if pausado else self.VERDE
        texto = self.fuente_pequena.render(f"Estado: {estado_pausa}", True, color_estado)
        self.pantalla.blit(texto, (self.estado_area.x + 10, self.estado_area.y + 45))
        
        # Velocidad
        velocidad_factor = velocidad_animacion / 60
        texto = self.fuente_pequena.render(f"Velocidad: {velocidad_factor}x", True, self.NEGRO)
        self.pantalla.blit(texto, (self.estado_area.x + 10, self.estado_area.y + 70))
        
        # Progreso de la simulación
        if self.tiempo_actual <= self.simulador.DURACION_SIMULACION:
            progreso = (self.tiempo_actual / self.simulador.DURACION_SIMULACION) * 100
            texto = self.fuente_pequena.render(f"Progreso: {progreso:.1f}%", True, self.NEGRO)
            color_barra = self.VERDE
        else:
            # Tiempo extra
            tiempo_extra = self.tiempo_actual - self.simulador.DURACION_SIMULACION
            minutos_extra = tiempo_extra // 60
            progreso = 100  # Mostrar 100% en horario normal
            texto = self.fuente_pequena.render(f"Tiempo extra: +{minutos_extra} min", True, self.MORADO)
            color_barra = self.MORADO
        
        self.pantalla.blit(texto, (self.estado_area.x + 10, self.estado_area.y + 95))
        
        # Barra de progreso
        barra_width = 280
        barra_height = 15
        barra_x = self.estado_area.x + 20
        barra_y = self.estado_area.y + 120
        
        # Fondo de la barra
        pygame.draw.rect(self.pantalla, self.BLANCO, (barra_x, barra_y, barra_width, barra_height))
        pygame.draw.rect(self.pantalla, self.NEGRO, (barra_x, barra_y, barra_width, barra_height), 2)
        
        # Progreso de la barra
        progreso_width = int((min(progreso, 100) / 100) * barra_width)
        if progreso_width > 0:
            pygame.draw.rect(self.pantalla, color_barra, (barra_x, barra_y, progreso_width, barra_height))
        
        # Estado de grabación
        if self.grabando:
            frames_capturados = len(self.frames)
            memoria_mb = (frames_capturados * 1200 * 800 * 3) / (1024 * 1024)  # Estimación aproximada
            texto = self.fuente_pequena.render(f"🔴 GRABANDO VIDEO", True, self.ROJO)
            self.pantalla.blit(texto, (self.estado_area.x + 10, self.estado_area.y + 150))
            
            texto_frames = self.fuente_pequena.render(f"Frames: {frames_capturados} (~{memoria_mb:.1f}MB)", True, self.ROJO)
            self.pantalla.blit(texto_frames, (self.estado_area.x + 10, self.estado_area.y + 175))
        
        # Tiempo restante estimado
        if not pausado and self.tiempo_actual > 0:
            tiempo_restante = self.simulador.DURACION_SIMULACION - self.tiempo_actual
            minutos_restantes = tiempo_restante // 60
            segundos_restantes = tiempo_restante % 60
            y_tiempo = self.estado_area.y + 200 if self.grabando else self.estado_area.y + 180
            texto = self.fuente_pequena.render(f"Tiempo restante: {minutos_restantes:02d}:{segundos_restantes:02d}", True, self.NEGRO)
            self.pantalla.blit(texto, (self.estado_area.x + 10, y_tiempo))
        
        # Estadísticas rápidas
        eficiencia = 0
        if len(self.simulador.todos_los_clientes) > 0:
            eficiencia = (len(self.simulador.clientes_atendidos) / len(self.simulador.todos_los_clientes)) * 100
        
        y_eficiencia = self.estado_area.y + 230 if self.grabando else self.estado_area.y + 210
        texto = self.fuente_pequena.render(f"Eficiencia actual: {eficiencia:.1f}%", True, self.AZUL)
        self.pantalla.blit(texto, (self.estado_area.x + 10, y_eficiencia))
    
    def cleanup(self):
        """Limpia recursos y guarda video si es necesario"""
        if self.grabando and self.frames:
            print("Guardando video antes de cerrar...")
            nombre_video = f"simulacion_interrupcion_{self.simulador.num_boxes}_boxes.avi"
            self.guardar_video(nombre_video)
        
        # Limpiar frames de memoria
        self.frames.clear()
        pygame.quit()
