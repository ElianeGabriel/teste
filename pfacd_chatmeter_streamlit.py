# =============================================================================
# Projeto Final Aplicado a Ciência de Dados
# Grupo: ChatMeter
#        André Silvestre | Eliane Gabriel | Margarida Pereira | Maria João Lourenço | Umeima Mahomed
# =============================================================================
# streamlit run pfacd_chatmeter_streamlit.py

# Import necessary libraries
import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title, hide_pages

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# ---- Configuração Inicial ----
st.set_page_config(page_title='ChatMeter',
                   page_icon='https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Vodafone_icon.svg/800px-Vodafone_icon.svg.png',
                   layout='wide',
                   initial_sidebar_state='expanded',
                   menu_items={
                       'Report a bug': 'mailto:afgse1@iscte-iul.pt',
                       'About': "# Esta app serve para a análise das operadoras! Viva a WIFI que presta!"
                   })

# ---- Carregar o estilo CSS ----
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.logo(image='static/640px-HD_transparent_picture.png', icon_image='static/ChatMeter_Logo_Bullet.png')


# -----------------------------
# Por a imagem do banner a prencer a largura da página
st.markdown("""
    <style>
        .h1, .h2, .h3, .h4, .h5, .h6, h1, h2, h3, h4, h5, h6 {
            font-weight: bold !important;
        }
        
        .banner {
            width: 117%;
            display: block;
            margin-left: -100px;
            margin-top: -60px;
        }
        .banner img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        @media (max-width: 768px) {
            .banner {
                width: 110%;
                display: block;
                margin-left: -20px;
                margin-top: -60px;
            }
            
            .banner img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
    </style>

    <!-- Adicionar a imagem do banner src='./app/static/Banner_PFACD.png' -->
    <div class="banner">
        <img src='./app/static/Banner_PFACD.png' alt="Banner Image">
    </div>
    """,
            unsafe_allow_html=True)

# -----------------------------

# =============================================================================
# --------------------------- Barra Lateral ---------------------------
# Fonte: https://dezoomcamp.streamlit.app/
add_page_title(layout="wide")

show_pages(
    [
        Page("pfacd_chatmeter_streamlit.py", "Home", ""),

        # Páginas - Análise Por Operadora
        Section("Análise Por Operadora", "🖇️"),
        Page("pfacd_chatmeter_vodafone.py", "Vodafone", "🔴", in_section=True),
        Page("pfacd_chatmeter_meo.py", "MEO", "🔵", in_section=True),
        Page("pfacd_chatmeter_nos.py", "NOS", "⚫", in_section=True),

        # Páginas - Análises de Sentimento, Tópicos e Mapa Interativo
        Section("Análises", "🩺"),
        Page("pfacd_chatmeter_texto_analise.py", "Word Analysis", "🔎", in_section=True),
        Page("pfacd_chatmeter_sentiment_analise.py", "Sentiment Analysis | Resultados", "🫀", in_section=True),
        Page("pfacd_chatmeter_topics_analise.py", "Topic Analysis | Resultados", "👁️", in_section=True),
        Page("pfacd_chatmeter_competitive_analise.py", "Competitive Analysis", "🥊", in_section=True),
        Page("pfacd_chatmeter_map.py", "Geo Analysis", "🗺️", in_section=True),

        # Páginas - DEMO
        Page("pfacd_chatmeter_models.py", "DEMO | Modelos", "💡", in_section=False),
        
        Page("pfacd_about.py", "About Us", icon="👥", in_section=False)
    ]
)

hide_pages(["Thank you"])

# =============================================================================
# Resumo do Trabalho
st.markdown("""
    <style>
        @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css");
            
        .team h1,
        .team h2,
        .team h3,
        .team h4,
        .team h5,
        .team h6 {
            color: #3d392d;
            font-weight: bold;
        }
    
        .team .font-weight-medium {
            font-weight: 700;
        }
    
        .team .bg-light {
            background-color: #f4f8fa !important;
        }
    
        .team .subtitle-title {
            color: rgb(255, 20, 30);
            line-height: 24px;
            font-size: 20px;
            font-weight: 700;
            margin-top: -10px;
        }
    
        .team .subtitle-names {
            color: rgb(255, 20, 30);
            line-height: 24px;
            font-size: 14px;
            font-weight: 600;
        }
    
        .team ul {
            margin-top: 30px;
        }
    
        .team h5 {
            line-height: 22px;
            font-size: 18px;
        }
    
        .team ul li a {
            color: #8d97ad;
            padding-right: 15px;
            -webkit-transition: 0.1s ease-in;
            -o-transition: 0.1s ease-in;
            transition: 0.1s ease-in;
        }
    
        .team ul li a:hover {
            -webkit-transform: translate3d(0px, -5px, 0px);
            transform: translate3d(0px, -5px, 0px);
            color: #ff141e;
        }
    
        .team .title {
            margin: 30px 0 0 0;
        }
    
        .team .subtitle {
            margin: 0 0 20px 0;
            font-size: 13px;
        }
        
        .st-emotion-cache-1629p8f a {
            display: none;
            pointer-events: none;
        }
        
        .st-emotion-cache-1629p8f h1, .st-emotion-cache-1629p8f h2, .st-emotion-cache-1629p8f h3, .st-emotion-cache-1629p8f h4,
        .st-emotion-cache-1629p8f h5, .st-emotion-cache-1629p8f h6, .st-emotion-cache-1629p8f span {
            font-weight: bolder;
        }
        
        .vodafone ul {
            list-style-type: none;
            line-height: 1.5;
            padding-left: 0.3em;
        }

        .vodafone ul li {
            position: relative;
        }

        .vodafone ul li::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 18px; 
            height: 18px;
            background-image: url('./app/static/ChatMeter_Logo_Bullet.png');
            background-size: cover;
            background-repeat: no-repeat;
            margin-left: -0.9em;
            margin-top: -0.6em;
        }
    </style>
    
    <!-- Bibliotecas de Icons-->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <script type="module" src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.esm.js"></script>
    <script nomodule src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js"></script>
    
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/css/bootstrap.min.css"
          integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    
    <script src="https://code.jquery.com/jquery-3.4.1.slim.min.js"
            integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n"
            crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js"
            integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo"
            crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/js/bootstrap.min.js"
            integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6"
            crossorigin="anonymous"></script>
    
    
    <div class="py-5 team">
        <div class="container" style="margin-top: -80px">
            <div class="row justify-content-center" style="margin-bottom: -40px">
                <div class="col-md-7 text-center">
                    <h1 class="mb-0 title-contactos">Solução desenvolvida</h1>
                    <p class="subtitle-title">Motivação</p>
                </div>
                <br><br>
                <p style="text-align: justify; max-width: 800px; margin: auto;">
                    No dinâmico mercado das Telecomunicações, a análise de dados provenientes de redes sociais revela-se 
                    um recurso inestimável para as equipas de Marketing e Comunicação.
                    <br><br>
                    Este projeto, destinado a estudantes de Data Science, visa explorar tal potencial. 
                    A relevância destes dados reside na sua capacidade de elucidar as necessidades, 
                    preferências, comportamentos e níveis de satisfação dos utilizadores de uma operadora 
                    de telecomunicações, que opera num ambiente bastante competitivo. 
                    <br><br>
                    Adicionalmente, possibilita a identificação de novas oportunidades, tendências e 
                    desafios inerentes ao setor.
                </p>
                <br><br><br>
            </div>
        </div>
    </div>     
    <div class="py-5 team">
            <div class="container">
                <div class="row justify-content-center" style="margin-bottom: -40px">
                    <div class="col-md-7 text-center">
                        <p class="subtitle-title">Casos de Uso</p>
                    </div>
                    <br><br>
                    <div class="vodafone">
                        <ul style="text-align: justify; max-width: 800px; margin: auto;" class="vodafone">
                            <li>
                                <p> Melhoria da experiência do cliente através de ofertas personalizadas, conteúdos e campanhas direcionadas a comunidades específicas. </p>
                            </li>
                            <li>
                                <p> Desenvolvimento de estratégias de segmentação mais eficazes, visando otimizar o ciclo de vida do cliente, especialmente nas fases de angariação e retenção. </p>
                            </li>
                            <li>
                                <p> Identificação de novos modelos de negócio e potenciais parcerias com entidades das redes sociais, visando promover produtos e serviços inovadores e competitivos. </p>
                            </li>
                            <li>
                                <p> Monitorização do mercado e dos concorrentes, analisando sentimentos, opiniões, avaliações e feedback dos clientes, assim como as atividades, estratégias e desempenhos dos competidores. </p>
                            </li>
                            <li>
                                <p> Antecipação de tendências emergentes, tecnologias e oportunidades no setor das telecomunicações, como 5G, IoT e cloud. </p>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="py-5 team">
        <div class="container text-center">
            <div class="row justify-content-center" style="margin-bottom: -40px">
                <div class="col-md-7 text-center">
                    <p class="subtitle-title">Objetivo</p>
                </div>
                <br><br>
                <p style="text-align: justify; max-width: 800px; margin: auto;">
                    O ChatMeter é uma aplicação que tem como objetivo o <b>desenvolvimento de um Termómetro de Sentimentos e 
                    Tópicos entre Operadoras de Telecomunicações do Mercado Português.</b>
                    <br><br>
                    Ou seja, analisar dados provenientes das redes sociais, de forma a identificar necessidades, preferências, 
                    comportamentos e níveis de satisfação dos utilizadores, visando encontrar novas oportunidades, 
                    tendências e desafios inerentes ao setor.
                    <br><br>
                    A aplicação permite assim analisar a satisfação dos clientes das operadoras Vodafone, MEO e NOS, 
                    através de análises de sentimentos, tópicos e localização geográfica.
                </p>
            </div>    
        </div>
    </div>
    <div class="py-5 team">
        <div class="container">
            <div class="row justify-content-center" style="margin-bottom: -40px">
                <div class="col-md-7 text-center">
                    <p class="subtitle-title">Arquitetura da Solução</p>
                </div>
                <br><br>
                <div class="col-md-10 text-center">
                    <img src="./app/static/Solucao_ChatMeter.png" class="img-fluid" alt="Solução ChatMeter">
                    <br><br>
                    <p class="text-center" style="color: #BBBBBB; font-style: italic;">
                        <b>Figura:</b> Arquitetura da Solução desenvolvida no ChatMeter.
                    </p>
                    <br><br><br>
                    <p style="text-align: justify; max-width: 800px; margin: auto;">
                        A solução desenvolvida no ChatMeter é composta por <b>3 Módulos Principais</b>:
                        <br><br>
                        <b>1. Recolha, Pré-Processamento e Análise Exploratória de Dados:</b> Neste módulo faz-se <i>scraping</i> dos dados da rede social Facebook, 
                                nomeadamente os Posts, Comentários e Utilizadores
                                das principais operadoras de telecomunicações a nível nacional. 
                                Os dados recolhidos são guardados numa base de dados. 
                                Posteriormente, faz-se o pré-processamento dos dados e a Análise Exploratória dos mesmos.
                        <br><br>
                        <b>2. Análise de Sentimentos e Tópicos:</b> 
                            Começa-se por realizar o pré-processamento do texto, através da utilização de algumas técnicas de Text Mining. 
                            A Análise de Sentimentos é feita através da utilização de modelos de Transformers, que classificam os posts/comentários em positivos, negativos ou neutros.
                            Por sua vez, a Análise de Tópicos recorre ao mesmo tipo de modelos, que classifica o texto recolhido em diferentes tópicos pré-definidos.
                        <br><br>
                        <b>3. Dashboard:</b> 
                        Este módulo é responsável pela visualização interativa dos dados, podendo-se recolher diversos <i>insights</i>, 
                        facilitando a visualização das conclusões obtidas, ajudando na tomada de decisão.
                        A aplicação presente, serve o propósito da conclusão desta última etapa.
                    </p>                    
                    <br><br><br><br>
                    <p class="subtitle-title">Outras Aplicações</p>
                    <p style="text-align: justify; max-width: 800px; margin: auto;">
                        A forma como esta solução está arquitetada, pode ser reproduzida noutras áreas de negócio, 
                        acrescentando valor às organizações e segmentos de negócio.
                        <br><br>
                        A aplicação pode ser ainda adaptada para analisar a satisfação dos clientes em diferentes 
                        plataformas das Redes Sociais, como o Twitter, Instagram, LinkedIn, entre outras.
                    </p>
                </div>
            </div>
        </div>
    </div>
    <footer class="footer" style="visibility: visible; margin-top: 40px;">
        <div class="container">
            <div class="row">
                <div class="col-lg-12 text-center">
                    <p class="company-name" style="color: #d3d3d3;">ChatMeter © 2024</p> <!-- Adicione a regra de cor aqui -->
                </div>
            </div>
        </div>
    </footer>
    """, unsafe_allow_html=True)

# =============================================================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
