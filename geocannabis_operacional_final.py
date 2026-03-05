import pandas as pd
import folium
from folium.plugins import MarkerCluster

print("🦅 EXECUTANDO PROTOCOLO FINAL: CERCAMENTO, ICONOGRAFIA E CRÉDITOS...")

# 1. DADOS
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv').dropna(subset=['codigo_ibge'])
    url_coords = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
    coords = pd.read_csv(url_coords)
    df['codigo_ibge'] = df['codigo_ibge'].astype(int)
    coords['codigo_ibge'] = coords['codigo_ibge'].astype(int)
    df_mapa = pd.merge(df, coords[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')
except Exception as e:
    print(f"❌ ERRO NA CARGA: {e}")
    exit()

# 2. MAPA CERCADO (BRASIL APENAS)
limites_br = [[-34.5, -74.5], [5.5, -34.0]]
mapa = folium.Map(
    location=[-14.2350, -51.9253], zoom_start=4, 
    tiles='cartodb positron', control_scale=True,
    min_zoom=4, max_bounds=True,
    min_lat=limites_br[0][0], max_lat=limites_br[1][0],
    min_lon=limites_br[0][1], max_lon=limites_br[1][1]
)

# 3. POLÍGONO DA MACONHA (SERTÃO)
folium.Polygon(
    locations=[[-8.1, -40.2], [-7.5, -39.0], [-8.0, -37.8], [-9.2, -38.0], [-9.8, -39.5], [-9.2, -40.8]],
    color="orange", weight=1, fill=True, fill_color="yellow", fill_opacity=0.15,
    tooltip="Polígono da Maconha"
).add_to(mapa)

# 4. ÍCONES E INSÍGNIAS (LINKS WEB ESTÁVEIS)
icon_leaf = "https://img.icons8.com/color/48/marijuana-leaf.png"
icon_pistol = "https://img.icons8.com/ios-filled/50/000000/pistol.png" # Link estável para pistola preta
icon_brick = "https://img.icons8.com/color/48/brick.png"
icon_link = "https://img.icons8.com/ios-glyphs/30/000000/link--v1.png"

def get_badge(row):
    f = str(row['Instituição que efetuou a apreensao']).upper()
    uf = str(row['estado_ibge']).upper()
    if 'FEDERAL' in f or 'PF' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Bras%C3%A3o_da_Pol%C3%ADcia_Federal.svg/100px-Bras%C3%A3o_da_Pol%C3%ADcia_Federal.svg.png"
    if 'PRF' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Bras%C3%A3o_da_Pol%C3%ADcia_Rodovi%C3%A1ria_Federal.svg/100px-Bras%C3%A3o_da_Pol%C3%ADcia_Rodovi%C3%A1ria_Federal.svg.png"
    if 'MINAS GERAIS' in uf or 'MG' in uf:
        if 'CIVIL' in f or 'PC' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Bras%C3%A3o_da_PCMG.png/100px-Bras%C3%A3o_da_PCMG.png"
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Bras%C3%A3o_da_PMMG.png/100px-Bras%C3%A3o_da_PMMG.png"
    if 'PERNAMBUCO' in uf or 'PE' in uf: return "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Bras%C3%A3o_da_PMPE.png/100px-Bras%C3%A3o_da_PMPE.png"
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Coat_of_arms_of_Brazil.svg/100px-Coat_of_arms_of_Brazil.svg.png"

# 5. CLUSTER E MARCADORES
marker_cluster = MarkerCluster(
    icon_create_function="""
        function(cluster) {
            var count = cluster.getChildCount();
            return L.divIcon({
                html: '<div style="background-image: url(' + '""" + icon_leaf + """' + '); background-size: contain; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; text-shadow: 1px 1px 2px black;">' + count + '</div>',
                className: 'custom-cluster', iconSize: L.point(40, 40)
            });
        }
    """,
    showCoverageOnHover=False
).add_to(mapa)

for _, row in df_mapa.iterrows():
    tem_arma = pd.notna(row['armas apreendidas']) and str(row['armas apreendidas']).strip() not in ['0', 'X', 'NÃO', '']
    icon_final = folium.CustomIcon(icon_pistol if tem_arma else icon_leaf, icon_size=(28, 28))
    
    badge_url = get_badge(row)
    
    html_card = f"""
    <div style="width: 200px; font-family: Arial, sans-serif; font-size: 12px; text-align: center;">
        <img src="{badge_url}" width="40"><br>
        <b style="font-size: 13px;">{row['municipio_ibge']} - {row['estado_ibge']}</b><hr>
        <div style="text-align: left; padding-left: 10px;">
            <img src="{icon_leaf}" width="14"> <b>Pés:</b> {row['Quantidade de pés encontrados']}<br>
            <img src="{icon_brick}" width="14"> <b>Prensada:</b> {row['quantidade prensada (embalada)']}<br>
            <img src="{icon_pistol}" width="14"> <b>Armas:</b> {row['armas apreendidas']}
        </div>
        <hr>
        <a href="{row['Link de acesso']}" target="_blank" style="color: #2980B9; font-size: 11px;">
            <img src="{icon_link}" width="12"> Matéria Completa
        </a>
    </div>
    """
    folium.Marker(location=[row['latitude'], row['longitude']], icon=icon_final, tooltip=folium.Tooltip(html_card)).add_to(marker_cluster)

# 6. INTERFACE DE COMANDO
layout_html = f"""
    <style> .leaflet-control-scale {{ left: auto !important; right: 20px !important; bottom: 20px !important; }} </style>
    <div style="position: fixed; top: 15px; left: 50%; transform: translateX(-50%); z-index: 9999; text-align: center;">
        <h1 style="font-family: 'Arial Black', sans-serif; font-weight: bold; font-size: 38px; color: black; margin: 0; text-shadow: 2px 2px white;">GEOCANNABIS BR</h1>
    </div>
    <div style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Compass_rose_simple.svg" width="60">
    </div>
    <div style="position: fixed; bottom: 50px; right: 20px; z-index: 9999; background: white; padding: 12px; border: 2px solid black; font-family: sans-serif; font-size: 11px;">
        <b style="font-size: 12px;">LEGENDA TÁTICA</b><hr style="margin: 3px 0;">
        <img src="{icon_pistol}" width="15"> = Arma de Fogo<br>
        <img src="{icon_leaf}" width="15"> = Cannabis (Local/Qtd)<br>
        <img src="{icon_brick}" width="15"> = Maconha Prensada<br>
        <img src="{icon_link}" width="15"> = Matéria Completa
    </div>
    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; font-family: Arial, sans-serif; font-size: 11px; color: black; background: rgba(255,255,255,0.7); padding: 5px; border-radius: 3px;">
        <b>Produzido por:</b> Alessandro Carneiro | <b>Dados:</b> Dr. Paulo Fraga
    </div>
"""
mapa.get_root().html.add_child(folium.Element(layout_html))

mapa.save('GEOCANNABIS_BR_DEFINITIVO.html')
print("\n✅ MAPA GERADO COM SUCESSO. SEM ERROS DE ARQUIVO.")