# meus-projetos-python
guardo meus scripts aqui
# GeoCannabis Brasil: Monitoramento Geospacial de Erradicação

Este repositório contém a metodologia e o código-fonte para a visualização cartográfica interativa do projeto **GeoCannabis Brasil**. O projeto utiliza geoprocessamento avançado para analisar a dinâmica das apreensões de cannabis em território nacional.

## 👨‍🔬 Autoria e Coordenação
* **Pesquisador:** Alessandro Carneiro, Mestre em Ciências Sociais (UFJF)
* **Coordenação de Dados:** Prof. Dr. Paulo Fraga (UFJF)

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.x
* **Pandas:** Manipulação e higienização de grandes volumes de dados.
* **Folium:** Renderização de mapas baseados em Leaflet.js.
* **Regex (re):** Extração de padrões, limpeza de strings e normalização de variáveis categóricas (como instituições e tipos de apreensão).

## 📊 Metodologia e Processamento
A robustez dos dados é garantida por um pipeline de limpeza que utiliza **Regex** para:
1. **Padronização Institucional**: Identificar e categorizar forças de segurança (PM, PC, PF, PRF) a partir de descrições textuais variadas.
2. **Filtragem de Quantitativos**: Extração de números de apreensões em textos não estruturados.
3. **Validação de Coordenadas**: Verificação de integridade de padrões geográficos.

## ⚖️ Licença
Este projeto segue os princípios da Ciência Aberta. O código é livre para fins acadêmicos, desde que citada a fonte.
