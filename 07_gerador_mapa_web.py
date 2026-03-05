import pandas as pd
import folium

print("🗺️ INICIANDO RENDERIZAÇÃO DO MAPA TÁTICO PARA A WEB...")

# 1. Carregar a nossa base definitiva
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv')
except FileNotFoundError:
    print("❌ ERRO: 'geocannabis_DASHBOARD_FINAL.csv' não encontrado. Você está na pasta certa?")
    exit()

# --- A GUILHOTINA ---
# Elimina sumariamente os registros sem código IBGE (os 15 órfãos) da visualização
df = df.dropna(subset=['codigo_ibge']).copy()

# 2. Resgate Automático de Coordenadas (Latitude e Longitude)
print("⏳ Extraindo coordenadas geográficas...")
url_coordenadas = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coordenadas = pd.read_csv(url_coordenadas)

# Agora a conversão funciona porque o lixo foi removido
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coordenadas['codigo_ibge'] = coordenadas['codigo_ibge'].astype(int)

# Cruzamento cirúrgico
print("⚔️ Cruzando dados com a matriz de coordenadas...")
df_mapa = pd.merge(df, coordenadas[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 3. Construção do Terreno (Mapa centrado no Brasil)
mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4, tiles='cartodb positron')

# 4. Inserção dos Alvos e Variáveis do Projeto
print("📌 Fixando alvos e injetando variáveis no HTML...")
for index, row in df_mapa.iterrows():
    
    # Blindagem contra dados nulos na planilha original
    instituicao = str(row['Instituição que efetuou a apreensao']) if pd.notna(row['Instituição que efetuou a apreensao']) else 'Não informada'
    qtd_pes = str(row['Quantidade de pés encontrados']) if pd.notna(row['Quantidade de pés encontrados']) else '0'
    qtd_prensada = str(row['quantidade prensada (embalada)']) if pd.notna(row['quantidade prensada (embalada)']) else '0'
    armas = str(row['armas apreendidas']) if pd.notna(row['armas apreendidas']) else '0'
    data_apreensao = str(row['data']) if pd.notna(row['data']) else 'Sem data'
    link = str(row['Link de acesso']) if pd.notna(row['Link de acesso']) else '#'

    # Construção do Front-End (O que aparece quando clica no ponto)
    html_popup = f"""
    <div style="width: 300px; font-family: Arial, sans-serif;">
        <h4 style="color: #196F3D; margin-bottom: 5px; font-size: 16px;">📍 {row['municipio_ibge']} - {row['estado_ibge']}</h4>
        <hr style="margin: 5px 0;">
        <p style="margin: 2px 0; font-size: 13px;"><b>Data:</b> {data_apreensao}</p>
        <p style="margin: 2px 0; font-size: 13px;"><b>Força de Segurança:</b> {instituicao}</p>
        <p style="margin: 2px 0; font-size: 13px;"><b>Pés Erradicados:</b> <span style="color: #27AE60; font-weight: bold;">{qtd_pes}</span></p>
        <p style="margin: 2px 0; font-size: 13px;"><b>Maconha Prensada:</b> {qtd_prensada}</p>
        <p style="margin: 2px 0; font-size: 13px;"><b>Armas Apreendidas:</b> <span style="color: #C0392B; font-weight: bold;">{armas}</span></p>
        <hr style="margin: 5px 0;">
        <a href="{link}" target="_blank" style="font-size: 12px; color: #2980B9; text-decoration: none;">🔗 Ver Notícia Original</a>
    </div>
    """
    
    # Injetar o HTML no formato exigido pelo Folium
    iframe = folium.IFrame(html=html_popup, width=320, height=210)
    popup = folium.Popup(iframe, max_width=320)
    
    # Adicionar o marcador no mapa
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=popup,
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(mapa)

# 5. Exportação do Produto Final
arquivo_saida = 'mapa_interativo_nevidh.html'
mapa.save(arquivo_saida)
print(f"\n✅ MISSÃO CUMPRIDA! O arquivo '{arquivo_saida}' foi gerado.")
print("Abra este arquivo no seu navegador (Chrome/Edge) para inspecionar o painel interativo.")