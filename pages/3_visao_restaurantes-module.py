########### BIBLIOTECAS ###########################

from haversine import haversine
import plotly.express as px
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image

st.set_page_config(page_title="Visão Empresa", layout="wide")

############ FUNÇÕES ############################

def clean_code(df1):
    
    """ Essa função tem a responsabilidade de limpar o dataframe
    
    Tipos de limpeza:
    1 - Remoção dos dados NaN
    2 - Mudança do tipo da coluna de dados
    3 - Remoção dos espaços variáveis de texto
    4 - Formatação da coluna de datas
    5 - Limpeza da coluna de tempo
    
    Input: dataframe
    Output: dataframe
    
    """
    remover_nan_age = df["Delivery_person_Age"] != "NaN "
    df1 = df1.loc[remover_nan_age, :]
    df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype(int)

    df1["Order_Date"] = pd.to_datetime(df1["Order_Date"], format = "%d-%m-%Y")

    remover_weather = df1['Weatherconditions'] != 'NaN '
    df1 = df1.loc[remover_weather, :]

    remover_road = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[remover_road, :]

    remover_city = df1['City'] != 'NaN '
    df1 = df1.loc[remover_city, :]

    remover_festival = (df1['Festival'] != 'NaN ') 
    df1 = df1.loc[remover_festival, :]

    remover_nan_ratings = df["Delivery_person_Ratings"] != "NaN "
    df1 = df1.loc[remover_nan_ratings, :]
    df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype(float)

    remover_type_order = (df1['Type_of_order'] != 'NaN ') 
    df1 = df1.loc[remover_type_order, :]

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(float)

    remover_veiculo = (df1['Type_of_vehicle'] != 'NaN ') 
    df1 = df1.loc[remover_veiculo, :]

    remover_veiculo = (df1['Type_of_vehicle'] != 'NaN ') 
    df1 = df1.loc[remover_veiculo, :]

    # limpando min
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('(min) ', '', regex=False)

    #limpando espaços city
    df1['City'] = df1['City'].str.replace(' ', '', regex=False)

    #limpando nan do min
    remover_nan_take = df['Time_taken(min)'] != "NaN "
    df1 = df1.loc[remover_nan_take, :]
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(float)
    print("limpeza ok")

    #visao semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    
    #distancia_media
    cols = ['Restaurant_latitude', 'Restaurant_longitude',                                             'Delivery_location_latitude','Delivery_location_longitude']
    df1['distance'] = (df1.loc[:, cols].apply( lambda x: haversine ( 
        (x['Restaurant_latitude'],       x['Restaurant_longitude']), 
                                                                    
        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1) )
    
    return df1

def grafico_restaurante(df1):
    avg_std_city = (df1.loc[:,['Time_taken(min)', 'City']]
    .groupby('City').agg({'Time_taken(min)':{'mean', 'std'}}))

    avg_std_city.columns = ['time_mean', 'time_std']
        
    avg_std_city = avg_std_city.reset_index()

    fig = px.histogram(avg_std_city, x="City", y=["time_std", "time_mean"], barmode="group")
            
            
    return fig
            

############ IMPORT DATASET ############################

df = pd.read_csv("train.csv")

############ lIMPANDO OS DADOS ############################

df1 = clean_code(df)


#=====================================================================
# LAYOUT NO STREAMLIT
#=====================================================================

st.header('Marketplace - Visão Restaurantes')
#image_path = 'logo.png'
image = Image.open('logo.png')
st.sidebar.image( image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### O melhor da região!')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.to_datetime("2022-04-13", errors='coerce'),
    value_timestamp = value.timestamp()
    min_value=pd.to_datetime("2022-02-11", errors='coerce').timestamp(),
    max_value=pd.to_datetime("2022-04-06", errors='coerce').timestamp(),
    value=value=value_timestamp)
selected_date = pd.to_datetime(date_slider, unit='s')


st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low ', 'Medium ', 'High ', 'Jam '],
    default=['Low ', 'Medium ', 'High ', 'Jam '])

st.sidebar.markdown("""---""")

st.sidebar.markdown('##### Powered by Comunidade DS')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de road
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


#=============================
# Layout no Streamlit
#======================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3 = st.columns(3, gap='large')
        with col1:
            entregadores_unicos = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos',  entregadores_unicos)
            
        with col2:
            avg_distance = df1['distance'].mean()
            col2.metric('Distância média', avg_distance)
            
        with col3:
            tempo_medio = df1.loc[:, ['Festival','Time_taken(min)']].groupby('Festival').mean().reset_index()
            tempo_medio = tempo_medio.iloc[1,1]
            col3.metric('Tempo médio c/ Festival', tempo_medio)
            
    with st.container():
        st.markdown("""___""")
        st.title('Gráficos')
        fig = grafico_restaurante(df1)
        st.plotly_chart(fig, user_container_width=True)
        
        
