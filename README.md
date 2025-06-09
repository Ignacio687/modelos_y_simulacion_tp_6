# Simulador de Sistema de Atención al Público

*Modelos y Simulación - Universidad de Mendoza - TP6*  
*Ignacio Chaves (Legajo: 61.220)*

Este proyecto implementa una simulación completa de un sistema de atención al público, desarrollado como parte del TP 6 de Modelos y Simulación.

## Características

- **Simulación realista**: Implementa todas las reglas especificadas en la consigna
- **Interfaz visual interactiva**: Visualización en tiempo real con pygame
- **Análisis comparativo**: Herramientas para comparar diferentes configuraciones
- **Generación de videos**: Capacidad de grabar la simulación en formato AVI
- **Estadísticas completas**: Informes detallados de rendimiento y costos

## Reglas de la Simulación

1. **Horario**: Local abierto de 8:00 a 12:00 (4 horas)
2. **Boxes**: 1 a 10 boxes de atención configurables
3. **Llegada de clientes**: Probabilidad de 1/144 por segundo
4. **Tiempo de atención**: Distribución normal (media=10 min, σ=5 min)
5. **Abandono**: Clientes abandonan después de 30 minutos de espera
6. **Costos**: 
   - Box: $1,000 por mañana
   - Cliente perdido: $10,000

## Instalación

```bash
# Navegar al directorio del proyecto
cd modelos_y_simulacion_tp_6

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Menú Interactivo
```bash
python main.py
```

### Simulación Simple (Solo Estadísticas)
```bash
python main.py -b 5
```

### Simulación Visual
```bash
python main.py -b 3 --visual
```

### Simulación con Grabación de Video
```bash
python main.py -b 4 --video
```

### Análisis Comparativo
```bash
python main.py --compare
```

## Controles de la Interfaz Visual

- **ESPACIO**: Pausar/Reanudar simulación
- **+/-**: Aumentar/Disminuir velocidad de animación
- **V**: Activar/Desactivar grabación de video
- **ESC**: Salir

## Interpretación Visual

### Colores de Boxes
- **Gris claro**: Box libre
- **Verde**: Box ocupado atendiendo cliente

### Colores de Clientes en Cola
- **Azul**: Cliente recién llegado (< 15 min esperando)
- **Amarillo**: Cliente esperando 15-25 minutos
- **Rojo**: Cliente esperando más de 25 minutos (cerca del abandono)

## Resultados y Estadísticas

El simulador proporciona las siguientes métricas:

1. Número total de clientes que ingresaron
2. Clientes atendidos exitosamente
3. Clientes que abandonaron por demora
4. Tiempos mínimo y máximo de atención
5. Tiempos mínimo y máximo de espera
6. Análisis de costos (boxes + pérdidas)

## Análisis Comparativo

La función de análisis comparativo permite:

- Evaluar diferentes configuraciones de boxes (1-10)
- Identificar la configuración óptima (menor costo total)
- Generar gráficos de rendimiento
- Exportar resultados a archivos PNG

## Archivos Generados

- `simulacion.avi`: Video de la simulación (si se activa grabación)
- `analisis_comparativo.png`: Gráficos del análisis comparativo

## Estructura del Proyecto

```
├── main.py              # Programa principal y menú
├── simulador.py         # Lógica de simulación
├── interfaz_visual.py   # Interfaz gráfica con pygame
├── requirements.txt     # Dependencias del proyecto
├── consigna.txt        # Especificaciones del TP
└── README.md           # Este archivo
```

## Dependencias

- `pygame`: Interfaz gráfica y animación
- `numpy`: Cálculos numéricos y distribuciones
- `matplotlib`: Generación de gráficos
- `opencv-python`: Generación de videos AVI
- `scipy`: Funciones estadísticas adicionales

## Ejemplo de Salida

```
==================================================
RESULTADOS DE LA SIMULACIÓN
==================================================
Número de boxes: 5
1) Clientes que ingresaron: 127
2) Clientes atendidos: 118
3) Clientes no atendidos (abandonaron): 9
4) Tiempo mínimo de atención: 2 minutos
5) Tiempo máximo de atención: 23 minutos
6) Tiempo mínimo de espera: 0 minutos
7) Tiempo máximo de espera: 30 minutos
8) Costo total de operación: $95,000
   - Costo de boxes: $5,000
   - Pérdidas por clientes: $90,000
==================================================
```

## Notas Técnicas

- La simulación utiliza eventos discretos para máxima precisión
- Los tiempos se manejan en segundos internamente
- La interfaz visual actualiza a 60 FPS por defecto
- Los videos se graban a 30 FPS para mejor compatibilidad
