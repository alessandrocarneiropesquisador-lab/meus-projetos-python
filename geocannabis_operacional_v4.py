import pandas as pd
import folium
from folium.plugins import MarkerCluster, FloatImage

print("🦅 EXECUTANDO REORDENAMENTO TÁTICO E INJEÇÃO DE INSÍGNIAS...")

# 1. Dados
df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv').dropna(subset=['codigo_ibge'])
url_coords = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coords = pd.read_csv(url_coords)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coords['codigo_ibge'] = coords['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coords[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 2. Mapa Base e Cercamento
mapa = folium.Map(
    location=[-14.2350, -51.9253], zoom_start=4, 
    tiles='cartodb positron', control_scale=False, # Escala manual depois
    min_zoom=4, max_bounds=True
)
# Escala no Canto Inferior Direito (Invertida com créditos)
folium.ControlScale(position='bottomright').add_to(mapa)

# 3. Seta Norte - Canto Superior Direito
url_norte = "https://www.svgrepo.com/show/447990/compass-north.svg"
FloatImage(url_norte, top=2, right=2).add_to(mapa)

# 4. Lógica de Insígnias e Ícones
icon_leaf = "https://img.icons8.com/color/48/marijuana-leaf.png"
icon_pistol = "https://img.icons8.com/ios-filled/50/000000/pistol.png"
icon_brick = "https://img.icons8.com/color/48/brick.png"
brasao_rep = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Coat_of_arms_of_Brazil.svg/200px-Coat_of_arms_of_Brazil.svg.png"

def get_insignia(forca):
    f = str(forca).upper()
    if 'PF' in f or 'FEDERAL' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Bras%C3%A3o_da_Pol%C3%ADcia_Federal.svg/200px-Bras%C3%A3o_da_Pol%C3%ADcia_Federal.svg.png"
    if 'PRF' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Bras%C3%A3o_da_Pol%C3%ADcia_Rodovi%C3%A1ria_Federal.svg/200px-Bras%C3%A3o_da_Pol%C3%ADcia_Rodovi%C3%A1ria_Federal.svg.png"
    if 'PM' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Bras%C3%A3o_da_PMMG.png/200px-Bras%C3%A3o_da_PMMG.png"
    return brasao_rep

marker_cluster = MarkerCluster(showCoverageOnHover=False).add_to(mapa)

for _, row in df_mapa.iterrows():
    # Decisão do Ícone de Marcador: Prioridade Pistola se houver arma
    tem_arma = pd.notna(row['armas apreendidas']) and str(row['armas apreendidas']).strip() not in ['0', 'X', '']
    icon_url = icon_pistol if tem_arma else icon_leaf
    
    insignia = get_insignia(row['Instituição que efetuou a apreensao'])
    
    html = f"""
    <div style="width: 200px; font-family: 'Arial Black', sans-serif; font-size: 11px;">
        <div style="text-align:center;"><img src="{insignia}" width="40"></div>
        <hr>
        <img src="{icon_leaf}" width="15"> <b>Pés:</b> {row['Quantidade de pés encontrados']}<br>
        <img src="{icon_brick}" width="15"> <b>Prensada:</b> {row['quantidade prensada (embalada)']}<br>
        <img src="{icon_pistol}" width="15"> <b>Armas:</b> {row['armas apreendidas']}<br>
        <a href="{row['Link de acesso']}" target="_blank" style="color: #2980B9;">[Ver Fonte]</a>
    </div>
    """
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_url, icon_size=(25, 25)),
        tooltip=folium.Tooltip(html)
    ).add_to(marker_cluster)

# 5. Interface Customizada (Título, Legenda e Créditos)
layout_html = f"""
    <div style="position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; text-align: center;">
        <h1 style="font-family: 'Arial Black', Gadget, sans-serif; font-size: 32px; color: #000; margin: 0; text-shadow: 2px 2px white;">GEOCANABIS BR</h1>
        <p style="font-family: Arial; font-size: 14px; margin: 0;">Monitoramento de Erradicação e Apreensão</p>
    </div>

    <div style="position: fixed; bottom: 80px; left: 20px; z-index: 9999; background: white; padding: 10px; border: 2px solid black; font-family: sans-serif; font-size: 12px;">
        <b>LEGENDA</b><br>
        <img src="{icon_leaf}" width="15"> Cannabis (Cultivo)<br>
        <img src="{icon_pistol}" width="15"> Arma de Fogo (Apreensão)<br>
        <img src="{icon_brick}" width="15"> Maconha Prensada<br>
        <hr>
        <img src="{brasao_rep}" width="15"> Força de Segurança
    </div>

    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; font-family: Arial; font-size: 10px; color: #333;">
        <b>Análise/Geoprocessamento:</b> Alessandro (PMMG/UFJF)<br>
        <b>Coordenação:</b> Prof. Dr. Paulo Fraga | 2026
    </div>
"""
mapa.get_root().html.add_child(folium.Element(layout_html))

mapa.save('GEOCANABIS_BR_OPERACIONAL.html')
print("\n✅ MAPA OPERACIONAL GERADO: 'GEOCANABIS_BR_OPERACIONAL.html'")