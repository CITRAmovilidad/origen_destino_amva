import streamlit as st
import plotly.express as px
import json
import pandas as pd
import os
import pickle


st.set_page_config(layout="wide")

# Cargar datos GeoJSON
with open('map.geo.json') as f:
    geojson_data = json.load(f)



# Convertir 'Nueva_Zona' a int dentro del GeoJSON, con manejo de errores

for feature in geojson_data.get('features', []):
    feature['properties']['Nueva_Zona'] = int(feature['properties']['Nueva_Zona'])



def crear_df():
    # Ruta de la carpeta donde están los archivos CSV
    csv_folder = 'csv'

    # Lista de nombres de archivos CSV
    csv_files = ['Grupo_00.csv', 'Grupo_01.csv', 'Grupo_02.csv', 'Grupo_03.csv']

    # Leer y combinar todos los archivos CSV en un solo DataFrame
    dataframes = []
    for file in csv_files:
        file_path = os.path.join(csv_folder, file)
        df = pd.read_csv(file_path, index_col="Unnamed: 0")
        dataframes.append(df)
    return dataframes

#def load_data():
#    try:
#        file_id = '1XqQO82n36aoyY4cd7h6Lawjn--vd9YZf'
#        url = f'https://drive.google.com/uc?export=download&id={file_id}'
#        output = 'odmatrix_lab.csv'
#        
#        gdown.download(url, output, quiet=False)
#        
#        df = pd.read_csv(output, delimiter='|')
#        return df
#    except Exception as e:
#        st.error(f"Ha ocurrido un error: {e}")
#        return None

# Crear un contenedor vacío para el spinner
spinner_placeholder = st.empty()

# HTML y CSS para centrar el spinner
spinner_html = """
<style>
.spinner-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 80vh;
}
.spinner {
    font-size: 24px;
}
</style>
<div class="spinner-container">
    <div class="spinner">
        ⏳ Cargando datos. Esto tardará unos minutos, por favor espere...
    </div>
</div>
"""

# Mostrar el spinner
spinner_placeholder.markdown(spinner_html, unsafe_allow_html=True)

# Cargar los datos
df = pd.concat(crear_df(), ignore_index=True)

# Importar el diccionario desde el archivo binario
#with open('odmatrix_lab.pkl', 'rb') as handle:
#    df = pickle.load(handle)

# Una vez que los datos se han cargado, eliminar el spinner
spinner_placeholder.empty()

if df is not None:
    st.success('¡los datos se cargaron correctamente!')
else:
    st.error("No se pudieron cargar los datos")


df = df[df.profesional == 'No'].drop(['residencia', 'profesional'], axis=1)


# Convertir 'PXX' en int en la columna 'periodo'

df['periodo'] = df['periodo'].apply(lambda x: int(x[1:]))

df['modo'] = df['modo'].replace('TP', 'Transporte Publico')


# Título de la aplicación

st.title('Viajes Origen y Destino en el AMVA')


# Filtros

selected_modo = st.multiselect(

    'Seleccione el modo de transporte que quiera evaluar',

    ['Privado', 'Transporte Publico', 'No Motorizado'],

    default=['Privado', 'Transporte Publico', 'No Motorizado']

)



df_base = df[df['modo'].isin(selected_modo)]

dist  = df_base.groupby(['periodo'])['viajes'].sum().reset_index()

st.header('Distribución Horaria de Viajes')

st.bar_chart(dist, x="periodo", y="viajes", color="#228B22")



selected_periodo = st.slider(

    'Seleccione el periodo del día',

    min_value=0, max_value=23, value=(0, 23), step=1

)



selected_zona = st.multiselect(

    'Seleccione la(s) zona(s) que desea analizar',

    df['origen'].unique()

)



# Filtrar los datos

df_filtered =df_base[(df_base['periodo'] >= selected_periodo[0]) & 

                 (df_base['periodo'] <= selected_periodo[1])]



if selected_zona:

    dir1 = 'destino'

    color1 = 'Greens'

    df_1 = df_filtered[df_filtered['origen'].isin(selected_zona)]



    dir2 = 'origen'

    color2 = 'Reds'

    df_2 = df_filtered[df_filtered['destino'].isin(selected_zona)]

else:

    dir1 = 'destino'

    color1 = 'Greens'

    dir2 = 'origen'

    color2 = 'Reds'

        



viajes_o = df_filtered.groupby([dir1])['viajes'].sum().reset_index()

viajes_d = df_filtered.groupby([dir2])['viajes'].sum().reset_index()



col1, col2 = st.columns(2)



with col1:

    st.header("Generación")

    fig1 = px.choropleth_mapbox(

    viajes_o, geojson=geojson_data, locations=dir1, featureidkey="properties.Nueva_Zona",

    color='viajes', color_continuous_scale=color1, mapbox_style="carto-darkmatter",

    zoom=10, center={"lat": 6.2321, "lon": -75.5746}, opacity=0.5,

    labels={'viajes': 'Viajes'})

    fig1.update_layout(

    margin={'l': 0, 'r': 0, 't': 50, 'b': 0},

    height=750,  # Ajustar la altura del gráfico

    width=2800,  # Ajustar el ancho del gráfico

    coloraxis_colorbar=dict(

        title="Viajes",

        titleside="right",

        titlefont=dict(size=24, color="black")

        )

    )

    st.plotly_chart(fig1)



with col2:

   st.header("Atracción")

   fig2 = px.choropleth_mapbox(

    viajes_d, geojson=geojson_data, locations=dir2, featureidkey="properties.Nueva_Zona",

    color='viajes', color_continuous_scale=color2, mapbox_style="carto-darkmatter",

    zoom=10, center={"lat": 6.2321, "lon": -75.5746}, opacity=0.5,

    labels={'viajes': 'Viajes'})

   fig2.update_layout(

    margin={'l': 0, 'r': 0, 't': 50, 'b': 0},

    height=750,  # Ajustar la altura del gráfico

    width=2800,  # Ajustar el ancho del gráfico

    coloraxis_colorbar=dict(

        title="Viajes",

        titleside="right",

        titlefont=dict(size=24, color="black")

        )

    )

   st.plotly_chart(fig2)





