import pandas as pd
import numpy as np
import streamlit as st

# Definir los nombres de las columnas
column_names = [
    'Sala', 'Día', 'Inicio Sesión', 'Fin Sesión', 'Maquina', 'Sesion', 'Puntos', 
    'Input', 'Output', 'Jackpot', 'Billete', 'Ticket_Cash_In', 'Ticket_Rest_In', 
    'Aft_Cash_In', 'Aft_Rest_In', 'Aft_NO_Rest_In', 'HandPay', 'Ticket_Cash_Out', 
    'Ticket_Rest_Out', 'Aft_Cash_Out', 'Aft_Rest_Out', 'Aft_NO_Rest_Out', 'Ganado'
]

# Leer el archivo Excel
try:
    df = pd.read_excel('archivo_clientes.xlsx', header=6, names=column_names)
except FileNotFoundError:
    st.error("El archivo 'archivo_clientes.xlsx' no se encontró en el directorio actual.")
    exit()

def calcular_bono(row):
    cliente_no_deseado = ['ROYAL', 'MNACO', 'FRON', 'MHTAN']
    
    if row['Sala'] in cliente_no_deseado:
        return None  # Retornar None para excluir estas filas
    
    try:
        # Calcular la diferencia entre HandPay y Billete
        diferencia = row['HandPay'] - row['Billete']
        
        # Si la diferencia es positiva o cero, el cliente ganó dinero o no perdió, por lo tanto el bono es 0
        if diferencia >= 0:
            return 0
        
        # Calcular el bono como el 6.5% de la pérdida (diferencia negativa)
        bono = abs(diferencia) * 0.065
        return bono
    except Exception as e:
        st.error(f"Error en fila {row.name}: {e}")
        return None  # Retornar None para excluir estas filas

# Convertir las columnas numéricas de formato string a numérico
df['HandPay'] = df['HandPay'].replace('[\$,]', '', regex=True).astype(float)
df['Billete'] = df['Billete'].replace('[\$,]', '', regex=True).astype(float)

# Aplicar la función calcular_bono y filtrar las filas no deseadas
df['Bono'] = df.apply(calcular_bono, axis=1)

# Filtrar los bonos superiores a 20000
df_bonos = df[df['Bono'] > 20000].copy()

# Redondear los valores de la columna 'Bono' al múltiplo más cercano de 20000
df_bonos['Bono'] = df_bonos['Bono'].apply(lambda x: int(np.ceil(x / 20000)) * 20000)

# Crear un DataFrame para los clientes con bono superior a 20000
df_clientes_bono = df_bonos[['Sala', 'Bono']].copy()
df_clientes_bono.columns = ['Cliente', 'Bono']  # Renombrar la columna Sala a Cliente

# Crear un DataFrame para los clientes con ganancia, excluyendo los no deseados
cliente_no_deseado = ['ROYAL', 'MNACO', 'FRON', 'MHTAN']
df_clientes_ganancia = df[(df['HandPay'] > df['Billete']) & (~df['Sala'].isin(cliente_no_deseado))].copy()
df_clientes_ganancia['Ganancia'] = df_clientes_ganancia['HandPay'] - df['Billete']
df_clientes_ganancia = df_clientes_ganancia[['Sala', 'Ganancia']]
df_clientes_ganancia.columns = ['Cliente', 'Ganancia']  # Renombrar la columna Sala a Cliente

# Crear un DataFrame para los clientes con bono inferior a 20000
df_bonos_inferiores = df[(df['Bono'] > 0) & (df['Bono'] <= 20000)].copy()
df_bonos_inferiores = df_bonos_inferiores[['Sala', 'Bono']]
df_bonos_inferiores.columns = ['Cliente', 'Bono']  # Renombrar la columna Sala a Cliente

# Crear una aplicación Streamlit
st.title("Bonos y Ganancias de Clientes")

# Mostrar la tabla de bonos
st.subheader("Bonos")
st.write(df_clientes_bono)

# Mostrar la tabla de pérdida insuficiente
st.subheader("Perdida Insuficiente")
st.write(df_bonos_inferiores)

# Mostrar la tabla de ganancias
st.subheader("Ganancia")
st.write(df_clientes_ganancia)
