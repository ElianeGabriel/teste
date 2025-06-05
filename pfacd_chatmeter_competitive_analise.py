import numpy as np
import streamlit as st
from st_pages import add_page_title
import pandas as pd
import pfacd_functions
import plotly.express as px
import plotly.graph_objects as go

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Configurações da Página
st.set_page_config(layout="wide")
add_page_title(layout="wide")
st.logo(image='static/640px-HD_transparent_picture.png', icon_image='static/ChatMeter_Logo_Bullet.png')
with open('style.css') as f:
    st.markdown(f'''<style>{f.read()}
                    /* Alterar a cor do slider | Fonte: https://discuss.streamlit.io/t/how-to-change-st-sidebar-slider-default-color/3900/2 */
                    div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{{
                        background-color: #CA0B4A;
                    }}

                    div.stSlider > div[data-baseweb="slider"] > div > div > div > div{{
                        color: #CA0B4A; 
                    }}

                    div.stSlider > div[data-baseweb = "slider"] > div > div {{
                        background: #CA0B4A;}}

                    div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {{
                        background: rgb(1 1 1 / 0%); }}

                    .stTabs [data-baseweb="tab"] {{
                        color: #CA0B4A;
                    }}

                    .stTabs [data-baseweb="tab-highlight"] {{
                        background-color: #CA0B4A;
                    }}
                    
                    button[kind="secondary"] {{
                        border: 1px solid #CA0B4A;
                    }}
                    
                    button[kind="secondary"]:hover {{
                        font-weight: bold;
                        color: #CA0B4A;
                        border: 2px solid #CA0B4A;
                    }}

            </style>''', unsafe_allow_html=True)
st.write("Esta página apresenta um conjunto de gráficos e tabelas que fornecem insights valiosos sobre os dados recolhidos, "
         "tornando esta análise <i><b>Competitive Inteligence</b></i>.", unsafe_allow_html=True)
st.divider()

# =============================================================================
# Definir Paleta de Cores para Operadoras
palette_operadoras = {
    'DIGI News': '#FFE807',  # Digi News
    'DIGI News ': '#FFE807',  # Digi News
    'MEO': '#007E8D',        # MEO
    'MEO ': '#007E8D',        # MEO
    'NOS': '#555555',        # NOS
    'NOS ': '#555555',        # NOS
    'Vodafone': '#E60001',    # Vodafone
    'Vodafone ': '#E60001'    # Vodafone
}

# Paleta de Cores para Género
colors_gender = {
    'Masculino': '#81BEF7',
    'Feminino': '#F5A9D0',
    'Indeterminado': '#BDBDBD'
}

# Paleta de Cores para Sentimentos - Gráficos
sentiment_colors = {'Positivo': '#64C548', 'Tendência Positiva': '#EBA722',
                    'Neutro': '#F47131',
                    'Tendência Negativa': '#F03F42', 'Negativo': '#CF213D'}

# Definição de Paletas de Cores para Tópicos - Cartões
palette_CompetitiveAnalysis = [
    [(141, 14, 64), '#8d0e40'],  # Escuro
    [(202, 11, 74), '#CA0B4A'],  # Médio
    [(255, 203, 213), '#ffcbd5'],  # Claro
]

# Pallete de Cores para Tópicos - Gráficos
topic_color_mapping = {
    # Tópicos associados às Operadoras
    "Pacotes de Serviços": "#FF5733",
    "Cobertura": "#FFC300",
    "Velocidade": "#C70039",
    "Preços": "#FF3131",
    "Qualidade": "#6704D9",
    "Atendimento ao Cliente": "#FF5733",
    "Concorrência": "#FF0000",
    "5G": "#FF4A00",
    "Satisfação": "#FFD500",
    "Rede": "#005AFF",
    "Fidelização": "#3392FF",
    "Promoções": "#53F601",
    "Segurança": "#2EB025",
    "Plataformas Streaming": "#2721E1",
    "Festivais": "#FD830A",
    "Comunicação": "#2213b1",
    # Tópicos de Eventos Anuais
    "Páscoa": "#FFA600",
    "Natal": "#FF0000",
    "Ano Novo": "#03FFF5",
    "Santos Populares": "#FF3131",
    "Passatempo": "#3392FF",
    "Black Friday": "#000000",
    "Regresso às Aulas": "#7300FF",

    # Tópicos Desportivos
    "Futebol": "#2EB025",
    "Cristiano Ronaldo": "#706C6D",
    "Surf": "#075DFF",
    "Outros desportos": "#53F601",

    # Tópicos Gerais
    "Problemas da Sociedade": "#FF5733",
    "Cinema": "#8A8788",
    "Filme/Série": "#C70039",
    "Economia": "#900C3F",
    "Saúde": "#00FFCF",
    "Videojogo": "#6704D9",
    "Política": "#461F02",
    "Emprego": "#592F03",
    "Tecnologia": "#0D05EC",
    "Inteligência Artificial": "#7300FF",
    "Ambiente": "#53F601",
    "Educação": "#075DFF",
    "Cultura": "#FFD500",
    "Ciência": "#53F601",
    "Arte": "#FF4A00",
    "Religião": "#A56CD3",
    "Negócios": "#52C5B8",
    "Sustentabilidade": "#9CF53E",
    "Moda": "#DC06EC",
    "Alimentação": "#FFA600",
    "Viagens": "#0B51AD",
    "Família": "#EC05F5",
    "Guerra": "#707070",
    "Pandemia": "#3BD293",
    "Redes Sociais": "#005AFF",
    "Sociedade": "#F66527"
}

# =============================================================================

# Import da Base de Dados
Facebook_PCU_Analysis, Facebook_Posts_Analysis = pfacd_functions.load_data()
Facebook_Posts_Analysis.loc[Facebook_Posts_Analysis['page'].str.contains('DIGI'), 'page'] = 'DIGI News'
Facebook_PCU_Analysis.loc[Facebook_PCU_Analysis['page'].str.contains('DIGI'), 'page'] = 'DIGI News'

# =============================================================================

# Filtros
# Definições do botão 'Filtrar' - https://docs.streamlit.io/develop/concepts/design/buttons
if 'clicked' not in st.session_state:
    st.session_state.clicked = False


def click_button():
    st.session_state.clicked = True


if 'filtros_button' in st.session_state and st.session_state.filtros_button is True:
    st.session_state.running = True
else:
    st.session_state.running = False


# Aplicar os filtros
@st.cache_data
def apply_filters(filters=None):
    if filters is None:
        return Facebook_PCU_Analysis

    filtered_Post_df = Facebook_Posts_Analysis.copy()
    filtered_PCU_df = Facebook_PCU_Analysis.copy()

    # # Converter datas para datetime64[ns]
    # filters['start_date'] = pd.to_datetime(filters['start_date'])
    # filters['end_date'] = pd.to_datetime(filters['end_date'])

    # Filtros para Página
    if filters['page'] and len(filters['page']) > 0:
        filtered_Post_df = filtered_Post_df[filtered_Post_df['page'].isin(filters['page'])]
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['page'].isin(filters['page'])]

    # Filtros para Data
    if filters['start_date'] and filters['end_date']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_date'].dt.date >= filters['start_date']) & (
                filtered_Post_df['post_date'].dt.date <= filters['end_date'])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_date'].dt.date >= filters['start_date']) & (
                filtered_PCU_df['post_date'].dt.date <= filters['end_date'])]

    # Filtros para Sentimento dos Posts
    if filters['sentiment-post'] and len(filters['sentiment-post']) > 0:
        filtered_Post_df = filtered_Post_df[filtered_Post_df['post_sentiment_label'].isin(filters['sentiment-post'])]
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['post_sentiment_label'].isin(filters['sentiment-post'])]

    # Filtros para Sentimento dos Comentários
    if filters['sentiment-comment'] and len(filters['sentiment-comment']) > 0:
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['comment_sentiment_label'].isin(filters['sentiment-comment'])]

    # Filtros para Tópico dos Posts
    if filters['topic-post'] and len(filters['topic-post']) > 0:
        filtered_Post_df = filtered_Post_df[filtered_Post_df['mDeBERTa_post_topic_label_1'].isin(filters['topic-post'])]
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['mDeBERTa_post_topic_label_1'].isin(filters['topic-post'])]

    # Filtros para Tópico dos Comentários
    if filters['topic-comment'] and len(filters['topic-comment']) > 0:
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['mDeBERTa_comment_topic_label_1'].isin(filters['topic-comment'])]

    if filters['n_reacts']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_reactions'] >= filters['n_reacts'][0]) & (
                filtered_Post_df['post_reactions'] <= filters['n_reacts'][1])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_reactions'] >= filters['n_reacts'][0]) & (
                filtered_PCU_df['post_reactions'] <= filters['n_reacts'][1])]

    # Filtros para Nº de Comentários
    if filters['n_comments']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_comments'] >= filters['n_comments'][0]) & (
                filtered_Post_df['post_comments'] <= filters['n_comments'][1])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_comments'] >= filters['n_comments'][0]) & (
                filtered_PCU_df['post_comments'] <= filters['n_comments'][1])]

    # Filtros para Nº de Partilhas
    if filters['n_shares']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_shares'] >= filters['n_shares'][0]) & (
                filtered_Post_df['post_shares'] <= filters['n_shares'][1])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_shares'] >= filters['n_shares'][0]) & (
                filtered_PCU_df['post_shares'] <= filters['n_shares'][1])]

    return filtered_PCU_df, filtered_Post_df


# Filtros | Esquerda
st.markdown("#### Filtros")

# 3 Colunas
col1_F, col2_F, col3_F, col4_F = st.columns(4)

# Filtro por Data | Intervalo de Datas
start_date, end_date = pfacd_functions.init_page_dates_pickers(Facebook_PCU_Analysis['post_date'], col1_F, col1_F)

# Filtro por Tópico
with col2_F:
    lista_topicos = Facebook_Posts_Analysis['mDeBERTa_post_topic_label_1'].dropna().unique()
    topic_post_filter = st.multiselect("Tópico dos Posts",
                                       Facebook_Posts_Analysis['mDeBERTa_post_topic_label_1'].dropna().unique(),
                                       placeholder="Escolha o Tópico dos Posts")
    topic_comment_filter = st.multiselect("Tópico dos Comentários",
                                          Facebook_PCU_Analysis['mDeBERTa_comment_topic_label_1'].dropna().unique(),
                                          placeholder="Escolha o Tópico dos Comentários")

# Filtro por Sentimento
with col3_F:
    lista_sentimentos = ['Positivo', 'Tendência Positiva', 'Neutro', 'Negativo', 'Tendência Negativa']
    sentiment_post_filter = st.multiselect("Sentimento dos Posts",
                                           Facebook_PCU_Analysis['post_sentiment_label'].dropna().unique(),
                                           placeholder="Escolha o Sentimento dos Posts")
    sentiment_comment_filter = st.multiselect("Sentimento dos Comentários",
                                              Facebook_PCU_Analysis['comment_sentiment_label'].dropna().unique(),
                                              placeholder="Escolha o Sentimento dos Comentários")

# Filtro por Página
with col4_F:
    page_filter = st.multiselect("Página(s)", Facebook_PCU_Analysis['page'].unique(), placeholder="Escolha a Página")

# 3 Colunas
col1_FF, col2_FF, col3_FF = st.columns(3)

# Filtrar po Nº de Reações
n_reacts = col1_FF.slider("Nº de Reações",
                          min_value=Facebook_PCU_Analysis['post_reactions'].min(),
                          max_value=Facebook_PCU_Analysis['post_reactions'].max(),
                          value=(Facebook_PCU_Analysis['post_reactions'].min(),
                                 Facebook_PCU_Analysis['post_reactions'].max()), format="%d")

# Filtrar por Nº de Comentários
n_comments = col2_FF.slider("Nº de Comentários",
                            min_value=Facebook_PCU_Analysis['post_comments'].min(),
                            max_value=Facebook_PCU_Analysis['post_comments'].max(),
                            value=(Facebook_PCU_Analysis['post_comments'].min(),
                                   Facebook_PCU_Analysis['post_comments'].max()), format="%d")

# Nº de Partilhas
n_shares = col3_FF.slider("Nº de Partilhas",
                          min_value=Facebook_PCU_Analysis['post_shares'].min(),
                          max_value=Facebook_PCU_Analysis['post_shares'].max(),
                          value=(Facebook_PCU_Analysis['post_shares'].min(),
                                 Facebook_PCU_Analysis['post_shares'].max()), format="%d")

if st.button("Filtrar", on_click=click_button, key='filtros_button'):
    Facebook_PCU_Analysis, Facebook_Posts_Analysis = apply_filters({
        'start_date': start_date,
        'end_date': end_date,
        'page': page_filter,
        'sentiment-post': sentiment_post_filter,
        'sentiment-comment': sentiment_comment_filter,
        'topic-post': topic_post_filter,
        'topic-comment': topic_comment_filter,
        'n_reacts': n_reacts,
        'n_comments': n_comments,
        'n_shares': n_shares
    })

st.divider()

# ================================================================================================
# Cartões com Nº de Posts, Comentários e Utilizadores Únicos
col1, col2, col3 = st.columns(3)

# Cartão 1 | Total de Posts
pfacd_functions.create_card(col1, "fas fa-newspaper", palette_CompetitiveAnalysis[0][0], (255, 255, 255),
                            "Total de Posts", Facebook_Posts_Analysis['post_id'].nunique())

# Cartão 2 | Total de Comentários
pfacd_functions.create_card(col2, "fas fa-comments", palette_CompetitiveAnalysis[1][0], (255, 255, 255),
                            "Total de Comentários", Facebook_PCU_Analysis['comment_id'].nunique())

# Cartão 3 | Total de Utilizadores Únicos
pfacd_functions.create_card(col3, "fas fa-users", palette_CompetitiveAnalysis[2][0], (255, 255, 255),
                            "Total de Utilizadores Únicos", Facebook_PCU_Analysis['user_link'].nunique())

st.markdown("<br><br>", unsafe_allow_html=True)

try:
    # ================================================================================================
    col1_P, col2_P = st.columns(2)

    # Gráfico Sunburst com Operadoras, Sentimentos e Género
    # Contar o número de ocorrências de cada combinação de operadora, sentimento e género
    df_sunburst = Facebook_PCU_Analysis.groupby(['page', 'comment_sentiment_label', 'user_predicted_genre']).size().reset_index(name='count')

    # Combinar todas as paletas de cores
    combined_colors = {**palette_operadoras, **sentiment_colors, **colors_gender}

    # Criar o gráfico Sunburst
    fig_sankey_sentimentos = px.sunburst(df_sunburst,
                                         path=['page', 'comment_sentiment_label', 'user_predicted_genre'],
                                         values='count',
                                         color='page',
                                         color_discrete_map=combined_colors,
                                         title='Sunburst - Operadoras, Sentimentos e Género',
                                         height=700)

    fig_sankey_sentimentos.update_traces(textinfo='label+percent parent',
                                         hoverinfo='label+percent parent',
                                         hovertemplate='''<b>%{id}</b><br>%{value} Comentários<br><b>%{parent}</b><br>%{percentRoot:.1%} do total<br>''',
                                         branchvalues='total')

    col1_P.plotly_chart(fig_sankey_sentimentos, use_container_width=True)

    # ================================================================================================

    # Tabela de Frequências das variáveis relativas à referência do nome das operadoras nos comentários do Facebook
    operators = ['Vodafone', 'MEO', 'NOS', 'DIGI']

    # Função para calcular a %
    def calculate_percentage(value, total):
        return round((value / total) * 100, 1) if total != 0 else 0


    if all(item in Facebook_PCU_Analysis.columns for item in ['comment_text_Vodafone', 'comment_text_MEO', 'comment_text_NOS', 'comment_text_DIGI']):
        df_comment_text_operators = pd.DataFrame({
            '0 | Não (n)': Facebook_PCU_Analysis[['comment_text_Vodafone', 'comment_text_MEO', 'comment_text_NOS', 'comment_text_DIGI']].apply(lambda x: x.value_counts().get(0, 0)),
            '0 | Não (%)': Facebook_PCU_Analysis[['comment_text_Vodafone', 'comment_text_MEO', 'comment_text_NOS', 'comment_text_DIGI']].apply(lambda x: calculate_percentage(x.value_counts().get(0, 0), len(x))),
            '1 | Sim (n)': Facebook_PCU_Analysis[['comment_text_Vodafone', 'comment_text_MEO', 'comment_text_NOS', 'comment_text_DIGI']].apply(lambda x: x.value_counts().get(1, 0)),
            '1 | Sim (%)': Facebook_PCU_Analysis[['comment_text_Vodafone', 'comment_text_MEO', 'comment_text_NOS', 'comment_text_DIGI']].apply(lambda x: calculate_percentage(x.value_counts().get(1, 0), len(x)))
        })

        df_comment_text_operators.index = [operators]

        with col2_P:
            st.write("""<h3 style="margin:0 auto; text-align:center;"> Tabela de Frequências das Variáveis Relativas à Referência do Nome das Operadoras nos Comentários</h3>""", unsafe_allow_html=True)
            st.write("A tabela apresenta o número de comentários que referem a cada operadora e à sua respetiva percentagem em relação ao total de comentários.")
            st.dataframe(df_comment_text_operators, use_container_width=True)

    # ------------------------------------------------------------------------------------------
    # Agrupar os dados pela variável 'page' e obter a contagem de comentários que referem cada operadora em cada página
    page_comments_by_operator = Facebook_PCU_Analysis.groupby('page')[['comment_text_Vodafone', 'comment_text_MEO', 'comment_text_NOS', 'comment_text_DIGI']].sum().reset_index()
    page_comments_by_operator = page_comments_by_operator.loc[page_comments_by_operator['page'].isin(['Vodafone', 'MEO', 'NOS', 'DIGI News'])]

    # Calcular a soma total de comentários para cada página
    total_comments = Facebook_PCU_Analysis[Facebook_PCU_Analysis['page'].isin(['Vodafone', 'MEO', 'NOS', 'DIGI News'])].groupby('page').size()

    # Preencher a variável 'total_comments' com os valores correspondentes
    page_comments_by_operator['total_comments'] = page_comments_by_operator['page'].map(total_comments)

    # Calcular as porcentagens de referências a cada operadora em relação ao total de comentários em cada página
    for operator in ['Vodafone', 'MEO', 'NOS', 'DIGI']:
        page_comments_by_operator['percentage_' + operator] = round((page_comments_by_operator['comment_text_' + operator] / page_comments_by_operator['total_comments']) * 100, 1)

    # Page Comments Matrix (n)
    page_comments_matrix_n = page_comments_by_operator.set_index('page')[['comment_text_Vodafone', 'comment_text_MEO', 'comment_text_NOS', 'comment_text_DIGI']]

    # Adicionar linha final com o total do número de comentários em cada coluna
    page_comments_matrix_n.loc['Total'] = page_comments_matrix_n.sum()

    page_comments_matrix_n.columns = ['Vodafone', 'MEO', 'NOS', 'DIGI News']
    page_comments_matrix_n.columns.name = 'Texto c/'
    page_comments_matrix_n = page_comments_matrix_n.reindex(['Vodafone', 'MEO', 'NOS', 'DIGI News', 'Total'])
    page_comments_matrix_n.index.name = 'Página'

    # Selecionar apenas as colunas relevantes | Page Comments Matrix (%)
    page_comments_matrix = page_comments_by_operator.set_index('page')[['percentage_Vodafone', 'percentage_MEO', 'percentage_NOS', 'percentage_DIGI']]
    page_comments_matrix.columns = ['Vodafone', 'MEO', 'NOS', 'DIGI News']
    page_comments_matrix.columns.name = 'Texto c/'
    page_comments_matrix = page_comments_matrix.reindex(['Vodafone', 'MEO', 'NOS', 'DIGI News'])
    page_comments_matrix.index.name = 'Página'

    with col2_P:
        st.write("""<h3 style="margin:0 auto; text-align:center;">Matriz de % Horizontais de Referências a Operadoras em Comentários </h3>""", unsafe_allow_html=True)
        st.write("""<p style="margin-left: 10px;">A matriz apresenta a percentagem de comentários que 
        referem cada operadora em relação ao total de comentários de cada página.</p>""", unsafe_allow_html=True)
        # 2 colunas
        col1_P2, col2_P2 = st.columns(2)

        with col1_P2:
            st.write("""<h4 style="margin:0 auto; text-align:center;">n</h4>""", unsafe_allow_html=True)
            st.dataframe(page_comments_matrix_n)

        with col2_P2:
            st.write("""<h4 style="margin:0 auto; text-align:center;"> % </h4>""", unsafe_allow_html=True)
            st.dataframe(page_comments_matrix)


    # ================================================================================================

    df = Facebook_PCU_Analysis.copy()

    # Definir os labels para os nodes
    operadoras = df['page'].dropna().unique().tolist()
    sentimentos = df['comment_sentiment_label'].dropna().unique().tolist()
    labels = operadoras + sentimentos

    # Criar um dicionário para mapear labels a índices
    label_indices = {label: i for i, label in enumerate(labels)}

    # Preparar as listas de source, target e value para o gráfico Sankey
    source = []
    target = []
    value = []
    colors = []
    colors.extend([palette_operadoras[op] for op in operadoras])
    colors.extend([sentiment_colors[op] for op in sentimentos])

    # Preencher os dados para as listas
    for operadora in operadoras:
        for sentimento in sentimentos:
            count = df[(df['page'] == operadora) & (df['comment_sentiment_label'] == sentimento)].shape[0]
            if count > 0:
                source.append(label_indices[operadora])
                target.append(label_indices[sentimento])
                value.append(count)

    # Criar o gráfico Sankey
    fig_sankey = go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(
            label=labels,
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            color=colors,
            hovertemplate='<b>%{label}</b> <br><b>Nº de Comentários</b>: %{value}'
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color='rgba(0, 0, 0, 0.1)',
            hovertemplate='<b> Nº de Comentários </b>%{value} <br> <b>%{source.label}</b> -> %{target.label}'
        )),
        layout=go.Layout(
            title="Gráfico Sankey - Operadoras e Sentimentos",
            height=800,
        ),
    )

    fig_sankey.update_layout(title_text="Diagrama Sankey: Sentimentos vs Operadoras", font_size=10)

    col1_P1, col2_P1 = st.columns([0.4, 0.6])

    col1_P1.plotly_chart(fig_sankey, use_container_width=True)


    # ------------------------------------------------------------------------------------------
    # Matriz de Performance de Operadoras (Tipo BCG) (x=Saldo de Sentimento | y= Nº de Comentários ou Reações | cores = Operadoras)
    fig_bcg_operadoras = px.scatter(
            data_frame=Facebook_PCU_Analysis,
            x='post_comments',
            y='post_reactions',
            size='comment_reactions',
            color='page',
            color_discrete_map=palette_operadoras,
            title='Matriz de Performance das Operadoras (Tipo BCG)',
            labels={'post_comments': 'Nº de Comentários do Post', 'comment_reactions': 'Nº de Reações do Comentário', 'post_reactions': 'Nº de Reações do Post', 'page': 'Operadora'},
            custom_data=['post_date', 'mDeBERTa_comment_CR_label', 'comment_sentiment_label', 'mDeBERTa_comment_topic_label_1'],
            height=1000
        )

    fig_bcg_operadoras.update_traces(marker=dict(line=dict(width=1, color='white')), selector=dict(mode='markers'))
    fig_bcg_operadoras.update_traces(
        hovertemplate='''<b>Nº de Comentários:</b> %{x}<br><b>Nº de Reações:</b> %{y}<br><b>Nº de Reações nos Comentários:</b> %{marker.size}<br><br><b>Data:</b> %{customdata[0]}<br><b>CR:</b> %{customdata[1]}<br><b>Sentimento:</b> %{customdata[2]}<br><b>Tópico:</b> %{customdata[3]}'''
    )

    col2_P1.plotly_chart(fig_bcg_operadoras, use_container_width=True)


    # ================================================================================================

    # Preparar listas para o gráfico Sankey
    labels = []
    colors = []
    source = []
    target = []
    value = []

    # Adicionar operadoras ao labels
    labels_operadoras = Facebook_PCU_Analysis['page'].unique().tolist()
    labels.extend(labels_operadoras)
    colors.extend([palette_operadoras[op] for op in labels_operadoras])

    # Adicionar sentimentos ao labels
    labels_sentimentos = Facebook_PCU_Analysis['comment_sentiment_label'].dropna().unique().tolist()
    labels_sentimentos = [sent for sent in labels_sentimentos if sent is not None]
    labels.extend(labels_sentimentos)
    colors.extend([sentiment_colors[sent] for sent in labels_sentimentos])

    # Adicionar tópicos ao labels
    labels_topicos = Facebook_PCU_Analysis['mDeBERTa_comment_topic_label_1'].unique().tolist()
    labels.extend(labels_topicos)
    colors.extend([topic_color_mapping[top] for top in labels_topicos])

    # Adicionar uma segunda camada de operadoras ao labels
    labels_operadoras_2 = [f"{op} " for op in labels_operadoras]
    labels.extend(labels_operadoras_2)
    colors.extend([palette_operadoras[op] for op in labels_operadoras_2])

    # Contar o número de ocorrências de cada combinação de operadora, sentimento e tópico
    df = Facebook_PCU_Analysis.groupby(['page', 'comment_sentiment_label', 'mDeBERTa_comment_topic_label_1']).size().reset_index()
    df.columns = ['page', 'comment_sentiment_label', 'mDeBERTa_comment_topic_label_1', 'Contagem']

    # Criar os links entre operadoras e sentimentos
    for idx, row in df.iterrows():
        source.append(labels.index(row['page']))
        target.append(labels.index(row['comment_sentiment_label']))
        value.append(row['Contagem'])

    # Criar os links entre sentimentos e tópicos
    for idx, row in df.iterrows():
        source.append(labels.index(row['comment_sentiment_label']))
        target.append(labels.index(row['mDeBERTa_comment_topic_label_1']))
        value.append(row['Contagem'])

    # Criar os links entre tópicos e a segunda camada de operadoras
    for idx, row in df.iterrows():
        source.append(labels.index(row['mDeBERTa_comment_topic_label_1']))
        target.append(labels.index(f"{row['page']} "))
        value.append(row['Contagem'])

    # Construir gráfico Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=colors,
            # hovertemplate='<b>%{label}</b> <br> <b>Nº de Comentários</b> %{value}'
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color='rgba(0, 0, 0, 0.05)',
            hovertemplate='<b> Nº de Comentários </b>%{value} <br> <b>%{source.label}</b> -> %{target.label}'
        ))],
        layout=go.Layout(
            title="Gráfico Sankey - Operadoras, Sentimentos e Tópicos",
            height=1000,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ================================================================================================
    # Gráfico Sunburst com Operadoras, Tópicos e Sentimentos
    # Contar o número de ocorrências de cada combinação de operadora, tópico e sentimento
    df_sunburst = Facebook_PCU_Analysis.groupby(['page', 'mDeBERTa_comment_topic_label_1', 'comment_sentiment_label']).size().reset_index(name='count')

    # Criar o gráfico Sunburst
    fig_sankey_topicos = px.sunburst(df_sunburst,
                                     path=['comment_sentiment_label', 'mDeBERTa_comment_topic_label_1', 'page'],
                                     values='count',
                                     color='comment_sentiment_label',
                                     color_discrete_map=combined_colors,
                                     title='Sunburst - Operadoras, Tópicos e Sentimentos',
                                     height=1500)

    fig_sankey_topicos.update_traces(textinfo='label+percent parent',
                                     hoverinfo='label+percent parent',
                                     hovertemplate='''<b>%{id}</b><br>%{value} Comentários<br><b>%{parent}</b><br>%{percentRoot:.1%} do total<br>''',
                                     branchvalues='total')

    st.plotly_chart(fig_sankey_topicos, use_container_width=True)

    # ================================================================================================

except KeyError or ValueError:
    st.warning("Não existem dados disponíveis com os filtros selecionados.")
    pass
