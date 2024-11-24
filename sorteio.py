import random
import streamlit as st

# Configura o título do aplicativo
st.title("Sorteio de Times de Futsal ⚽")
st.write("Adicione os jogadores e clique no botão para formar os times.")

# Seção para entrada de múltiplos jogadores
st.header("Adicionar Jogadores")

adicionar_jogadores_expander = st.expander("Adicionar Jogadores", expanded=True)

with adicionar_jogadores_expander:
    jogadores_texto = st.text_area(
        "Cole a lista de jogadores (formato: Nome)",
        height=200,
        help="Exemplo: João\nPedro\nCarlos"
    )

    adicionar_jogadores = st.button("Adicionar Jogadores")

    if "jogadores" not in st.session_state:
        st.session_state.jogadores = []

    if adicionar_jogadores and jogadores_texto:
        st.session_state.jogadores.clear()
        jogadores_listados = jogadores_texto.split("\n")
        for jogador in jogadores_listados:
            nome = jogador.strip()
            if nome:  # Evitar nomes vazios
                st.session_state.jogadores.append({"nome": nome, "qualidade": None, "goleiro": False})
        st.success(f"{len(st.session_state.jogadores)} jogadores foram adicionados à lista!")

# Exibir o número total de jogadores na lista
st.write(f"Total de jogadores na lista: {len(st.session_state.jogadores)}")

# Seção para editar jogadores e atribuir qualidade
st.subheader("Atribuir Qualidade e Goleiro")
atribuir_qualidade_expander = st.expander("Atribuir Qualidade e Goleiro", expanded=True)

with atribuir_qualidade_expander:
    for idx, jogador in enumerate(st.session_state.jogadores):
        # Criação de uma área visual para cada jogador
        with st.container():
            st.markdown("---")  # Linha divisória
            st.markdown(f"### Jogador {idx + 1}")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                nome_editado = st.text_input(f"Nome", value=jogador["nome"], key=f"nome_{idx}")
            with col2:
                qualidade_editada = st.selectbox(
                    f"Qualidade",
                    options=[1, 2, 3],
                    index=(jogador["qualidade"] or 2)-1,
                    key=f"qualidade_{idx}"
                )
            with col3:
                goleiro_editado = st.checkbox(f"Goleiro", value=jogador["goleiro"], key=f"goleiro_{idx}")

            # Atualiza o estado do jogador
            st.session_state.jogadores[idx] = {
                "nome": nome_editado,
                "qualidade": qualidade_editada,
                "goleiro": goleiro_editado
            }
# Botão para limpar lista de jogadores
if st.button("Limpar Lista de Jogadores"):
    st.session_state.jogadores.clear()  # Limpa a lista de jogadores
    # Reseta todos os estados associados aos inputs de qualidade e goleiro
    for key in list(st.session_state.keys()):
        if key.startswith("nome_") or key.startswith("qualidade_") or key.startswith("goleiro_"):
            del st.session_state[key]
    st.success("Lista de jogadores e configurações limpas.")

# Seleção do número de times
num_times = st.selectbox("Quantos times você deseja?", options=[2, 3, 4, 5, 6], index=2)

# Botão para sortear os times
if st.button("Sortear Times"):
    jogadores = st.session_state.jogadores.copy()  # Faz uma cópia para evitar alterações diretas
    times = [[] for _ in range(num_times)]

    # Separar jogadores por características
    goleiros = [j for j in jogadores if j["goleiro"]]
    nivel_1 = [j for j in jogadores if j["qualidade"] == 1 and not j["goleiro"]]
    nivel_2 = [j for j in jogadores if j["qualidade"] == 2 and not j["goleiro"]]
    nivel_3 = [j for j in jogadores if j["qualidade"] == 3 and not j["goleiro"]]

    # Distribuir goleiros: 1 por time, se possível
    for i in range(num_times):
        if goleiros:
            times[i].append(goleiros.pop(0))

    # Distribuir jogadores de nível 1
    for i in range(num_times):
        if nivel_1:
            times[i].append(nivel_1.pop(0))

    # Distribuir jogadores de nível 3
    for i in range(num_times):
        if nivel_3:
            times[i].append(nivel_3.pop(0))

    # Distribuir jogadores restantes
    jogadores_restantes = nivel_1 + nivel_2 + nivel_3  # Todos os jogadores que sobraram
    jogadores_restantes.sort(key=lambda x: x["qualidade"], reverse=True)  # Priorizar maiores qualidades

    for jogador in jogadores_restantes[:]:  # Trabalhar com cópia da lista
        menor_time = min(times, key=lambda t: sum(j["qualidade"] for j in t))
        menor_time.append(jogador)
        jogadores_restantes.remove(jogador)

    # Adicionar jogadores fictícios para completar os times com menos de 5 jogadores
    for time in times:
        while len(time) < 5:
            time.append({"nome": "FALTOU", "qualidade": 3, "goleiro": False})

    # Exibir os times e total de qualidade
    for i, time in enumerate(times):
        total_qualidade = sum(j["qualidade"] for j in time)
        st.subheader(f"Time {i+1} (Total de Nível: {total_qualidade})")
        for jogador in time:
            st.write(f"{jogador['nome']} {'[Goleiro]' if jogador['goleiro'] else ''}")
