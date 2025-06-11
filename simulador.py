import random
import numpy as np
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import time

class ClienteEstado(Enum):
    ESPERANDO = "esperando"
    SIENDO_ATENDIDO = "siendo_atendido"
    ATENDIDO = "atendido"
    ABANDONO = "abandono"

@dataclass
class Cliente:
    id: int
    tiempo_llegada: int  # en segundos desde apertura
    tiempo_inicio_atencion: Optional[int] = None
    tiempo_fin_atencion: Optional[int] = None
    tiempo_abandono: Optional[int] = None
    estado: ClienteEstado = ClienteEstado.ESPERANDO
    box_asignado: Optional[int] = None
    
    @property
    def tiempo_espera(self) -> int:
        """Tiempo que esperó en cola antes de ser atendido (en segundos)"""
        if self.tiempo_inicio_atencion:
            return self.tiempo_inicio_atencion - self.tiempo_llegada
        elif self.tiempo_abandono:
            return self.tiempo_abandono - self.tiempo_llegada
        else:
            return 0
    
    @property
    def tiempo_atencion(self) -> int:
        """Tiempo que duró la atención (en segundos)"""
        if self.tiempo_fin_atencion and self.tiempo_inicio_atencion:
            return self.tiempo_fin_atencion - self.tiempo_inicio_atencion
        return 0

@dataclass
class Box:
    id: int
    ocupado: bool = False
    cliente_actual: Optional[Cliente] = None
    tiempo_fin_atencion: Optional[int] = None

class SimuladorAtencion:
    def __init__(self, num_boxes: int):
        self.num_boxes = num_boxes
        self.boxes = [Box(i) for i in range(num_boxes)]
        self.cola_espera: List[Cliente] = []
        self.clientes_atendidos: List[Cliente] = []
        self.clientes_abandonaron: List[Cliente] = []
        self.todos_los_clientes: List[Cliente] = []
        
        # Configuración de la simulación
        self.TIEMPO_APERTURA = 8 * 3600  # 8 AM en segundos
        self.TIEMPO_CIERRE = 12 * 3600   # 12 PM en segundos
        self.DURACION_SIMULACION = 4 * 3600  # 4 horas
        self.PROB_LLEGADA_POR_SEGUNDO = 1/144
        self.TIEMPO_MAX_ESPERA = 30 * 60  # 30 minutos en segundos
        self.MEDIA_ATENCION = 10 * 60     # 10 minutos en segundos
        self.DESVIO_ATENCION = 5 * 60     # 5 minutos en segundos
        self.COSTO_BOX = 1000
        self.PERDIDA_CLIENTE = 10000
        
        # Estadísticas
        self.tiempo_actual = 0
        self.contador_clientes = 0
        
        # Para la animación
        self.eventos_animacion = []
        
    def generar_tiempo_atencion(self) -> int:
        """Genera tiempo de atención siguiendo distribución normal"""
        tiempo = np.random.normal(self.MEDIA_ATENCION, self.DESVIO_ATENCION)
        return max(int(tiempo), 30)  # mínimo 30 segundos
    
    def llega_cliente(self) -> bool:
        """Determina si llega un cliente en este segundo"""
        return random.random() < self.PROB_LLEGADA_POR_SEGUNDO
    
    def agregar_cliente(self):
        """Agrega un nuevo cliente al sistema"""
        cliente = Cliente(
            id=self.contador_clientes,
            tiempo_llegada=self.tiempo_actual
        )
        self.contador_clientes += 1
        self.todos_los_clientes.append(cliente)
        
        # Buscar box libre
        box_libre = self.buscar_box_libre()
        if box_libre:
            self.asignar_cliente_a_box(cliente, box_libre)
        else:
            self.cola_espera.append(cliente)
            
        # Evento para animación
        self.eventos_animacion.append({
            'tipo': 'llegada_cliente',
            'tiempo': self.tiempo_actual,
            'cliente_id': cliente.id,
            'total_cola': len(self.cola_espera)
        })
    
    def buscar_box_libre(self) -> Optional[Box]:
        """Busca un box que esté libre"""
        for box in self.boxes:
            if not box.ocupado:
                return box
        return None
    
    def asignar_cliente_a_box(self, cliente: Cliente, box: Box):
        """Asigna un cliente a un box específico"""
        cliente.estado = ClienteEstado.SIENDO_ATENDIDO
        cliente.tiempo_inicio_atencion = self.tiempo_actual
        cliente.box_asignado = box.id
        
        box.ocupado = True
        box.cliente_actual = cliente
        box.tiempo_fin_atencion = self.tiempo_actual + self.generar_tiempo_atencion()
        
        # Evento para animación
        self.eventos_animacion.append({
            'tipo': 'inicio_atencion',
            'tiempo': self.tiempo_actual,
            'cliente_id': cliente.id,
            'box_id': box.id
        })
    
    def procesar_finalizacion_atencion(self):
        """Procesa los boxes donde termina la atención"""
        for box in self.boxes:
            if (box.ocupado and box.tiempo_fin_atencion and 
                self.tiempo_actual >= box.tiempo_fin_atencion):
                
                cliente = box.cliente_actual
                if cliente is not None:
                    cliente.estado = ClienteEstado.ATENDIDO
                    cliente.tiempo_fin_atencion = self.tiempo_actual
                    
                    self.clientes_atendidos.append(cliente)
                    
                    # Evento para animación
                    self.eventos_animacion.append({
                        'tipo': 'fin_atencion',
                        'tiempo': self.tiempo_actual,
                        'cliente_id': cliente.id,
                        'box_id': box.id
                    })
                
                # Liberar box
                box.ocupado = False
                box.cliente_actual = None
                box.tiempo_fin_atencion = None
                
                # Asignar siguiente cliente de la cola
                if self.cola_espera:
                    siguiente_cliente = self.cola_espera.pop(0)
                    self.asignar_cliente_a_box(siguiente_cliente, box)
    
    def procesar_abandonos(self, durante_horario_normal=True):
        """Procesa clientes que abandonan por tiempo de espera"""
        # Después del cierre, los clientes NO abandonan (según regla 3)
        if not durante_horario_normal:
            return
            
        clientes_a_remover = []
        
        for cliente in self.cola_espera:
            tiempo_esperando = self.tiempo_actual - cliente.tiempo_llegada
            if tiempo_esperando >= self.TIEMPO_MAX_ESPERA:
                cliente.estado = ClienteEstado.ABANDONO
                cliente.tiempo_abandono = self.tiempo_actual
                self.clientes_abandonaron.append(cliente)
                clientes_a_remover.append(cliente)
                
                # Evento para animación
                self.eventos_animacion.append({
                    'tipo': 'abandono',
                    'tiempo': self.tiempo_actual,
                    'cliente_id': cliente.id
                })
        
        for cliente in clientes_a_remover:
            self.cola_espera.remove(cliente)
    
    def simular(self):
        """Ejecuta la simulación completa"""
        print(f"Iniciando simulación con {self.num_boxes} boxes...")
        
        for segundo in range(self.DURACION_SIMULACION):
            self.tiempo_actual = segundo
            
            # Solo durante horario de atención (8-12h)
            if segundo < self.DURACION_SIMULACION:
                if self.llega_cliente():
                    self.agregar_cliente()
            
            # Procesar eventos
            self.procesar_finalizacion_atencion()
            self.procesar_abandonos(durante_horario_normal=True)
            
            # Progreso cada 10%
            if segundo % (self.DURACION_SIMULACION // 10) == 0:
                progreso = (segundo / self.DURACION_SIMULACION) * 100
                print(f"Progreso: {progreso:.0f}%")
        
        # Después del horario de cierre, continuar atendiendo a clientes restantes
        # según la regla 3: "Los clientes que están en cola o siendo atendidos pueden permanecer luego de la hora de cierre"
        clientes_en_cola = len(self.cola_espera)
        boxes_ocupados = sum(1 for box in self.boxes if box.ocupado)
        
        if clientes_en_cola > 0 or boxes_ocupados > 0:
            print(f"Procesando clientes restantes después del cierre...")
            print(f"  - Clientes en cola: {clientes_en_cola}")
            print(f"  - Boxes ocupados: {boxes_ocupados}")
        
        while (len(self.cola_espera) > 0 or 
               any(box.ocupado for box in self.boxes)):
            
            self.tiempo_actual += 1
            
            # Solo procesar finalizaciones, NO abandonos después del cierre
            # porque según la regla 3, los clientes pueden permanecer
            self.procesar_finalizacion_atencion()
            
            # Mostrar progreso cada minuto (60 segundos)
            if (self.tiempo_actual - self.DURACION_SIMULACION) % 60 == 0:
                minutos_extra = (self.tiempo_actual - self.DURACION_SIMULACION) // 60
                cola_actual = len(self.cola_espera)
                boxes_actuales = sum(1 for box in self.boxes if box.ocupado)
                print(f"  Tiempo extra: +{minutos_extra} min, Cola: {cola_actual}, Atendiendo: {boxes_actuales}")
            
            # Prevenir bucles infinitos (máximo 3 horas adicionales)
            if self.tiempo_actual > self.DURACION_SIMULACION + 10800:
                print("⚠️  Tiempo límite alcanzado (3h extra), finalizando simulación forzadamente...")
                # Marcar clientes restantes como atendidos (asumiendo que eventualmente serían atendidos)
                for cliente in self.cola_espera:
                    cliente.estado = ClienteEstado.ATENDIDO
                    cliente.tiempo_inicio_atencion = self.tiempo_actual
                    cliente.tiempo_fin_atencion = self.tiempo_actual + 600  # 10 min promedio
                    self.clientes_atendidos.append(cliente)
                self.cola_espera.clear()
                
                # Finalizar atenciones en curso como completadas
                for box in self.boxes:
                    if box.ocupado and box.cliente_actual:
                        cliente = box.cliente_actual
                        cliente.estado = ClienteEstado.ATENDIDO
                        cliente.tiempo_fin_atencion = self.tiempo_actual
                        self.clientes_atendidos.append(cliente)
                        box.ocupado = False
                        box.cliente_actual = None
                        box.tiempo_fin_atencion = None
                break
        
        tiempo_total_minutos = self.tiempo_actual // 60
        tiempo_extra_minutos = max(0, (self.tiempo_actual - self.DURACION_SIMULACION) // 60)
        print(f"Simulación completada en {tiempo_total_minutos} minutos total (+{tiempo_extra_minutos} min extra)")
    
    def obtener_estadisticas(self) -> dict:
        """Calcula y retorna las estadísticas de la simulación"""
        clientes_ingresaron = len(self.todos_los_clientes)
        clientes_atendidos = len(self.clientes_atendidos)
        clientes_no_atendidos = len(self.clientes_abandonaron)
        
        # Tiempos de atención
        tiempos_atencion = [c.tiempo_atencion for c in self.clientes_atendidos if c.tiempo_atencion > 0]
        tiempo_min_atencion = min(tiempos_atencion) if tiempos_atencion else 0
        tiempo_max_atencion = max(tiempos_atencion) if tiempos_atencion else 0
        
        # Tiempos de espera
        tiempos_espera = []
        for cliente in self.clientes_atendidos + self.clientes_abandonaron:
            if cliente.tiempo_espera > 0:
                tiempos_espera.append(cliente.tiempo_espera)
        
        tiempo_min_espera = min(tiempos_espera) if tiempos_espera else 0
        tiempo_max_espera = max(tiempos_espera) if tiempos_espera else 0
        
        # Costos
        costo_boxes = self.num_boxes * self.COSTO_BOX
        costo_perdidas = clientes_no_atendidos * self.PERDIDA_CLIENTE
        costo_total = costo_boxes + costo_perdidas
        
        return {
            'clientes_ingresaron': clientes_ingresaron,
            'clientes_atendidos': clientes_atendidos,
            'clientes_no_atendidos': clientes_no_atendidos,
            'tiempo_min_atencion_seg': tiempo_min_atencion,
            'tiempo_max_atencion_seg': tiempo_max_atencion,
            'tiempo_min_espera_seg': tiempo_min_espera,
            'tiempo_max_espera_seg': tiempo_max_espera,
            'costo_boxes': costo_boxes,
            'costo_perdidas': costo_perdidas,
            'costo_total': costo_total,
            'tiempo_min_atencion_min': tiempo_min_atencion // 60,
            'tiempo_max_atencion_min': tiempo_max_atencion // 60,
            'tiempo_min_espera_min': tiempo_min_espera // 60,
            'tiempo_max_espera_min': tiempo_max_espera // 60
        }
    
    def imprimir_estadisticas(self):
        """Imprime las estadísticas de forma legible"""
        stats = self.obtener_estadisticas()
        
        print("\n" + "="*50)
        print("RESULTADOS DE LA SIMULACIÓN")
        print("="*50)
        print(f"Número de boxes: {self.num_boxes}")
        print(f"1) Clientes que ingresaron: {stats['clientes_ingresaron']}")
        print(f"2) Clientes atendidos: {stats['clientes_atendidos']}")
        print(f"3) Clientes no atendidos (abandonaron): {stats['clientes_no_atendidos']}")
        
        # Verificación de integridad
        total_procesado = stats['clientes_atendidos'] + stats['clientes_no_atendidos']
        clientes_en_cola = len(self.cola_espera)
        clientes_siendo_atendidos = sum(1 for box in self.boxes if box.ocupado)
        
        print(f"   - Total procesado: {total_procesado}")
        print(f"   - Clientes en cola: {clientes_en_cola}")
        print(f"   - Siendo atendidos: {clientes_siendo_atendidos}")
        print(f"   - Eficiencia: {(stats['clientes_atendidos'] / max(1, stats['clientes_ingresaron'])) * 100:.1f}%")
        
        print(f"4) Tiempo mínimo de atención: {stats['tiempo_min_atencion_min']} minutos")
        print(f"5) Tiempo máximo de atención: {stats['tiempo_max_atencion_min']} minutos")
        print(f"6) Tiempo mínimo de espera: {stats['tiempo_min_espera_min']} minutos")
        print(f"7) Tiempo máximo de espera: {stats['tiempo_max_espera_min']} minutos")
        print(f"8) Costo total de operación: ${stats['costo_total']:,}")
        print(f"   - Costo de boxes: ${stats['costo_boxes']:,}")
        print(f"   - Pérdidas por clientes: ${stats['costo_perdidas']:,}")
        print("="*50)
