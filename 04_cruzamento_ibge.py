import pandas as pd
import requests
import unicodedata

def limpar_texto(texto):
    if pd.isna(texto) or not isinstance(texto, str): return texto
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.category(c).startswith('M')]).lower().strip()

print("⏳ Conectando aos servidores do IBGE e blindando contra falhas da API...")

url_ibge = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
response = requests.get(url_ibge)
dados_ibge = response.json()

lista_ibge = []
for mun in dados_ibge:
    # Tática de evasão: Se o IBGE enviar 'microrregiao' nula (erro do governo), usamos a estrutura nova
    try:
        sigla = mun['microrregiao']['mesorregiao']['UF']['sigla']
        estado = mun['microrregiao']['mesorregiao']['UF']['nome']
    except TypeError:
        sigla = mun['regiao-imediata']['regiao-intermediaria']['UF']['sigla']
        estado = mun['regiao-imediata']['regiao-intermediaria']['UF']['nome']

    lista_ibge.append({
        'codigo_ibge': mun['id'],
        'municipio_ibge': mun['nome'],
        'uf_sigla': sigla,
        'estado_ibge': estado
    })

df_ibge = pd.DataFrame(lista_ibge)
df_ibge['municipio_match'] = df_ibge['municipio_ibge'].apply(limpar_texto)
df_ibge['estado_match'] = df_ibge['estado_ibge'].apply(limpar_texto)

try:
    df_cannabis = pd.read_csv('base_pronta_para_mapa.csv')
except FileNotFoundError:
    print("❌ ERRO CRÍTICO: 'base_pronta_para_mapa.csv' sumiu.")
    exit()

df_cannabis['municipio_match'] = df_cannabis['municipio_limpo']
df_cannabis['estado_match'] = df_cannabis['estado_limpo']

print("⚔️ Executando o cruzamento relacional (Match)...")
df_final = pd.merge(df_cannabis, df_ibge, on=['municipio_match', 'estado_match'], how='left')

orfaos = df_final[df_final['codigo_ibge'].isnull()][['municipio_limpo', 'estado_limpo']].drop_duplicates()

print(f"\n✅ GEORREFERENCIAMENTO CONCLUÍDO!")
print(f"Total de registros com código IBGE: {df_final['codigo_ibge'].notnull().sum()}")
print(f"Total de falhas (Órfãos): {len(orfaos)}")

if len(orfaos) > 0:
    print("\n🚨 ALERTA DE SUJEIRA: O IBGE rejeitou estas cidades (provável erro do Paulo ou estado incorreto):")
    for index, row in orfaos.iterrows():
        print(f" - Município: '{row['municipio_limpo']}' | Estado: '{row['estado_limpo']}'")

df_final = df_final.drop(columns=['municipio_match', 'estado_match'])
df_final.to_csv('geocannabis_com_ibge.csv', index=False, encoding='utf-8-sig')
print("\n💾 Arquivo 'geocannabis_com_ibge.csv' forjado com sucesso!")