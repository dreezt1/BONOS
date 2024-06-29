import streamlit as st
import pandas as pd
import os

# Configurar la página para que ocupe toda la pantalla horizontal
st.set_page_config(layout="wide")

# Definir los nombres de las columnas esperadas
column_names = [
    'Sala', 'Día', 'Inicio Sesión', 'Fin Sesión', 'Máquina', 'Sesión', 'Puntos', 
    'Input', 'Output', 'Jackpot', 'Billete', 'Ticket_Cash_In', 'Ticket_Rest_In', 
    'Aft_Cash_In', 'Aft_Rest_In', 'Aft_NO_Rest_In', 'HandPay', 'Ticket_Cash_Out', 
    'Ticket_Rest_Out', 'Aft_Cash_Out', 'Aft_Rest_Out', 'Aft_NO_Rest_Out', 'Ganado'
]

# Carpeta donde se guardarán los archivos CSV de bonos procesados
folder_path = 'bonos_procesados'

# Crear la carpeta si no existe
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Función para procesar los datos del archivo subido
def procesar_archivo(archivo, ano, mes, casino):
    try:
        df = pd.read_excel(archivo, header=6)
    except FileNotFoundError:
        st.error("El archivo no se encontró.")
        return None
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return None
    
    # Verificar si las columnas esperadas están presentes en el DataFrame
    if not set(column_names).issubset(df.columns):
        st.error(f"Las siguientes columnas faltan en el archivo: {', '.join(set(column_names) - set(df.columns))}")
        st.write("Columnas disponibles en el archivo:", df.columns.tolist())
        return None

    # Filtrar y calcular el bono para cada fila
    df['Diferencia'] = df['HandPay'] - df['Billete']
    df['Bono'] = df.apply(lambda row: calcular_bono(row), axis=1)
    
    # Agregar columna para marcar la entrega del bono (inicialmente False)
    df['Entregado'] = False
    
    # Guardar el DataFrame procesado como archivo CSV
    file_path = f'{folder_path}/{ano}_{mes}_{casino}.csv'
    df.to_csv(file_path, index=False)
    
    return df

def calcular_bono(row):
    try:
        # Calcular la diferencia entre HandPay y Billete
        diferencia = row['HandPay'] - row['Billete']
        
        # Calcular el bono como el 6.5% de la diferencia negativa si es mayor a 20000
        if diferencia < 0:
            bono = abs(diferencia) * 0.065
            # Redondear el bono al múltiplo de 10000 más cercano
            bono = round(bono / 10000) * 10000
            return bono if bono >= 20000 else 0  # Filtrar bonos menores a 20000
        else:
            return 0  # Retornar 0 si no cumple con los criterios
    except Exception as e:
        st.error(f"Error en fila {row.name}: {e}")
        return 0  # Retornar 0 en caso de error

# Pantalla inicial con menú de opciones
st.title('Sistema de Gestión de Bonos')

opcion = st.selectbox('Seleccione una opción', ['Cargar Archivo', 'Ver Bonos Procesados'])

if opcion == 'Cargar Archivo':
    password = st.text_input('Ingrese la contraseña para continuar', type='password')
    
    if password == 'riviera0001':
        st.success('Contraseña correcta. Puede continuar con la carga de archivos.')
        
        submenu = st.selectbox('Seleccione una acción', ['Subir Archivo', 'Administrar Archivos'])

        if submenu == 'Subir Archivo':
            ano_subir = st.selectbox('Seleccione el año (Subir)', range(2024, 2031), key='ano_subir')
            mes_subir = st.selectbox('Seleccione el mes (Subir)', ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'], key='mes_subir')
            casino_subir = st.selectbox('Seleccione el casino (Subir)', ['MANHATTAN', 'FARAON', 'ROYAL', 'MONACO'], key='casino_subir')
            archivo = st.file_uploader(f"Cargar archivo Excel para {mes_subir} {ano_subir} - {casino_subir}", type=['xlsx'])

            if archivo is not None:
                bonos_df = procesar_archivo(archivo, ano_subir, mes_subir, casino_subir)
                if bonos_df is not None and 'Bono' in bonos_df.columns:  # Ensure 'Bono' column exists
                    st.success(f'Archivo para {mes_subir} {ano_subir} - {casino_subir} procesado exitosamente.')

        elif submenu == 'Administrar Archivos':
            st.subheader('Administrar Archivos Cargados')

            archivos = os.listdir(folder_path)
            if not archivos:
                st.info('No hay archivos cargados actualmente.')
            else:
                archivo_a_eliminar = st.selectbox('Seleccione el archivo a eliminar', archivos)
                clave_eliminar = st.text_input('Ingrese la clave para eliminar el archivo', type='password')
                
                if clave_eliminar == 'riviera0001' and st.button('Eliminar'):
                    os.remove(os.path.join(folder_path, archivo_a_eliminar))
                    st.success(f'Archivo {archivo_a_eliminar} eliminado exitosamente.')

elif opcion == 'Ver Bonos Procesados':
    ver_ano = st.selectbox('Seleccione el año (Ver)', range(2024, 2031), key='ver_ano')
    ver_mes = st.selectbox('Seleccione el mes (Ver)', ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'], key='ver_mes')
    ver_casino = st.selectbox('Seleccione el casino (Ver)', ['MANHATTAN', 'FARAON', 'ROYAL', 'MONACO'], key='ver_casino')

    if st.button('Ver Bonos'):
        file_path = f'{folder_path}/{ver_ano}_{ver_mes}_{ver_casino}.csv'
        if os.path.exists(file_path):
            bonos_df = pd.read_csv(file_path)
            # Ensure 'Bono' column exists
            if 'Bono' in bonos_df.columns:
                bonos_df = bonos_df[bonos_df['Bono'] > 0]  # Filtrar bonos positivos
                
                # Mostrar la tabla de bonos con el formato deseado
                st.subheader(f'Bonos para {ver_mes} {ver_ano} - {ver_casino}')
                bonos_df['Entregado'] = bonos_df.apply(lambda row: st.checkbox(f'Entregar a {row["Sala"]}', row['Entregado']), axis=1)
                st.table(bonos_df[['Sala', 'Bono', 'Entregado']])  # Usar st.table para mostrar la tabla completa
                
                # Guardar el DataFrame modificado de vuelta al archivo CSV al hacer clic en un botón
                if st.button('Guardar cambios'):
                    bonos_df.to_csv(file_path, index=False)
                    st.success(f'Información de entrega guardada para {ver_mes} {ver_ano} - {ver_casino}.')
            else:
                st.warning('No se encontraron bonos procesados para mostrar.')
        else:
            st.warning(f'No se encontró el archivo {file_path}. Sube un archivo primero.')
