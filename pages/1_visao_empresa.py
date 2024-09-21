
# Libraries:
# Bibliotecas necessárias
# Importando as bibliotecas necessárias
import pandas as pd
import numpy as np
from datetime import datetime 
import re
from matplotlib import pyplot as plt
import folium
from streamlit_folium import folium_static
from haversine import haversine
import streamlit as st
from PIL import Image #para a logo utilizada - biblioteca de manipulação de imagens
import plotly.express as px

#------------------------------------------------------------------------------------
#Funções
#------------------------------------------------------------------------------------
def country_maps( df1 ):
        cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df_aux = df1.loc[:, cols].groupby( ['City', 'Road_traffic_density'] ).median().reset_index()
        df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

        map = folium.Map()

        for index, location_info in df_aux.iterrows():
          folium.Marker ( [location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
                    

        folium_static( map,width=1024 , height=600 )
#------------------------------------------------------------------------------------
def order_by_week( df1 ):
         df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
         df1.head()
         df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( ['week_of_year'] ).count().reset_index()
         df_aux.head()
         fig = px.line( df_aux, x='week_of_year', y='ID' )
    
         return fig
#------------------------------------------------------------------------------------
def order_share_by_week( df1):
          df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
          df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby( ['week_of_year'] ).count().reset_index()
          df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( ['week_of_year'] ).nunique().reset_index()
          df_aux = pd.merge( df_aux01, df_aux02, how='inner' )
          df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']          
          fig = px.line( df_aux, x='week_of_year', y=['order_by_deliver'] )
    
          return fig
#------------------------------------------------------------------------------------
def traffic_order_city( df1 ):
            df_aux = ( df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                        .groupby( ['City', 'Road_traffic_density']).count().reset_index() )
            df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]   
            fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City' )
          
            return fig
#------------------------------------------------------------------------------------
def traffic_order_share( df1 ):
            df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby( ['Road_traffic_density'] ).count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
            fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density' )
    
            return fig
#------------------------------------------------------------------------------------
def order_metric( df1 ): 
             cols = ['ID', 'Order_Date']       
             #selecao de linhas
             df_aux = df1.loc[:, cols].groupby( ['Order_Date'] ).count().reset_index()
             # desenhar o gráfico de linhas
             fig = px.bar( df_aux, x='Order_Date', y='ID' ) 
             
             return fig
#------------------------------------------------------------------------------------    
def clean_code ( df1 ):
    """ Esta fução tem a responsabilidade de limpar o Dataframe 

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variávei de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )

        Input: Dataframe
        Output: Dataframe
    """
    # 1. removendos linhas NaN

    df1 = df[~pd.isna(df['Time_taken(min)'])] # o til significa negação, ou seja, todos diferentes de Nan.
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].replace(r'\(min\)', '', regex=True)  # remove (min)
    
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    

    # 2. Convertendo a coluna Delivery_person_Age de texto para ( int )
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    
    # 2. convertendo a coluna Ratings de texto para numero decimal (float) 
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    
    # 3. covertendo a coluna Order_Date para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    
    # 4. convertendo multiple_deliveries de texto para numero inteiro ( int )
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( float )

    # 5. outra maneira de remover espacos dentro de strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 6. Limpando a coluna de time_taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)  # convert to integer

    return df1 
#---------------------- Inicio da Estrutura Lógica do código! ------------------------------
#-------------------------------------------------------------------------------------------
# Import dataset
#-------------------------------------------------------------------------------------------
df = pd.read_csv( 'dataset/train.csv')
df1 = df.copy()
#-------------------------------------------------------------------------------------------
# Limpando os dados
df1 = clean_code( df )
#=============================
# Barra Lateral
#=============================
st.header( 'Marketplace - Visão Cliente' )

image = Image.open( 'logo.png' )
st.sidebar.image ( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
                     'Até qual valor?',
                      value=datetime(2022, 4, 6),
                      min_value=datetime(2022, 2, 11),
                      max_value=datetime(2022, 4, 6),
                      format='DD-MM-YYYY' ) 

st.header( date_slider )
st.sidebar.markdown( """---""" )

#st.dateframe( df1 ) visualizar o arquivo no streamlit

traffic_options = st.sidebar.multiselect(
                'Quais as condições do trânsito',
                df1['Road_traffic_density'].unique(),
                default=df1['Road_traffic_density'].unique() )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '## Powered by Comunidade DS' ) 

#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]
#st.dateframe( df1 ) visualização

#filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#Criando abas
tab1, tab2, tab3 = st.tabs ( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
   with st.container():
         st.markdown(' #Orders by Day' )
         fig = order_metric( df1 )
         st.plotly_chart( fig, use_container_width=True )
        
   with st.container():
    col1 , col2,  = st.columns( 2 )
    
    with col1:
         st.markdown( "# Traffic Order Share" )
         fig = traffic_order_share( df1 )
         st.plotly_chart( fig, use_container_width=True )
         st.markdown( """----------------------------------------------""" )
       
   with col2:
     with st.container():
          st.markdown( "# Traffic Order City" )
          fig = traffic_order_city( df1 )
          st.plotly_chart( fig, use_container_width=True )
          st.markdown( """----------------------------------------------""" )
       
     with st.container():
          st.markdown( "# Order Share by Week" )
          fig = order_share_by_week( df1)
          st.plotly_chart( fig, use_container_width=True )
          
       
with tab2:
    st.markdown( "# Order by Week" )
    fig = order_by_week( df1 )
    st.plotly_chart( fig, use_container_width=True )
   
with tab3:
    st.markdown("# Country Maps ")
    country_maps( df1 )
   
st.header( 'Next page' )