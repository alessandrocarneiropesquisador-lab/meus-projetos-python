import pandas as pd
import folium
from folium.plugins import MarkerCluster

print("🚀 FORJANDO A VERSÃO DE EXCELÊNCIA: DESIGN RESPONSIVO E DADOS PROFUNDOS...")

# 1. Carga e Purga de Dados
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv')
    df = df.dropna(subset=['codigo_ibge']).copy()
except FileNotFoundError:
    print("❌ ERRO CRÍTICO: Base de dados sumiu.")
    exit()

# 2. Resgate de Coordenadas
url_coordenadas = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coordenadas = pd.read_csv(url_coordenadas)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coordenadas['codigo_ibge'] = coordenadas['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coordenadas[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 3. Terreno (Claro/Institucional)
mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4, tiles='cartodb positron')

# Ícone da folha
icon_url = "https://img.icons8.com/color/48/marijuana-leaf.png"

# Clusterização Customizada
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

print("📌 Injetando fichas técnicas com scroll e links ativos...")

for index, row in df_mapa.iterrows():
    # Sanitização de Variáveis
    instituicao = str(row['Instituição que efetuou a apreensao']) if pd.notna(row['Instituição que efetuou a apreensao']) else 'N/I'
    qtd_pes = str(row['Quantidade de pés encontrados']) if pd.notna(row['Quantidade de pés encontrados']) else '0'
    prensada = str(row['quantidade prensada (embalada)']) if pd.notna(row['quantidade prensada (embalada)']) else '0'
    armas = str(row['armas apreendidas']) if pd.notna(row['armas apreendidas']) else '0'
    data_apreensao = str(row['data']) if pd.notna(row['data']) else 'Sem data'
    link = str(row['Link de acesso']) if pd.notna(row['Link de acesso']) else '#'

    # HTML ROBUSTO: Com scrollbar (overflow-y) e largura fixa para não estourar
    html_content = f"""
    <div style="
        width: 250px; 
        max-height: 200px; 
        overflow-y: auto; 
        font-family: 'Segoe UI', Tahoma, sans-serif; 
        padding: 10px; 
        border-left: 5px solid #27AE60;
        background-color: #f9f9f9;
        line-height: 1.4;
    ">
        <b style="color: #196F3D; font-size: 15px;">📍 {row['municipio_ibge']} ({row['estado_ibge']})</b><br>
        <hr style="margin: 5px 0; border: 0.5px solid #ddd;">
        <b>🗓️ Data:</b> {data_apreensao}<br>
        <b>🚔 Força:</b> {instituicao}<br>
        <b>🌿 Pés Erradicados:</b> <span style="color: #27AE60; font-weight: bold;">{qtd_pes}</span><br>
        <b>📦 Prensada:</b> {prensada}<br>
        <b>🔫 Armas:</b> <span style="color: #C0392B;">{armas}</span><br>
        <hr style="margin: 5px 0; border: 0.5px solid #ddd;">
        <a href="{link}" target="_blank" style="
            display: inline-block; 
            margin-top: 5px; 
            color: #2980B9; 
            font-weight: bold; 
            text-decoration: none;
        ">🔗 ABRIR REPORTAGEM ORIGINAL</a>
    </div>
    """

    # Marcador
    icon = folium.CustomIcon(icon_url, icon_size=(30, 30))
    
    # Usamos Tooltip para o hover (rápido) e Popup para garantir que o link seja clicável
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=icon,
        tooltip=folium.Tooltip(html_content, sticky=False),
        popup=folium.Popup(html_content, max_width=300)
    ).add_to(marker_cluster)

# 5. Entrega do Produto
mapa.save('mapa_geocannabis_EXCELENCIA.html')
print("\n✅ PRODUTO FINALIZADO: 'mapa_geocannabis_EXCELENCIA.html'")