import os
import random
import sqlite3
from PIL import Image
import streamlit as st

# Caminho para salvar as fotos dos jogadores
PHOTO_FOLDER = "fotos_jogadores"
DEFAULT_PHOTO = "default.jpg"  # Caminho da foto padrão
DB_PATH = "jogadores.db"

# Verificar se a foto padrão existe
if not os.path.exists(DEFAULT_PHOTO):
    st.error("A imagem padrão 'default.jpg' não foi encontrada. Verifique o diretório.")
    st.stop()

# Criar a pasta de fotos, se não existir
if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)

def criar_tabela():
    """Cria ou atualiza a tabela de jogadores."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            qualidade INTEGER NOT NULL CHECK(qualidade IN (1, 2, 3)),
            goleiro BOOLEAN NOT NULL DEFAULT 0,
            foto TEXT
        )
    """)
    conn.commit()
    conn.close()

def verificar_ou_adicionar_coluna_foto():
    """Verifica se a coluna 'foto' existe, e a adiciona se necessário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE jogadores ADD COLUMN foto TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # A coluna já existe
    conn.close()

def redimensionar_imagem(caminho_imagem, largura=100, altura=100):
    """Redimensiona uma imagem para o tamanho especificado."""
    try:
        with Image.open(caminho_imagem) as img:
            img = img.resize((largura, altura))
            return img
    except Exception as e:
        st.error(f"Erro ao carregar a imagem: {e}")
        return None

def inserir_jogador(nome, qualidade, goleiro, foto=None):
    """Insere um jogador no banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jogadores (nome, qualidade, goleiro, foto)
        VALUES (?, ?, ?, ?)
    """, (nome, qualidade, goleiro, foto))
    conn.commit()
    conn.close()

def atualizar_jogador(jogador_id, nome, qualidade, goleiro, foto=None):
    """Atualiza os dados de um jogador no banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE jogadores
        SET nome = ?, qualidade = ?, goleiro = ?, foto = ?
        WHERE id = ?
    """, (nome, qualidade, goleiro, foto, jogador_id))
    conn.commit()
    conn.close()

def listar_jogadores():
    """Retorna a lista de jogadores do banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, qualidade, goleiro, foto FROM jogadores")
    jogadores = cursor.fetchall()
    conn.close()
    return jogadores

def deletar_jogador(jogador_id):
    """Deleta um jogador pelo ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jogadores WHERE id = ?", (jogador_id,))
    conn.commit()
    conn.close()

# Inicializa o banco de dados
criar_tabela()
verificar_ou_adicionar_coluna_foto()

# Configura o título do aplicativo
st.title("Sorteio de Times de Futsal ⚽")
st.write("Cadastre os jogadores e monte seus times.")

# Aba de navegação
aba = st.sidebar.radio("Menu", ["Cadastro de Jogadores", "Sorteio de Times"])

if aba == "Cadastro de Jogadores":
    st.header("Cadastro de Jogadores")

    # Variável para armazenar jogador a ser editado
    if "jogador_edicao" not in st.session_state:
        st.session_state.jogador_edicao = None

    # Formulário de cadastro ou edição
    with st.form("cadastro_form"):
        nome = st.text_input("Nome do Jogador", value=st.session_state.jogador_edicao["nome"] if st.session_state.jogador_edicao else "")
        qualidade = st.selectbox("Nível do Jogador", [1, 2, 3], index=(st.session_state.jogador_edicao["qualidade"] - 1) if st.session_state.jogador_edicao else 0)
        goleiro = st.checkbox("Goleiro", value=st.session_state.jogador_edicao["goleiro"] if st.session_state.jogador_edicao else False)
        foto = st.file_uploader("Foto do Jogador (opcional)", type=["jpg", "png", "jpeg"])

        submit = st.form_submit_button("Salvar")

        if submit:
            if nome.strip():
                # Salvar a foto se ela foi enviada
                foto_caminho = None
                if foto:
                    foto_nome = f"{nome.strip()}_{foto.name}"
                    foto_caminho = os.path.join(PHOTO_FOLDER, foto_nome)
                    with open(foto_caminho, "wb") as f:
                        f.write(foto.getbuffer())
                elif st.session_state.jogador_edicao:
                    # Manter a foto existente se não for enviada uma nova
                    foto_caminho = st.session_state.jogador_edicao["foto"]
                else:
                    # Usar a foto padrão
                    foto_caminho = DEFAULT_PHOTO

                if st.session_state.jogador_edicao:
                    # Atualizar jogador existente
                    atualizar_jogador(st.session_state.jogador_edicao["id"], nome.strip(), qualidade, goleiro, foto_caminho)
                    st.success(f"Jogador {nome} atualizado com sucesso!")
                    st.session_state.jogador_edicao = None
                else:
                    # Inserir novo jogador
                    inserir_jogador(nome.strip(), qualidade, goleiro, foto_caminho)
                    st.success(f"Jogador {nome} cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("O nome do jogador não pode estar vazio.")

    # Exibir jogadores cadastrados
    st.subheader("Jogadores Cadastrados")
    jogadores = listar_jogadores()
    for jogador in jogadores:
        id_, nome, qualidade, goleiro, foto = jogador
        col1, col2, col3 = st.columns([1, 3, 2])

        # Exibir a foto redimensionada
        with col1:
            imagem = redimensionar_imagem(foto if foto and os.path.exists(foto) else DEFAULT_PHOTO)
            if imagem:
                st.image(imagem)
            else:
                if imagem.mode != "RGBA":
                    imagem = imagem.convert("RGBA")
                st.image(DEFAULT_PHOTO, use_container_width=True)

        with col2:
            st.write(f"**{nome}** (Nível {qualidade}, {'Goleiro' if goleiro else 'Jogador de linha'})")

        with col3:
            if st.button("Editar", key=f"edit_{id_}"):
                st.session_state.jogador_edicao = {
                    "id": id_,
                    "nome": nome,
                    "qualidade": qualidade,
                    "goleiro": goleiro,
                    "foto": foto
                }
                st.rerun()
            if st.button("Deletar", key=f"delete_{id_}"):
                deletar_jogador(id_)
                st.rerun()

elif aba == "Sorteio de Times":
    st.header("Sorteio de Times")

    # Seleção de jogadores para o sorteio
    st.subheader("Selecione os Jogadores")
    jogadores = listar_jogadores()

    # Ordenação dos jogadores conforme a regra definida
    goleiros = sorted([j for j in jogadores if j[3]], key=lambda x: x[1])
    nivel_1 = sorted([j for j in jogadores if j[2] == 1 and not j[3]], key=lambda x: x[1])
    nivel_2 = sorted([j for j in jogadores if j[2] == 2 and not j[3]], key=lambda x: x[1])
    nivel_3 = sorted([j for j in jogadores if j[2] == 3 and not j[3]], key=lambda x: x[1])

    # Inicializa o estado dos checkboxes
    if "checkbox_states" not in st.session_state:
        st.session_state.checkbox_states = {j[0]: False for j in jogadores}

    # Botão "Selecionar Todos"
    if st.button("Selecionar Todos"):
        todos_marcados = all(st.session_state.checkbox_states.values())
        for jogador in jogadores:
            st.session_state.checkbox_states[jogador[0]] = not todos_marcados

    # Função para exibir jogadores por seção
    jogadores_selecionados = []

    def exibir_secao(titulo, jogadores):
        with st.expander(titulo, expanded=True):
            for jogador in jogadores:
                id_, nome, qualidade, goleiro, foto = jogador
                col1, col2 = st.columns([1, 5])

                with col1:
                    # Exibir a foto redimensionada do jogador ou a foto padrão
                    imagem = redimensionar_imagem(foto if foto and os.path.exists(foto) else DEFAULT_PHOTO)
                    if imagem:
                        st.image(imagem)
                    else:
                        if imagem.mode != "RGBA":
                            imagem = imagem.convert("RGBA")
                        st.image(DEFAULT_PHOTO, use_container_width=True)

                with col2:
                    # Checkbox para seleção de jogadores
                    if st.checkbox(
                        f"{nome} (Nível {qualidade}, {'Goleiro' if goleiro else 'Jogador de linha'})",
                        key=f"select_{id_}",
                        value=st.session_state.checkbox_states[id_]
                    ):
                        st.session_state.checkbox_states[id_] = True
                        jogadores_selecionados.append({"nome": nome, "qualidade": qualidade, "goleiro": goleiro, "foto": foto})
                    else:
                        st.session_state.checkbox_states[id_] = False

    # Exibir os jogadores em seções
    exibir_secao("Goleiros", goleiros)
    exibir_secao("Nível 1", nivel_1)
    exibir_secao("Nível 2", nivel_2)
    exibir_secao("Nível 3", nivel_3)

    # Exibir o número de jogadores selecionados
    st.sidebar.subheader("Jogadores Selecionados")
    st.sidebar.write(f"Total: {len(jogadores_selecionados)} jogador(es) selecionado(s).")

    # Seleção do número de times
    num_times = st.selectbox("Quantos times você deseja?", options=[2, 3, 4, 5, 6], index=2)

    # Botão para sortear os times
    if st.button("Sortear Times"):
        if not jogadores_selecionados:
            st.warning("Nenhum jogador foi selecionado!")
        else:
            num_jogadores_selecionados = len(jogadores_selecionados)
            jogadores_necessarios = num_times * 5

            # Verificar o número máximo de times possíveis com os jogadores selecionados e fictícios
            max_times_possiveis = (num_jogadores_selecionados + 4) // 5  # Inclui jogadores fictícios

            # Caso haja jogadores excedentes
            if num_jogadores_selecionados > jogadores_necessarios:
                excedente = num_jogadores_selecionados - jogadores_necessarios
                times_adicionais = (excedente + 4) // 5  # Arredonda para cima
                st.warning(
                    f"Jogadores selecionados excedem a capacidade dos times! "
                    f"Adicione mais {times_adicionais} time(s) para acomodar todos os jogadores."
                )
                st.stop()
            elif num_times > max_times_possiveis:
                st.error(
                    f"Faltam jogadores para completar os times! O número máximo de times possíveis para "
                    f"{num_jogadores_selecionados} jogadores, considerando jogadores fictícios, é {max_times_possiveis}. "
                    "Por favor, ajuste o número de times."
                )
                st.stop()

            # Caso faltem jogadores para completar os times
            elif num_jogadores_selecionados < jogadores_necessarios:
                faltando = jogadores_necessarios - num_jogadores_selecionados
                if faltando <= 4:
                    st.info(f"Faltam {faltando} jogador(es) para completar os times. Jogadores fictícios ('FICTÍCIO') serão adicionados.")
                else:
                    times_adicionais = (faltando + 4) // 5
                    st.warning(
                        f"Faltam jogadores para completar os times! "
                        f"Adicione mais {times_adicionais} time(s) para acomodar todos os jogadores."
                    )
                    st.stop()

            # Calcular o número de jogadores fictícios necessários para completar os times
            faltando = (num_times * 5) - len(jogadores_selecionados)

            # Adicionar jogadores fictícios, se necessário
            jogadores_ficticios = [{"nome": f"COMPLETE COM ALGUÉM {i+1}", "qualidade": 3, "goleiro": False, "foto": None} for i in range(faltando)]
            jogadores_selecionados.extend(jogadores_ficticios)

            # Inicializar times
            times = [[] for _ in range(num_times)]
            jogadores_usados = set()

            # Separar jogadores por categorias
            goleiros = [j for j in jogadores_selecionados if j["goleiro"]]
            nivel_1 = [j for j in jogadores_selecionados if j["qualidade"] == 1 and not j["goleiro"]]
            nivel_2 = [j for j in jogadores_selecionados if j["qualidade"] == 2 and not j["goleiro"]]
            nivel_3 = [j for j in jogadores_selecionados if j["qualidade"] == 3 and not j["goleiro"]]

            # Preencher os times com goleiros (priorizando reais e distribuindo fictícios apenas quando necessário)
            random.shuffle(goleiros)
            for i, time in enumerate(times):
                if goleiros:
                    time.append(goleiros.pop(0))
                    jogadores_usados.add(time[-1]["nome"])
                else:
                    # Garantir que apenas fictícios já adicionados sejam usados como goleiros, se necessário
                    for jogador in jogadores_ficticios:
                        if jogador["nome"] not in jogadores_usados:
                            jogador["goleiro"] = True
                            time.append(jogador)
                            jogadores_usados.add(jogador["nome"])
                            break

            # Garantir pelo menos 1 jogador de nível 1 ou substituto de nível 2 por time
            for time in times:
                if len(time) < 2:  # Verifica se o time já tem um jogador de nível 1/substituto
                    if nivel_1:
                        jogador = nivel_1.pop(0)
                        time.append(jogador)
                        jogadores_usados.add(jogador["nome"])
                    elif nivel_2:
                        jogador = nivel_2.pop(0)
                        time.append(jogador)
                        jogadores_usados.add(jogador["nome"])

            # Função para distribuir jogadores de um nível
            def distribuir_jogadores_por_nivel(jogadores, times):
                random.shuffle(jogadores)
                for jogador in jogadores:
                    if jogador["nome"] in jogadores_usados:
                        continue
                    for time in sorted(times, key=lambda t: (len(t), sum(j["qualidade"] for j in t))):
                        if len(time) < 5:  # Substituído 't' por 'time'
                            time.append(jogador)
                            jogadores_usados.add(jogador["nome"])
                            break

            # Distribuir jogadores de nível 3 (incluindo fictícios)
            distribuir_jogadores_por_nivel(nivel_3, times)

            # Completar os times com jogadores de nível 2
            distribuir_jogadores_por_nivel(nivel_2, times)

            # Preencher os times incompletos com jogadores fictícios
            for time in times:
                while len(time) < 5:
                    for jogador in jogadores_ficticios:
                        if jogador["nome"] not in jogadores_usados:
                            time.append(jogador)
                            jogadores_usados.add(jogador["nome"])
                            break

            # Exibir os times com fotos em uma quadra de futsal
            st.header("Visualização dos Times na Quadra")
            from PIL import Image, ImageDraw, ImageFont

            # Configurações de tamanho da quadra e posições dos jogadores
            QUADRA_LARGURA = 800
            QUADRA_ALTURA = 1200

            formacao = {
                "goleiro": (QUADRA_LARGURA // 2, 100),
                "fixo": (QUADRA_LARGURA // 2, 300),
                "ala_esq": (QUADRA_LARGURA // 4, 500),
                "ala_dir": (3 * QUADRA_LARGURA // 4, 500),
                "pivo": (QUADRA_LARGURA // 2, 700),
            }

            # Carregar a imagem da quadra
            quadra_base = Image.open("quadra_futsal.jpg")
            quadra_base = quadra_base.resize((QUADRA_LARGURA, QUADRA_ALTURA))

            if quadra_base.mode != "RGBA":
                quadra_base = quadra_base.convert("RGBA")

            for idx, time in enumerate(times):
                quadra = quadra_base.copy()
                draw = ImageDraw.Draw(quadra)

                # Fonte para os nomes
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except IOError:
                    font = ImageFont.load_default()

                # Adicionar os jogadores na formação
                posicoes = list(formacao.values())
                for jogador, posicao in zip(time, posicoes):
                    x, y = posicao
                    nome = jogador["nome"]

                    # Desenhar a foto do jogador
                    if jogador["foto"] and os.path.exists(jogador["foto"]):
                        foto = Image.open(jogador["foto"])
                    else:
                        foto = Image.open(DEFAULT_PHOTO)

                    foto = foto.resize((100, 100))
                    if foto.mode != "RGBA":
                        foto = foto.convert("RGBA")

                    quadra.paste(foto, (x - 50, y - 50), mask=foto)

                    # Adicionar o nome abaixo da foto
                    draw.text((x, y + 60), nome, fill="white", font=font, anchor="mm")

                # Exibir a quadra
                st.image(quadra, caption=f"Time {idx + 1}", use_container_width=True)
                from urllib.parse import quote

                def gerar_link_whatsapp(times):
                    """Gera um link de compartilhamento para WhatsApp com a composição dos times."""
                    mensagem = "⚽ *Times Sorteados* ⚽\n\n"
                    for idx, time in enumerate(times, start=1):
                        mensagem += f"*Time {idx}:*\n"
                        for jogador in time:
                            mensagem += f"- {jogador['nome']} {'(Goleiro)' if jogador['goleiro'] else ''}\n"
                        mensagem += "\n"
                    link = f"https://api.whatsapp.com/send?text={quote(mensagem)}"
                    return link
                
                # Gerar link para compartilhar os times no WhatsApp
                link_whatsapp = gerar_link_whatsapp(times)
                st.markdown(
                    f"[📤 Compartilhar Times no WhatsApp]({link_whatsapp})",
                    unsafe_allow_html=True,
                )
