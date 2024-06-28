import streamlit as st
import pandas as pd
import os

# Configurar la página para que ocupe toda la pantalla
st.set_page_config(layout="wide")

# Carpeta donde se guardarán los archivos CSV de bonos procesados
folder_path = 'bonos_procesados'

# Función para cargar los bonos procesados
def cargar_bonos(file_path):
    bonos_df = pd.read_csv(file_path)
    bonos_df = bonos_df[bonos_df['Bono'] > 0]  # Filtrar bonos positivos
    return bonos_df[['Sala', 'Bono']]  # Retornar solo las columnas Sala y Bono

# Verificar y crear la carpeta si no existe
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Pantalla inicial con menú de opciones
st.title('Bonos Otorgados')

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
                    df.to_csv(f'{folder_path}/{ano_subir}_{mes_subir}_{casino_subir}.csv', index=False)
                    st.success(f'Archivo para {mes_subir} {ano_subir} - {casino_subir} cargado exitosamente.')
                except Exception as e:
                    st.error(f'Error al procesar el archivo: {str(e)}')

        elif submenu == 'Administrar Archivos':
            st.subheader('Administrar Archivos Cargados')

            archivos = os.listdir(folder_path)
            if not archivos:
                st.info('No hay archivos cargados actualmente.')
            else:
                archivo_a_eliminar = st.selectbox('Seleccione el archivo a eliminar', archivos)
                clave_eliminar = st.text_input('Ingrese la clave para eliminar el archivo', type='password')
                
                if clave_eliminar == 'riviera0001' and st.button('Eliminar'):
                    try:
                        os.remove(os.path.join(folder_path, archivo_a_eliminar))
                        st.success(f'Archivo {archivo_a_eliminar} eliminado exitosamente.')
                    except Exception as e:
                        st.error(f'Error al eliminar el archivo: {str(e)}')

elif opcion == 'Ver Bonos Procesados':
    ver_ano = st.selectbox('Seleccione el año (Ver)', range(2024, 2031), key='ver_ano')
    ver_mes = st.selectbox('Seleccione el mes (Ver)', ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'], key='ver_mes')
    ver_casino = st.selectbox('Seleccione el casino (Ver)', ['MANHATTAN', 'FARAON', 'ROYAL', 'MONACO'], key='ver_casino')

    file_path = f'{folder_path}/{ver_ano}_{ver_mes}_{ver_casino}.csv'
    if os.path.exists(file_path):
        bonos_df = cargar_bonos(file_path)

        # Mostrar tabla con nombre del cliente y valor del bono
        st.title(f'Bonos para {ver_mes} {ver_ano} - {ver_casino}')
        for index, row in bonos_df.iterrows():
            st.write(f'{row["Sala"]}: {row["Bono"]}')
            st.write('---')

    else:
        st.warning('No hay bonos procesados para la selección actual.')
