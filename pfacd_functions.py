import pandas as pd
import streamlit as st
import matplotlib as mpl
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from PIL import Image

# Lista de Colunas da Base de Dados
df_colunas = ['page',
              'post_id', 'post_link', 'post_date', 'post_reactions', 'post_comments', 'post_shares',
              'post_text', 'post_text_clean', 'post_sentiment_label',
              'post_day', 'post_month', 'post_year', 'post_hour', 'post_language',

              'TXRBSF_post_sentiment_label', 'TXRBSF_post_sentiment_score',
              'mDeBERTa_post_sentiment_label', 'mDeBERTa_post_sentiment_score',
              'post_text_Vodafone', 'post_text_MEO', 'post_text_NOS', 'post_text_DIGI',

              'mDeBERTa_post_topic_label_1', 'mDeBERTa_post_topic_score_1',
              'mDeBERTa_post_topic_label_2', 'mDeBERTa_post_topic_score_2',
              'mDeBERTa_post_topic_label_3', 'mDeBERTa_post_topic_score_3',
              'mDeBERTa_post_CR_label', 'mDeBERTa_post_CR_score',
              'comment_date', 'comment_day_ago', 'comment_language',

              'comment_id', 'comment_link', 'comment_reactions', 'comment_num_responses',
              'comment_operator_responded', 'comment_text', 'comment_text_clean', 'comment_sentiment_label',
              'TXRBSF_comment_sentiment_label', 'TXRBSF_comment_sentiment_score',
              'mDeBERTa_comment_sentiment_label', 'mDeBERTa_comment_sentiment_score',
              'comment_text_Vodafone', 'comment_text_MEO', 'comment_text_NOS', 'comment_text_DIGI',
              'mDeBERTa_comment_topic_label_1', 'mDeBERTa_comment_topic_score_1',
              'mDeBERTa_comment_topic_label_2', 'mDeBERTa_comment_topic_score_2',
              'mDeBERTa_comment_topic_label_3', 'mDeBERTa_comment_topic_score_3',
              'mDeBERTa_comment_CR_label', 'mDeBERTa_comment_CR_score',

              'user_name', 'user_link', 'user_freguesia', 'user_concelho', 'user_distrito',
              'user_pais', 'user_predicted_genre',
              'user_current_city', 'user_hometown', 'user_city_not_portugal']


# Import da Base de Dados com Análise
# Caching: https://docs.streamlit.io/develop/concepts/architecture/caching
@st.cache_resource
def load_data(columns=None):
    # Carregar as partes dos arquivos
    parts = []
    for i in range(3):
        part = pd.read_pickle(f'Datasets_Vodafone/Facebook_PCU_Analysis_part_{i+1}.pkl')
        if columns is not None:
            part = part[columns]
        parts.append(part)

    # Concatenar as partes para obter o DataFrame completo
    Facebook_PCU_Analysis = pd.concat(parts)

    # Selecionar colunas, se necessário
    if columns is not None:
        Facebook_PCU_Analysis = Facebook_PCU_Analysis[columns]

    # Alterar tipos de dados
    Facebook_PCU_Analysis['post_id'] = Facebook_PCU_Analysis['post_id'].astype(str)
    Facebook_PCU_Analysis['post_date'] = pd.to_datetime(Facebook_PCU_Analysis['post_date'])

    # Calcular o dia da semana (0 = Segunda-Feira, 6 = Domingo)
    Facebook_PCU_Analysis['post_weekday'] = Facebook_PCU_Analysis['post_date'].dt.weekday
    weekday_names = {0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'}
    Facebook_PCU_Analysis['post_weekday'] = Facebook_PCU_Analysis['post_weekday'].map(weekday_names)

    # Base de Dados dos Posts
    Facebook_Posts_Analysis = Facebook_PCU_Analysis.groupby('post_id').first().reset_index()

    # Selecionar apenas as colunas relevantes para o Facebook_Posts_Analysis
    Facebook_Posts_Analysis = Facebook_Posts_Analysis[
        ['post_id', 'page', 'post_link', 'post_date', 'post_day', 'post_weekday', 'post_month',
         'post_year', 'post_hour', 'post_reactions', 'post_comments', 'post_shares',
         'post_text', 'post_text_clean', 'post_language', 'post_sentiment_label',
         'TXRBSF_post_sentiment_label', 'TXRBSF_post_sentiment_score',
         'mDeBERTa_post_sentiment_label', 'mDeBERTa_post_sentiment_score',
         'post_text_Vodafone', 'post_text_MEO', 'post_text_NOS', 'post_text_DIGI',
         'mDeBERTa_post_topic_label_1', 'mDeBERTa_post_topic_score_1',
         'mDeBERTa_post_topic_label_2', 'mDeBERTa_post_topic_score_2',
         'mDeBERTa_post_topic_label_3', 'mDeBERTa_post_topic_score_3',
         'mDeBERTa_post_CR_label', 'mDeBERTa_post_CR_score']]

    # Dicionário para mapear os números de mês para seus equivalentes por extenso
    month_names = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                   7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

    # Aplicar a conversão para extenso
    Facebook_Posts_Analysis['post_month'] = Facebook_Posts_Analysis['post_month'].map(month_names)
    Facebook_PCU_Analysis['post_month'] = Facebook_PCU_Analysis['post_month'].map(month_names)

    return Facebook_PCU_Analysis, Facebook_Posts_Analysis


# Função para datas de seleção de inicialização da barra lateral
# Fonte: https://github.com/korenkaplan/Admin-dashboard/blob/main/sidebar.py
def init_sidebar_dates_pickers(data_frame_datatime):
    # Convert the order_date column to datetime
    data_frame_datatime = pd.to_datetime(data_frame_datatime).dt.date
    # Convert the order_date column to datetime for manipulation and find the min and max value
    min_date = data_frame_datatime.min()
    max_date = data_frame_datatime.max()
    # Initialize the sidebar date pickers and define the min and max value to choose from
    start_date = st.sidebar.date_input('Data de Início', min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.sidebar.date_input('Data de Fim', min_value=min_date, max_value=max_date, value=max_date)
    # Return the values
    return start_date, end_date


# Função para datas de seleção de inicialização na página
def init_page_dates_pickers(data_frame_datatime, col1=None, col2=None):
    # Convert the order_date column to datetime
    data_frame_datatime = pd.to_datetime(data_frame_datatime).dt.date
    # Convert the order_date column to datetime for manipulation and find the min and max value
    min_date = data_frame_datatime.min()
    max_date = data_frame_datatime.max()
    # Initialize the sidebar date pickers and define the min and max value to choose from
    if col1 is not None and col2 is not None:
        start_date = col1.date_input('Data de Início', min_value=min_date, max_value=max_date, value=min_date)
        end_date = col2.date_input('Data de Fim', min_value=min_date, max_value=max_date, value=max_date)
    else:
        start_date = st.date_input('Data de Início', min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.date_input('Data de Fim', min_value=min_date, max_value=max_date, value=max_date)
    # Return the values
    return start_date, end_date


# Função para criar um cartão personalizado HTML
def create_card(col, icon_name, color, color_text, title, value):
    htmlstr = f"""
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">
    <p style="background-color: rgb({color[0]}, {color[1]}, {color[2]});
            color: rgb({color_text[0]}, {color_text[1]}, {color_text[2]});
            font-weight: 700;
            font-size: 30px;
            border-radius: 7px;
            padding-left: 20px; 
            padding-top: 18px; 
            padding-bottom: 18px;
            line-height: 25px;">
        <i class='{icon_name} fa-xs' style='margin-right: 5px;'></i>{value}</style>
        <br>
        <span style='font-size: 18px; margin-top: 0; font-weight: 100;margin-left: 30px;'>{title}</style></span></p>
    """
    col.markdown(htmlstr, unsafe_allow_html=True)


# Função para criar o Wordcloud
@st.cache_resource
def plot_wordcloud(word_df_text, colormap="Greens"):
    cmap = mpl.cm.get_cmap(colormap)(np.linspace(0, 1, 20))
    cmap = mpl.colors.ListedColormap(cmap[10:15])
    mask = np.array(Image.open("static/facebook_mask.png"))
    text_string_list = word_df_text.tolist()
    post_text_string = ' '.join(text_string_list)
    wc = WordCloud(
        background_color="white",
        max_words=90,
        colormap=cmap,
        mask=mask,
        random_state=42,
        collocations=False,
        min_word_length=2,
        max_font_size=200,
    )
    wc.generate(post_text_string)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    plt.title("Wordcloud", fontdict={"fontsize": 16}, fontweight="heavy", pad=20, y=1.0)
    return fig
