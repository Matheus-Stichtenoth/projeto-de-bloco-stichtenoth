import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import time

#Carregando o modelo
model = joblib.load('model.pkl')

def predict_risco(carteira, operacoes, estado, modalidade):
    data = pd.DataFrame({
        'CARTEIRA': [carteira],
        'OPERACOES': [operacoes],
        'ESTADO': [estado],
        'MODALIDADE': [modalidade]
    })
    prediction = model.predict(data)
    return prediction[0]
#Começando a interatividade com o usuário
background_color = st.selectbox("Escolha uma cor de fundo para a página:", ["Light Grey", "Blue"])
    
colormap = {
    "Light Grey": "#fafafa",
    "Blue": "#d6e3e9"
}

if st.checkbox('Deseja utilizar essa cor para a página?'):
            progress_bar = st.progress(0)
            for counter in range(1, 101):
                time.sleep(0.015)
                progress_bar.progress(counter)
            with st.spinner('Ajustado a cor...'):
                time.sleep(3)

            st.markdown(f"""
            <style>
            .stApp {{
                background-color: {colormap[background_color]};
            }}
            </style>
            """, unsafe_allow_html=True)

#Definindo título e cabeçalho da página
st.title('RiskMap 🗺')
st.header('Previsão de Risco de Crédito por Tamanho da Carteira, Região e Modalidades')
st.write('''
Nesse aplicativo, iremos disponbilizar a grande oportunidade de você simular uma carteira de crédito,
com as características que mais se enquadram no seu negócio! Vamos começar? 📌''')

st.write('''
         Antes de começar, o que acha que ver alguns dados interessantes sobre a inadimplência?
         ''')

#Adicionando os dados extraídos da página do serasa
df_serasa = pd.read_csv('data/informacoes_inadimplencia.csv')

for i in range(3):
    curiosidade = f'Curiosidade n° {i}: {df_serasa["conteudo"][i]}'
    st.write(curiosidade)

st.write('Fonte: https://www.serasa.com.br/limpa-nome-online/blog/mapa-da-inadimplencia-e-renogociacao-de-dividas-no-brasil/')

st.write(
'''Agora que já consumiu alguns conteúdos interessante sobre inadimplência, 
preencha os dados abaixo e depois clique em prever, após isso, você terá a resposta se é uma característica de uma carteira de alto ou baixo risco.
''')

carteira = st.number_input('CARTEIRA', min_value=0)
operacoes = st.number_input('OPERACOES', min_value=0)

estados = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 
    'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 
    'SP', 'SE', 'TO'
]
#Tive que definir novamente as funções pois quando importava do 'services', sempre me gerava um erro no qual não consegui resolver
def get_bcb_data(file_path):
    response = requests.get(file_path)
    if response.status_code == 200:
        data = response.json()
        df = pd.json_normalize(data['value'])
        return df.dropna()
    else:
        raise ValueError(f"Erro na solicitação: {response.status_code}")

def risco_alto(risco):
    mapping = {'AA-C': '0', 'D-H': '1'}
    return mapping.get(risco)

caminho = 'https://olinda.bcb.gov.br/olinda/servico/scr_sub_regiao/versao/v1/odata/scr_sub_regiao(DataBase=@DataBase)?@DataBase=202407&$format=json&$select=DATA_BASE,CLIENTE,ESTADO,SUB_REGIAO,MODALIDADE,RISCO,OPERACOES,CARTEIRA'
df_bcb = get_bcb_data(caminho)
df_bcb['RISCO'] = df_bcb['RISCO'].apply(risco_alto)
df_bcb = df_bcb.drop(columns=['DATA_BASE','SUB_REGIAO'])

modalidades = df_bcb['MODALIDADE'].unique()

estado = st.selectbox('ESTADO', options=sorted(estados))
modalidade = st.selectbox('MODALIDADE', options=sorted(modalidades))

if st.button('Prever'):
    risco = predict_risco(carteira, operacoes, estado, modalidade)
    st.write(f'O risco previsto é: {risco}')

# Adicionando o gráfico de correlação
st.subheader('Gráfico de Correlação entre Volume de Carteira e Quantidade de Operações')

plt.figure(figsize=(10, 6))
sns.scatterplot(x='OPERACOES', y='CARTEIRA', hue='RISCO', data=df_bcb, palette='coolwarm', alpha=0.7)
plt.title('Correlação entre CARTEIRA e OPERACOES')
plt.xlabel('OPERACOES')
plt.ylabel('CARTEIRA')

st.pyplot(plt)

st.subheader('Amostra dos Dados Utilizados ⬇⬇⬇')
st.dataframe(df_bcb)

st.subheader('Links Correlacionados com o Projeto 🔗')
st.write('API utilizada no projeto: https://dadosabertos.bcb.gov.br/dataset/scr-por-sub-regiao')
st.write('O que faz parte da base de dados utilizada, e qual o objetivo? https://www.bcb.gov.br/estabilidadefinanceira/scr')