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
        
        # Configuración de pantalla
        self.ANCHO = 1200
        self.ALTO = 800
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
        
        # Fuentes
        self.fuente_grande = pygame.font.Font(None, 36)
        self.fuente_mediana = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 18)
        
        self.simulador = simulador
        self.velocidad = velocidad
        self.tiempo_actual = 0
        self.indice_evento = 0
        
        # Para grabar video
        self.grabando = False
        self.frames = []
        
        # Posiciones de elementos
        self.setup_posiciones()
        
    def setup_posiciones(self):
        """Configura las posiciones de los elementos visuales"""
        # Área de boxes
        self.boxes_area = pygame.Rect(50, 100, 500, 400)
        self.box_width = 80
        self.box_height = 60
        
        # Área de cola
        self.cola_area = pygame.Rect(600, 100, 200, 400)
        
        # Área de estadísticas
        self.stats_area = pygame.Rect(50, 520, 750, 250)
        
        # Área de controles
        self.controles_area = pygame.Rect(820, 100, 330, 400)
        
        # Área de estado
        self.estado_area = pygame.Rect(820, 520, 330, 250)
        
    def dibujar_boxes(self):
        """Dibuja los boxes de atención"""
        # Título
        texto = self.fuente_mediana.render("BOXES DE ATENCIÓN", True, self.NEGRO)
        self.pantalla.blit(texto, (self.boxes_area.x, self.boxes_area.y - 30))
        
        # Calcular posiciones de boxes
        boxes_por_fila = 5
        filas = (self.simulador.num_boxes + boxes_por_fila - 1) // boxes_por_fila
        
        for i, box in enumerate(self.simulador.boxes):
            fila = i // boxes_por_fila
            col = i % boxes_por_fila
            
            x = self.boxes_area.x + col * (self.box_width + 20)
            y = self.boxes_area.y + fila * (self.box_height + 30)
            
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
            text_rect = texto.get_rect(center=(x + self.box_width//2, y + 15))
            self.pantalla.blit(texto, text_rect)
            
            # Cliente siendo atendido
            if box.ocupado and box.cliente_actual:
                texto = self.fuente_pequena.render(f"Cliente {box.cliente_actual.id}", True, color_texto)
                text_rect = texto.get_rect(center=(x + self.box_width//2, y + 35))
                self.pantalla.blit(texto, text_rect)
                
                # Tiempo restante aproximado
                if box.tiempo_fin_atencion:
                    tiempo_restante = max(0, box.tiempo_fin_atencion - self.tiempo_actual)
                    minutos_restantes = tiempo_restante // 60
                    texto = self.fuente_pequena.render(f"{minutos_restantes}min", True, color_texto)
                    text_rect = texto.get_rect(center=(x + self.box_width//2, y + 50))
                    self.pantalla.blit(texto, text_rect)
    
    def dibujar_cola(self):
        """Dibuja la cola de espera"""
        # Título
        texto = self.fuente_mediana.render(f"COLA DE ESPERA ({len(self.simulador.cola_espera)} clientes)", True, self.NEGRO)
        self.pantalla.blit(texto, (self.cola_area.x, self.cola_area.y - 30))
        
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
        
        # Título
        texto = self.fuente_mediana.render("ESTADÍSTICAS EN TIEMPO REAL", True, self.NEGRO)
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
            ("Cliente esperando 15+ min", self.AMARILLO),
            ("Cliente esperando 25+ min", self.ROJO)
        ]
        
        for i, (texto, color) in enumerate(elementos):
            x = 50 + i * 200
            pygame.draw.circle(self.pantalla, color, (x, leyenda_y), 10)
            pygame.draw.circle(self.pantalla, self.NEGRO, (x, leyenda_y), 10, 2)
            
            texto_render = self.fuente_pequena.render(texto, True, self.NEGRO)
            self.pantalla.blit(texto_render, (x + 20, leyenda_y - 8))
    
    def capturar_frame(self):
        """Captura el frame actual para el video"""
        if self.grabando:
            # Convertir superficie de pygame a array numpy
            frame = pygame.surfarray.array3d(self.pantalla)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.frames.append(frame)
    
    def guardar_video(self, nombre_archivo: str = "simulacion.avi"):
        """Guarda los frames capturados como video AVI"""
        if not self.frames:
            print("No hay frames para guardar")
            return
        
        try:
            import cv2
            height, width, layers = self.frames[0].shape
            
            # Intentar diferentes formas de crear el codec
            try:
                fourcc = cv2.VideoWriter.fourcc('X','V','I','D')
            except:
                try:
                    fourcc = cv2.VideoWriter.fourcc(*'XVID')
                except:
                    fourcc = -1  # Sin compresión
            
            video = cv2.VideoWriter(nombre_archivo, fourcc, 30.0, (width, height))
            
            for frame in self.frames:
                video.write(frame)
            
            video.release()
            print(f"Video guardado como {nombre_archivo}")
            
        except Exception as e:
            print(f"Error al guardar video: {e}")
            print("La funcionalidad de video requiere una instalación completa de OpenCV")
    
    def animar_simulacion(self, grabar_video: bool = False):
        """Anima la simulación paso a paso"""
        self.grabando = grabar_video
        clock = pygame.time.Clock()
        
        # NO ejecutar la simulación completa primero
        # self.simulador.simular()  # REMOVIDO
        
        print("Iniciando simulación en tiempo real...")
        print("Controles:")
        print("- ESPACIO: Pausar/Reanudar")
        print("- +/-: Cambiar velocidad")
        print("- ESC: Salir")
        print("- V: Activar/desactivar grabación de video")
        
        pausado = False
        velocidad_animacion = 60  # FPS base
        
        # Inicializar simulador para animación
        print(f"Iniciando simulación con {self.simulador.num_boxes} boxes...")
        
        while self.tiempo_actual < self.simulador.DURACION_SIMULACION:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pausado = not pausado
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        velocidad_animacion = min(velocidad_animacion * 2, 480)
                        print(f"Velocidad: {velocidad_animacion//60}x")
                    elif event.key == pygame.K_MINUS:
                        velocidad_animacion = max(velocidad_animacion // 2, 15)
                        print(f"Velocidad: {velocidad_animacion//60}x")
                    elif event.key == pygame.K_ESCAPE:
                        if self.grabando:
                            self.guardar_video()
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_v:
                        self.grabando = not self.grabando
                        print(f"Grabación: {'ACTIVADA' if self.grabando else 'DESACTIVADA'}")
            
            if not pausado:
                # Ejecutar un paso de la simulación
                self.ejecutar_paso_simulacion()
                self.tiempo_actual += 1
            
            # Dibujar todo
            self.pantalla.fill(self.BLANCO)
            self.dibujar_leyenda()
            self.dibujar_boxes()
            self.dibujar_cola()
            self.dibujar_estadisticas()
            self.dibujar_controles()
            self.dibujar_estado(pausado, velocidad_animacion)
            
            pygame.display.flip()
            self.capturar_frame()
            clock.tick(velocidad_animacion)
        
        # Mostrar estadísticas finales
        print("Simulación completada!")
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
        self.simulador.procesar_abandonos()
        
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
        
        pygame.quit()
    
    def dibujar_controles(self):
        """Dibuja el panel de controles"""
        pygame.draw.rect(self.pantalla, self.GRIS_CLARO, self.controles_area)
        pygame.draw.rect(self.pantalla, self.NEGRO, self.controles_area, 2)
        
        # Título
        texto = self.fuente_mediana.render("CONTROLES", True, self.NEGRO)
        self.pantalla.blit(texto, (self.controles_area.x + 10, self.controles_area.y + 10))
        
        # Lista de controles
        controles = [
            "ESPACIO - Pausar/Reanudar",
            "+ - Aumentar velocidad",
            "- - Disminuir velocidad",
            "V - Activar/desactivar video",
            "ESC - Salir de la simulación",
            "",
            "INFORMACIÓN:",
            "• La simulación corre de 8:00 a 12:00",
            "• Los clientes llegan aleatoriamente",
            "• Abandono después de 30 min",
            "• Tiempo de atención: 10±5 min"
        ]
        
        y_pos = self.controles_area.y + 45
        for control in controles:
            if control == "":
                y_pos += 15
                continue
            elif control.startswith("INFORMACIÓN:"):
                texto = self.fuente_pequena.render(control, True, self.AZUL)
            elif control.startswith("•"):
                texto = self.fuente_pequena.render(control, True, self.GRIS)
            else:
                texto = self.fuente_pequena.render(control, True, self.NEGRO)
            
            self.pantalla.blit(texto, (self.controles_area.x + 10, y_pos))
            y_pos += 25
    
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
        velocidad_factor = velocidad_animacion // 60
        texto = self.fuente_pequena.render(f"Velocidad: {velocidad_factor}x", True, self.NEGRO)
        self.pantalla.blit(texto, (self.estado_area.x + 10, self.estado_area.y + 70))
        
        # Progreso de la simulación
        progreso = (self.tiempo_actual / self.simulador.DURACION_SIMULACION) * 100
        texto = self.fuente_pequena.render(f"Progreso: {progreso:.1f}%", True, self.NEGRO)
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
        progreso_width = int((progreso / 100) * barra_width)
        if progreso_width > 0:
            pygame.draw.rect(self.pantalla, self.VERDE, (barra_x, barra_y, progreso_width, barra_height))
        
        # Estado de grabación
        if self.grabando:
            texto = self.fuente_pequena.render("🔴 GRABANDO VIDEO", True, self.ROJO)
            self.pantalla.blit(texto, (self.estado_area.x + 10, self.estado_area.y + 150))
        
        # Tiempo restante estimado
        if not pausado and self.tiempo_actual > 0:
            tiempo_restante = self.simulador.DURACION_SIMULACION - self.tiempo_actual
            minutos_restantes = tiempo_restante // 60
            segundos_restantes = tiempo_restante % 60
            texto = self.fuente_pequena.render(f"Tiempo restante: {minutos_restantes:02d}:{segundos_restantes:02d}", True, self.NEGRO)
            self.pantalla.blit(texto, (self.estado_area.x + 10, self.estado_area.y + 180))
        
        # Estadísticas rápidas
        eficiencia = 0
        if len(self.simulador.todos_los_clientes) > 0:
            eficiencia = (len(self.simulador.clientes_atendidos) / len(self.simulador.todos_los_clientes)) * 100
        
        texto = self.fuente_pequena.render(f"Eficiencia actual: {eficiencia:.1f}%", True, self.AZUL)
        self.pantalla.blit(texto, (self.estado_area.x + 10, self.estado_area.y + 210))
