##Libraries:
#bibliotecas necessárias
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
import plotly.graph_objects as go
#------------------------------------------------------------------------------------
# Funções
#------------------------------------------------------------------------------------
def distance( df1 ):
      col = ['Delivery_location_latitude', 'Restaurant_longitude', 'Delivery_location_longitude', 'Restaurant_latitude']
      df1['distance'] = df1.loc[:, col].apply( lambda x: haversine( (x['Delivery_location_latitude'],                          x['Delivery_location_longitude']), (x['Restaurant_latitude'], x['Restaurant_longitude']) ), axis=1 ) 
      avg_distance = np.round( df1['distance'].mean() , 2 ) 
    
      return avg_distance 
#------------------------------------------------------------------------------------
def avg_std_time_yes( df1 ):
      df_aux = ( df1.loc[:, ['Time_taken(min)', 'Festival']]
                   .groupby( 'Festival' )
                   .agg( {'Time_taken(min)': ['mean', 'std']} ) )   
      df_aux.columns = ['avg_time', 'std_time']
      df_aux = df_aux.reset_index()                 
      df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2 )

      return df_aux
#------------------------------------------------------------------------------------
def avg_std_time_no( df1 ):
       df_aux = ( df1.loc[:, ['Time_taken(min)', 'Festival']]
                   .groupby( 'Festival' )
                   .agg( {'Time_taken(min)': ['mean', 'std']} ) )

       df_aux.columns = ['avg_time', 'std_time']
       df_aux = df_aux.reset_index()
     
       df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2 )  

       return df_aux
#------------------------------------------------------------------------------------
def std_avg_time_yes( df1 ):
       df_aux = ( df1.loc[:, ['Time_taken(min)', 'Festival']]
                   .groupby( 'Festival' )
                   .agg( {'Time_taken(min)': ['mean', 'std']} ) )

       df_aux.columns = ['avg_time', 'std_time']
       df_aux = df_aux.reset_index()
       df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2 )

       return df_aux
#------------------------------------------------------------------------------------
def std_avg_time_no( df1 ):
       df_aux = ( df1.loc[:, ['Time_taken(min)', 'Festival']]
                   .groupby( 'Festival' )
                   .agg( {'Time_taken(min)': ['mean', 'std']} ) )

       df_aux.columns = ['avg_time', 'std_time']
       df_aux = df_aux.reset_index()
     
       df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2 )

       return df_aux
#------------------------------------------------------------------------------------
def avg_mean_delivery_city( df1 ):
            df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']} )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
                        
            fig = go.Figure()                    
            fig.add_trace( go.Bar( name='Control', 
                                       x=df_aux.index, 
                                       y=df_aux['avg_time'],
                                       error_y=dict(type='data', array=df_aux['std_time'])))
                        
            fig.update_layout( barmode='group' )

            return fig
#------------------------------------------------------------------------------------
def time_distribuiction( df1 ):
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = df1.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'],                                                         x['Delivery_location_longitude']) ), axis=1 )
            avg_distance = df1.loc[:, ['City', 'distance']].groupby( ['City'] ).mean().reset_index()
            fig = go.Figure( data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0] )] )

            return fig 
#------------------------------------------------------------------------------------
def avg_std_time_distribuiction( df1 ):
           df_aux = ( df1.loc[:, ['Time_taken(min)' ,'City','Road_traffic_density']]
                              .groupby( ['City','Road_traffic_density'] )
                              .agg( {'Time_taken(min)': ['mean', 'std']} ) )      
           df_aux.columns = ['avg_time', 'std_time']
           df_aux = df_aux.reset_index()                
           fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                                  color='std_time', color_continuous_scale='RdBu',
                                  color_continuous_midpoint=np.average(df_aux['std_time'] ) )

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
# Limpando os dados
df1 = clean_code( df )
#=============================
# Barra Lateral
#=============================
st.header( 'Marketplace - Visão Restaurantes' )

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
#=============================
# Layout no streamlit
#=============================
tab1, tab2, tab3 = st.tabs ([ 'Visão Gerencial' , '_', '_'] )

with tab1:
    with st.container():
          st.markdown( """---""" )
          st.title( "Overal Metrics" )

          col1, col2, col3, col4, col5, col6 = st.columns( 6 )
          with col1:
              delivery_unique = len( df1.loc[:, 'Delivery_person_ID'].unique() )
              col1.metric( 'Entregadores', delivery_unique ) #ok
          
          with col2:
            avg_distance = distance( df1 ) 
            col2.metric( 'A Distância media', avg_distance ) #ok
                         
          with col3:
                  df_aux = avg_std_time_yes( df1 )
                  col3.metric('Tempo Médio Yes', df_aux )#ok
              
          with col4:
                   df_aux = avg_std_time_no( df1 )
                   col4.metric('Tempo Médio No ', df_aux ) #ok
              
          with col5:
                 df_aux = std_avg_time_yes( df1 )
                 col5.metric('STD Entrega Yes', df_aux ) #ok
                
          with col6:
                 df_aux = std_avg_time_no( df1 )
                 col6.metric('STD Entrega No', df_aux ) #ok
              
    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
         st.markdown( " Time médio por entrega " )
         fig = avg_mean_delivery_city( df1 )
         st.plotly_chart( fig ) #ok
            
    with col2:
       st.title( "Distribuição da Distância" )
       df_aux = ( df1.loc[:, ['City', 'Time_taken(min)','Type_of_order']]
                            .groupby( ['City','Type_of_order'] )
                            .agg( {'Time_taken(min)': ['mean', 'std']} ) )

       df_aux.columns = ['avg_time', 'std_time']
       df_aux = df_aux.reset_index()
       st.dataframe ( df_aux )

with st.container():
             st.markdown( """---""" )
             st.title( "Distribuição do Tempo" )

             col1, col2 = st.columns ( 2 )
with col1:   
        fig = time_distribuiction( df1 )
        st.plotly_chart( fig ) #ok
                 

with col2:
      fig = avg_std_time_distribuiction( df1 )
      st.plotly_chart( fig ) #ok