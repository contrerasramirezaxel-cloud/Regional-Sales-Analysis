# ==================================================
# PROYECTO: Análisis y Automatización de Ventas Regionales
# PAÍSES OBJETIVO: Colombia, Costa Rica y México
# HERRAMIENTAS: Python 3.10+ | SQL Server 2022
# UBICACIÓN DEL PROYECTO: C:\Users\contr\OneDrive\Documentos
# DESCRIPCIÓN: Script automatizado para la extracción, limpieza, transformación 
#              y exportación de datos de ventas regionales. Optimiza el flujo de trabajo 
#              y garantiza la calidad de la información para análisis posteriores.
# ESTADO: Código funcional, optimizado y listo para implementación
# ==================================================

# ==================================================
# 1. IMPORTACIÓN DE LIBRERÍAS REQUERIDAS
# ==================================================
import pandas as pd
import pyodbc
import numpy as np
from datetime import datetime
import os

# --------------------------------------------------
# CONFIGURACIÓN DE RUTAS - AJUSTADO A TU UBICACIÓN
# --------------------------------------------------
RUTA_PROYECTO = r'C:\Users\contr\OneDrive\Documentos'
os.chdir(RUTA_PROYECTO)
print(f"📂 Directorio de trabajo establecido: {RUTA_PROYECTO}")


# ==================================================
# 2. FUNCIÓN: CONEXIÓN A LA BASE DE DATOS
# Propósito: Establecer comunicación segura y estable con SQL Server
# ==================================================
def conectar_base_datos():
    """
    Función que crea y valida la conexión con la base de datos.
    Retorna: Objeto de conexión activo
    """
    try:
        # ✅ DATOS EXACTOS SEGÚN TU IMAGEN
        conexion = pyodbc.connect(
            'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=localhost;'             
            'DATABASE=master;'              
            'Trusted_Connection=yes;'
            'Encrypt=yes;'
            'TrustServerCertificate=yes;'
        )
        print("✅ Conexión establecida exitosamente con SQL Server")
        return conexion

    except Exception as error:
        print(f"❌ Error de conexión: {str(error)}")
        raise SystemExit("No se pudo establecer conexión. Proceso finalizado.")


# ==================================================
# 3. FUNCIÓN: LIMPIEZA Y TRANSFORMACIÓN DE DATOS
# Propósito: Garantizar calidad, consistencia y crear nuevas métricas de valor
# ==================================================
def limpiar_y_transformar(datos_brutos):
    """
    Procesa el conjunto de datos aplicando reglas de negocio y calidad:
    - Eliminación de duplicados
    - Manejo de valores nulos
    - Corrección de tipos de datos
    - Validación geográfica
    - Creación de indicadores de rentabilidad
    
    Parámetro: DataFrame con la información extraída
    Retorna: DataFrame limpio y enriquecido
    """
    # Crear copia para preservar los datos originales
    df = datos_brutos.copy()

    # --------------------------------------------------
    # APLICACIÓN DE REGLAS DE CALIDAD
    # --------------------------------------------------
    
    # Eliminar registros duplicados basados en el identificador único de venta
    df = df.drop_duplicates(subset=['id_venta'], keep='first')

    # Manejo de valores nulos o vacíos
    df['porcentaje_margen'] = df['porcentaje_margen'].fillna(0.00)
    df['tipo_pago'] = df['tipo_pago'].fillna('No Especificado')

    # Estandarización y corrección de tipos de datos
    df['cantidad_vendida'] = df['cantidad_vendida'].astype(int)
    df['monto_total'] = df['monto_total'].astype(float)

    # Eliminación de registros con valores no válidos
    df = df[df['monto_total'] > 0]

    # Validación estricta de países permitidos
    paises_permitidos = ['Colombia', 'Costa Rica', 'México']
    df = df[df['pais'].isin(paises_permitidos)]

    # --------------------------------------------------
    # CREACIÓN DE NUEVOS INDICADORES DE NEGOCIO
    # --------------------------------------------------
    
    # Porcentaje de rentabilidad por transacción
    df['rentabilidad_porcentaje'] = np.where(
        df['monto_total'] > 0,
        (df['margen_ganancia'] / df['monto_total']) * 100,
        0.00
    ).round(2)

    # Clasificación del nivel de rentabilidad
    df['nivel_rentabilidad'] = np.select(
        condlist=[
            df['rentabilidad_porcentaje'] > 30,
            df['rentabilidad_porcentaje'] > 15
        ],
        choicelist=['Alta', 'Media'],
        default='Baja'
    )

    print(f"✅ Transformación finalizada | Registros válidos procesados: {len(df)}")
    return df


# ==================================================
# 4. FUNCIÓN: GENERACIÓN DE ANÁLISIS AGRUPADOS
# Propósito: Crear resúmenes estadísticos para análisis comparativo regional
# ==================================================
def generar_analisis_agrupados(datos_procesados):
    """
    Genera tablas resumen con indicadores clave de rendimiento:
    - Ventas y rentabilidad por país y año
    - Desempeño de ventas por ciudad
    - Comportamiento de productos por región
    
    Parámetro: DataFrame limpio y transformado
    Retorna: Tres conjuntos de datos con análisis consolidados
    """
    # Análisis: Ventas y rentabilidad por país y año
    ventas_pais_anio = datos_procesados.groupby(['pais', 'anio']).agg(
        cantidad_ventas=('id_venta', 'count'),
        monto_total=('monto_total', 'sum'),
        promedio_venta=('monto_total', 'mean'),
        margen_total=('margen_ganancia', 'sum'),
        rentabilidad_promedio=('rentabilidad_porcentaje', 'mean')
    ).round(2).sort_values(['pais', 'anio'])

    # Análisis: Desempeño de ventas por ciudad
    desempeño_ciudad = datos_procesados.groupby(['pais', 'ciudad']).agg(
        cantidad_ventas=('id_venta', 'count'),
        monto_total=('monto_total', 'sum'),
        unidades_vendidas=('cantidad_vendida', 'sum')
    ).round(2).sort_values(['pais', 'monto_total'], ascending=[True, False])

    # Análisis: Productos más vendidos por región
    productos_regionales = datos_procesados.groupby(['pais', 'categoria', 'nombre_producto']).agg(
        cantidad_vendida=('cantidad_vendida', 'sum'),
        monto_total=('monto_total', 'sum'),
        margen_total=('margen_ganancia', 'sum'),
        rentabilidad_promedio=('rentabilidad_porcentaje', 'mean')
    ).round(2).sort_values(['pais', 'monto_total'], ascending=[True, False])

    print("✅ Análisis agrupados generados correctamente")
    return ventas_pais_anio, desempeño_ciudad, productos_regionales


# ==================================================
# 5. FUNCIÓN: EXPORTACIÓN DE RESULTADOS A EXCEL
# Propósito: Almacenar la información procesada en formato accesible y estructurado
# ==================================================
def exportar_a_excel(datos_limpios, resumen_pais, ciudades, productos):
    """
    Crea un archivo Excel con múltiples hojas que contienen toda la información procesada:
    - Hoja 1: Datos completos y limpios
    - Hoja 2: Resumen estadístico por país y año
    - Hoja 3: Desempeño de ventas por ciudad
    - Hoja 4: Análisis de productos por región
    
    Parámetros: Todos los conjuntos de datos generados
    Retorna: Ruta completa del archivo creado
    """
    # Nombre de archivo único con marca de tiempo
    nombre_archivo = f"Analisis_Ventas_Regionales_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    ruta_completa = os.path.join(RUTA_PROYECTO, nombre_archivo)

    # Creación y escritura del archivo Excel
    with pd.ExcelWriter(ruta_completa, engine='openpyxl') as escritor:
        # Hoja 1: Datos completos
        datos_limpios.to_excel(escritor, sheet_name='Datos_Completos', index=False)
        
        # Hoja 2: Resumen por país y año
        resumen_pais.to_excel(escritor, sheet_name='Resumen_Por_Pais_Y_Año')
        
        # Hoja 3: Desempeño por ciudad
        ciudades.to_excel(escritor, sheet_name='Desempeno_Por_Ciudad')
        
        # Hoja 4: Análisis de productos
        productos.to_excel(escritor, sheet_name='Productos_Por_Region')

    print(f"📁 Archivo Excel generado exitosamente en: {ruta_completa}")
    return ruta_completa


# ==================================================
# 🚀 EJECUCIÓN DEL PROCESO COMPLETO
# ==================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO PROCESO AUTOMATIZADO DE ANÁLISIS REGIONAL")
    print("🌎 Países objetivo: Colombia, Costa Rica y México")
    print("=" * 60)

    try:
        # Paso 1: Conexión con la base de datos
        conexion = conectar_base_datos()

        # Paso 2: Extracción de datos desde la vista consolidada
        consulta_sql = "SELECT * FROM vw_VentasAnalizadas"
        datos_brutos = pd.read_sql(consulta_sql, conexion)
        print(f"📥 Datos extraídos de la base: {len(datos_brutos)} registros")

        # Paso 3: Limpieza y transformación
        datos_procesados = limpiar_y_transformar(datos_brutos)

        # Paso 4: Generación de análisis estadísticos
        resumen_pais, desempeño_ciudades, productos_regionales = generar_analisis_agrupados(datos_procesados)

        # Paso 5: Exportación final a Excel
        archivo_generado = exportar_a_excel(datos_procesados, resumen_pais, desempeño_ciudades, productos_regionales)

        # Paso 6: Cierre de conexión
        conexion.close()
        print("🔌 Conexión con la base de datos cerrada correctamente")

        print("\n" + "=" * 60)
        print("✨ PROCESO FINALIZADO AL 100% DE FORMA AUTOMÁTICA")
        print(f"📂 Resultados guardados en: {RUTA_PROYECTO}")
        print("=" * 60)

    except Exception as error_general:
        print(f"\n❌ PROCESO INTERRUMPIDO: {str(error_general)}")
        print("Revise la configuración y vuelva a intentarlo")
    
