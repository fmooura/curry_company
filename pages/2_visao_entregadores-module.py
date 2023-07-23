########### BIBLIOTECAS ###########################

from haversine import haversine
import plotly.express as px
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image
from datetime import datetime


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
    
    return df1

def top_delivers(df1, top_asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
            .groupby(['City', 'Delivery_person_ID'])
            .mean()
            .sort_values(['City', 'Time_taken(min)'], ascending = top_asc)
            .reset_index())
                
    df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index()
            
    return df3

############ IMPORT DATASET ############################

df = pd.read_csv("train.csv")

############ lIMPANDO OS DADOS ############################

df1 = clean_code(df)
        



#=====================================================================
# LAYOUT NO STREAMLIT
#=====================================================================

st.header('Marketplace - Visão Entregadores')
#image_path = 'logo.png'
image = Image.open('logo.png')
st.sidebar.image( image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### O melhor da região!')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')


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
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:, "Delivery_person_Age"].max()
            col1.metric('Maior de idade', maior_idade)
            
        with col2:
            menor_idade = df1.loc[:, "Delivery_person_Age"].min()
            col2.metric('Menor de idade', menor_idade)
            
        with col3:
            melhor_condicao = df1.loc[:, "Vehicle_condition"].max()
            col3.metric('Melhor condição', melhor_condicao)
                        
        with col4:
            pior_condicao = df1.loc[:, "Vehicle_condition"].min()
            col4.metric('Pior condição', pior_condicao)
            
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Avaliação média por entregador')
            avg_per_deliver = (df1.loc[:, ['Delivery_person_ID',                            
                                        'Delivery_person_Ratings']]
                                        .groupby('Delivery_person_ID')
                                        .mean().reset_index())
            st.dataframe(avg_per_deliver)

            
        with col2:
            st.subheader('Avaliação média por transito')
            avg_per_trafic = (df1.loc[:,['Delivery_person_Ratings',
                                        'Road_traffic_density']]
                                        .groupby('Road_traffic_density')
                                        .agg({'Delivery_person_Ratings':{'mean', 'std'}}))

            avg_per_trafic.columns = ['delivery_mean', 'delivery_std']

            avg_per_trafic = avg_per_trafic.reset_index()
            st.dataframe(avg_per_trafic)
            
            st.subheader('Avaliação média por clima')
            
            avg_std_wheather = (df1.loc[:,['Delivery_person_Ratings',
                                            'Weatherconditions']]
                                            .groupby('Weatherconditions')
                                            .agg({'Delivery_person_Ratings':{'mean', 'std'}}))

            avg_std_wheather.columns = ['delivery_mean', 'delivery_std']

            avg_std_wheather = avg_std_wheather.reset_index()
            st.dataframe(avg_std_wheather)
            
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de entrega')
            
        col1, col2 = st.columns(2)
            
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
                
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
            
         
            
            
        
