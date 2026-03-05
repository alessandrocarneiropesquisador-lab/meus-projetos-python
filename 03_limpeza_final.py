import pandas as pd
import unicodedata

# Função cirúrgica para remover acentos e forçar minúsculas
def limpar_texto(texto):
    if pd.isna(texto) or not isinstance(texto, str):
        return texto
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.category(c).startswith('M')]).lower().strip()

# 1. Carregar a base que explodimos no passo anterior
try:
    df = pd.read_csv('base_explodida.csv')
except FileNotFoundError:
    print("❌ ERRO CRÍTICO: 'base_explodida.csv' não encontrado. O arquivo sumiu ou você está na pasta errada.")
    exit()

# 2. Limpar as colunas de localização (Alvo: município e Estado)
df['municipio_limpo'] = df['municipio_limpo'].apply(limpar_texto)
df['estado_limpo'] = df['Estado'].apply(limpar_texto)

# 3. Remover as colunas de lixo que vieram do Excel original do Paulo
df = df.loc[:, ~df.columns.str.contains('^Unnamed|^unnamed', case=False)]

print("--- AMOSTRA DOS DADOS LIMPOS ---")
print(df[['municipio_limpo', 'estado_limpo']].head(10))

# 4. Salvar a base PRONTA para o cruzamento com o IBGE
df.to_csv('base_pronta_para_mapa.csv', index=False, encoding='utf-8-sig')
print("\n✅ MISSÃO CUMPRIDA: 'base_pronta_para_mapa.csv' gerada com texto limpo!")