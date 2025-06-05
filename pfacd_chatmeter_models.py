import streamlit as st
import numpy as np
from st_pages import add_page_title
from transformers import pipeline
import torch

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Configurações da Página
st.set_page_config(layout="wide")
add_page_title(layout="wide")
st.logo(image='static/640px-HD_transparent_picture.png', icon_image='static/ChatMeter_Logo_Bullet.png')
with open('style.css') as f:
    st.markdown(f'''<style>{f.read()}
                    .h1, .h2, .h3, .h4, .h5, .h6, h1, h2, h3, h4, h5, h6 {{
                            font-weight: bold !important;
                        }}
    </style>''', unsafe_allow_html=True)
# st.write("""Esta página permite testar os <i><b>Modelos</b></i> que utilizámos na análise.""", unsafe_allow_html=True)

# ========================================================================================================
# Funções dos modelos
# Adaptado de: https://discuss.streamlit.io/t/how-can-i-set-a-model-from-hugging-face-into-streamlit/45587
#        e de: https://stackoverflow.com/questions/70274841/streamlit-unhashable-typeerror-when-i-use-st-cache

# Verificar se a GPU está disponível
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Carregar o modelo TXRBSF
@st.cache_resource
def TXRBSF_model():
    TXRBSF_model_path = "citizenlab/twitter-xlm-roberta-base-sentiment-finetunned"
    return pipeline("text-classification", model=TXRBSF_model_path, tokenizer=TXRBSF_model_path,
                    framework="pt", device=device)


# Definir a função de classificação | Modelo TXRBSF_classify_sentiment
@st.cache_resource
def TXRBSF_classify_sentiment(text):
    TXRBSF_sentiment_classifier = TXRBSF_model()
    if text.strip() == '' or text is None:
        return np.NaN, np.NaN
    outputs = TXRBSF_sentiment_classifier(text)
    return outputs[0]['label'], outputs[0]['score']


# Carregar o modelo mDeBERTa [Não tem @st.cache_resource porque dá erro devido ao tamanho do modelo]
@st.cache_resource
def mDeBERTa_model():
    # TXRBSF_model.clear()  # Limpar o cache para evitar que o server fique sem memória
    mDeBERTa_model_path = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
    return pipeline("zero-shot-classification", model=mDeBERTa_model_path, tokenizer=mDeBERTa_model_path,
                    framework="pt", device=device)


# Definir a função de classificação | Modelo mDeBERTa_classify_sentiment
@st.cache_resource
def mDeBERTa_classify_sentiment(texts):
    moritz_classifier = mDeBERTa_model()
    outputs = moritz_classifier([texts], candidate_labels=['Positivo', 'Neutro', 'Negativo'], multi_label=False)
    labels = [output['labels'][0] for output in outputs]
    scores = [output['scores'][0] for output in outputs]
    return labels, scores


# ----------------------------------------------------------------------------------------------------------------
# Defina a função de classificação
@st.cache_resource
def mDeBERTa_classify_topics(texts):
    # Defina as classes a classificar pelo modelo como tópicos
    candidate_labels = [

        # Tópicos associados às Operadoras
        "Pacotes de Serviços", "Cobertura", "Velocidade", "Preços", "Qualidade", "Atendimento ao Cliente",
        "Concorrência", "5G",
        "Satisfação", "Rede", "Fidelização", "Promoções", "Segurança", "Plataformas Streaming", "Festivais",
        "Comunicação",

        # Tópicos de Eventos Anuais
        "Páscoa", "Natal", "Ano Novo", "Santos Populares", "Passatempo", "Black Friday", "Regresso às Aulas",

        # Tópicos Desportivos
        "Futebol", "Cristiano Ronaldo", "Surf", "Outros desportos",

        # Tópicos Gerais
        "Problemas da Sociedade", "Cinema", "Filme/Série", "Economia", "Saúde", "Videojogo", "Política", "Emprego",
        "Tecnologia", "Inteligência Artificial", "Ambiente", "Educação", "Cultura", "Ciência", "Arte", "Religião",
        "Negócios", "Sustentabilidade", "Moda", "Alimentação", "Viagens", "Família", "Guerra", "Pandemia",
        "Redes Sociais", "Sociedade"
    ]
    moritz_classifier = mDeBERTa_model()
    outputs = moritz_classifier([texts], candidate_labels, multi_label=True)
    labels = [output['labels'] for output in outputs]
    scores = [output['scores'] for output in outputs]
    # Guardar os 2 tópicos 'labels' e 'scores' que dão de resultado
    return labels[0][:3], scores[0][:3]


# ========================================================================================================

st.write("#### Demonstração dos Modelos")
st.divider()

# Criar uma caixa de texto para entrada
input_text = st.text_area(label="Insira a sua frase",
                          value="As operadoras de telecomunicações oferecem uma gama de serviços de comunicação.",
                          help="Experimenta com outra frase! (Opcional)",
                          max_chars=1000,
                          placeholder="Insira a sua frase aqui...")

# Criar um botão para iniciar a análise
if not input_text.strip():
    # Desabilitar o botão se a caixa de texto estiver vazia
    st.button("Analisar", disabled=True)
else:
    if st.button("Analisar"):
        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Análise de Sentimentos", "Análise de Tópicos"])
        with tab1:
            # Executar ambas as funções de classificação de sentimentos
            result_TXRBSF = TXRBSF_classify_sentiment(input_text)
            result_mDeBERTa = mDeBERTa_classify_sentiment(input_text)

            # Exibir os resultados em 2 colunas
            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    "## Modelo [TXRBSF](https://huggingface.co/citizenlab/twitter-xlm-roberta-base-sentiment-finetunned)")
                st.markdown("**Autor:** Arian Pasquali", unsafe_allow_html=True)
                st.image("static/SA_Model_1.png", use_column_width=True, caption="Modelo TXRBSF no HuggingFace")
                st.markdown("<br><div style='margin-top:10px;margin-bottom: 24px;'></div>", unsafe_allow_html=True)
                st.divider()

                st.markdown(
                    """<p class="text-justify">
                    O modelo TXRBSF é um modelo de classificação de sentimentos, treinado com o Twitter XLM-RoBERTa base,
                    que foi finetunned para classificar sentimentos em textos. Este modelo é capaz de classificar
                    sentimentos em 3 classes: Positivo, Neutro e Negativo.
                    <br><br>
                    Este modelo é um modelo <b>Text Classification</b> que foi treinado com exemplos rotulados de sentimentos 
                    e por isso apenas consegue classificar sentimentos em textos, mas não consegue extrapolar para outros labels.
                    </p>
                    """, unsafe_allow_html=True
                )

                st.divider()
                st.write("### Sentimento Classificado:")
                # Se o sentimento for 'Positive'
                if result_TXRBSF[0] == "Positive":
                    st.markdown("<h1 style='align-items:center;text-align:center;color: green;'>Positivo</h1><br>",
                                unsafe_allow_html=True)
                    col1_S, col2_S, col3_S = st.columns(3)
                    with col2_S:
                        st.image("static/Sentiment_P.png", use_column_width=True)

                    st.write(f"**Score:** :green-background[${round(float(result_TXRBSF[1]), 4)}$]")

                # Se o sentimento for 'Neutral'
                elif result_TXRBSF[0] == "Neutral":
                    st.markdown("<h1 style='align-items:center;text-align:center;color: #F47131;'>Neutro</h1><br>",
                                unsafe_allow_html=True)
                    col1_S, col2_S, col3_S = st.columns(3)
                    with col2_S:
                        st.image("static/Sentiment_N.png", use_column_width=True)

                    st.write(f"**Score:** :orange-background[${round(float(result_TXRBSF[1]), 4)}$]")

                # Se o sentimento for 'Negative'
                elif result_TXRBSF[0] == "Negative":
                    st.markdown("<h1 style='align-items:center;text-align:center;color: red;'>Negativo</h1><br>",
                                unsafe_allow_html=True)
                    col1_S, col2_S, col3_S = st.columns(3)
                    with col2_S:
                        st.image("static/Sentiment_Ne.png", use_column_width=True)

                    st.write(f"**Score:** :red-background[${round(float(result_TXRBSF[1]), 4)}$]")

                # Se não for possível classificar o sentimento
                else:
                    st.write("### Não foi possível classificar o sentimento. Por favor tente novamente mais tarde!")

            with col2:
                st.write(
                    "## Modelo [mDeBERTa](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7)")
                st.markdown("**Autor:** Moritz Laurer", unsafe_allow_html=True)
                st.image("static/SA_Model_2.png", use_column_width=True, caption="Modelo mDeBERTa no HuggingFace")
                st.divider()

                st.markdown(
                    """<p class="text-justify">
                    O modelo mDeBERTa é um modelo do tipo <b>Zero-Shot Classification</b>, que foi treinado com o XLM-RoBERTa base, 
                    e que atua a nível do processamento de linguagem natural, sendo <i>finetunned</i> com dados <i>multilinguals</i>.
                    <br><br>
                    Este tipo de modelo é treinado com exemplos rotulados, mas consegue extrapolar as classificações em novos <i>labels</i>,
                    contudo, para a classificação de sentimentos, neste modelo foram definidos os 3 labels: Positivo, Neutro e Negativo.
                    </p>
                """, unsafe_allow_html=True
                )
                
                st.divider()

                st.write("### Sentimento Classificado:")

                # Se o sentimento for 'Positivo'
                if result_mDeBERTa[0][0] == "Positivo":
                    st.markdown("<h1 style='align-items:center;text-align:center;color: green;'>Positivo</h1><br>",
                                unsafe_allow_html=True)
                    col1_S, col2_S, col3_S = st.columns(3)
                    with col2_S:
                        st.image("static/Sentiment_P.png", use_column_width=True)
                    st.write(f"**Score:** :green-background[${round(float(result_mDeBERTa[1][0]), 4)}$]")

                # Se o sentimento for 'Neutro'
                elif result_mDeBERTa[0][0] == "Neutro":
                    st.markdown("<h1 style='align-items:center;text-align:center;color: #F47131;'>Neutro</h1><br>",
                                unsafe_allow_html=True)
                    col1_S, col2_S, col3_S = st.columns(3)
                    with col2_S:
                        st.image("static/Sentiment_N.png", use_column_width=True)

                    st.write(f"**Score:** :orange-background[${round(float(result_mDeBERTa[1][0]), 4)}$]")

                # Se o sentimento for 'Negativo'
                elif result_mDeBERTa[0][0] == "Negativo":
                    st.markdown("<h1 style='align-items:center;text-align:center;color: red;'>Negativo</h1><br>",
                                unsafe_allow_html=True)
                    col1_S, col2_S, col3_S = st.columns(3)
                    with col2_S:
                        st.image("static/Sentiment_Ne.png", use_column_width=True)

                    st.write(f"**Score:** :red-background[${round(float(result_mDeBERTa[1][0]), 4)}$]")

                # Se não for possível classificar o sentimento
                else:
                    st.write("### Não foi possível classificar o sentimento. Por favor tente novamente mais tarde!")

            st.markdown("<br>", unsafe_allow_html=True)
            # ========================================================================================================
            # Juntar os Modelos
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.write("## 🔗 Juntar Modelos")
            st.divider()

            st.markdown(
                '''
                <style>               
                    .st-emotion-cache-1629p8f h1, .st-emotion-cache-1629p8f h2, .st-emotion-cache-1629p8f h3, .st-emotion-cache-1629p8f h4,
                    .st-emotion-cache-1629p8f h5, .st-emotion-cache-1629p8f h6, .st-emotion-cache-1629p8f span {
                        font-weight: bolder;
                    }
    
                    .st-emotion-cache-11se1re:active, .st-emotion-cache-11se1re:visited, .st-emotion-cache-11se1re:hover {
                        text-decoration: none;
                        font-weight: 400;
                    }
                    .st-emotion-cache-11se1re {
                        font-weight: 400;
                    }
                </style>
    
                <!-- Bibliotecas de Icons-->
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
                <script type="module" src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.esm.js"></script>
                <script nomodule src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js"></script>
    
                <!-- Bootstrap CSS -->
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/css/bootstrap.min.css"
                      integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    
                <div class="container col-md-10">
                    <h1 class="text-center">Explicação da Combinação dos Modelos</h1>                    
                    <br><br>
                    <p class="text-justify" style="padding-left: 15px; margin-right: 15px;">
                        Para combinar os resultados dos modelos <b>TXRBSF</b> e <b>mDeBERTa</b>, utilizamos a seguinte lógica:
                    </p>
                    <ul style="padding-left: 30px; margin-right: 15px;">
                        <li>Se ambos os modelos classificarem o sentimento como <b style="color: #64C548;">Positivo</b>, então o sentimento final é <b style="color: #64C548;">Positivo</b>.</li>
                        <li>Se ambos os modelos classificarem o sentimento como <b style="color: #CF213D;">Negativo</b>, então o sentimento final é <b style="color: #CF213D;">Negativo</b>.</li>
                        <li>Se ambos os modelos classificarem o sentimento como <b style="color: #F47131;">Neutro</b>, então o sentimento final é <b style="color: #F47131;">Neutro</b>.</li>
                        <br>
                        <li>Se um dos modelos classificar o sentimento como <b style="color: #64C548;">Positivo</b> e o outro como <b style="color: #F47131;">Neutro</b>, então o sentimento final é <b style="color: #EBA722;">Tendência Positiva</b>.</li>
                        <li>Se um dos modelos classificar o sentimento como <b style="color: #CF213D;">Negativo</b> e o outro como <b style="color: #F47131;">Neutro</b>, então o sentimento final é <b style="color: #F03F42;">Tendência Negativa</b>.</li>
                        <li>Se um dos modelos classificar o sentimento como <b style="color: #64C548;">Positivo</b> e o outro como <b style="color: #CF213D;">Negativo</b>, então o sentimento final é <b style="color: #F47131;">Neutro</b>.</li>
                    </ul>
                    <br>
                    <p class="text-justify" style="padding-left: 15px; margin-right: 15px;">
                        Ou seja, segundo a <b>Matriz:</b>
                    </p>
                    <!-- Matriz de Confusão com esta explicação e cores numa tabela em HTML -->
                    <div class="table-responsive">
                        <table class="col-md-7 table table-bordered text-center" style="margin: auto;">
                            <thead>
                                <tr>
                                    <th></th>
                                    <th>Positivo</th>
                                    <th>Neutro</th>
                                    <th>Negativo</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><b>Positivo</b></td>
                                    <td style="background-color: #64C548; color: white; opacity: 0.85;">Positivo</td>
                                    <td style="background-color: #EBA722; color: white; opacity: 0.85;">Tendência Positiva</td>
                                    <td style="background-color: #F47131; color: white; opacity: 0.85;">Neutro</td>
                                </tr>
                                <tr>
                                    <td><b>Neutro</b></td>
                                    <td style="background-color: #EBA722; color: white; opacity: 0.85;">Tendência Positiva</td>
                                    <td style="background-color: #F47131; color: white; opacity: 0.85;">Neutro</td>
                                    <td style="background-color: #F03F42; color: white; opacity: 0.85;">Tendência Negativa</td>
                                </tr>
                                <tr>
                                    <td><b>Negativo</b></td>
                                    <td style="background-color: #F47131; color: white; opacity: 0.85;">Neutro</td>
                                    <td style="background-color: #F03F42; color: white; opacity: 0.85;">Tendência Negativa</td>
                                    <td style="background-color: #CF213D; color: white; opacity: 0.85;">Negativo</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <br>
                    <hr class="solid">
                    <br>
                    <h1 class="text-center">Resultados nos Dados Extraídos</h1>
                    <div class="py-5">
                        <div class="container">
                            <div class="row justify-content-center text-center" style="margin-bottom: -40px">
                                <div class="col-md-10">
                                    <img src="./app/static/combine-modelos.png" class="img-fluid" alt="Resultado dos Modelos nos Comentários Analisados">
                                    <br><br>
                                    <p class="text-center text-muted" style="font-style: italic;">
                                        <b>Figura:</b> Resultado dos Modelos nos Comentários Analisados.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True
            )

        with tab2:
            # Executar a função de classificação de tópicos
            result_mDeBERTa_topics = mDeBERTa_classify_topics(input_text)

            # Exibir os resultados em 2 colunas
            col1, col2 = st.columns(2)

            with col1:          
                st.write("## Modelo [mDeBERTa](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7)")
                st.markdown("**Autor:** Moritz Laurer", unsafe_allow_html=True)
                st.image("static/SA_Model_2.png", use_column_width=True, caption="Modelo mDeBERTa no HuggingFace")
                st.divider()

                st.markdown(
                    """<p class="text-justify">
                    Sendo o modelo mDeBERTa um modelo <b>Zero-Shot Classification</b>, este consegue classificar tópicos em textos, dado 
                    um conjunto de <i>labels</i> possíveis. Neste caso, foram definidos os tópicos mais comuns nestes comentários e de
                    forma geral para que o modelo consiga classificar os tópicos mais relevantes.
                    <br><br>
                    A lista de tópicos possíveis é apresentados na secção abaixo.
                    </p>
                """, unsafe_allow_html=True)

            with col2:
                # Mapeamento de Cores para os Tópicos
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
                st.markdown(f"""
                <style>               
                    .st-emotion-cache-1629p8f h1, .st-emotion-cache-1629p8f h2, .st-emotion-cache-1629p8f h3, .st-emotion-cache-1629p8f h4,
                    .st-emotion-cache-1629p8f h5, .st-emotion-cache-1629p8f h6, .st-emotion-cache-1629p8f span {{
                        font-weight: bolder;
                    }}
                    
                    .st-emotion-cache-11se1re:active, .st-emotion-cache-11se1re:visited, .st-emotion-cache-11se1re:hover {{
                        text-decoration: none;
                        font-weight: 400;
                    }}
                    .st-emotion-cache-11se1re {{
                        font-weight: 400;
                    }}
                </style>
                
                <!-- Bibliotecas de Icons-->
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
                <script type="module" src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.esm.js"></script>
                <script nomodule src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js"></script>
                
                <!-- Bootstrap CSS -->
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/css/bootstrap.min.css"
                      integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
                          
                
                <div style='margin-bottom: 100px;'> </div>
                            
                <h1 style='text-align: center; margin-top: 50px;'>Tópicos Classificados</h1>
                <br>
                <div class="container">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <div class="card text-center" style="border-color: {topic_color_mapping[result_mDeBERTa_topics[0][0]]};">
                                <div class="card-header" style="background-color: {topic_color_mapping[result_mDeBERTa_topics[0][0]]}; color: #FFF;">
                                    <h1 style="margin: 0;color: #FFF;">1º</h1>
                                </div>
                                <div class="card-body">
                                    <h2 class="card-text" style="color: {topic_color_mapping[result_mDeBERTa_topics[0][0]]}; margin-bottom: -5px; font-size: 1.6em;">
                                        {result_mDeBERTa_topics[0][0]}
                                    </h2>
                                    <p class="card-text" style="color: {topic_color_mapping[result_mDeBERTa_topics[0][0]]}; opacity: 0.65;">
                                        <b>Score:</b> {round(float(result_mDeBERTa_topics[1][0]), 4)}
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="card text-center" style="border-color: {topic_color_mapping[result_mDeBERTa_topics[0][1]]};">
                                <div class="card-header" style="background-color: {topic_color_mapping[result_mDeBERTa_topics[0][1]]}; color: #FFF;">
                                    <h1 style="margin: 0;color: #FFF;">2º</h1>
                                </div>
                                <div class="card-body">
                                    <h2 class="card-text" style="color: {topic_color_mapping[result_mDeBERTa_topics[0][1]]}; margin-bottom: -5px; font-size: 1.6em;">
                                        {result_mDeBERTa_topics[0][1]}
                                    </h2>
                                    <p class="card-text" style="color: {topic_color_mapping[result_mDeBERTa_topics[0][1]]}; opacity: 0.65;">
                                        <b>Score:</b> {round(float(result_mDeBERTa_topics[1][1]), 4)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
    
    
                """, unsafe_allow_html=True)

            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)

            # Tópicos Possíveis
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.write("## 🔗 Tópicos Possíveis")

            st.markdown(
                '''
                <br>
                <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">
    
                <style>
                    .list-group {
                        margin-left: -20px;
                    }
                </style>
    
                <div class="container">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="card" style="border-radius: 10px; border: 1px solid #FADBD8;">
                                <div class="card-header text-center" style="background-color: #E74C3C; opacity: 0.8; border-radius: 10px 10px 0 0;">
                                    <h4 style="margin-bottom:-5px; color: #fff;">
                                        <i class="fas fa-mobile-alt" style="margin-right: 10px;"></i> Operadoras
                                    </h4>
                                </div>
                                <div class="card-body text-center">
                                    <!-- <style> .list-group-flush .list-group-item {border-color: #E74C3C;} </style>  -->
                                    <ul class="list-group list-group-flush">
                                        <li class="list-group-item">Pacotes de Serviços</li>
                                        <li class="list-group-item">Cobertura</li>
                                        <li class="list-group-item">Velocidade</li>
                                        <li class="list-group-item">Preços</li>
                                        <li class="list-group-item">Qualidade</li>
                                        <li class="list-group-item">Atendimento ao Cliente</li>
                                        <li class="list-group-item">Concorrência</li>
                                        <li class="list-group-item">5G</li>
                                        <li class="list-group-item">Satisfação</li>
                                        <li class="list-group-item">Rede</li>
                                        <li class="list-group-item">Fidelização</li>
                                        <li class="list-group-item">Promoções</li>
                                        <li class="list-group-item">Segurança</li>
                                        <li class="list-group-item">Plataformas Streaming</li>
                                        <li class="list-group-item">Festivais</li>
                                        <li class="list-group-item">Comunicação</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card" style="border-radius: 10px; border: 1px solid #D4E6F1;">
                               <div class="card-header text-center" style="background-color: #3498DB; opacity: 0.8; border-radius: 10px 10px 0 0;">
                                    <h4 style="margin-bottom:-5px; color: #fff;">
                                        <i class="far fa-calendar-alt" style="margin-right: 10px;"></i> Eventos Anuais
                                    </h4>
                               </div>
                               <div class="card-body text-center">
                                    <!-- <style> .list-group-flush .list-group-item {border-color: #3498DB;} </style> -->
                                    <ul class="list-group list-group-flush">
                                        <li class="list-group-item">Páscoa</li>
                                        <li class="list-group-item">Natal</li>
                                        <li class="list-group-item">Ano Novo</li>
                                        <li class="list-group-item">Santos Populares</li>
                                        <li class="list-group-item">Passatempo</li>
                                        <li class="list-group-item">Black Friday</li>
                                        <li class="list-group-item">Regresso às Aulas</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card" style="border-radius: 10px; border: 1px solid #A9DFBF;">
                                <div class="card-header text-center" style="background-color: #229954; opacity: 0.8; border-radius: 10px 10px 0 0;">
                                    <h4 style="margin-bottom:-5px; color: #fff;">
                                        <i class="fas fa-heartbeat" style="margin-right: 10px;"></i> Desportivos
                                    </h4>
                                </div>
                                <!-- <style> .list-group-flush .list-group-item {border-color: #229954;} </style>  -->
                                <div class="card-body text-center">
                                    <ul class="list-group list-group-flush">
                                        <li class="list-group-item">Futebol</li>
                                        <li class="list-group-item">Cristiano Ronaldo</li>
                                        <li class="list-group-item">Surf</li>
                                        <li class="list-group-item">Outros desportos</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card" style="border-radius: 10px; border: 1px solid #D5DBDB;">
                                <div class="card-header text-center" style="background-color: #566573; opacity: 0.8;border-radius: 10px 10px 0 0;">
                                    <h4 style="margin-bottom:-5px; color: #fff;">
                                        <i class="fas fa-globe" style="margin-right: 10px;"></i> Gerais
                                    </h4>
                                </div>
                                <div class="card-body text-center">
                                    <!-- <style> .list-group-flush .list-group-item {border-color: #566573;} </style> -->
                                    <ul class="list-group list-group-flush">
                                        <li class="list-group-item">Problemas da Sociedade</li>
                                        <li class="list-group-item">Cinema</li>
                                        <li class="list-group-item">Filme/Série</li>
                                        <li class="list-group-item">Economia</li>
                                        <li class="list-group-item">Saúde</li>
                                        <li class="list-group-item">Videojogo</li>
                                        <li class="list-group-item">Política</li>
                                        <li class="list-group-item">Emprego</li>
                                        <li class="list-group-item">Tecnologia</li>
                                        <li class="list-group-item">Inteligência Artificial</li>
                                        <li class="list-group-item">Ambiente</li>
                                        <li class="list-group-item">Educação</li>
                                        <li class="list-group-item">Cultura</li>
                                        <li class="list-group-item">Ciência</li>
                                        <li class="list-group-item">Arte</li>
                                        <li class="list-group-item">Religião</li>
                                        <li class="list-group-item">Negócios</li>
                                        <li class="list-group-item">Sustentabilidade</li>
                                        <li class="list-group-item">Moda</li>
                                        <li class="list-group-item">Alimentação</li>
                                        <li class="list-group-item">Viagens</li>
                                        <li class="list-group-item">Família</li>
                                        <li class="list-group-item">Guerra</li>
                                        <li class="list-group-item">Pandemia</li>
                                        <li class="list-group-item">Redes Sociais</li>
                                        <li class="list-group-item">Sociedade</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <br><br>
                <hr class="solid">
                <br>
                ''', unsafe_allow_html=True)

        # ========================================================================================================
