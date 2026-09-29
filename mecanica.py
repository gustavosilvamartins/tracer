# Módulo de mecânica do Tracer.
# Código adaptado de sugestão gerada com o Claude (Anthropic), acessado em 28/09/2026.
# Tabuleiros gerados e verificados (solução única) com auxílio do Claude, na mesma data.


def obter_tabuleiros():
    """
    Devolve a lista com os 10 níveis do jogo, do mais fácil ao mais difícil.
    Cada célula é uma tupla (linha, coluna), começando em (0, 0) no canto superior esquerdo.
    "numeros": célula -> número de passagem (a linha começa no 1 e termina no maior)
    "paredes": pares de células vizinhas que a linha não pode atravessar
    list -> list
    """
    return [
        # Nível 1: 4x4
        {"tamanho": 4,
         "numeros": {(3, 0): 1, (0, 1): 2, (3, 3): 3, (2, 3): 4, (0, 2): 5},
         "paredes": [((1, 1), (1, 2))]},
        # Nível 2: 4x4
        {"tamanho": 4,
         "numeros": {(0, 1): 1, (1, 1): 2, (2, 2): 3, (0, 2): 4},
         "paredes": [((1, 1), (1, 2))]},
        # Nível 3: 5x5
        {"tamanho": 5,
         "numeros": {(4, 4): 1, (2, 3): 2, (4, 3): 3, (0, 2): 4, (2, 0): 5, (4, 0): 6},
         "paredes": [((0, 2), (0, 3)), ((2, 1), (2, 2)), ((3, 0), (4, 0))]},
        # Nível 4: 5x5
        {"tamanho": 5,
         "numeros": {(3, 3): 1, (4, 1): 2, (2, 1): 3, (2, 4): 4, (1, 3): 5},
         "paredes": [((1, 1), (1, 2)), ((1, 2), (2, 2)), ((2, 1), (2, 2))]},
        # Nível 5: 5x5
        {"tamanho": 5,
         "numeros": {(4, 4): 1, (3, 3): 2, (2, 0): 3, (0, 4): 4},
         "paredes": [((1, 1), (2, 1)), ((1, 3), (2, 3)), ((2, 0), (3, 0)), ((2, 2), (3, 2))]},
        # Nível 6: 6x6
        {"tamanho": 6,
         "numeros": {(3, 3): 1, (3, 4): 2, (5, 1): 3, (4, 1): 4, (0, 2): 5, (0, 5): 6},
         "paredes": [((0, 2), (0, 3)), ((1, 5), (2, 5)), ((3, 3), (3, 4)), ((4, 2), (4, 3)), ((5, 2), (5, 3))]},
        # Nível 7: 6x6
        {"tamanho": 6,
         "numeros": {(2, 0): 1, (3, 5): 2, (3, 0): 3, (1, 4): 4, (3, 2): 5},
         "paredes": [((1, 2), (2, 2)), ((2, 1), (3, 1)), ((2, 2), (3, 2))]},
        # Nível 8: 6x6
        {"tamanho": 6,
         "numeros": {(0, 4): 1, (5, 1): 2, (2, 5): 3, (4, 3): 4},
         "paredes": [((0, 1), (1, 1)), ((5, 3), (5, 4))]},
        # Nível 9: 7x7
        {"tamanho": 7,
         "numeros": {(2, 0): 1, (3, 6): 2, (6, 1): 3, (2, 3): 4, (3, 5): 5, (5, 1): 6},
         "paredes": [((0, 2), (1, 2)), ((2, 0), (2, 1)), ((2, 0), (3, 0)), ((2, 2), (2, 3)), ((2, 5), (2, 6)), ((3, 3), (3, 4)), ((4, 4), (4, 5)), ((5, 3), (5, 4)), ((5, 3), (6, 3))]},
        # Nível 10: 7x7
        {"tamanho": 7,
         "numeros": {(6, 6): 1, (5, 5): 2, (0, 1): 3, (4, 3): 4, (2, 4): 5},
         "paredes": [((1, 1), (2, 1)), ((1, 3), (2, 3)), ((3, 2), (4, 2)), ((3, 4), (3, 5)), ((3, 4), (4, 4)), ((4, 1), (5, 1)), ((4, 3), (5, 3))]},
    ]


def carregar_nivel(estado, nivel):
    """Coloca no estado o tabuleiro do nível pedido (0 a 9) e zera o caminho."""
    tabuleiro = obter_tabuleiros()[nivel]
    estado["nivel"] = nivel
    estado["tamanho"] = tabuleiro["tamanho"]
    estado["numeros"] = tabuleiro["numeros"]
    estado["paredes"] = tabuleiro["paredes"]
    estado["jogadas"] = 0
    estado["tempo_nivel"] = 0.0
    # A linha sempre começa na célula do número 1
    for celula in estado["numeros"]:
        if estado["numeros"][celula] == 1:
            estado["caminho"] = [celula]


def novo_jogo():
    """Cria o dicionário de estado de uma partida nova, já no nível 1."""
    estado = {
        "nivel": 0,            # índice do nível atual (0 a 9)
        "tamanho": 0,          # lado do tabuleiro
        "numeros": {},         # célula -> número de passagem
        "paredes": [],         # pares de células separadas por parede
        "caminho": [],         # células já percorridas, em ordem
        "jogadas": 0,          # jogadas no nível atual
        "jogadas_total": 0,    # jogadas somando todos os níveis
        "tempo_nivel": 0.0,    # segundos gastos no nível atual
        "tempo_total": 0.0,    # segundos somando todos os níveis
        "tempos": [],          # tempo de cada nível já completado, em ordem
        "nome": "",            # iniciais, pedidas pela interface no fim
    }
    carregar_nivel(estado, 0)
    return estado


def total_niveis():
    """Quantidade de níveis do jogo."""
    return len(obter_tabuleiros())


def sao_vizinhas(a, b):
    """Verifica se duas células estão lado a lado (sem diagonal)."""
    distancia = abs(a[0] - b[0]) + abs(a[1] - b[1])
    return distancia == 1


def tem_parede(estado, a, b):
    """Verifica se existe parede entre as células a e b."""
    return (a, b) in estado["paredes"] or (b, a) in estado["paredes"]


def maior_numero(estado):
    """Maior número de passagem do tabuleiro (onde a linha precisa terminar)."""
    return max(estado["numeros"].values())


def proximo_numero(estado):
    """Próximo número que a linha precisa alcançar."""
    alcancados = 0
    for celula in estado["caminho"]:
        if celula in estado["numeros"]:
            alcancados += 1
    return alcancados + 1


def movimento_valido(estado, celula):
    """
    Verifica se a linha pode avançar para a célula.
    Devolve uma tupla (True/False, mensagem explicando o motivo).
    """
    linha, coluna = celula
    tamanho = estado["tamanho"]
    atual = estado["caminho"][-1]

    if not (0 <= linha < tamanho and 0 <= coluna < tamanho):
        return False, "Essa célula está fora do tabuleiro."
    if celula in estado["caminho"]:
        return False, "Essa célula já faz parte da linha."
    if not sao_vizinhas(atual, celula):
        return False, "A linha só anda para cima, baixo, esquerda ou direita."
    if tem_parede(estado, atual, celula):
        return False, "Existe uma parede no caminho."

    if celula in estado["numeros"]:
        numero = estado["numeros"][celula]
        if numero != proximo_numero(estado):
            return False, f"Antes do {numero}, a linha precisa passar pelo {proximo_numero(estado)}."
        total_celulas = tamanho * tamanho
        if numero == maior_numero(estado) and len(estado["caminho"]) + 1 < total_celulas:
            return False, f"O {numero} é o fim da linha: passe por todas as células antes."

    return True, ""


def adicionar_tempo(estado, segundos):
    """Soma segundos ao tempo do nível atual e ao tempo total (medidos pela interface)."""
    estado["tempo_nivel"] += segundos
    estado["tempo_total"] += segundos


def fazer_jogada(estado, celula):
    """Avança a linha para a célula, se for válido. Devolve (True/False, mensagem)."""
    valido, mensagem = movimento_valido(estado, celula)
    if valido:
        estado["caminho"].append(celula)
        estado["jogadas"] += 1
        estado["jogadas_total"] += 1
        # Ao completar o nível, guarda quanto tempo ele levou
        if nivel_completo(estado):
            estado["tempos"].append(estado["tempo_nivel"])
    return valido, mensagem


def desfazer_jogada(estado):
    """Apaga a última célula da linha (o número 1 nunca é apagado)."""
    if len(estado["caminho"]) > 1:
        estado["caminho"].pop()
        return True
    return False


def reiniciar_nivel(estado):
    """Apaga a linha inteira, deixando só o número 1. Jogadas e tempo continuam contando."""
    if len(estado["caminho"]) > 1:
        estado["caminho"] = estado["caminho"][:1]
        return True
    return False


def nivel_completo(estado):
    """O nível acaba quando a linha cobre todas as células e termina no maior número."""
    total_celulas = estado["tamanho"] * estado["tamanho"]
    ultima = estado["caminho"][-1]
    return (len(estado["caminho"]) == total_celulas
            and estado["numeros"].get(ultima) == maior_numero(estado))


def avancar_nivel(estado):
    """Passa para o próximo nível. Devolve False se não houver mais níveis."""
    if estado["nivel"] + 1 < total_niveis():
        carregar_nivel(estado, estado["nivel"] + 1)
        return True
    return False


def jogo_terminou(estado):
    """O jogo termina (com vitória) quando o último nível é completado."""
    return estado["nivel"] == total_niveis() - 1 and nivel_completo(estado)