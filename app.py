# Este ficheiro implementa, em Streamlit, o jogo do Semáforo 2x2.
# A aplicação tem quatro células, dois jogadores, alternância de vez,
# bloqueio das células vermelhas, nomes editáveis e deteção de vencedor.

# Permite usar anotações de tipo modernas sem problemas em versões antigas do Python.
# Por exemplo, deixa escrever `list[str]` e `tuple[int, int] | None` com mais segurança.
from __future__ import annotations

# Importa a biblioteca Streamlit, usada para construir toda a interface web.
# A convenção `as st` é o padrão da comunidade Streamlit.
import streamlit as st


# Lista com a ordem completa das cores usadas no jogo.
# A célula começa em "preto" e avança, por cliques, até "vermelho".
COLORS = ["preto", "verde", "amarelo", "vermelho"]

# Dicionário que define a transição de cada cor para a próxima cor.
# Esta é a regra principal de evolução de uma célula.
NEXT_COLOR = {
    # Se a célula está preta, o próximo clique muda para verde.
    "preto": "verde",
    # Se a célula está verde, o próximo clique muda para amarelo.
    "verde": "amarelo",
    # Se a célula está amarela, o próximo clique muda para vermelho.
    "amarelo": "vermelho",
    # Se a célula está vermelha, permanece vermelha; ela está bloqueada.
    "vermelho": "vermelho",
}

# Dicionário com nomes bonitos para apresentar as cores na interface.
# As chaves são os valores internos; os valores são os textos exibidos ao utilizador.
COLOR_LABEL = {
    # Texto apresentado para a cor preta.
    "preto": "Preto",
    # Texto apresentado para a cor verde.
    "verde": "Verde",
    # Texto apresentado para a cor amarela.
    "amarelo": "Amarelo",
    # Texto apresentado para a cor vermelha.
    "vermelho": "Vermelho",
}

# Dicionário com o estilo visual de cada cor.
# Cada cor tem fundo, cor do texto, borda e sombra própria.
COLOR_STYLE = {
    # Estilos da célula preta, que representa o estado inicial.
    "preto": {
        # Cor de preenchimento da célula.
        "bg": "#111827",
        # Cor do texto, mesmo que o texto esteja visualmente escondido.
        "fg": "#F9FAFB",
        # Cor da borda da célula.
        "border": "#030712",
        # Sombra colorida usada para dar profundidade ao botão.
        "glow": "rgba(17, 24, 39, 0.35)",
    },
    # Estilos da célula verde.
    "verde": {
        # Cor de preenchimento da célula.
        "bg": "#16A34A",
        # Cor do texto sobre o verde.
        "fg": "#FFFFFF",
        # Cor da borda da célula verde.
        "border": "#166534",
        # Sombra associada ao verde.
        "glow": "rgba(22, 163, 74, 0.35)",
    },
    # Estilos da célula amarela.
    "amarelo": {
        # Cor de preenchimento da célula.
        "bg": "#FACC15",
        # Texto escuro para garantir contraste no fundo amarelo.
        "fg": "#1F2937",
        # Cor da borda amarela.
        "border": "#CA8A04",
        # Sombra amarela.
        "glow": "rgba(250, 204, 21, 0.4)",
    },
    # Estilos da célula vermelha, que representa célula bloqueada.
    "vermelho": {
        # Cor de preenchimento da célula.
        "bg": "#DC2626",
        # Texto claro para contraste no fundo vermelho.
        "fg": "#FFFFFF",
        # Cor da borda vermelha.
        "border": "#991B1B",
        # Sombra vermelha.
        "glow": "rgba(220, 38, 38, 0.35)",
    },
}

# Lista das combinações vencedoras do tabuleiro 2x2.
# As células são numeradas internamente assim:
# 0 1
# 2 3
WINNING_LINES = [
    # Primeira linha horizontal: célula 0 com célula 1.
    (0, 1),
    # Segunda linha horizontal: célula 2 com célula 3.
    (2, 3),
    # Primeira coluna vertical: célula 0 com célula 2.
    (0, 2),
    # Segunda coluna vertical: célula 1 com célula 3.
    (1, 3),
    # Diagonal principal: célula 0 com célula 3.
    (0, 3),
    # Diagonal secundária: célula 1 com célula 2.
    (1, 2),
]


# Esta função reinicia apenas o estado do jogo.
# Mantém os nomes dos jogadores porque esses nomes estão guardados noutros campos
# do `st.session_state` e não são apagados aqui.
def reset_game() -> None:
    # Cria o tabuleiro inicial com quatro células pretas.
    st.session_state.board = ["preto"] * 4
    # Define que o Jogador 1 começa a partida.
    st.session_state.current_player = 1
    # Sincroniza o seletor da sidebar com o Jogador 1.
    st.session_state.turn_selector = 1
    # Remove qualquer vencedor anterior.
    st.session_state.winner = None
    # Remove qualquer linha vencedora anterior.
    st.session_state.winning_line = None
    # Remove a mensagem de célula bloqueada, se ela existir.
    st.session_state.blocked_message = None
    # Apaga o histórico de jogadas.
    st.session_state.moves = []


# Esta função garante que todos os valores necessários existem no `session_state`.
# O `session_state` é a memória da aplicação entre cliques e recarregamentos.
def ensure_game_state() -> None:
    # Se ainda não existe tabuleiro, significa que a app acabou de iniciar.
    if "board" not in st.session_state:
        # Nesse caso, criamos o estado inicial do jogo.
        reset_game()

    # Define um nome padrão para o Jogador 1 se o utilizador ainda não escreveu nada.
    st.session_state.setdefault("player_1_name", "Jogador 1")
    # Define um nome padrão para o Jogador 2 se o utilizador ainda não escreveu nada.
    st.session_state.setdefault("player_2_name", "Jogador 2")
    # Garante que o seletor de vez existe e aponta para o jogador atual.
    st.session_state.setdefault("turn_selector", st.session_state.current_player)
    # Garante que a mensagem de célula bloqueada existe, mesmo que vazia.
    st.session_state.setdefault("blocked_message", None)


# Esta função devolve o nome visível de um jogador.
# Se o campo estiver vazio, volta a usar "Jogador 1" ou "Jogador 2".
def player_name(player: int) -> str:
    # Monta o nome da chave no session_state: "player_1_name" ou "player_2_name".
    key = f"player_{player}_name"
    # Define o texto padrão caso o campo esteja vazio.
    fallback = f"Jogador {player}"
    # Lê o nome, remove espaços em branco extras e usa o padrão se ficar vazio.
    return st.session_state.get(key, fallback).strip() or fallback


# Esta função verifica se existe uma linha, coluna ou diagonal vencedora.
# Ela recebe o tabuleiro e devolve a dupla de índices vencedora, ou None.
def find_winning_line(board: list[str]) -> tuple[int, int] | None:
    # Percorre todas as combinações vencedoras possíveis.
    for first, second in WINNING_LINES:
        # Lê a cor da primeira célula da combinação.
        color = board[first]
        # A cor preta não conta como vitória porque o tabuleiro começa todo preto.
        # Só há vitória se as duas células tiverem a mesma cor não preta.
        if color != "preto" and color == board[second]:
            # Devolve a combinação vencedora encontrada.
            return first, second

    # Se nenhuma combinação venceu, devolve None.
    return None


# Esta função é chamada sempre que o utilizador clica numa célula.
# O parâmetro `index` indica qual célula foi clicada: 0, 1, 2 ou 3.
def play_cell(index: int) -> None:
    # Se já existe vencedor, nenhum clique deve alterar o jogo.
    if st.session_state.winner is not None:
        # Sai imediatamente da função.
        return

    # Lê a cor atual da célula clicada.
    current_color = st.session_state.board[index]

    # Se a célula está vermelha, ela está bloqueada.
    if current_color == "vermelho":
        # Mostra uma mensagem clara ao utilizador.
        st.session_state.blocked_message = (
            f"A célula {index + 1} está bloqueada. Clique noutra célula."
        )
        # Não muda cor, não regista jogada e não passa a vez.
        return

    # Se o clique foi válido, limpamos qualquer aviso antigo de célula bloqueada.
    st.session_state.blocked_message = None
    # Calcula a nova cor da célula usando a regra definida em NEXT_COLOR.
    new_color = NEXT_COLOR[current_color]
    # Atualiza a célula no tabuleiro.
    st.session_state.board[index] = new_color
    # Guarda a jogada no histórico.
    st.session_state.moves.append(
        {
            # Guarda quem fez a jogada.
            "player": st.session_state.current_player,
            # Guarda a célula em formato humano: 1, 2, 3 ou 4.
            "cell": index + 1,
            # Guarda a nova cor obtida após o clique.
            "color": new_color,
        }
    )

    # Depois da jogada, verifica se surgiu uma linha vencedora.
    winning_line = find_winning_line(st.session_state.board)

    # Se existe linha vencedora, a partida termina.
    if winning_line is not None:
        # Regista o jogador atual como vencedor.
        st.session_state.winner = st.session_state.current_player
        # Guarda a dupla de células vencedoras para destacar visualmente.
        st.session_state.winning_line = winning_line
        # Sai da função sem trocar a vez.
        return

    # Se ninguém venceu, alterna a vez entre Jogador 1 e Jogador 2.
    st.session_state.current_player = 2 if st.session_state.current_player == 1 else 1
    # Atualiza o seletor da sidebar para mostrar o novo jogador ativo.
    st.session_state.turn_selector = st.session_state.current_player


# Esta função verifica se todas as células já chegaram ao vermelho.
# Isso serve para identificar empate quando não há vencedor.
def board_is_full(board: list[str]) -> bool:
    # Devolve True apenas se todas as cores do tabuleiro forem "vermelho".
    return all(color == "vermelho" for color in board)


# Esta função desenha a barra lateral da aplicação.
# Nela ficam os nomes dos jogadores e o controlador de quem joga.
def render_sidebar() -> None:
    # Título principal da barra lateral.
    st.sidebar.header("Jogadores")
    # Campo para escrever o nome do Jogador 1.
    st.sidebar.text_input("Nome do Jogador 1", key="player_1_name")
    # Campo para escrever o nome do Jogador 2.
    st.sidebar.text_input("Nome do Jogador 2", key="player_2_name")

    # Linha visual para separar a parte dos nomes da parte da vez.
    st.sidebar.divider()
    # Subtítulo do controlador de vez.
    st.sidebar.subheader("Vez de jogar")

    # Radio button que permite escolher manualmente quem joga.
    selected_player = st.sidebar.radio(
        # Texto mostrado acima das opções.
        "Escolha o jogador ativo",
        # As opções internas são os números dos jogadores.
        options=[1, 2],
        # A chave liga o radio ao session_state.
        key="turn_selector",
        # Mostra o nome do jogador em vez de apenas 1 ou 2.
        format_func=lambda player: f"{player_name(player)}",
        # Quando o jogo acaba, o seletor fica desativado.
        disabled=st.session_state.winner is not None,
    )

    # Enquanto não houver vencedor, o seletor controla a vez atual.
    if st.session_state.winner is None:
        # Atualiza o jogador atual com base na escolha da sidebar.
        st.session_state.current_player = selected_player

    # Pequena explicação para o utilizador.
    st.sidebar.caption("O seletor permite corrigir ou escolher manualmente quem joga.")


# Esta função cria todo o CSS personalizado da aplicação.
# O CSS é necessário para termos células grandes, coloridas e sem texto visível.
def render_styles() -> None:
    # Lista onde serão guardados os estilos CSS específicos de cada célula.
    cell_styles = []

    # Percorre o tabuleiro para gerar um estilo individual para cada célula.
    for index, color in enumerate(st.session_state.board):
        # Lê o estilo correspondente à cor atual da célula.
        style = COLOR_STYLE[color]
        # Verifica se esta célula pertence à linha vencedora.
        is_winning_cell = (
            st.session_state.winning_line is not None
            and index in st.session_state.winning_line
        )
        # Define uma sombra especial se a célula faz parte da vitória.
        winner_shadow = (
            # Sombra com aro azul para destacar a linha vencedora.
            "0 0 0 5px #FFFFFF, 0 0 0 10px #2563EB, "
            f"0 18px 35px {style['glow']}"
            # Usa a sombra especial apenas nas células vencedoras.
            if is_winning_cell
            # Caso contrário, usa uma sombra normal da cor da célula.
            else f"0 18px 35px {style['glow']}"
        )

        # Acrescenta à lista o CSS específico da célula atual.
        cell_styles.append(
            f"""
            /* Estilo base do botão que representa a célula {index + 1}. */
            .st-key-cell_{index} button {{
                /* Altura responsiva: menor em ecrãs pequenos, maior em ecrãs largos. */
                min-height: clamp(125px, 18vw, 175px);
                /* O botão ocupa toda a largura da coluna. */
                width: 100%;
                /* Cantos suavemente arredondados. */
                border-radius: 10px;
                /* Borda colorida de acordo com a cor da célula. */
                border: 4px solid {style['border']} !important;
                /* Fundo totalmente preenchido pela cor atual da célula. */
                background-color: {style['bg']} !important;
                /* Camadas visuais para dar volume sem esconder a cor principal. */
                background-image:
                    radial-gradient(circle at 30% 22%, rgba(255,255,255,0.28), transparent 22%),
                    linear-gradient(145deg, rgba(255,255,255,0.14), rgba(0,0,0,0.18)) !important;
                /* Cor do texto; o texto existe por acessibilidade, mas fica invisível. */
                color: {style['fg']} !important;
                /* Sombra normal ou destaque de vitória. */
                box-shadow: {winner_shadow} !important;
                /* Mantém quebras de linha se algum texto existir. */
                white-space: pre-line;
                /* Remove altura visual do texto dentro da célula. */
                line-height: 0;
                /* Esconde visualmente qualquer texto dentro da célula. */
                font-size: 0;
                /* Peso alto, caso o texto volte a ser exibido no futuro. */
                font-weight: 900;
                /* Texto em maiúsculas, caso seja reativado no futuro. */
                text-transform: uppercase;
                /* Evita espaçamento negativo ou instável entre letras. */
                letter-spacing: 0;
                /* Animações suaves ao passar o rato e clicar. */
                transition: transform 150ms ease, box-shadow 150ms ease, filter 150ms ease;
            }}

            /* Efeito visual quando o rato passa sobre uma célula ativa. */
            .st-key-cell_{index} button:hover:enabled {{
                /* Aumenta levemente o brilho. */
                filter: brightness(1.06);
                /* Levanta ligeiramente a célula. */
                transform: translateY(-2px);
                /* Mantém a borda da mesma cor da célula. */
                border-color: {style['border']} !important;
                /* Mantém a cor do texto. */
                color: {style['fg']} !important;
            }}

            /* Efeito visual no instante do clique. */
            .st-key-cell_{index} button:active:enabled {{
                /* Dá sensação de pressão física no botão. */
                transform: translateY(1px) scale(0.99);
            }}

            /* Streamlit coloca texto dentro de parágrafos; aqui escondemos esses parágrafos. */
            .st-key-cell_{index} button p {{
                /* Remove o tamanho do texto. */
                font-size: 0;
                /* Remove altura de linha. */
                line-height: 0;
                /* Remove margem padrão. */
                margin: 0;
            }}

            /* Estilo de célula desativada, usado sobretudo quando já existe vencedor. */
            .st-key-cell_{index} button:disabled {{
                /* Mantém opacidade total para não empalidecer a cor. */
                opacity: 1;
                /* Mantém a cor do texto configurada. */
                color: {style['fg']} !important;
                /* Mantém o fundo da cor atual. */
                background-color: {style['bg']} !important;
                /* Mantém o efeito de volume mesmo quando está desativada. */
                background-image:
                    radial-gradient(circle at 30% 22%, rgba(255,255,255,0.24), transparent 22%),
                    linear-gradient(145deg, rgba(255,255,255,0.08), rgba(0,0,0,0.22)) !important;
                /* Mantém a borda correspondente à cor. */
                border-color: {style['border']} !important;
                /* Indica que já não é possível jogar após a vitória. */
                cursor: not-allowed;
            }}
            """
        )

    # Injeta o CSS completo na página.
    st.markdown(
        f"""
        <style>
        /* Variáveis gerais de cor usadas no layout. */
        :root {{
            --page-bg: #F7FAFC;
            --ink: #172033;
            --muted: #64748B;
            --panel: #FFFFFF;
            --line: #D9E2EC;
        }}

        /* Limita a largura do conteúdo principal para a app ficar centrada. */
        .main .block-container {{
            max-width: 820px;
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }}

        /* Caixa superior com título e explicação curta do jogo. */
        .game-hero {{
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 1.2rem 1.35rem;
            background: var(--panel);
            box-shadow: 0 16px 35px rgba(15, 23, 42, 0.08);
            margin-bottom: 1rem;
        }}

        /* Pequena etiqueta acima do título. */
        .game-kicker {{
            color: #DC2626;
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.15rem;
        }}

        /* Título principal da aplicação. */
        .game-title {{
            color: var(--ink);
            font-size: clamp(2rem, 5vw, 3rem);
            font-weight: 950;
            line-height: 1;
            margin: 0;
            letter-spacing: 0;
        }}

        /* Texto explicativo abaixo do título. */
        .game-copy {{
            color: var(--muted);
            font-size: 1rem;
            margin: 0.75rem 0 0;
        }}

        /* Cartão que mostra a vez do jogador. */
        .status-card {{
            border: 1px solid var(--line);
            border-left: 7px solid #2563EB;
            border-radius: 12px;
            padding: 0.85rem 1rem;
            background: #FFFFFF;
            margin: 0.85rem 0 1rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        }}

        /* Nome do jogador ativo dentro do cartão de estado. */
        .status-card strong {{
            color: var(--ink);
            font-size: 1.1rem;
        }}

        /* Texto secundário dentro do cartão de estado. */
        .status-card span {{
            color: var(--muted);
        }}

        /* Área que envolve o tabuleiro 2x2. */
        .st-key-board {{
            padding: 0.55rem;
            border-radius: 16px;
            background: #E2E8F0;
            border: 1px solid #CBD5E1;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
            margin: 0.5rem auto 0;
            max-width: 560px;
        }}

        /* Espaçamento interno das colunas do tabuleiro. */
        .st-key-board [data-testid="column"] {{
            padding: 0.25rem;
        }}

        /* Estilo específico do botão Novo jogo. */
        .st-key-reset_button button {{
            min-height: 44px;
            border-radius: 8px;
            font-weight: 800;
            border: 1px solid #CBD5E1;
        }}

        /* Legenda horizontal das quatro cores. */
        .legend {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.45rem;
            margin: 0.75rem 0 0.25rem;
        }}

        /* Cada item da legenda. */
        .legend-item {{
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.55rem;
            background: #FFFFFF;
            color: var(--ink);
            font-size: 0.82rem;
            font-weight: 800;
            text-align: center;
        }}

        /* Pequeno círculo colorido dentro da legenda. */
        .legend-dot {{
            display: inline-block;
            width: 0.85rem;
            height: 0.85rem;
            border-radius: 999px;
            margin-right: 0.25rem;
            vertical-align: -0.1rem;
            border: 1px solid rgba(15, 23, 42, 0.2);
        }}

        /* Junta ao CSS geral os estilos individuais das quatro células. */
        {"".join(cell_styles)}
        </style>
        """,
        # Permite que o HTML/CSS seja interpretado pelo Streamlit.
        unsafe_allow_html=True,
    )


# Esta função desenha uma célula individual do tabuleiro.
# A célula é um botão Streamlit estilizado por CSS.
def render_cell(index: int) -> None:
    # Lê a cor atual da célula.
    color = st.session_state.board[index]
    # A célula só fica realmente desativada depois de haver vencedor.
    # Células vermelhas continuam clicáveis para mostrar a mensagem de bloqueio.
    is_locked = st.session_state.winner is not None

    # Cria o botão que representa a célula.
    st.button(
        # O texto é um espaço para o botão existir, mas o CSS esconde visualmente.
        " ",
        # Chave única da célula no Streamlit.
        key=f"cell_{index}",
        # Desativa todos os botões quando o jogo já terminou.
        disabled=is_locked,
        # Faz o botão ocupar toda a largura disponível da coluna.
        use_container_width=True,
        # Função chamada quando o botão é clicado.
        on_click=play_cell,
        # Argumento passado para play_cell, indicando qual célula foi clicada.
        args=(index,),
    )


# Define configurações da página Streamlit.
# Isto deve ser feito antes de desenhar a interface.
st.set_page_config(
    # Título da aba do navegador.
    page_title="Jogo do Semáforo 2x2",
    # Ícone da aba do navegador.
    page_icon="🚦",
    # Layout centrado para deixar o tabuleiro mais organizado.
    layout="centered",
)

# Garante que todos os valores do jogo existem no session_state.
ensure_game_state()
# Renderiza a barra lateral com nomes dos jogadores e seletor de vez.
render_sidebar()
# Injeta os estilos CSS conforme o estado atual das células.
render_styles()

# Renderiza o cabeçalho visual da aplicação.
st.markdown(
    """
    <!-- Bloco superior da aplicação. -->
    <div class="game-hero">
        <!-- Etiqueta pequena acima do título. 
        <div class="game-kicker">Jogo combinatório</div> -->
        <!-- Título principal. -->
        <h1 class="game-title">Semáforo 2x2</h1>
        <!-- Explicação curta das regras de mudança de cor. -->
        <p class="game-copy">
            Clique numa célula para avançar a cor: preto → verde → amarelo → vermelho.
            Ao chegar ao vermelho, a célula fica bloqueada.
        </p>
    </div>
    """,
    # Permite que o HTML acima seja renderizado.
    unsafe_allow_html=True,
)

# Se já existe vencedor, mostra uma caixa de sucesso.
if st.session_state.winner is not None:
    # Messagebox de vitória.
    st.success(
        # Nome do vencedor.
        f"{player_name(st.session_state.winner)} venceu! "
        # Informação complementar sobre o destaque visual.
        "A linha vencedora está destacada no tabuleiro."
    )
# Se não há vencedor, mas todas as células estão vermelhas, há empate.
elif board_is_full(st.session_state.board):
    # Messagebox de empate.
    st.warning("Empate. Todas as células estão bloqueadas.")
# Se o jogo continua, mostra o cartão de vez.
else:
    # Cartão HTML com o nome do jogador ativo.
    st.markdown(
        f"""
        <div class="status-card">
            <strong>Vez de {player_name(st.session_state.current_player)}</strong><br>
            <span>Vence quem formar duas células não pretas da mesma cor numa linha, coluna ou diagonal.</span>
        </div>
        """,
        # Permite renderizar o HTML do cartão.
        unsafe_allow_html=True,
    )

# Se o jogador clicou numa célula vermelha, mostra aviso de bloqueio.
if st.session_state.blocked_message:
    # Messagebox informando qual célula está bloqueada.
    st.warning(st.session_state.blocked_message)

# Renderiza a legenda das quatro cores.
st.markdown(
    """
    <!-- Legenda das cores do jogo. -->
    <div class="legend">
        <!-- Estado inicial. -->
        <div class="legend-item"><span class="legend-dot" style="background:#111827"></span>Preto</div>
        <!-- Primeiro avanço. -->
        <div class="legend-item"><span class="legend-dot" style="background:#16A34A"></span>Verde</div>
        <!-- Segundo avanço. -->
        <div class="legend-item"><span class="legend-dot" style="background:#FACC15"></span>Amarelo</div>
        <!-- Estado final e bloqueado. -->
        <div class="legend-item"><span class="legend-dot" style="background:#DC2626"></span>Vermelho</div>
    </div>
    """,
    # Permite renderizar HTML.
    unsafe_allow_html=True,
)

# Cria um container com chave "board".
# Essa chave permite aplicar CSS especificamente ao tabuleiro.
with st.container(key="board"):
    # Cria a primeira linha do tabuleiro, com duas colunas.
    top_left, top_right = st.columns(2)
    # Cria a segunda linha do tabuleiro, também com duas colunas.
    bottom_left, bottom_right = st.columns(2)

    # Primeira célula, posição superior esquerda.
    with top_left:
        # Renderiza a célula de índice 0.
        render_cell(0)
    # Segunda célula, posição superior direita.
    with top_right:
        # Renderiza a célula de índice 1.
        render_cell(1)
    # Terceira célula, posição inferior esquerda.
    with bottom_left:
        # Renderiza a célula de índice 2.
        render_cell(2)
    # Quarta célula, posição inferior direita.
    with bottom_right:
        # Renderiza a célula de índice 3.
        render_cell(3)

# Cria duas colunas abaixo do tabuleiro.
# A primeira recebe o botão Novo jogo; a segunda recebe uma legenda curta.
left, right = st.columns([1, 2])

# Coluna esquerda: botão de reinício.
with left:
    # Botão que chama reset_game para recomeçar a partida.
    st.button(
        # Texto visível no botão.
        "Novo jogo",
        # Chave única do botão.
        key="reset_button",
        # Ocupa toda a largura da coluna.
        use_container_width=True,
        # Função chamada quando se clica no botão.
        on_click=reset_game,
    )

# Coluna direita: nota explicativa.
with right:
    # Texto pequeno sobre o significado das células vermelhas.
    st.caption("As células vermelhas ficam bloqueadas e não podem ser alteradas.")

# Se há jogadas no histórico, mostra um painel expansível.
if st.session_state.moves:
    # Cria uma área que pode abrir/fechar.
    with st.expander("Histórico de jogadas"):
        # Percorre as jogadas guardadas, começando a numeração em 1.
        for number, move in enumerate(st.session_state.moves, start=1):
            # Mostra uma linha textual para cada jogada.
            st.write(
                # Número da jogada e nome do jogador.
                f"{number}. {player_name(move['player'])} mudou a célula "
                # Número da célula e cor obtida.
                f"{move['cell']} para {move['color']}."
            )
