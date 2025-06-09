#!/usr/bin/env python3
"""
Simulador de Sistema de Atención al Público
TP 6 - Modelos y Simulación

Autor: Sistema de Simulación
Fecha: 2025

Este programa simula un sistema de atención al público con múltiples boxes,
permitiendo analizar diferentes configuraciones para optimizar la atención
y minimizar costos.
"""

import argparse
import sys
from simulador import SimuladorAtencion
from interfaz_visual import InterfazVisual
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

def ejecutar_simulacion_simple(num_boxes: int, mostrar_stats: bool = True):
    """Ejecuta una simulación simple sin interfaz visual"""
    simulador = SimuladorAtencion(num_boxes)
    simulador.simular()
    
    if mostrar_stats:
        simulador.imprimir_estadisticas()
    
    return simulador

def ejecutar_simulacion_visual(num_boxes: int, grabar_video: bool = False):
    """Ejecuta la simulación con interfaz visual"""
    simulador = SimuladorAtencion(num_boxes)
    interfaz = InterfazVisual(simulador)
    interfaz.animar_simulacion(grabar_video)

def comparar_configuraciones(max_boxes: int = 10):
    """Compara diferentes configuraciones de boxes"""
    print("Comparando configuraciones de boxes...")
    print("Esto puede tomar varios minutos...\n")
    
    resultados = []
    
    for num_boxes in range(1, max_boxes + 1):
        print(f"Simulando con {num_boxes} boxes...")
        simulador = ejecutar_simulacion_simple(num_boxes, False)
        stats = simulador.obtener_estadisticas()
        
        resultados.append({
            'boxes': num_boxes,
            'costo_total': stats['costo_total'],
            'clientes_atendidos': stats['clientes_atendidos'],
            'clientes_perdidos': stats['clientes_no_atendidos'],
            'eficiencia': stats['clientes_atendidos'] / max(1, stats['clientes_ingresaron']) * 100
        })
        
        print(f"  Costo total: ${stats['costo_total']:,}")
        print(f"  Clientes atendidos: {stats['clientes_atendidos']}")
        print(f"  Clientes perdidos: {stats['clientes_no_atendidos']}")
        print(f"  Eficiencia: {stats['clientes_atendidos'] / max(1, stats['clientes_ingresaron']) * 100:.1f}%\n")
    
    # Encontrar configuración óptima
    mejor_config = min(resultados, key=lambda x: x['costo_total'])
    
    print("="*60)
    print("ANÁLISIS COMPARATIVO")
    print("="*60)
    print(f"Configuración óptima: {mejor_config['boxes']} boxes")
    print(f"Costo mínimo: ${mejor_config['costo_total']:,}")
    print(f"Eficiencia: {mejor_config['eficiencia']:.1f}%")
    print("="*60)
    
    # Generar gráficos
    generar_graficos_comparacion(resultados)
    
    return resultados

def generar_graficos_comparacion(resultados):
    """Genera gráficos comparativos de las configuraciones"""
    boxes = [r['boxes'] for r in resultados]
    costos = [r['costo_total'] for r in resultados]
    atendidos = [r['clientes_atendidos'] for r in resultados]
    perdidos = [r['clientes_perdidos'] for r in resultados]
    eficiencia = [r['eficiencia'] for r in resultados]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Análisis Comparativo de Configuraciones de Boxes', fontsize=16)
    
    # Gráfico 1: Costo total vs número de boxes
    ax1.plot(boxes, costos, 'b-o', linewidth=2, markersize=6)
    ax1.set_xlabel('Número de Boxes')
    ax1.set_ylabel('Costo Total ($)')
    ax1.set_title('Costo Total por Configuración')
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Gráfico 2: Clientes atendidos vs perdidos
    width = 0.35
    x = np.arange(len(boxes))
    ax2.bar(x - width/2, atendidos, width, label='Atendidos', color='green', alpha=0.7)
    ax2.bar(x + width/2, perdidos, width, label='Perdidos', color='red', alpha=0.7)
    ax2.set_xlabel('Número de Boxes')
    ax2.set_ylabel('Cantidad de Clientes')
    ax2.set_title('Clientes Atendidos vs Perdidos')
    ax2.set_xticks(x)
    ax2.set_xticklabels(boxes)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Gráfico 3: Eficiencia
    ax3.plot(boxes, eficiencia, 'g-o', linewidth=2, markersize=6)
    ax3.set_xlabel('Número de Boxes')
    ax3.set_ylabel('Eficiencia (%)')
    ax3.set_title('Eficiencia de Atención')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 100)
    
    # Gráfico 4: Desglose de costos
    mejor_idx = min(range(len(resultados)), key=lambda i: resultados[i]['costo_total'])
    mejor = resultados[mejor_idx]
    
    costo_boxes = mejor['boxes'] * 1000
    costo_perdidas = mejor['clientes_perdidos'] * 10000
    
    ax4.pie([costo_boxes, costo_perdidas], 
            labels=['Costo Boxes', 'Pérdidas por Abandono'],
            colors=['lightblue', 'lightcoral'],
            autopct='%1.1f%%',
            startangle=90)
    ax4.set_title(f'Desglose de Costos\n(Configuración Óptima: {mejor["boxes"]} boxes)')
    
    plt.tight_layout()
    plt.savefig('analisis_comparativo.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Gráficos guardados en 'analisis_comparativo.png'")

def menu_interactivo():
    """Muestra un menú interactivo para el usuario"""
    print("="*60)
    print("SIMULADOR DE SISTEMA DE ATENCIÓN AL PÚBLICO")
    print("="*60)
    print("1. Simulación simple (solo estadísticas)")
    print("2. Simulación con interfaz visual")
    print("3. Simulación visual con grabación de video")
    print("4. Análisis comparativo de configuraciones")
    print("5. Salir")
    print("="*60)
    
    while True:
        try:
            opcion = input("\nSeleccione una opción (1-5): ").strip()
            
            if opcion == '1':
                num_boxes = int(input("Número de boxes (1-10): "))
                if 1 <= num_boxes <= 10:
                    ejecutar_simulacion_simple(num_boxes)
                    print("\n" + "="*60)
                    print("1. Simulación simple (solo estadísticas)")
                    print("2. Simulación con interfaz visual")
                    print("3. Simulación visual con grabación de video")
                    print("4. Análisis comparativo de configuraciones")
                    print("5. Salir")
                    print("="*60)
                else:
                    print("Número de boxes debe estar entre 1 y 10")
                    
            elif opcion == '2':
                num_boxes = int(input("Número de boxes (1-10): "))
                if 1 <= num_boxes <= 10:
                    print("Iniciando simulación visual...")
                    print("Una vez iniciada, use los controles mostrados en consola")
                    ejecutar_simulacion_visual(num_boxes, False)
                    print("\n" + "="*60)
                    print("1. Simulación simple (solo estadísticas)")
                    print("2. Simulación con interfaz visual")
                    print("3. Simulación visual con grabación de video")
                    print("4. Análisis comparativo de configuraciones")
                    print("5. Salir")
                    print("="*60)
                else:
                    print("Número de boxes debe estar entre 1 y 10")
                    
            elif opcion == '3':
                num_boxes = int(input("Número de boxes (1-10): "))
                if 1 <= num_boxes <= 10:
                    print("Iniciando simulación visual con grabación...")
                    print("Se generará un archivo 'simulacion.avi' al finalizar")
                    ejecutar_simulacion_visual(num_boxes, True)
                    print("\n" + "="*60)
                    print("1. Simulación simple (solo estadísticas)")
                    print("2. Simulación con interfaz visual")
                    print("3. Simulación visual con grabación de video")
                    print("4. Análisis comparativo de configuraciones")
                    print("5. Salir")
                    print("="*60)
                else:
                    print("Número de boxes debe estar entre 1 y 10")
                    
            elif opcion == '4':
                max_boxes = input("Número máximo de boxes a comparar (por defecto 10): ").strip()
                max_boxes = int(max_boxes) if max_boxes else 10
                if 1 <= max_boxes <= 10:
                    comparar_configuraciones(max_boxes)
                    print("\n" + "="*60)
                    print("1. Simulación simple (solo estadísticas)")
                    print("2. Simulación con interfaz visual")
                    print("3. Simulación visual con grabación de video")
                    print("4. Análisis comparativo de configuraciones")
                    print("5. Salir")
                    print("="*60)
                else:
                    print("Número debe estar entre 1 y 10")
                    
            elif opcion == '5':
                print("¡Gracias por usar el simulador!")
                sys.exit(0)
                
            else:
                print("Opción inválida. Por favor seleccione 1-5.")
                
        except ValueError:
            print("Por favor ingrese un número válido.")
        except KeyboardInterrupt:
            print("\n¡Gracias por usar el simulador!")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Función principal del programa"""
    parser = argparse.ArgumentParser(
        description='Simulador de Sistema de Atención al Público',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py                    # Menú interactivo
  python main.py -b 5               # Simulación simple con 5 boxes
  python main.py -b 3 --visual      # Simulación visual con 3 boxes
  python main.py -b 4 --video       # Simulación con video
  python main.py --compare          # Análisis comparativo
        """
    )
    
    parser.add_argument('-b', '--boxes', type=int, metavar='N',
                       help='Número de boxes (1-10)')
    parser.add_argument('--visual', action='store_true',
                       help='Ejecutar con interfaz visual')
    parser.add_argument('--video', action='store_true',
                       help='Grabar video de la simulación')
    parser.add_argument('--compare', action='store_true',
                       help='Ejecutar análisis comparativo')
    parser.add_argument('--max-boxes', type=int, default=10, metavar='N',
                       help='Número máximo de boxes para comparación (default: 10)')
    
    args = parser.parse_args()
    
    # Si no se proporcionan argumentos, mostrar menú interactivo
    if len(sys.argv) == 1:
        menu_interactivo()
        return
    
    # Validar número de boxes
    if args.boxes and not (1 <= args.boxes <= 10):
        print("Error: El número de boxes debe estar entre 1 y 10")
        sys.exit(1)
    
    # Ejecutar según los argumentos
    if args.compare:
        comparar_configuraciones(args.max_boxes)
    elif args.boxes:
        if args.video:
            print(f"Ejecutando simulación visual con {args.boxes} boxes y grabación de video...")
            ejecutar_simulacion_visual(args.boxes, True)
        elif args.visual:
            print(f"Ejecutando simulación visual con {args.boxes} boxes...")
            ejecutar_simulacion_visual(args.boxes, False)
        else:
            print(f"Ejecutando simulación simple con {args.boxes} boxes...")
            ejecutar_simulacion_simple(args.boxes)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
