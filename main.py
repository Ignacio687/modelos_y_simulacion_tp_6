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

def ejecutar_simulacion_visual(num_boxes: int, grabar_video: bool = False, velocidad_inicial: float = 1.0):
    """Ejecuta la simulación con interfaz visual"""
    simulador = SimuladorAtencion(num_boxes)
    interfaz = InterfazVisual(simulador)
    interfaz.animar_simulacion(grabar_video, velocidad_inicial)

def comparar_configuraciones(max_boxes: int = 10, num_iteraciones: int = 10):
    """Compara diferentes configuraciones de boxes con múltiples simulaciones"""
    import time
    
    total_simulaciones = max_boxes * num_iteraciones
    print(f"Comparando configuraciones de boxes...")
    print(f"Ejecutando {num_iteraciones} simulaciones por cada configuración (1-{max_boxes} boxes)")
    print(f"Total de simulaciones: {total_simulaciones}")
    
    # Estimación de tiempo
    if total_simulaciones >= 100:
        tiempo_estimado = total_simulaciones * 2  # Aproximadamente 2 segundos por simulación
        minutos = tiempo_estimado // 60
        segundos = tiempo_estimado % 60
        print(f"Tiempo estimado: ~{minutos} min {segundos} seg")
    
    print("Esto puede tomar varios minutos...\n")
    
    resultados = []
    tiempo_inicio = time.time()
    
    for num_boxes in range(1, max_boxes + 1):
        print(f"Simulando con {num_boxes} boxes ({num_iteraciones} iteraciones)...")
        
        # Listas para almacenar resultados de cada iteración
        costos_totales = []
        clientes_atendidos_list = []
        clientes_perdidos_list = []
        eficiencias = []
        clientes_ingresaron_list = []
        
        for iteracion in range(num_iteraciones):
            if num_iteraciones > 1:
                progreso = ((iteracion + 1) / num_iteraciones) * 100
                print(f"  Iteración {iteracion + 1}/{num_iteraciones} ({progreso:.1f}%)...", end="")
            
            simulador = ejecutar_simulacion_simple(num_boxes, False)
            stats = simulador.obtener_estadisticas()
            
            costos_totales.append(stats['costo_total'])
            clientes_atendidos_list.append(stats['clientes_atendidos'])
            clientes_perdidos_list.append(stats['clientes_no_atendidos'])
            clientes_ingresaron_list.append(stats['clientes_ingresaron'])
            eficiencia = stats['clientes_atendidos'] / max(1, stats['clientes_ingresaron']) * 100
            eficiencias.append(eficiencia)
            
            if num_iteraciones > 1:
                print(f" ${stats['costo_total']:,}")
            
            # Mostrar progreso parcial cada 25 iteraciones para simulaciones largas
            if num_iteraciones >= 50 and (iteracion + 1) % 25 == 0:
                costo_parcial = np.mean(costos_totales)
                eficiencia_parcial = np.mean(eficiencias)
                print(f"    Progreso parcial - Costo promedio: ${costo_parcial:,.0f}, Eficiencia: {eficiencia_parcial:.1f}%")
        
        # Calcular promedios y desviaciones estándar
        costo_promedio = np.mean(costos_totales)
        costo_std = np.std(costos_totales)
        atendidos_promedio = np.mean(clientes_atendidos_list)
        atendidos_std = np.std(clientes_atendidos_list)
        perdidos_promedio = np.mean(clientes_perdidos_list)
        perdidos_std = np.std(clientes_perdidos_list)
        eficiencia_promedio = np.mean(eficiencias)
        eficiencia_std = np.std(eficiencias)
        ingresaron_promedio = np.mean(clientes_ingresaron_list)
        
        resultados.append({
            'boxes': num_boxes,
            'costo_total': costo_promedio,
            'costo_std': costo_std,
            'clientes_atendidos': atendidos_promedio,
            'clientes_atendidos_std': atendidos_std,
            'clientes_perdidos': perdidos_promedio,
            'clientes_perdidos_std': perdidos_std,
            'clientes_ingresaron': ingresaron_promedio,
            'eficiencia': eficiencia_promedio,
            'eficiencia_std': eficiencia_std,
            'num_iteraciones': num_iteraciones
        })
        
        print(f"  Promedio - Costo: ${costo_promedio:,.0f} (±${costo_std:,.0f})")
        print(f"  Promedio - Atendidos: {atendidos_promedio:.1f} (±{atendidos_std:.1f})")
        print(f"  Promedio - Perdidos: {perdidos_promedio:.1f} (±{perdidos_std:.1f})")
        print(f"  Promedio - Eficiencia: {eficiencia_promedio:.1f}% (±{eficiencia_std:.1f}%)\n")
    
    # Encontrar configuración óptima (más flexible - considera eficiencia y costo)
    # Criterio flexible: dentro del 5% del menor costo, priorizar eficiencia
    config_menor_costo = min(resultados, key=lambda x: x['costo_total'])
    costo_minimo = config_menor_costo['costo_total']
    umbral_costo_flexibilidad = costo_minimo * 1.05  # 5% de tolerancia
    
    # Entre las configuraciones dentro del 5% del menor costo, elegir la de mayor eficiencia
    candidatos_optimos = [r for r in resultados if r['costo_total'] <= umbral_costo_flexibilidad]
    mejor_config = max(candidatos_optimos, key=lambda x: x['eficiencia'])
    
    # Encontrar configuración que asegura NO perder clientes (más restrictivo)
    # Criterio restrictivo: menos de 1.0 cliente perdido promedio (prácticamente cero)
    config_sin_perdidas = None
    umbral_perdidas = 0.1  # Menos de 1.0 cliente perdido promedio
    
    print("📊 Análisis de pérdidas por configuración:")
    for config in sorted(resultados, key=lambda x: x['boxes']):
        perdidas = config['clientes_perdidos']
        print(f"   {config['boxes']} boxes: {perdidas:.2f} clientes perdidos promedio")
        if config_sin_perdidas is None and perdidas < umbral_perdidas:  # Cambié <= por <
            config_sin_perdidas = config
            print(f"   ✅ Primera configuración sin pérdidas: {config['boxes']} boxes (<{umbral_perdidas} clientes)")
    
    # Si no hay configuración con pérdidas < 1.0, relajar criterio gradualmente
    if config_sin_perdidas is None:
        # Probar con 2.0, luego 5.0, etc.
        for umbral_relajado in [1.1, 1.2, 1.5, 2.0, 5.0, 10.0]:
            for config in sorted(resultados, key=lambda x: x['boxes']):
                if config['clientes_perdidos'] < umbral_relajado:
                    config_sin_perdidas = config
                    print(f"   ⚠️  Relajando criterio: {config['boxes']} boxes (<{umbral_relajado} clientes)")
                    break
            if config_sin_perdidas:
                break
    
    # Si aún no hay, usar la de menor pérdida
    if config_sin_perdidas is None:
        config_sin_perdidas = min(resultados, key=lambda x: x['clientes_perdidos'])
        print(f"   ❌ No hay configuración sin pérdidas, usando la de menor pérdida: {config_sin_perdidas['boxes']} boxes")
    print()
    
    tiempo_total = time.time() - tiempo_inicio
    minutos_total = int(tiempo_total // 60)
    segundos_total = int(tiempo_total % 60)
    
    print("="*80)
    print("ANÁLISIS COMPARATIVO CON MÚLTIPLES SIMULACIONES")
    print("="*80)
    print(f"🏆 Configuración óptima (mejor balance costo-eficiencia): {mejor_config['boxes']} boxes")
    if mejor_config['boxes'] != config_menor_costo['boxes']:
        print(f"   📈 Seleccionada por mayor eficiencia dentro del 5% del menor costo")
        print(f"   💰 Costo de referencia (mínimo): ${config_menor_costo['costo_total']:,.0f}")
    else:
        print(f"   💰 También es la configuración de menor costo absoluto")
    print(f"   Costo promedio: ${mejor_config['costo_total']:,.0f} (±${mejor_config['costo_std']:,.0f})")
    print(f"   Eficiencia: {mejor_config['eficiencia']:.1f}% (±{mejor_config['eficiencia_std']:.1f}%)")
    print(f"   Clientes perdidos: {mejor_config['clientes_perdidos']:.2f} (±{mejor_config['clientes_perdidos_std']:.2f})")
    print()
    print(f"🛡️  Configuración que elimina pérdidas de clientes: {config_sin_perdidas['boxes']} boxes")
    if config_sin_perdidas['clientes_perdidos'] <= 0.3:
        print(f"   ✅ Prácticamente CERO pérdidas de clientes")
    elif config_sin_perdidas['clientes_perdidos'] <= 0.5:
        print(f"   ✅ Pérdidas mínimas de clientes")
    else:
        print(f"   ⚠️  Configuración de menor pérdida disponible")
    print(f"   Costo promedio: ${config_sin_perdidas['costo_total']:,.0f} (±${config_sin_perdidas['costo_std']:,.0f})")
    print(f"   Eficiencia: {config_sin_perdidas['eficiencia']:.1f}% (±{config_sin_perdidas['eficiencia_std']:.1f}%)")
    print(f"   Clientes perdidos: {config_sin_perdidas['clientes_perdidos']:.2f} (±{config_sin_perdidas['clientes_perdidos_std']:.2f})")
    print()
    
    # Análisis de diferencia de costo
    diferencia_costo = config_sin_perdidas['costo_total'] - mejor_config['costo_total']
    diferencia_boxes = config_sin_perdidas['boxes'] - mejor_config['boxes']
    
    if diferencia_costo > 0:
        if config_sin_perdidas['clientes_perdidos'] <= 0.1:
            print(f"💰 Costo adicional para ELIMINAR pérdidas: +${diferencia_costo:,.0f}")
        else:
            print(f"💰 Costo adicional para minimizar pérdidas: +${diferencia_costo:,.0f}")
        porcentaje_aumento = (diferencia_costo / mejor_config['costo_total']) * 100
        print(f"   Aumento porcentual: +{porcentaje_aumento:.1f}%")
        print(f"   Boxes adicionales necesarios: +{diferencia_boxes}")
        
        # Calcular el costo por cliente no perdido
        clientes_salvados = mejor_config['clientes_perdidos'] - config_sin_perdidas['clientes_perdidos']
        if clientes_salvados > 0:
            costo_por_cliente_salvado = diferencia_costo / clientes_salvados
            print(f"   Costo por cliente no perdido: ${costo_por_cliente_salvado:,.0f}")
            
    elif diferencia_costo == 0:
        print(f"✨ ¡La configuración óptima también elimina las pérdidas de clientes!")
    else:
        print(f"🎯 ¡La configuración sin pérdidas es TAMBIÉN más económica!")
        ahorro = abs(diferencia_costo)
        porcentaje_ahorro = (ahorro / config_sin_perdidas['costo_total']) * 100
        print(f"   Ahorro adicional: ${ahorro:,.0f} ({porcentaje_ahorro:.1f}%)")
    
    print()
    print(f"Iteraciones por configuración: {num_iteraciones}")
    print(f"Tiempo total de análisis: {minutos_total} min {segundos_total} seg")
    print("="*80)
    
    # Generar gráficos
    generar_graficos_comparacion(resultados)
    
    return resultados

def generar_graficos_comparacion(resultados):
    """Genera gráficos comparativos de las configuraciones con barras de error"""
    boxes = [r['boxes'] for r in resultados]
    costos = [r['costo_total'] for r in resultados]
    costos_std = [r.get('costo_std', 0) for r in resultados]
    atendidos = [r['clientes_atendidos'] for r in resultados]
    atendidos_std = [r.get('clientes_atendidos_std', 0) for r in resultados]
    perdidos = [r['clientes_perdidos'] for r in resultados]
    perdidos_std = [r.get('clientes_perdidos_std', 0) for r in resultados]
    eficiencia = [r['eficiencia'] for r in resultados]
    eficiencia_std = [r.get('eficiencia_std', 0) for r in resultados]
    
    num_iteraciones = resultados[0].get('num_iteraciones', 1)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    titulo_principal = f'Análisis Comparativo de Configuraciones de Boxes'
    if num_iteraciones > 1:
        titulo_principal += f'\n(Promedio de {num_iteraciones} simulaciones por configuración)'
    fig.suptitle(titulo_principal, fontsize=16)
    
    # Gráfico 1: Costo total vs número de boxes con barras de error
    ax1.errorbar(boxes, costos, yerr=costos_std, fmt='b-o', linewidth=2, markersize=6, 
                capsize=5, capthick=2, elinewidth=1.5)
    
    # Marcar configuración óptima (mejor balance costo-eficiencia)
    config_menor_costo = min(resultados, key=lambda x: x['costo_total'])
    costo_minimo = config_menor_costo['costo_total']
    umbral_costo_flexibilidad = costo_minimo * 1.05
    candidatos_optimos = [r for r in resultados if r['costo_total'] <= umbral_costo_flexibilidad]
    mejor_config_grafico = max(candidatos_optimos, key=lambda x: x['eficiencia'])
    
    mejor_idx = next(i for i, r in enumerate(resultados) if r['boxes'] == mejor_config_grafico['boxes'])
    ax1.plot(resultados[mejor_idx]['boxes'], resultados[mejor_idx]['costo_total'], 
             'go', markersize=12, label=f'Óptimo: {resultados[mejor_idx]["boxes"]} boxes')
    
    # Marcar configuración sin pérdidas (criterio restrictivo)
    config_sin_perdidas_idx = None
    for i, config in enumerate(resultados):
        if config['clientes_perdidos'] < 1.0:  # Criterio restrictivo pero realista
            config_sin_perdidas_idx = i
            break
    
    # Si no encuentra con < 1.0, relajar gradualmente
    if config_sin_perdidas_idx is None:
        for umbral in [2.0, 5.0, 10.0]:
            for i, config in enumerate(resultados):
                if config['clientes_perdidos'] < umbral:
                    config_sin_perdidas_idx = i
                    break
            if config_sin_perdidas_idx is not None:
                break
    
    # Si aún no encuentra, usar el de menor pérdida
    if config_sin_perdidas_idx is None:
        config_sin_perdidas_idx = min(range(len(resultados)), key=lambda i: resultados[i]['clientes_perdidos'])
    
    label_sin_perdidas = f'Sin pérdidas: {resultados[config_sin_perdidas_idx]["boxes"]} boxes'
    if resultados[config_sin_perdidas_idx]['clientes_perdidos'] >= 1.0:
        label_sin_perdidas = f'Min. pérdidas: {resultados[config_sin_perdidas_idx]["boxes"]} boxes'
    
    ax1.plot(resultados[config_sin_perdidas_idx]['boxes'], resultados[config_sin_perdidas_idx]['costo_total'], 
             'ro', markersize=12, label=label_sin_perdidas)
    
    ax1.set_xlabel('Número de Boxes')
    ax1.set_ylabel('Costo Total ($)')
    ax1.set_title('Costo Total por Configuración')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Gráfico 2: Clientes atendidos vs perdidos con barras de error
    width = 0.35
    x = np.arange(len(boxes), dtype=float)
    bars1 = ax2.bar(x - width/2, atendidos, width, label='Atendidos', 
                    color='green', alpha=0.7, yerr=atendidos_std, capsize=4)
    bars2 = ax2.bar(x + width/2, perdidos, width, label='Perdidos', 
                    color='red', alpha=0.7, yerr=perdidos_std, capsize=4)
    ax2.set_xlabel('Número de Boxes')
    ax2.set_ylabel('Cantidad de Clientes')
    ax2.set_title('Clientes Atendidos vs Perdidos')
    ax2.set_xticks(x)
    ax2.set_xticklabels(boxes)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Gráfico 3: Eficiencia con barras de error
    ax3.errorbar(boxes, eficiencia, yerr=eficiencia_std, fmt='g-o', linewidth=2, 
                markersize=6, capsize=5, capthick=2, elinewidth=1.5)
    ax3.set_xlabel('Número de Boxes')
    ax3.set_ylabel('Eficiencia (%)')
    ax3.set_title('Eficiencia de Atención')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 105)  # Ajustado para mostrar un poco por encima del 100%
    
    # Gráfico 4: Desglose de costos de la configuración óptima
    # Usar la misma lógica que en el análisis principal
    config_menor_costo = min(resultados, key=lambda x: x['costo_total'])
    costo_minimo = config_menor_costo['costo_total']
    umbral_costo_flexibilidad = costo_minimo * 1.05
    candidatos_optimos = [r for r in resultados if r['costo_total'] <= umbral_costo_flexibilidad]
    mejor = max(candidatos_optimos, key=lambda x: x['eficiencia'])
    
    # Encontrar configuración sin pérdidas para comparación (criterio restrictivo)
    config_sin_perdidas = None
    for config in resultados:
        if config['clientes_perdidos'] < 1.0:  # Criterio restrictivo pero realista
            config_sin_perdidas = config
            break
    
    # Relajar criterio si es necesario
    if config_sin_perdidas is None:
        for umbral in [2.0, 5.0, 10.0]:
            for config in resultados:
                if config['clientes_perdidos'] < umbral:
                    config_sin_perdidas = config
                    break
            if config_sin_perdidas:
                break
    
    if config_sin_perdidas is None:
        config_sin_perdidas = min(resultados, key=lambda x: x['clientes_perdidos'])
    
    costo_boxes = mejor['boxes'] * 1000
    costo_perdidas = mejor['clientes_perdidos'] * 10000
    
    # Colores más distintivos
    colors = ['#66b3ff', '#ff9999']  # Azul claro y rojo claro
    wedges, texts, autotexts = ax4.pie([costo_boxes, costo_perdidas], 
            labels=['Costo Boxes', 'Pérdidas por Abandono'],
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            explode=(0.05, 0.05))  # Separar un poco las secciones
    
    # Mejorar el formato del texto
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    titulo_pie = f'Desglose de Costos - Configuración Óptima\n({mejor["boxes"]} boxes - Balance costo-eficiencia)'
    if num_iteraciones > 1:
        titulo_pie += f'\nCosto promedio: ${mejor["costo_total"]:,.0f} (±${mejor.get("costo_std", 0):,.0f})'
    
    # Agregar información sobre configuración sin pérdidas
    if config_sin_perdidas['boxes'] != mejor['boxes']:
        if config_sin_perdidas['clientes_perdidos'] <= 0.1:
            titulo_pie += f'\n\nCero pérdidas: {config_sin_perdidas["boxes"]} boxes'
        else:
            titulo_pie += f'\n\nMin. pérdidas: {config_sin_perdidas["boxes"]} boxes'
        titulo_pie += f' (${config_sin_perdidas["costo_total"]:,.0f})'
    
    ax4.set_title(titulo_pie)
    
    plt.tight_layout()
    
    # Guardar con nombre que incluya número de iteraciones
    filename = f'analisis_comparativo_{num_iteraciones}_iter.png' if num_iteraciones > 1 else 'analisis_comparativo.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Gráficos guardados en '{filename}'")

def mostrar_menu():
    """Muestra las opciones del menú"""
    print("="*60)
    print("SIMULADOR DE SISTEMA DE ATENCIÓN AL PÚBLICO")
    print("="*60)
    print("1. Simulación simple (solo estadísticas)")
    print("2. Simulación con interfaz visual")
    print("3. Simulación visual con grabación de video")
    print("4. Análisis comparativo de configuraciones")
    print("5. Salir")
    print("="*60)

def esperar_enter():
    """Espera a que el usuario presione Enter"""
    input("\nPresione Enter para continuar...")

def menu_interactivo():
    """Muestra un menú interactivo para el usuario"""
    mostrar_menu()
    
    while True:
        try:
            opcion = input("\nSeleccione una opción (1-5): ").strip()
            
            if opcion == '1':
                num_boxes = int(input("Número de boxes (1-10): "))
                if 1 <= num_boxes <= 10:
                    ejecutar_simulacion_simple(num_boxes)
                    esperar_enter()
                    mostrar_menu()
                else:
                    print("Número de boxes debe estar entre 1 y 10")
                    
            elif opcion == '2':
                num_boxes = int(input("Número de boxes (1-10): "))
                if 1 <= num_boxes <= 10:
                    print("Iniciando simulación visual...")
                    print("Una vez iniciada, use los controles mostrados en consola")
                    ejecutar_simulacion_visual(num_boxes, False)
                    esperar_enter()
                    mostrar_menu()
                else:
                    print("Número de boxes debe estar entre 1 y 10")
                    
            elif opcion == '3':
                num_boxes = int(input("Número de boxes (1-10): "))
                velocidad = input("Velocidad inicial (0.25, 0.5, 1, 2, 4, 8, 16, 32) [1]: ").strip()
                velocidad = float(velocidad) if velocidad else 1.0
                
                if 1 <= num_boxes <= 10 and velocidad in [0.25, 0.5, 1, 2, 4, 8, 16, 32]:
                    print("Iniciando simulación visual con grabación...")
                    print(f"Velocidad inicial: {velocidad}x")
                    print("Se generará un archivo 'simulacion.avi' al finalizar")
                    ejecutar_simulacion_visual(num_boxes, True, velocidad)
                    esperar_enter()
                    mostrar_menu()
                else:
                    if not (1 <= num_boxes <= 10):
                        print("Número de boxes debe estar entre 1 y 10")
                    if velocidad not in [0.25, 0.5, 1, 2, 4, 8, 16, 32]:
                        print("Velocidad debe ser una de: 0.25, 0.5, 1, 2, 4, 8, 16, 32")
                    
            elif opcion == '4':
                max_boxes = input("Número máximo de boxes para comparar [10]: ").strip()
                max_boxes = int(max_boxes) if max_boxes else 10
                
                iteraciones = input("Número de simulaciones por configuración (1-200) [10]: ").strip()
                iteraciones = int(iteraciones) if iteraciones else 10
                
                if not (1 <= max_boxes <= 10):
                    print("Número máximo de boxes debe estar entre 1 y 10")
                elif not (1 <= iteraciones <= 200):
                    print("Número de iteraciones debe estar entre 1 y 200")
                else:
                    if iteraciones == 1:
                        print("Ejecutando análisis con una sola simulación por configuración...")
                    else:
                        print(f"Ejecutando análisis con {iteraciones} simulaciones por configuración...")
                        print("Los resultados mostrarán promedios y desviaciones estándar.")
                    
                    comparar_configuraciones(max_boxes, iteraciones)
                    esperar_enter()
                    mostrar_menu()
                    
            elif opcion == '5':
                print("¡Gracias por usar el simulador!")
                sys.exit(0)
                
            else:
                print("Opción no válida. Seleccione 1-5.")
                
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
        python main.py                          # Menú interactivo
        python main.py -b 5                     # Simulación simple con 5 boxes
        python main.py -b 3 --visual            # Simulación visual con 3 boxes
        python main.py -b 4 --video             # Simulación con video
        python main.py -b 4 --video --speed 16  # Video a velocidad 16x
        python main.py -b 4 --video --speed 32  # Video a velocidad 32x
        python main.py --compare                 # Análisis comparativo (10 iter/config)
        python main.py --compare --iterations 50 # Análisis con 50 iter/config
        python main.py --compare --max-boxes 5 --iterations 100  # 5 boxes max, 100 iter/config
        python main.py --compare --iterations 200 # Máxima precisión: 200 iter/config
                """
    )
    
    parser.add_argument('-b', '--boxes', type=int, metavar='N',
                       help='Número de boxes (1-10)')
    parser.add_argument('--visual', action='store_true',
                       help='Ejecutar con interfaz visual')
    parser.add_argument('--video', action='store_true',
                       help='Grabar video de la simulación')
    parser.add_argument('--speed', type=float, default=1.0, metavar='N',
                       help='Velocidad inicial de simulación (0.25, 0.5, 1, 2, 4, 8, 16, 32)')
    parser.add_argument('--compare', action='store_true',
                       help='Ejecutar análisis comparativo')
    parser.add_argument('--max-boxes', type=int, default=10, metavar='N',
                       help='Número máximo de boxes para comparación (default: 10)')
    parser.add_argument('--iterations', type=int, default=10, metavar='N',
                       help='Número de simulaciones por configuración en análisis comparativo (1-200, default: 10)')
    
    args = parser.parse_args()
    
    # Si no se proporcionan argumentos, mostrar menú interactivo
    if len(sys.argv) == 1:
        menu_interactivo()
        return
    
    # Validar número de boxes
    if args.boxes and not (1 <= args.boxes <= 10):
        print("Error: El número de boxes debe estar entre 1 y 10")
        sys.exit(1)
    
    # Validar velocidad
    velocidades_validas = [0.25, 0.5, 1, 2, 4, 8, 16, 32]
    if args.speed not in velocidades_validas:
        print(f"Error: La velocidad debe ser una de: {velocidades_validas}")
        print(f"Velocidad proporcionada: {args.speed}")
        sys.exit(1)
    
    # Validar número de iteraciones
    if args.iterations and not (1 <= args.iterations <= 200):
        print("Error: El número de iteraciones debe estar entre 1 y 200")
        sys.exit(1)
    
    # Ejecutar según los argumentos
    if args.compare:
        comparar_configuraciones(args.max_boxes, args.iterations)
    elif args.boxes:
        if args.video:
            print(f"Ejecutando simulación visual con {args.boxes} boxes y grabación de video...")
            if args.speed != 1.0:
                print(f"Velocidad inicial: {args.speed}x")
            ejecutar_simulacion_visual(args.boxes, True, args.speed)
        elif args.visual:
            print(f"Ejecutando simulación visual con {args.boxes} boxes...")
            if args.speed != 1.0:
                print(f"Velocidad inicial: {args.speed}x")
            ejecutar_simulacion_visual(args.boxes, False, args.speed)
        else:
            print(f"Ejecutando simulación simple con {args.boxes} boxes...")
            ejecutar_simulacion_simple(args.boxes)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
