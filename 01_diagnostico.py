import pandas as pd
import os

# 1. Verificar onde o Python está sendo executado (Current Working Directory)
diretorio_atual = os.getcwd()
print(f"DEBUG: O Python está trabalhando na pasta: {diretorio_atual}")

# 2. Listar TUDO que o Python está enxergando nessa pasta
arquivos_na_pasta = os.listdir('.')
print(f"DEBUG: Arquivos que eu encontrei aqui: {arquivos_na_pasta}")

# 3. Tentar localizar o arquivo, seja qual for o nome dele (desde que seja CSV)
csv_encontrados = [f for f in arquivos_na_pasta if f.endswith('.csv')]

if not csv_encontrados:
    print("❌ ERRO: Não encontrei NENHUM arquivo .csv nesta pasta.")
    print("Mova o arquivo do Paulo para dentro de: " + diretorio_atual)
else:
    alvo = csv_encontrados[0]
    print(f"🎯 ALVO ENCONTRADO: Tentando ler o arquivo '{alvo}'...")
    
    try:
        # Tenta ler com encoding latin1 (comum em planilhas brasileiras) caso dê erro de acento
        df = pd.read_csv(alvo, encoding='latin1', sep=None, engine='python')
        print("✅ SUCESSO! Conexão estabelecida.")
        print(f"Linhas detectadas: {len(df)}")
        print(f"Colunas: {df.columns.tolist()}")
    except Exception as e:
        print(f"❌ ERRO AO LER O CONTEÚDO: {e}")

        