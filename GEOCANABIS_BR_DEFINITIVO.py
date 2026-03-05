import pandas as pd
import folium
from folium.plugins import MarkerCluster

print("🦅 REFORMULANDO ESTRUTURA: GEOCANABIS BR EM MODO OPERACIONAL...")

# 1. Carga de Dados
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv').dropna(subset=['codigo_ibge'])
except:
    print("❌ Base de dados não encontrada.")
    exit()

url_coords = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coords = pd.read_csv(url_coords)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coords['codigo_ibge'] = coords['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coords[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 2. Mapa Base com Escala Ativada
mapa = folium.Map(
    location=[-14.2350, -51.9253], zoom_start=4, 
    tiles='cartodb positron', control_scale=True,
    min_zoom=4, max_bounds=True
)

# 3. Definição de Ícones e Insígnias (Links de Alta Estabilidade)
icon_leaf = "https://img.icons8.com/color/48/marijuana-leaf.png"
icon_pistol = "https://img.icons8.com/ios-filled/50/000000/pistol.png"
icon_brick = "https://img.icons8.com/color/48/brick.png"

def get_insignia(forca):
    f = str(forca).upper()
    if 'PF' in f or 'FEDERAL' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Bras%C3%A3o_da_Pol%C3%ADcia_Federal.svg/100px-Bras%C3%A3o_da_Pol%C3%ADcia_Federal.svg.png"
    if 'PRF' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Bras%C3%A3o_da_Pol%C3%ADcia_Rodovi%C3%A1ria_Federal.svg/100px-Bras%C3%A3o_da_Pol%C3%ADcia_Rodovi%C3%A1ria_Federal.svg.png"
    if 'PM' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Bras%C3%A3o_da_PMMG.png/100px-Bras%C3%A3o_da_PMMG.png"
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Coat_of_arms_of_Brazil.svg/100px-Coat_of_arms_of_Brazil.svg.png"

# 4. Clusterização Customizada (Folha com contador)
icon_cluster = """
    function(cluster) {
        var count = cluster.getChildCount();
        return L.divIcon({
            html: '<div style="background-image: url(' + '""" + icon_leaf + """' + '); background-size: contain; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; text-shadow: 1px 1px 2px black;">' + count + '</div>',
            className: 'custom-cluster', iconSize: L.point(40, 40)
        });
    }
"""
marker_cluster = MarkerCluster(icon_create_function=icon_cluster, showCoverageOnHover=False).add_to(mapa)

# 5. Marcadores e Cards
for _, row in df_mapa.iterrows():
    # Lógica do Ícone: Pistola se houver arma, Folha se não.
    tem_arma = pd.notna(row['armas apreendidas']) and str(row['armas apreendidas']).strip() not in ['0', 'X', '']
    icon_url = icon_pistol if tem_arma else icon_leaf
    
    insignia = get_insignia(row['Instituição que efetuou a apreensao'])
    
    html_card = f"""
    <div style="width: 180px; font-family: sans-serif; text-align: center;">
        <img src="{insignia}" width="40" style="margin-bottom: 5px;"><br>
        <b style="font-size: 13px; color: #1B5E20;">📍 {row['municipio_ibge']}</b>
        <hr style="margin: 5px 0;">
        <div style="text-align: left; font-size: 11px;">
            <img src="{icon_leaf}" width="14"> <b>Pés:</b> {row['Quantidade de pés encontrados']}<br>
            <img src="{icon_brick}" width="14"> <b>Prensada:</b> {row['quantidade prensada (embalada)']}<br>
            <img src="{icon_pistol}" width="14"> <b>Armas:</b> {row['armas apreendidas']}
        </div>
        <a href="{row['Link de acesso']}" target="_blank" style="display: block; margin-top: 8px; font-size: 10px; color: #2980B9;">[Ver Fonte]</a>
    </div>
    """
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_url, icon_size=(25, 25)),
        tooltip=folium.Tooltip(html_card)
    ).add_to(marker_cluster)

# 6. Interface (Título, Seta Norte, Legenda e Créditos)
layout_css = f"""
    <style>
        .leaflet-control-scale {{ left: auto !important; right: 20px !important; bottom: 20px !important; }}
    </style>

    <div style="position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; text-align: center;">
        <h1 style="font-family: 'Arial Black', sans-serif; font-size: 40px; color: black; margin: 0; text-shadow: 3px 3px 0 white;">GEOCANABIS BR</h1>
        <p style="font-family: Arial; font-weight: bold; margin: 0;">SISTEMA DE MONITORAMENTO E ERRADICAÇÃO</p>
    </div>

    <div style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Compass_rose_simple.svg" width="60">
    </div>

    <div style="position: fixed; bottom: 85px; left: 20px; z-index: 9999; background: white; padding: 10px; border: 3px solid black; font-family: sans-serif; font-size: 12px;">
        <b style="font-size: 14px;">LEGENDA TÁTICA</b><hr style="margin: 5px 0;">
        <img src="{icon_leaf}" width="16"> Cannabis (Cultivo)<br>
        <img src="{icon_pistol}" width="16"> Arma de Fogo (Apreensão)<br>
        <img src="{icon_brick}" width="16"> Maconha Prensada<br>
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Coat_of_arms_of_Brazil.svg/100px-Coat_of_arms_of_Brazil.svg.png" width="16"> Unidade de Segurança
    </div>

    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; font-family: Arial; font-size: 10px; color: black; background: rgba(255,255,255,0.7); padding: 5px;">
        <b>Geoprocessamento:</b> Alessandro (UFJF)<br>
        <b>Coordenação:</b> Prof. Dr. Paulo Fraga | 2026
    </div>
"""
mapa.get_root().html.add_child(folium.Element(layout_css))

mapa.save('GEOCANABIS_BR_OPERACIONAL_V6.html')
print("\n✅ PRODUTO ENTREGUE: 'GEOCANABIS_BR_OPERACIONAL_V6.html'")