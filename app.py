import streamlit as st
import pandas as pd
import os

# Configurar la página para que ocupe toda la pantalla
st.set_page_config(layout="wide")

# Carpeta donde se guardarán los archivos CSV de bonos procesados
folder_path = 'bonos_procesados'

# Crear la carpeta si no existe
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

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
                try:
                    df = pd.read_excel(archivo, header=6)
                    cliente_no_deseado = ['ROYAL', 'MNACO', 'FRON', 'MHTAN']
                    df = df[~df['Sala'].isin(cliente_no_deseado)]
                    df['Diferencia'] = df['HandPay'] - df['Billete']
                    df['Bono'] = df.apply(lambda row: calcular_bono(row), axis=1)
                    df = df[df['Billete'] > 20000]
                    
                    # Formatear la columna 'Bono' con separador de miles
                    df['Bono'] = df['Bono'].apply(lambda x: '{:,}'.format(x))

                    # Guardar el DataFrame procesado como archivo CSV
                    file_path = f'{folder_path}/{ano_subir}_{mes_subir}_{casino_subir}.csv'
                    df[['Sala', 'Bono']].to_csv(file_path, index=False)
                    
                    st.success(f'Archivo para {mes_subir} {ano_subir} - {casino_subir} procesado exitosamente.')
                    
                except Exception as e:
                    st.error(f"Error al procesar el archivo: {e}")

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
    st.subheader('Ver Bonos Procesados')

    archivos = os.listdir(folder_path)
    if not archivos:
        st.info('No hay archivos procesados actualmente.')
    else:
        archivo_mostrar = st.selectbox('Seleccione el archivo a mostrar', archivos)
        file_path = os.path.join(folder_path, archivo_mostrar)
        
        try:
            bonos_df = pd.read_csv(file_path)

            # Mostrar solo la columna 'Sala' y 'Bono' en formato de tabla de Excel
            bonos_df['Bono'] = bonos_df['Bono'].apply(lambda x: '{:,}'.format(x))
            st.table(bonos_df[['Sala', 'Bono']].reset_index(drop=True))

        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")

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
