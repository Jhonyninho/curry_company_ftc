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
#------------------------------------------------------------------------------------
# Funções
#------------------------------------------------------------------------------------
def top_delivers( df1, top_asc ):  
     df2 = ( df1.loc[:, ['City', 'Delivery_person_ID', 'Time_taken(min)']]
                .groupby(['City', 'Delivery_person_ID'])
                .max().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index() )

     df_aux01 = df2.loc[df2['City'] == 'Metropotian', :].head(10)
     df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
     df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    
     df3 = pd.concat ( [df_aux01, df_aux02, df_aux03] ).reset_index ( drop=True )
    
     return df3
#------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------
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
st.header( 'Marketplace - Visão Entregadores' )

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

tab1, tab2, tab3 = st.tabs ( ['Visão Gerencial', '_', '_'] )


with tab1:
    with st.container():
            st.subheader( 'Overall Metrics' )

            col1, col2, col3, col4 = st.columns( 4, gap='large' )
            with col1:
                # A maior idade dos entregadores
                maior_idade = df1.loc[:, 'Delivery_person_Age'].max() 
                col1.metric( 'Maior de Idade', maior_idade )

            with col2:
                # A menor idade dos entregadores
                menor_idade = df1.loc[:, 'Delivery_person_Age'].min() 
                col2.metric( 'Menor de Idade', menor_idade )


            with col3:
                melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
                col3.metric( 'Melhor condicao', melhor_condicao )

            with col4:
                pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
                col4.metric( 'Pior condicao', pior_condicao )

with st.container():
          st.markdown( """---""" )
          st.title( 'Avaliações' )

          col1,col2 = st.columns( 2 )
          with col1: 
             st.markdown( '##### Avaliações media por Entregador' )
             df_avg_ratings_per_deliver = ( df1.loc[:,['Delivery_person_Ratings', 'Delivery_person_ID']]
                                               .groupby( 'Delivery_person_ID' ).mean().reset_index() )
             st.dataframe( df_avg_ratings_per_deliver )
            

          with col2:
             st.markdown( '##### Avaliações medias por Transito' )
             #agg: segregar por coluna
             df_avg_std_rating_by_traffic = ( df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                                                 .groupby(['Road_traffic_density'])
                                                 .agg({'Delivery_person_Ratings': ['mean', 'std']}) )
              # renomeando colunas
             df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
              # reset do index
             df_avg_std_rating_by_traffic.reset_index()
             st.dataframe( df_avg_std_rating_by_traffic )

             st.markdown( '##### Avaliações media por Clima' )
              # agg = funcao de agregacao (quantas funcoes queremos)
              # .agg( {<a coluna que recebe a operacao: [uma lista de operacao a ser aplicado]})
             df_avg_rating_by_weather = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                .groupby(['Weatherconditions'])
                                .agg({'Delivery_person_Ratings': ['mean', 'std']}) )
              # mudanca do nome das colunas
             df_avg_rating_by_weather.columns = ['delivery_mean', 'delivery_std']

              # reset do index
             df_avg_rating_by_weather.reset_index()
             st.dataframe( df_avg_rating_by_weather )


with st.container():
         st.markdown( """---""" )
         st.title( 'Velocidade de Entrega' )

         col1,col2 = st.columns( 2 )
         with col1: 
               st.subheader( 'Top entregadores mais rapidos' )
               df3 = top_delivers( df1, top_asc=True )
               st.dataframe( df3 )
               
         with col2:
               st.subheader( 'Top entregadores mais lentos' )
               df3 = top_delivers( df1, top_asc=False )
               st.dataframe( df3 )