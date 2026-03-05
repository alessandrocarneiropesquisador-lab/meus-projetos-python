import pandas as pd
import requests
import unicodedata
import re

def limpar_texto(texto):
    if pd.isna(texto) or not isinstance(texto, str): return texto
    nfkd = unicodedata.normalize('NFKD', str(texto))
    return "".join([c for c in nfkd if not unicodedata.category(c).startswith('M')]).lower().strip()

print("🦅 OPERAÇÃO CIRÚRGICA DE REPESCAGEM: IGNORANDO ESPAÇOS FANTASMAS...")

arquivo_original = 'Planilha de notícias - maconha - Planilha1.csv'
try:
    df = pd.read_csv(arquivo_original, encoding='utf-8')
except Exception as e:
    print(f"❌ FALHA DE LEITURA: {e}")
    exit()

col_municipio = df.columns[6] 
col_estado = df.columns[7]

# Forçar todos os dados para string e remover espaços extras e quebras de linha antes de qualquer coisa
df[col_municipio] = df[col_municipio].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
df[col_estado] = df[col_estado].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)

# 1. Dicionário de Inteligência Tática (Agressivo)
dicionario_correcao = {
    "Parauaopebas": "Parauapebas",
    "Cabobró": "Cabrobó",
    "Caraúba": "Caraúbas",
    "Santo Amaro": "Santo Amaro do Maranhão",
    "Conceição do Lago Açu": "Conceição do Lago-Açu",
    "Rio Japurá": "Japurá",
    "DF - Ceilândia": "Brasília", 
    "Circunscrição de Salgueiro": "Salgueiro",
    "proximidades de Angico": "Mairi", # Angico é povoado de Mairi na BA
    "Encontrado no km 402 da rodovia 020 em Caucaia": "Caucaia",
    "Barco próximo ao município de Novo Airão": "Novo Airão",
    "Entre Curaçá e Abaré": "Curaçá, Abaré",
    "Alto Paranaíba": "Patrocínio, Coromandel",
    "Mulungu e Pacoti": "Mulungu, Pacoti",
    "Entre Tacuru e Iguatemi": "Tacuru, Iguatemi",
    "Santa Helena e Mirinzal": "Santa Helena, Mirinzal",
    "Benedito Leite e São Domingos do Azeitão": "Benedito Leite, São Domingos do Azeitão",
    "Barro Alto e Souto Soares": "Barro Alto, Souto Soares",
    "Orocó/PE, Triunfo/PE, Salgueiro/PE, Cabrobó/PE, Belém do São Francisco/PE, Betânia/PE, Flores/PE, Carnaubeira da Penha/PE e Sertânia/PE e Dormentes/PE": "Orocó, Triunfo, Salgueiro, Cabrobó, Belém do São Francisco, Betânia, Flores, Carnaubeira da Penha, Sertânia, Dormentes",
    "Abaré, Andorinha, Cabrobó/PE, Campo Formoso, Casa Nova, Curaçá, João Dourado, Sento Sé e Xique-Xique": "Abaré, Andorinha, Cabrobó, Campo Formoso, Casa Nova, Curaçá, João Dourado, Sento Sé, Xique-Xique",
    "Cabrobó e Belém de São Francisco": "Cabrobó, Belém do São Francisco",
    "Salgueiro, Cabrobó, Orocó, Belém do São Francisco, Ibimirim e Serra Talhada": "Salgueiro, Cabrobó, Orocó, Belém do São Francisco, Ibimirim, Serra Talhada",
    "Ilhas do Rio São Francisco e na Região de Orocó, Cabrobó, Belém do São Francisco e Santa Maria da Boa Vista. Além disso, a PF também esteve presente em áreas de caatinga em Salgueiro, Carnaubeira da Penha, Serra Talhada, Betânia, Parnamirim, Ibó e Floresta": "Orocó, Cabrobó, Belém do São Francisco, Santa Maria da Boa Vista, Salgueiro, Carnaubeira da Penha, Serra Talhada, Betânia, Parnamirim, Floresta",
    "Ilhas do Rio São Francisco e nas regiões de Orocó, Cabobró, Belém do São Francisco, Santa Maria da Boa Vista, e nas áreas de caatinga em Salgueiro, Carnaubeira da Penha, Serra Talhada, Betânia e Floresta": "Orocó, Cabrobó, Belém do São Francisco, Santa Maria da Boa Vista, Salgueiro, Carnaubeira da Penha, Serra Talhada, Betânia, Floresta",
    "Principalmente Salgueiro, Cabrobó, Sertânia, Floresta, Belém de São Francisco e Afogados da Ingazeira": "Salgueiro, Cabrobó, Sertânia, Floresta, Belém do São Francisco, Afogados da Ingazeira",
    "Garrafão do Norte, Cachoeira do Piriá, Capitão Poço, Concórdia do Pará e Nova Esperança do Piriá": "Garrafão do Norte, Cachoeira do Piriá, Capitão Poço, Concórdia do Pará, Nova Esperança do Piriá",
    "Buriticupu, Alto Alegre do Pindaré, Maracaçumé, Centro do Guilherme, Centro Novo do Maranhão": "Buriticupu, Alto Alegre do Pindaré, Maracaçumé, Centro do Guilherme, Centro Novo do Maranhão",
    "Nova Orlinda do Norte e Maués": "Nova Olinda do Norte, Maués",
    "Orocó, Cabrobó e Ibó": "Orocó, Cabrobó"
}

# Varredura Substring: Destrói qualquer trecho que dê match
for errado, certo in dicionario_correcao.items():
    df[col_municipio] = df[col_municipio].apply(lambda x: str(x).replace(errado, certo) if errado in str(x) else x)

# 2. Varredor Regex
df[col_municipio] = df[col_municipio].apply(lambda x: re.sub(r"\(.*?\)", "", str(x)).strip())
df[col_estado] = df[col_estado].apply(lambda x: re.sub(r"\(.*?\)", "", str(x)).strip())

# 3. Explosão
df['municipio_explodido'] = df[col_municipio].str.replace(' e ', ', ', regex=False).str.split(',')
df = df.explode('municipio_explodido')
df['municipio_explodido'] = df['municipio_explodido'].str.split('/') # Lida com "Orocó/PE"
df = df.explode('municipio_explodido')
df['municipio_explodido'] = df['municipio_explodido'].str.strip()

df['municipio_match'] = df['municipio_explodido'].apply(limpar_texto)
df['estado_match'] = df[col_estado].apply(limpar_texto)

# Correções Forçadas de Estado para garantir que o IBGE aprove
df['estado_match'] = df['estado_match'].str.replace('norte da bahia.', 'bahia', regex=False)
df['estado_match'] = df['estado_match'].str.replace('pernambuco e paraiba', 'pernambuco', regex=False)
df['estado_match'] = df['estado_match'].str.replace('maranhao e para', 'maranhao', regex=False)
df.loc[df['municipio_match'] == 'brasilia', 'estado_match'] = 'distrito federal' # Conserta o DF que estava em Goiás

# Filtro de Expurgo
df = df[~df['estado_match'].isin(['chile', 'paraguai', 'nan'])]
df = df[~df['municipio_match'].isin(['x', 'nan', 'aparato geral', 'sem informacoes', 'pe'])]
df = df[~df['municipio_match'].str.startswith('aparato geral', na=False)]

# 4. Cruzamento IBGE
print("⏳ A extrair malha georreferenciada do IBGE...")
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

df_final = pd.merge(df, df_ibge, on=['municipio_match', 'estado_match'], how='left')

# Limpeza
df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed|^unnamed', case=False)]
df_final = df_final.drop(columns=['municipio_match', 'estado_match', 'municipio_explodido'])

# Relatório de Danos
orfaos = df_final[df_final['codigo_ibge'].isnull()][[col_municipio, col_estado]].drop_duplicates()

print(f"\n🎯 PROCESSO CONCLUÍDO COM RIGOR!")
print(f"Alvos resgatados com sucesso (Com código IBGE): {df_final['codigo_ibge'].notnull().sum()}")
print(f"Baixas irrecuperáveis (Lixo Puro): {len(orfaos)}")

if len(orfaos) > 0:
    for index, row in orfaos.iterrows():
        print(f" - {row[col_municipio]} ({row[col_estado]})")

df_final.to_csv('geocannabis_DASHBOARD_FINAL.csv', index=False, encoding='utf-8-sig')
print("\n💾 Ficheiro 'geocannabis_DASHBOARD_FINAL.csv' forjado com sucesso absoluto.")