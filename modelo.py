import pandas as pd
import requests
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
import joblib

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
df_bcb = df_bcb.drop(columns=['DATA_BASE'])

X = df_bcb.drop(columns=['RISCO'])
y = df_bcb['RISCO']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['OPERACOES', 'CARTEIRA']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['ESTADO', 'SUB_REGIAO', 'MODALIDADE'])
    ])

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression())
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
model.fit(X_train, y_train)

joblib.dump(model, 'model.pkl')
