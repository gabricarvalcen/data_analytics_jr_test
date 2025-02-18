import os
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

# Conectar ao banco de dados SQLite 

engine = create_engine("sqlite:///data_analytics_jr_test.db")  


# schema "test_analytics"

metadata = MetaData()
metadata.create_all(engine)


# Definindo o caminho da pasta onde estão os arquivos
pasta = "C:\\Users\\Gabriel de Carvalho\\Documents\\data_analytics_jr_test\\data_analytics_jr_test\\Resolução\\Data\\Escolas"

# Conectar ao banco de dados (SQLite, PostgreSQL, etc.)
# Altere para seu banco de dados

# Função para importar arquivos para o banco de dados
def importar_arquivo(arquivo):
    caminho_arquivo = os.path.join(pasta, arquivo)

    # Verifica se é um arquivo CSV ou XLSX
    if arquivo.endswith(".csv"):
        try:
            df = pd.read_csv(caminho_arquivo, encoding='latin1', sep=";")  
        except UnicodeDecodeError:
            print(f"Erro de codificação ao ler {arquivo}. Tentando outra codificação.")
            return

    elif arquivo.endswith(".xlsx"):
        # Importar XLSX para um DataFrame
        df = pd.read_excel(caminho_arquivo)

    else:
        print(f"Arquivo {arquivo} não é CSV nem XLSX. Ignorado.")
        return

    # Criação de tabela dinamicamente
    tabela_nome = arquivo.split('.')[0]  # Nome da tabela baseado no nome do arquivo

    # Criação das tabelas no banco de dados
    metadata.create_all(engine)

    # Importar os dados do DataFrame para o banco
    df.to_sql(tabela_nome, con=engine, if_exists='replace', index=False)
    print(f"Arquivo {arquivo} importado com sucesso!")

# Percorrer a pasta e importar os arquivos CSV e XLSX
for arquivo in os.listdir(pasta):
    if arquivo.endswith((".csv", ".xlsx")):
        importar_arquivo(arquivo)

print("Importação de todos os arquivos concluída!")


# Definindo a pasta educandos e colocando no banco de dados

pasta = "C:\\Users\\Gabriel de Carvalho\\Documents\\data_analytics_jr_test\\data_analytics_jr_test\\Resolução\\Data\\Perfil dos educandos"

for arquivo in os.listdir(pasta):
    if arquivo.endswith((".csv", ".xlsx")):
        importar_arquivo(arquivo)

print("Importação de todos os arquivos concluída!")
# Definindo o caminho da pasta onde estão os arquivos de escolas para empilhar

pasta = "C:\\Users\\Gabriel de Carvalho\\Documents\\data_analytics_jr_test\\data_analytics_jr_test\\Resolução\\Data\\Escolas"

# Lista para armazenar os DataFrames
lista_csvs = []

# Função para importar e empilhar arquivos CSV
def empilhar_csvs():
    # Percorrer a pasta e verificar os arquivos CSV
    for arquivo in os.listdir(pasta):
        caminho_arquivo = os.path.join(pasta, arquivo)

        # Verifica se é um arquivo CSV
        if arquivo.endswith(".csv"):
            try:
                # Importar o CSV para um DataFrame
                df = pd.read_csv(caminho_arquivo, encoding='latin1', sep=";")
                
                # Adicionar o DataFrame à lista
                lista_csvs.append(df)
                print(f"Arquivo {arquivo} importado com sucesso!")
            
            except Exception as e:
                print(f"Erro ao importar {arquivo}: {e}")
        
        else:
            print(f"{arquivo} não é um arquivo CSV, ignorado.")

    # Empilhar todos os CSVs em um único DataFrame
    if lista_csvs:
        df_completo = pd.concat(lista_csvs, ignore_index=True)
        print(f"{len(lista_csvs)} arquivos CSV empilhados com sucesso!")
        return df_completo
    else:
        print("Nenhum arquivo CSV encontrado.")
        return None

# Chamar a função para empilhar os CSVs
df_final = empilhar_csvs()

# Mostrar as primeiras linhas do DataFrame final
if df_final is not None:
    print(df_final.head())

# Definindo o caminho da pasta onde estão os arquivos de alunos para empilhar

pasta = "C:\\Users\\Gabriel de Carvalho\\Documents\\data_analytics_jr_test\\data_analytics_jr_test\\Resolução\\Data\\Perfil dos Educandos"
lista_csvs = []
df_final_2 = empilhar_csvs()

#Reorganizando as colunas para subir no sql

colunas = pd.read_excel("C:\\Users\\Gabriel de Carvalho\\Documents\\data_analytics_jr_test\\data_analytics_jr_test\\Resolução\\Data\\Escolas\\dicionarioescolas.xlsx")["CAMPO"]

df_final = df_final.rename(columns={"NOMESCOFI":"NOMESCOF"})

df_final  = df_final[colunas]

#subindo no sql

df_final.to_sql('escolas_agregado', con=engine, if_exists='replace', index=False)

#Reorganizando as colunas alunos para subir no sql

colunas = pd.read_excel("C:\\Users\\Gabriel de Carvalho\\Documents\\data_analytics_jr_test\data_analytics_jr_test\\Resolução\\Data\\Perfil dos educandos\\dicionariopefileducando.xlsx")["CAMPO "]
df_final_2  = df_final_2[colunas]

#subindo no sql

df_final_2.to_sql('alunos_agregado', con=engine, if_exists='replace', index=False)


from sqlalchemy import inspect

# Criar um inspetor para verificar as tabelas no banco
inspector = inspect(engine)

# Obter todas as tabelas no banco de dados
tabelas = inspector.get_table_names()

print("Tabelas no banco de dados:", tabelas)


# Estabelecendo relação entre as duas tabelas
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

# Referenciando as tabelas já criadas
escolas_agregado = Table('escolas122023', metadata, autoload_with=engine)
alunos_agregado = Table('idadeserieneeracadez23', metadata, autoload_with=engine)


# Consulta com LEFT JOIN
query = (
    select(alunos_agregado, escolas_agregado)  
    .select_from(alunos_agregado.join(escolas_agregado, alunos_agregado.c.CODESC == escolas_agregado.c.CODESC, isouter=True))
)
# Executando a consulta
resultado = session.execute(query).fetchall()

# Exibir os resultados
for row in resultado:
    print(row)


#EDA dataset 2023

df = pd.read_sql_query(query, engine)

df.head()

# Summary

df.info()

## Sumário Descritivo

df.describe()

print(f"Número de escolas {(len(df['CODESC'].unique()))}")

df.isnull().sum()

## Duplicate records
df[df.duplicated()]

## Correlation
import matplotlib.pyplot as plt
import seaborn as sns

df["SEXO"].value_counts().plot(kind="pie")
plt.show()

sns.histplot(df["IDADE"])


import folium
from folium.plugins import HeatMap


df_2 = df.groupby(["LATITUDE", "LONGITUDE"]).size().reset_index(name="Quantidade_Alunos")

# Criar um mapa centralizado no Brasil
mapa = folium.Map(location=[-15, -55], zoom_start=4)

# Adicionar pontos de calor (peso baseado na quantidade de registros)
heat_data = [[row["LATITUDE"], row["LONGITUDE"], row["Quantidade_Alunos"]] for index, row in df_2.iterrows()]
HeatMap(heat_data).add_to(mapa)

# Salvar e exibir o mapa
mapa.save("mapa.html")
mapa


#Fazendo algumas limpezas nas datas


import datetime
print(df_final_2.columns)

print(df_final_2['DATABASE'].unique())

df_final_2['DATABASE'] = df_final_2['DATABASE'].replace("30/09/2016", datetime.datetime(2016,9,30))
df_final_2['DATABASE'] = df_final_2['DATABASE'].replace("31/12/2020", datetime.datetime(2020,12,31))
df_final_2['DATABASE'] = df_final_2['DATABASE'].replace("31/12/2021", datetime.datetime(2021,12,31))
df_final_2['DATABASE'] = df_final_2['DATABASE'].replace("28-dez-17", datetime.datetime(2017,12,28))
df_final_2['DATABASE'] = df_final_2['DATABASE'].replace("30/12/2022 00:00", datetime.datetime(2022,12,30))
df_final_2['DATABASE'] = df_final_2['DATABASE'].replace("25/12/2023 00:00", datetime.datetime(2023,12,25))

import pandas as pd
import plotly.express as px

df_plot = df_final_2.groupby(["DATABASE","IDADE"]).size().reset_index(name="Quantidade_Alunos")


# Convertendo a coluna 'DATABASE' para datetime
df_plot['DATABASE'] = pd.to_datetime(df_plot['DATABASE'])

# Criando o histograma histórico com animação por ano (coluna 'DATABASE')
fig = px.bar(df_plot, x="IDADE", y="Quantidade_Alunos", animation_frame=df_plot['DATABASE'].dt.year.astype(str),
             title="Histograma Histórico de Quantidade de Alunos por Idade",
             labels={"IDADE": "Idade", "Quantidade_Alunos": "Quantidade de Alunos", "DATABASE": "Ano"},
             opacity=0.7, color="IDADE", color_continuous_scale="Viridis")

# Exibindo o gráfico
fig.show()

