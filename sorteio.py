import random
import streamlit as st

# Configura o título do aplicativo
st.title("Sorteio de Times de Futsal ⚽")
st.write("Adicione os jogadores e clique no botão para formar os times.")

# Seção para entrada de múltiplos jogadores
st.header("Adicionar Jogadores")

# Botão para esconder/mostrar a área de adicionar jogadores
adicionar_jogadores_expander = st.expander("Adicionar Jogadores", expanded=True)

with adicionar_jogadores_expander:
    # Caixa de texto para adicionar vários jogadores de uma vez (sem necessidade de qualidade neste momento)
    jogadores_texto = st.text_area(
        "Cole a lista de jogadores (formato: Nome)",
        height=200,
        help="Exemplo: João\nPedro\nCarlos"
    )

    # Botão para processar a entrada de jogadores
    adicionar_jogadores = st.button("Adicionar Jogadores")

    # Lista global de jogadores
    if "jogadores" not in st.session_state:
        st.session_state.jogadores = []

    # Limpar jogadores se nova lista for enviada
    if adicionar_jogadores and jogadores_texto:
        st.session_state.jogadores.clear()  # Limpa os jogadores antes de adicionar os novos
        jogadores_listados = jogadores_texto.split("\n")
        for jogador in jogadores_listados:
            nome = jogador.strip()
            if nome:  # Verifica se o nome não está vazio
                st.session_state.jogadores.append({"nome": nome, "qualidade": None, "goleiro": False})

# Seção para editar jogadores e atribuir qualidade
st.subheader("Atribuir Qualidade e Goleiro")

# Botão para esconder/mostrar a área de atribuir qualidade e goleiro
atribuir_qualidade_expander = st.expander("Atribuir Qualidade e Goleiro", expanded=True)

with atribuir_qualidade_expander:
    for idx, jogador in enumerate(st.session_state.jogadores):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            nome_editado = st.text_input(f"Nome {idx+1}", value=jogador["nome"], key=f"nome_{idx}")
        with col2:
            if jogador["qualidade"] is None:
                qualidade_editada = st.selectbox(f"Qualidade", options=[1, 2, 3], index=1, key=f"qualidade_{idx}")
            else:
                qualidade_editada = st.selectbox(f"Qualidade", options=[1, 2, 3], index=jogador["qualidade"]-1, key=f"qualidade_{idx}")
        with col3:
            goleiro_editado = st.checkbox(f"Goleiro", value=jogador["goleiro"], key=f"goleiro_{idx}")

        # Atualiza os dados do jogador na lista
        if nome_editado != jogador["nome"] or qualidade_editada != jogador["qualidade"] or goleiro_editado != jogador["goleiro"]:
            st.session_state.jogadores[idx] = {"nome": nome_editado, "qualidade": qualidade_editada, "goleiro": goleiro_editado}

# Botão para limpar a lista de jogadores
limpar_lista = st.button("Limpar Lista de Jogadores")
if limpar_lista:
    st.session_state.jogadores.clear()
    st.success("Lista de jogadores limpa.")

# Alteração do slider para lista suspensa para selecionar a quantidade de times
num_times = st.selectbox("Quantos times você deseja?", options=[2, 3, 4, 5, 6], index=2)

# Botão para sortear os times
if st.button("Sortear Times"):
    jogadores = st.session_state.jogadores

    # Verifica se há jogadores suficientes
    total_jogadores_necessarios = num_times * 5
    if len(jogadores) < total_jogadores_necessarios:
        st.warning(f"Faltam jogadores! Serão adicionados jogadores fictícios ('FALTOU') para completar {total_jogadores_necessarios} jogadores.")
        jogadores_faltantes = total_jogadores_necessarios - len(jogadores)
        for i in range(jogadores_faltantes):
            jogadores.append({"nome": f"FALTOU-{i+1}", "qualidade": 3, "goleiro": False})

    # Separa goleiros e jogadores de linha
    goleiros = [j for j in jogadores if j["goleiro"]]
    linha = [j for j in jogadores if not j["goleiro"]]

    # Garante um goleiro por time (se possível)
    times = [[] for _ in range(num_times)]
    for i in range(num_times):
        if goleiros:
            times[i].append(goleiros.pop(0))

    # Preenche os times restantes com jogadores de linha
    jogadores_restantes = goleiros + linha
    jogadores_restantes.sort(key=lambda x: x["qualidade"], reverse=True)

    # Distribui jogadores para balancear qualidade
    soma_times = [sum(j["qualidade"] for j in time) for time in times]
    for jogador in jogadores_restantes:
        menor_time = soma_times.index(min(soma_times))
        times[menor_time].append(jogador)
        soma_times[menor_time] += jogador["qualidade"]

    # Garante que todos os times tenham 5 jogadores
    for i, time in enumerate(times):
        while len(time) < 5:
            time.append({"nome": "FALTOU", "qualidade": 3, "goleiro": False})

    # Exibe os times
    for i, time in enumerate(times):
        st.subheader(f"Time {i+1}")
        for jogador in time:
            st.write(f"{jogador['nome']} {'[Goleiro]' if jogador['goleiro'] else ''}")
