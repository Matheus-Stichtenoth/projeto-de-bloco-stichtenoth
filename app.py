import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import time

#Carregando o modelo com cache
@st.cache_data
def load_model():
    return joblib.load('model.pkl')

#Carregando os dados com cache
@st.cache_data
def get_bcb_data(file_path):
    response = requests.get(file_path)
    if response.status_code == 200:
        data = response.json()
        df = pd.json_normalize(data['value'])
        return df.dropna()
    else:
        raise ValueError(f"Erro na solicitação: {response.status_code}")

#Carregando o modelo
model = load_model()

def predict_risco(carteira, operacoes, estado, modalidade):
    data = pd.DataFrame({
        'CARTEIRA': [carteira],
        'OPERACOES': [operacoes],
        'ESTADO': [estado],
        'MODALIDADE': [modalidade]
    })
    prediction = model.predict(data)
    return prediction[0]
def page_curiosidades() -> None:

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
        curiosidade = f'💭 Curiosidade n° {i+1}: {df_serasa["conteudo"][i+1]}'
        st.write(curiosidade)

    st.write('Fonte: https://www.serasa.com.br/limpa-nome-online/blog/mapa-da-inadimplencia-e-renogociacao-de-dividas-no-brasil/')

    st.download_button(label='Clique aqui para baixar o arquivo com TODAS as curiosidades ▶',
                            data=df_serasa.to_csv(index=False),
                            file_name=f'curiosidades_serasa.csv')

    st.write('Quer complementar com mais informações? Utilize o botão abaixo para adicionar mais dados para à análise!')

    uploaded_file = st.file_uploader('Escolha um arquivo CSV (deve conter apenas uma coluna (com cabeçalho!))', type='csv')

    if uploaded_file is not None:
        # Carregando o CSV em um DataFrame
        df_upload = pd.read_csv(uploaded_file)
        
        # Verificando se o DataFrame tem apenas uma coluna
        if len(df_upload.columns) == 1:
            st.write('Informações novas:')
            st.write(df_upload.iloc[:, 0])  # Exibe a única coluna do DataFrame
        else:
            st.error('O arquivo deve conter apenas uma coluna.')

    st.write(
    '''Agora que já consumiu alguns conteúdos interessante sobre inadimplência, 
    acesse a página de "Simulador" para identificar o risco de crédito, baseado na característica da sua carteira.
    ''')

def page_simulador() -> None:
    carteira = st.number_input('CARTEIRA (Em R$)', min_value=0)
    operacoes = st.number_input('OPERACOES (Em Quantidade)', min_value=0)

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
        if risco == '1':
            st.write(f'As características informadas acima tendem a se tornar inadimplente.')
        else:
            st.write(f'As características informadas acima não têm tendência de inadimplência.')
        ##st.write(f'O risco previsto é: {risco}')

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

def dashboard() -> None:
    st.title('RiskMap 🗺')
    menu_lateral = ['Home','Curiosidades','Simulador']
    choice = st.sidebar.selectbox('Páginas',menu_lateral)
    if choice == 'Home':
        #Começando a interatividade com o usuário
        background_color = st.selectbox("Escolha uma cor de fundo para a página:", ["Sand", "Blue"])
            
        colormap = {
            "Sand": "#e2d9bc",
            "Blue": "#d6e3e9"
        }

        if st.checkbox('Deseja utilizar a cor acima para o fundo da página?'):
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
        else: st.markdown(f"""
                    <style>
                    .stApp {{
                        background-color: {"#fafafa"};
                    }}
                    </style>
                    """, unsafe_allow_html=True)
        st.write('Selecione ao lado esquerdo, a página que deseja visualizar.')
        st.image('https://cdn-icons-png.flaticon.com/512/1865/1865269.png')
    elif choice == 'Curiosidades':
        page_curiosidades()
    elif choice == 'Simulador':
        page_simulador()

if __name__ == '__main__':
    dashboard() 