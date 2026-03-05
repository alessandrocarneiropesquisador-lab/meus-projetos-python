import pandas as pd
import folium
from folium.plugins import MarkerCluster

print("🎨 REFORMULANDO ESTÉTICA: CLUSTERING E MINIMALISMO VISUAL...")

# 1. Carga de Dados
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv')
    df = df.dropna(subset=['codigo_ibge']).copy()
except FileNotFoundError:
    print("❌ Erro: Arquivo final não encontrado.")
    exit()

# 2. Resgate de Coordenadas
url_coordenadas = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coordenadas = pd.read_csv(url_coordenadas)

df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coordenadas['codigo_ibge'] = coordenadas['codigo_ibge'].astype(int)

df_mapa = pd.merge(df, coordenadas[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 3. Configuração do Mapa (Fundo escuro para destacar o cultivo - opcional, mudei para destacar o verde)
# Tiles 'cartodb dark_matter' dão um ar muito mais 'inteligência de estado'
mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4, tiles='cartodb dark_matter')

# 4. Criando o Cluster (O segredo da limpeza visual)
marker_cluster = MarkerCluster(name="Apreensões Georreferenciadas").add_to(mapa)

print("📌 Injetando marcadores minimalistas...")
for index, row in df_mapa.iterrows():
    
    instituicao = str(row['Instituição que efetuou a apreensao']) if pd.notna(row['Instituição que efetuou a apreensao']) else 'Não informada'
    qtd_pes = str(row['Quantidade de pés encontrados']) if pd.notna(row['Quantidade de pés encontrados']) else '0'
    data_apreensao = str(row['data']) if pd.notna(row['data']) else 'Sem data'
    link = str(row['Link de acesso']) if pd.notna(row['Link de acesso']) else '#'

    html_popup = f"""
    <div style="width: 250px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <h5 style="color: #2ECC71; margin-bottom: 5px;">📍 {row['municipio_ibge']}</h5>
        <p style="font-size: 12px; margin: 0;"><b>Data:</b> {data_apreensao}</p>
        <p style="font-size: 12px; margin: 0;"><b>Agência:</b> {instituicao}</p>
        <p style="font-size: 12px; margin: 0;"><b>Volume:</b> <span style="color: #2ECC71;">{qtd_pes} pés</span></p>
        <a href="{link}" target="_blank" style="font-size: 11px; color: #3498DB;">Acessar notícia</a>
    </div>
    """
    
    # Em vez de Marker, usamos CircleMarker (Pequeno, circular e discreto)
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,  # Tamanho fixo e pequeno
        popup=folium.Popup(html_popup, max_width=300),
        color='#2ECC71',
        fill=True,
        fill_color='#2ECC71',
        fill_opacity=0.7,
        weight=1
    ).add_to(marker_cluster)

# 5. Exportação
mapa.save('mapa_geocannabis_PRO.html')
print("\n✅ MAPA PROFISSIONAL GERADO: 'mapa_geocannabis_PRO.html'")