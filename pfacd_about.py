import streamlit as st
from st_pages import add_page_title

# ------------- Configuração Inicial -------------
st.set_page_config(layout="wide")
add_page_title(layout="wide")
st.divider()
st.logo(image='static/640px-HD_transparent_picture.png', icon_image='static/ChatMeter_Logo_Bullet.png')

# ---- Carregar o estilo CSS ----
with open('style.css') as f:
    st.markdown(f'''<style>{f.read()}
        .h1, .h2, .h3, .h4, .h5, .h6, h1, h2, h3, h4, h5, h6 {{
                font-weight: bold !important;
            }}
    </style>''', unsafe_allow_html=True)

# ------------- Sobre Nós -------------
st.markdown("""
    
    <!-- CSS -->
    <style>
        @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css");
    
        /*@font-face {*/
        /*    font-display: block;*/
        /*    font-family: "bootstrap-icons";*/
        /*    src: url("./fonts/bootstrap-icons.woff2?8d200481aa7f02a2d63a331fc782cfaf") format("woff2"),*/
        /*    url("./fonts/bootstrap-icons.woff?8d200481aa7f02a2d63a331fc782cfaf") format("woff");*/
        /*}*/
    
        /* Geral | Base */
    
    
        .st-emotion-cache-1629p8f h1, .st-emotion-cache-1629p8f h2, .st-emotion-cache-1629p8f h3, .st-emotion-cache-1629p8f h4,
        .st-emotion-cache-1629p8f h5, .st-emotion-cache-1629p8f h6, .st-emotion-cache-1629p8f span {
            font-weight: bolder;
        }
    
        pre,
        p {
            color: #393a3e;
            font-size: 16px;
        }
    
        img {
            max-width: 100%;
        }
    
        ul,
        ol {
            margin: 0;
            padding: 0;
        }
    
        a {
            text-decoration: none;
        }
    
        a:hover,
        a:focus,
        a:active {
            text-decoration: none;
            outline: 0 none;
        }
    
        li {
            list-style: none;
        }
    
        /* Contactos - Sobre Nós */
        .layout_padding {
            padding-top: 90px;
            padding-bottom: 90px;
        }
    
        .about_section .row {
            -webkit-box-align: center;
            -ms-flex-align: center;
            align-items: center;
        }
    
        .about_section .img_container .img-box img {
            width: 100%;
            height: 500px;
            object-fit: cover;
        }
    
        .about_section .detail-box {
            width: 800px;
            background-color: #ffffff;
            padding: 45px 30px;
            -webkit-box-shadow: 0 0 5px 0 rgba(0, 0, 0, 0.2);
            box-shadow: 0 0 5px 0 rgba(0, 0, 0, 0.2);
            position: relative;
            margin-left: -150px;
        }
    
        .about_section .detail-box p {
            margin-top: 5px;
            font-family: 'Poppins', sans-serif;
            font-weight: normal;
            text-align: justify;
        }
    
        .team {
            color: #8d97ad;
            font-weight: 300;
        }
    
    
        .team .title-contactos {
            font-weight: 800;
            font-size: 40px;
        }
    
        .team h1,
        .team h2,
        .team h3,
        .team h4,
        .team h5,
        .team h6 {
            color: #3d392d;
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
        
        @media (max-width: 768px) {
            .about_section .img_container .img-box img {
                height: 300px;
            }
            
            .about_section .detail-box {
                width: 100%;
                margin-left: 0;
            }
            
            .about_section .detail-box p {
                font-size: 16px;
                margin-left: 0px !important;
            }
            
            .about_section .detail-box {
                margin: 0 auto;
            }
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
    
    <!-- Topo da Página -->
    <br>
    <!-- Contactos - Sobre Nós -->
    <section class="about_section layout_padding">
        <div class="container">
            <div class="row">
                <div class="col-md-6 px-0">     <!-- data-aos="fade-right" data-aos-duration="800" -->
                    <div class="img_container">
                        <div class="img-box">
                            <img src="./app/static/contactos/sobre-nos-final.png" style="border-radius: 5px;" alt=""/>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 px-0">     <!-- data-aos="fade-left" data-aos-duration="800" -->
                    <div class="detail-box" style="border-radius: 20px;">
                        <div class="heading_container mb-3" style="margin-left: 10px" href="#">
                            <h2 style="font-family: 'Poppins', sans-serif; font-weight: bold">
                                Sobre Nós
                            </h2>
                        </div>
                        <p style="margin-left: 15px; margin-right: 10px">
                            Face à constante mudança que se verifica em todos os negócios e setores de atividade, decidimos aliarmo-nos à Vodafone 
                            na tentativa de encontrar uma solução, que permitisse às empresas uma constante perceção
                            do seu negócio, levando a uma progressiva melhoria deste.
                        </p>
                        <p style="margin-left: 15px; margin-right: 10px">
                            Através de uma interface simples e agradável, enriquecida por filtros e várias
                            funcionalidades fáceis de utilizar, proporcionamos uma experiência de navegação
                            descomplicada e intuitiva, tornando a exploração e criação de receitas
                            acessíveis para todos os utilizadores, independentemente da sua experiência na área.
                        </p>
                        <p style="margin-left: 15px; margin-right: 10px">
                            Este aplicação foi desenvolvida por um grupo de 5 alunos da Licenciatura em Ciência de Dados do ISCTE, 
                            no âmbito da unidade curricular de <b>Projeto Final Aplicado a Ciência de Dados</b>.
                        </p>    
                    </div>
                </div>
            </div>
        </div>
    </section>
    <!-- Contactos - Equipa | Fonte: https://snippets.wrappixel.com/bootstrap-our-team-section/ -->
    <div class="py-5 team">
        <div class="container">
            <div class="row justify-content-center" style="margin-bottom: -40px">
                <div class="col-md-7 text-center">
                    <h1 class="mb-1 title-contactos">Equipa</h1> <!-- data-aos="fade-right" data-aos-duration="800" -->
                    <p class="subtitle-title">ChatMeter</p> <!-- data-aos="fade-left" data-aos-duration="800" -->
                </div>
            </div>
        </div>
    </div>
    <div class="py-5 team bg-light" style="border-radius: 50px;">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-2 mt-2 mb-2"> <!-- data-aos="zoom-in" data-aos-duration="800"  | style="margin-left:11.5rem"-->
                    <div class="row">
                        <div class="col-md-12 pro-pic">
                            <a href="https://www.linkedin.com/in/andrefgsilvestre/" target="_blank">
                                <img src="./app/static/contactos/Andre_Silvestre.jpg" alt="wrapkit"
                                     class="img-fluid rounded-circle"/>
                            </a>
                        </div>
                        <div class="col-md-12" style="margin-left: 5px; padding-right: 25px">
                            <div class="pt-2">
                                <h5 class="mt-4 font-weight-medium mb-0">André Silvestre</h5>
                                <h6 class="subtitle-names" style="margin-top: -10px;">Estudante | LCD</h6>
                                <ul class="list-inline" style="margin-top: 0rem; margin-left: 1.5rem">
                                    <li class="list-inline-item"><a
                                            href="https://www.linkedin.com/in/andrefgsilvestre/"
                                            class="text-decoration-none d-block px-1"><i class="fa fa-linkedin" aria-hidden="true"></i></a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-2 mt-2 mb-2">  <!-- data-aos="fade-right" data-aos-duration="800" -->
                    <div class="row">
                        <div class="col-md-12 pro-pic">
                            <img src="./app/static/contactos/Foto_Eliane.jpeg" alt="wrapkit"
                                 class="img-fluid rounded-circle"/>
                        </div>
                        <div class="col-md-12" style="margin-left: 5px; padding-right: 25px">
                            <div class="pt-2">
                                <h5 class="mt-4 font-weight-medium mb-0">Eliane Gabriel</h5>
                                <h6 class="subtitle-names" style="margin-top: -10px;">Estudante | LCD</h6>
                                <ul class="list-inline" style="margin-top: 0rem; margin-left: 1.5rem">
                                    <li class="list-inline-item"><a
                                            href="https://www.linkedin.com/in/eliane-gabriel-4462a02b3/"
                                            class="text-decoration-none d-block px-1"><i class="fa fa-linkedin" aria-hidden="true"></i></a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-2 mt-2 mb-2">  <!-- data-aos="fade-left" data-aos-duration="800" -->
                    <div class="row">
                        <div class="col-md-12">
                            <img src='./app/static/contactos/Maria.jpg' alt="wrapkit"
                                 class="img-fluid rounded-circle"/>
                        </div>
                        <div class="col-md-12" style="margin-left: 5px; padding-right: 25px">
                            <div class="pt-2">
                                <h5 class="mt-4 font-weight-medium mb-0 ml-0 mr-0">Mª João Lourenço</h5>
                                <h6 class="subtitle-names" style="margin-top: -10px;">Estudante | LCD</h6>
                                <ul class="list-inline" style="margin-top: 0rem; margin-left: 1.5rem">
                                    <li class="list-inline-item"><a href="https://www.linkedin.com/in/maria-louren%C3%A7o-9b3283229/"
                                                                    class="text-decoration-none d-block px-1"><i
                                            class="fa fa-linkedin" aria-hidden="true"></i></a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-2 mt-2 mb-2"> <!-- data-aos="zoom-in" data-aos-duration="800" -->
                    <div class="row">
                        <div class="col-md-12 pro-pic">
                            <img src="./app/static/contactos/Margarida_Pereira.jpg" alt="wrapkit"
                                 class="img-fluid rounded-circle"/>
                        </div>
                        <div class="col-md-12" style="margin-left: 5px; padding-right: 25px">
                            <div class="pt-2">
                                <h5 class="mt-4 font-weight-medium mb-0">Margarida Pereira</h5>
                                <h6 class="subtitle-names" style="margin-top: -10px;">Estudante | LCD</h6>
                                <ul class="list-inline" style="margin-top: 0rem; margin-left: 1.5rem">
                                    <li class="list-inline-item"><a
                                            href="https://www.linkedin.com/in/maria-margarida-pereira/"
                                            class="text-decoration-none d-block px-1"><i class="fa fa-linkedin" aria-hidden="true"></i></a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-2 mt-2 mb-2">  <!-- data-aos="fade-right" data-aos-duration="800" -->
                    <div class="row">
                        <div class="col-md-12 pro-pic">
                            <img src="./app/static/contactos/Umeima_Mahomed.jpg" alt="wrapkit"
                                 class="img-fluid rounded-circle"/>
                        </div>
                        <div class="col-md-12" style="margin-left: 5px; padding-right: 25px">
                            <div class="pt-2">
                                <h5 class="mt-4 font-weight-medium mb-0">Umeima Mahomed</h5>
                                <h6 class="subtitle-names" style="margin-top: -10px;">Estudante | LCD</h6>
                                <ul class="list-inline" style="margin-top: 0rem; margin-left: 1.5rem">
                                    <li class="list-inline-item"><a
                                            href="https://www.linkedin.com/in/umeima-mahomed-4996801b4/"
                                            class="text-decoration-none d-block px-1"><i class="fa fa-linkedin" aria-hidden="true"></i></a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <br>
    
    <div class="py-5 team">
        <div class="container">
            <div class="row justify-content-center" style="margin-bottom: -40px">
                <div class="col-md-7 text-center">
                    <h1 class="mb-1 title-contactos">Agradecimentos</h1> <!-- data-aos="fade-right" data-aos-duration="800" -->
                    <p class="subtitle-title">ISCTE & Vodafone Portugal</p> <!-- data-aos="fade-left" data-aos-duration="800" -->
                </div>
            </div>
        </div>
    </div>
    <div class="py-5 team">
        <div class="container text-center">
            <p style="text-align: justify; max-width: 800px; margin: auto;">
                Gostaríamos de agradecer especialmente ao nosso orientador, <b>Nuno Santos</b>, e à Vodafone Portugal, 
            nomeadamente, ao <b>Carlos Santos</b>, por nos terem lançado este desafio e por toda a ajuda e recomendações dadas ao longo de todo o projeto.
                <br><br>
                </p>
        </div>
    </div>
    <br>
    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-lg-12 text-center"> <!-- Adicione a classe text-center aqui -->
                    <p class="company-name" style="color: #d3d3d3;">ChatMeter © 2024</p> <!-- Adicione a regra de cor aqui -->
                </div>
            </div>
        </div>
    </footer>
""", unsafe_allow_html=True)
