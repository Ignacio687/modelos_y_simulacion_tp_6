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

### Análisis Comparativo Avanzado
```bash
# Análisis con 50 simulaciones por configuración (más preciso)
python main.py --compare --iterations 50

# Análisis estadístico robusto con 100 simulaciones por configuración
python main.py --compare --iterations 100

# Comparar hasta 5 boxes con 200 simulaciones cada uno (máxima precisión)
python main.py --compare --max-boxes 5 --iterations 200
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

- **Análisis estadístico robusto**: Ejecuta múltiples simulaciones (1-200) por cada configuración de boxes
- **Resultados promediados**: Calcula promedios y desviaciones estándar para mayor precisión
- **Evaluación de configuraciones**: Compara diferentes números de boxes (1-10)
- **Identificación óptima flexible**: Encuentra la mejor configuración considerando balance costo-eficiencia (dentro del 5% del menor costo, prioriza eficiencia)
- **Configuración sin pérdidas restrictiva**: Identifica el mínimo de boxes que garantiza prácticamente cero pérdidas (<1.0 cliente perdido promedio)
- **Análisis costo-beneficio avanzado**: Calcula el costo por cliente no perdido y ROI de eliminar pérdidas
- **Visualización avanzada**: Genera gráficos con barras de error y marcadores para ambas configuraciones clave
- **Exportación**: Guarda resultados en archivos PNG con nomenclatura descriptiva

## Archivos Generados

- `simulacion.avi`: Video de la simulación (si se activa grabación)
- `analisis_comparativo.png`: Gráficos del análisis comparativo (1 simulación por config)
- `analisis_comparativo_N_iter.png`: Gráficos con N simulaciones por configuración

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

## Ejemplo de Salida del Análisis Comparativo

```
Comparando configuraciones de boxes...
Ejecutando 50 simulaciones por cada configuración (1-5 boxes)
Total de simulaciones: 250
Tiempo estimado: ~8 min 20 seg
Esto puede tomar varios minutos...

Simulando con 1 boxes (50 iteraciones)...
  Iteración 1/50 (2.0%)... $435,000
  Iteración 2/50 (4.0%)... $442,000
  ...
  Iteración 25/50 (50.0%)... $428,000
    Progreso parcial - Costo promedio: $431,200, Eficiencia: 60.2%
  ...
  Iteración 50/50 (100.0%)... $439,000
  Promedio - Costo: $432,800 (±$8,400)
  Promedio - Atendidos: 57.8 (±2.1)
  Promedio - Perdidos: 36.2 (±2.1)
  Promedio - Eficiencia: 61.5% (±2.3%)

📊 Análisis de pérdidas por configuración:
   1 boxes: 67.20 clientes perdidos promedio
   2 boxes: 42.10 clientes perdidos promedio
   3 boxes: 18.50 clientes perdidos promedio
   4 boxes: 5.80 clientes perdidos promedio
   5 boxes: 1.20 clientes perdidos promedio
   6 boxes: 0.30 clientes perdidos promedio
   7 boxes: 0.05 clientes perdidos promedio
   ✅ Primera configuración sin pérdidas: 6 boxes (<1.0 cliente)

================================================================================
ANÁLISIS COMPARATIVO CON MÚLTIPLES SIMULACIONES
================================================================================
🏆 Configuración óptima (mejor balance costo-eficiencia): 5 boxes
   📈 Seleccionada por mayor eficiencia dentro del 5% del menor costo
   💰 Costo de referencia (mínimo): $16,800 (±$2,000)
   Costo promedio: $17,000 (±$2,100)
   Eficiencia: 98.7% (±0.8%)
   Clientes perdidos: 1.20 (±1.10)

🛡️  Configuración que elimina pérdidas de clientes: 6 boxes
   ✅ Prácticamente CERO pérdidas de clientes
   Costo promedio: $18,000 (±$1,500)
   Eficiencia: 99.7% (±0.3%)
   Clientes perdidos: 0.30 (±0.20)

💰 Costo adicional para ELIMINAR pérdidas: +$1,000
   Aumento porcentual: +5.9%
   Boxes adicionales necesarios: +1
   Costo por cliente no perdido: $1,111

Iteraciones por configuración: 50
Tiempo total de análisis: 8 min 15 seg
================================================================================
```

## Notas Técnicas

- La simulación utiliza eventos discretos para máxima precisión
- Los tiempos se manejan en segundos internamente
- La interfaz visual actualiza a 60 FPS por defecto
- Los videos se graban a 15 FPS constante independiente de la velocidad de simulación
- **Recomendaciones para análisis estadístico**:
  - Para análisis preliminar: 10-25 iteraciones
  - Para análisis confiable: 50-100 iteraciones  
  - Para máxima precisión: 150-200 iteraciones
  - Más iteraciones reducen la variabilidad y aumentan la confianza estadística
