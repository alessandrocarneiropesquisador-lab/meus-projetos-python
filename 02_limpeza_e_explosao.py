import pandas as pd

arquivo = 'Planilha de notícias - maconha - Planilha1.csv'

# 1. Carregar tentando detectar o separador automaticamente
try:
    # sep=None com engine='python' faz o pandas descobrir se é , ou ;
    df = pd.read_csv(arquivo, encoding='latin1', sep=None, engine='python')
    
    print("--- DIAGNÓSTICO DE COLUNAS ---")
    # Isso vai mostrar o nome REAL de cada coluna entre aspas
    print([f"'{col}'" for col in df.columns])
    print("------------------------------")

    # 2. Localizar a coluna que contém a palavra 'municipio' ou 'localidade'
    # Vamos renomear na força bruta para não ter erro
    possiveis_nomes = ['município', 'municipio', 'localidade', 'cidade']
    coluna_alvo = None
    
    for col in df.columns:
        col_limpa = col.strip().lower()
        if any(nome in col_limpa for nome in possiveis_nomes):
            coluna_alvo = col
            break

    if coluna_alvo:
        print(f"🎯 Alvo detectado: Vou usar a coluna '{coluna_alvo}'")
        df = df.rename(columns={coluna_alvo: 'municipio_padrao'})
    else:
        raise ValueError("Não encontrei nenhuma coluna parecida com 'município'.")

    # 3. Explosão
    df['municipio_padrao'] = df['municipio_padrao'].astype(str).str.strip()
    df['municipio_limpo'] = df['municipio_padrao'].str.replace(' e ', ', ', regex=False).str.split(',')
    df_final = df.explode('municipio_limpo')
    df_final['municipio_limpo'] = df_final['municipio_limpo'].str.strip()

    print(f"\n✅ SUCESSO! Linhas após explosão: {len(df_final)}")
    df_final.to_csv('base_explodida.csv', index=False, encoding='utf-8-sig')

except Exception as e:
    print(f"❌ ERRO CRÍTICO: {e}")