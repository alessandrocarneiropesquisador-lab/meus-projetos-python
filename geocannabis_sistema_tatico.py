import pandas as pd
import folium
from folium.plugins import MarkerCluster, FloatImage

print("🦅 EXECUTANDO PROTOCOLO TÁTICO FINAL: IDENTIDADE VISUAL E CRÉDITOS...")

# 1. Carga de Dados
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv').dropna(subset=['codigo_ibge'])
except:
    print("❌ Erro: Base de dados não encontrada.")
    exit()

url_coords = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coords = pd.read_csv(url_coords)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coords['codigo_ibge'] = coords['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coords[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 2. Mapa Base
mapa = folium.Map(
    location=[-14.2350, -51.9253], zoom_start=4, 
    tiles='cartodb positron', control_scale=True,
    min_zoom=4, max_bounds=True
)

# 3. Definição de Ícones Táticos (Links Estáveis)
icon_leaf = "https://img.icons8.com/color/48/marijuana-leaf.png"
icon_pistol = "https://img.icons8.com/ios-filled/50/000000/pistol.png" # Ícone de pistola preta tática
icon_brick = "https://img.icons8.com/color/48/brick.png"
icon_link = "https://img.icons8.com/ios-glyphs/30/000000/link--v1.png"
br_flag = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Brazil.svg/200px-Flag_of_Brazil.svg.png"

# Função de Seleção de Insígnia com base na força e estado
def get_badge(row):
    forca = str(row['Instituição que efetuou a apreensao']).upper()
    uf = str(row['estado_ibge']).upper()
    
    if 'FEDERAL' in forca or 'PF' in forca:
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Bras%C3%A3o_da_Pol%C3%ADcia_Federal.svg/100px-Bras%C3%A3o_da_Pol%C3%ADcia_Federal.svg.png"
    if 'PRF' in forca:
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Bras%C3%A3o_da_Pol%C3%ADcia_Rodovi%C3%A1ria_Federal.svg/100px-Bras%C3%A3o_da_Pol%C3%ADcia_Rodovi%C3%A1ria_Federal.svg.png"
    if 'EXÉRCITO' in forca or 'FORÇAS ARMADAS' in forca or 'AERONÁUTICA' in forca or 'MARINHA' in forca:
        return br_flag
    
    # Lógica para PC e PM (Exemplo para MG e PE, expansível para outros estados conforme a tabela)
    if 'PC' in forca or 'CIVIL' in forca:
        if 'MINAS GERAIS' in uf or 'MG' in uf: return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Bras%C3%A3o_da_PCMG.png/100px-Bras%C3%A3o_da_PCMG.png"
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Coat_of_arms_of_Brazil.svg/100px-Coat_of_arms_of_Brazil.svg.png" # Fallback
    
    if 'PM' in forca or 'MILITAR' in forca:
        if 'MINAS GERAIS' in uf or 'MG' in uf: return "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Bras%C3%A3o_da_PMMG.png/100px-Bras%C3%A3o_da_PMMG.png"
        if 'PERNAMBUCO' in uf or 'PE' in uf: return "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Bras%C3%A3o_da_PMPE.png/100px-Bras%C3%A3o_da_PMPE.png"
        
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Coat_of_arms_of_Brazil.svg/100px-Coat_of_arms_of_Brazil.svg.png"

# 4. Seta Norte no Canto Superior Direito
url_norte = "https://www.svgrepo.com/show/447990/compass-north.svg"
FloatImage(url_norte, top=2, right=2).add_to(mapa)

marker_cluster = MarkerCluster(showCoverageOnHover=False).add_to(mapa)

# 5. Marcadores e Cards
for _, row in df_mapa.iterrows():
    # Marcador Dinâmico: Pistola se houver arma, senão Folha
    tem_arma = pd.notna(row['armas apreendidas']) and str(row['armas apreendidas']).strip() not in ['0', 'X', '']
    icon_marker = icon_pistol if tem_arma else icon_leaf
    
    badge_url = get_badge(row)
    
    # Conteúdo do Card com Fonte Arial 12
    html_card = f"""
    <div style="width: 200px; font-family: Arial, sans-serif; font-size: 12px; text-align: center;">
        <img src="{badge_url}" width="35" style="margin-bottom: 5px;"><br>
        <b style="font-size: 14px; color: #1B5E20;">{row['municipio_ibge']} - {row['estado_ibge']}</b>
        <hr style="margin: 5px 0; border: 0.5px solid #eee;">
        <div style="text-align: left; margin-left: 10px;">
            <img src="{icon_leaf}" width="14"> <b>Pés:</b> {row['Quantidade de pés encontrados']}<br>
            <img src="{icon_brick}" width="14"> <b>Prensada:</b> {row['quantidade prensada (embalada)']}<br>
            <img src="{icon_pistol}" width="14"> <b>Armas:</b> {row['armas apreendidas']}
        </div>
        <hr style="margin: 5px 0; border: 0.2px solid #eee;">
        <a href="{row['Link de acesso']}" target="_blank" style="text-decoration: none; color: #2980B9;">
            <img src="{icon_link}" width="12"> Matéria Completa
        </a>
    </div>
    """
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_marker, icon_size=(25, 25)),
        tooltip=folium.Tooltip(html_card)
    ).add_to(marker_cluster)

# 6. Interface: Título, Legenda (Canto Direito Inferior) e Créditos (Canto Esquerdo Inferior)
layout_css = f"""
    <style>
        .leaflet-control-scale {{ left: auto !important; right: 20px !important; bottom: 10px !important; }}
    </style>

    <div style="position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; text-align: center;">
        <h1 style="font-family: 'Arial Black', sans-serif; font-weight: bold; font-size: 38px; color: black; margin: 0; text-shadow: 2px 2px white;">GEOCANNABIS BR</h1>
    </div>

    <div style="position: fixed; bottom: 50px; right: 20px; z-index: 9999; background: white; padding: 10px; border: 2px solid black; font-family: sans-serif; font-size: 11px;">
        <b style="font-size: 12px;">LEGENDA</b><hr style="margin: 3px 0;">
        <img src="{icon_pistol}" width="14"> = Força (Poder de Fogo)<br>
        <img src="{icon_leaf}" width="14"> = Local e Quantidade<br>
        <img src="{icon_brick}" width="14"> = Prensada<br>
        <img src="{icon_link}" width="14"> = Matéria Completa
    </div>

    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; font-family: Arial; font-size: 11px; color: black; background: rgba(255,255,255,0.7); padding: 5px; border-radius: 3px;">
        <b>Produzido por:</b> Alessandro Carneiro<br>
        <b>Dados:</b> Dr. Paulo Fraga
    </div>
"""
mapa.get_root().html.add_child(folium.Element(layout_css))

mapa.save('GEOCANNABIS_BR_OPERACIONAL_FINAL.html')
print("\n✅ PRODUTO TÁTICO FINALIZADO: 'GEOCANNABIS_BR_OPERACIONAL_FINAL.html'")