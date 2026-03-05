import pandas as pd
import requests
import unicodedata

def limpar_texto(texto):
    if pd.isna(texto) or not isinstance(texto, str): return texto
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.category(c).startswith('M')]).lower().strip()

print("🚜 INICIANDO OPERAÇÃO TERRA ARRASADA: RECONSTRUINDO PIPELINE...")

# 1. Carregando o arquivo original com a codificação correta
arquivo_original = 'Planilha de notícias - maconha - Planilha1.csv'
try:
    # Lendo em utf-8 para não destruir os acentos (Adeus 'para¡')
    df = pd.read_csv(arquivo_original, encoding='utf-8')
except Exception as e:
    print(f"❌ ERRO AO LER ARQUIVO ORIGINAL: {e}")
    exit()

# 2. Seleção Tática por Posição (Ignorando nomes bizarros de colunas)
# A coluna 6 é o Município. A coluna 7 é o Estado.
col_municipio = df.columns[6] 
col_estado = df.columns[7]

print(f"✅ Alvos travados: Municípios na coluna '{col_municipio}' | Estados na coluna '{col_estado}'")

# 3. Limpeza e Explosão corretas
df[col_municipio] = df[col_municipio].astype(str).str.strip()
df['municipio_explodido'] = df[col_municipio].str.replace(' e ', ', ', regex=False).str.split(',')
df = df.explode('municipio_explodido')

df['municipio_match'] = df['municipio_explodido'].apply(limpar_texto)
df['estado_match'] = df[col_estado].apply(limpar_texto)

# 4. Extração da Malha do IBGE
print("⏳ Baixando malha do IBGE...")
url_ibge = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
dados_ibge = requests.get(url_ibge).json()

lista_ibge = []
for mun in dados_ibge:
    try:
        estado = mun['microrregiao']['mesorregiao']['UF']['nome']
    except TypeError:
        estado = mun['regiao-imediata']['regiao-intermediaria']['UF']['nome']
    
    lista_ibge.append({
        'codigo_ibge': mun['id'],
        'municipio_ibge': mun['nome'],
        'estado_ibge': estado
    })

df_ibge = pd.DataFrame(lista_ibge)
df_ibge['municipio_match'] = df_ibge['municipio_ibge'].apply(limpar_texto)
df_ibge['estado_match'] = df_ibge['estado_ibge'].apply(limpar_texto)

# 5. O Cruzamento Real
print("⚔️ Cruzando dados...")
df_final = pd.merge(df, df_ibge, on=['municipio_match', 'estado_match'], how='left')

# Removendo colunas lixo (Unnamed) e colunas auxiliares de match
df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed|^unnamed', case=False)]
df_final = df_final.drop(columns=['municipio_match', 'estado_match', 'municipio_explodido'])

# 6. Relatório de Danos Reais
orfaos = df_final[df_final['codigo_ibge'].isnull()][[col_municipio, col_estado]].drop_duplicates()

print(f"\n🎯 PIPELINE CONCLUÍDO!")
print(f"Sucessos (Com código IBGE): {df_final['codigo_ibge'].notnull().sum()}")
print(f"Falhas reais (Órfãos): {len(orfaos)}")

if len(orfaos) > 0:
    print("\n🚨 CIDADES NÃO ENCONTRADAS NO IBGE (Estes são os erros reais do Paulo):")
    for index, row in orfaos.iterrows():
        print(f" - {row[col_municipio]} ({row[col_estado]})")

df_final.to_csv('geocannabis_FINAL.csv', index=False, encoding='utf-8-sig')
print("\n💾 Arquivo 'geocannabis_FINAL.csv' salvo com sucesso. Este é o arquivo do Dashboard.")