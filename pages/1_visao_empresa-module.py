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
    
    return df1

def pedidos_semana(df1):
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')
    return fig

def pedidos_entregador(df1):
        df_aux1 = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux2 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
        .groupby('week_of_year').nunique().reset_index())
        df_aux = pd.merge(df_aux1, df_aux2, how='inner')
        df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')
        return fig
    
def country_maps(df1):
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude',         
    'Delivery_location_longitude']]
    .groupby(['City', 'Road_traffic_density']).median().reset_index())
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'], 
            location_info['Delivery_location_longitude']], popup=location_info[['City',                                                 'Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024, height=600)
    
    return df1

def order_metric(df1):
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')
            
    return fig

def traffic_order_share(df1):
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
    .groupby('Road_traffic_density').count().reset_index())
    fig = px.pie(df_aux, values='ID', names='Road_traffic_density')
    
    return fig

def traffic_order_city(df1):
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
    .groupby(['City','Road_traffic_density'])
    .count()
    .reset_index())
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig
############ IMPORT DATASET ############################

df = pd.read_csv("train.csv")

############ lIMPANDO OS DADOS ############################

df1 = clean_code(df)


#=====================================================================
# LAYOUT NO STREAMLIT
#=====================================================================

st.header('Marketplace - Visão Cliente')
#image_path = 'logo.png'
image = Image.open('logo.png')
st.sidebar.image( image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### O melhor da região!')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('#### Pedidos por dia')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)

        
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Tipo de tráfego')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)
            
            
        with col2:
            st.markdown('#### Densidade de tráfego por Cidade')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)

        
with tab2:
    with st.container():
        st.markdown('### Pedidos por entregador')
        fig = pedidos_entregador(df1)
        st.plotly_chart(fig, use_container_width=True)
        
       
    with st.container():
        st.markdown('### Pedidos por semana')
        fig = pedidos_semana(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('# Mapa de endereços')
    country_maps(df1)
    
   
