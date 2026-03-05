import pandas as pd
import folium
from folium.plugins import MarkerCluster

print("🛡️ EXECUTANDO CERCAMENTO TÁTICO E FINALIZAÇÃO VISUAL...")

# 1. Carga de Dados
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv')
    df = df.dropna(subset=['codigo_ibge']).copy()
except FileNotFoundError:
    print("❌ ERRO: Base de dados não encontrada. Verifique o diretório.")
    exit()

# 2. Resgate de Coordenadas e Cruzamento
url_coordenadas = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coordenadas = pd.read_csv(url_coordenadas)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coordenadas['codigo_ibge'] = coordenadas['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coordenadas[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# --- CONFIGURAÇÃO DE FRONTEIRAS (O CERCAMENTO) ---
# Definindo os limites aproximados do território brasileiro [Sul, Oeste], [Norte, Leste]
limites_br = [[-34.5, -74.5], [5.5, -34.0]]

# 3. Criação do Mapa com Restrição de Navegação
mapa = folium.Map(
    location=[-14.2350, -51.9253], 
    zoom_start=4, 
    tiles='cartodb positron',
    min_zoom=4,               # Impede o usuário de ver o globo todo
    max_bounds=True,          # Trava a câmera no perímetro
    min_lat=limites_br[0][0], 
    max_lat=limites_br[1][0],
    min_lon=limites_br[0][1], 
    max_lon=limites_br[1][1]
)

# 4. Customização de Ícones e Clusters
icon_url = "https://img.icons8.com/color/48/marijuana-leaf.png"
icon_create_function = """
    function(cluster) {
        var childCount = cluster.getChildCount(); 
        return L.divIcon({ 
            html: '<div style="background-image: url(' + '""" + icon_url + """' + '); background-size: cover; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; text-shadow: 1px 1px 2px black;">' + childCount + '</div>', 
            className: 'marker-cluster-custom', 
            iconSize: L.point(40, 40) 
        });
    }
"""
marker_cluster = MarkerCluster(icon_create_function=icon_create_function).add_to(mapa)

# 5. Injeção de Dados (Hover + Popup)
for index, row in df_mapa.iterrows():
    # Tratamento de Nulos para a Ficha Técnica
    instituicao = str(row['Instituição que efetuou a apreensao']) if pd.notna(row['Instituição que efetuou a apreensao']) else 'N/I'
    qtd_pes = str(row['Quantidade de pés encontrados']) if pd.notna(row['Quantidade de pés encontrados']) else '0'
    data_ap = str(row['data']) if pd.notna(row['data']) else 'Sem data'
    link = str(row['Link de acesso']) if pd.notna(row['Link de acesso']) else '#'

    html_content = f"""
    <div style="width: 240px; font-family: sans-serif; padding: 5px; line-height: 1.5;">
        <b style="color: #27AE60; font-size: 14px;">📍 {row['municipio_ibge']} - {row['estado_ibge']}</b><br>
        <hr style="margin: 5px 0;">
        <b>Data:</b> {data_ap}<br>
        <b>Força:</b> {instituicao}<br>
        <b>Pés:</b> <span style="color: #27AE60; font-weight: bold;">{qtd_pes}</span><br>
        <hr style="margin: 5px 0;">
        <a href="{link}" target="_blank" style="color: #2980B9; font-weight: bold; text-decoration: none;">🔗 ABRIR NOTÍCIA</a>
    </div>
    """

    # Marcador Customizado
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_url, icon_size=(30, 30)),
        tooltip=folium.Tooltip(html_content, sticky=False), # O "passar do rato"
        popup=folium.Popup(html_content, max_width=300)      # O clique para o link
    ).add_to(marker_cluster)

# 6. Salvamento
mapa.save('mapa_geocannabis_DELIMITADO.html')
print("\n✅ SUCESSO ABSOLUTO: O mapa está cercado e operacional.")