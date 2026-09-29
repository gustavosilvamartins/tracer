# Módulo de interface com o usuário do Tracer (tudo que é mostrado ou pedido).
# Código adaptado de sugestão gerada com o Claude (Anthropic), acessado em 28/09/2026.
# Leitura de teclas e limpeza de tela baseadas no getch_teste.py visto em aula.
from sys import platform
import os
import time
import mecanica
import arquivos
import gui

if platform == 'linux': from getch import getch  # type: ignore
if platform == 'win32': from msvcrt import getch  # type: ignore

# Cores ANSI (funcionam no terminal do VS Code, no PowerShell e no Terminal do Windows)
CIANO = "\033[96m"
MAGENTA = "\033[95m"
AMARELO = "\033[93m"
CINZA = "\033[90m"
NEGRITO = "\033[1m"
NORMAL = "\033[0m"

DIRECOES = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}


# ---------- Utilidades de tela e teclado ----------

def limpa_tela():
    if platform == 'linux':
        os.system('clear')
    if platform == 'win32':
        os.system('cls')


def ler_tecla():
    """
    Espera uma tecla e devolve a letra em minúsculo.
    Enter vira "enter" e, no Windows, as setas viram w/a/s/d.
    """
    codigo = ord(getch())
    if codigo in (0, 224):                   # tecla especial do Windows (setas)
        seta = ord(getch())
        return {72: "w", 80: "s", 75: "a", 77: "d"}.get(seta, "")
    if codigo in (10, 13):
        return "enter"
    return chr(codigo).lower()


def esperar_tecla(texto="Pressione qualquer tecla para voltar."):
    print(f"\n{CINZA}{texto}{NORMAL}")
    ler_tecla()


def formatar_tempo(segundos):
    """Converte segundos em mm:ss."""
    segundos = int(segundos)
    return f"{segundos // 60:02d}:{segundos % 60:02d}"


def titulo(texto):
    print(f"{CIANO}{NEGRITO}  {texto}{NORMAL}")
    print(f"{MAGENTA}  {'─' * len(texto)}{NORMAL}\n")


def logo():
    print(CIANO + NEGRITO + r"""
   ████████ ██████   █████   ██████ ███████ ██████
      ██    ██   ██ ██   ██ ██      ██      ██   ██
      ██    ██████  ███████ ██      █████   ██████
      ██    ██   ██ ██   ██ ██      ██      ██   ██
      ██    ██   ██ ██   ██  ██████ ███████ ██   ██""" + NORMAL)
    print(f"{MAGENTA}        passe por todas as casas, na ordem certa{NORMAL}\n")


def escolher_opcao(opcoes, cabecalho=None, rodape="", inicial=0):
    """
    Menu navegável com w/s (ou setas) e Enter, como no getch_teste.py.
    'cabecalho' é uma função que desenha o topo da tela; 'inicial' é a opção
    que começa marcada. Devolve o índice escolhido.
    """
    opcao = inicial
    while True:
        limpa_tela()
        if cabecalho is not None:
            cabecalho()
        for i in range(len(opcoes)):
            if i == opcao:
                print(f"  {MAGENTA}▶ {NEGRITO}{opcoes[i]}{NORMAL}")
            else:
                print(f"    {opcoes[i]}")
        print(f"\n{CINZA}  w/s ou setas para escolher, Enter para confirmar{NORMAL}")
        if rodape:
            print(rodape)
        tecla = ler_tecla()
        if tecla == "enter":
            return opcao
        if tecla == "s":
            opcao = (opcao + 1) % len(opcoes)
        elif tecla == "w":
            opcao = (opcao - 1) % len(opcoes)


def confirmar(pergunta):
    """Pergunta de sim ou não respondida com uma tecla."""
    print(f"\n{AMARELO}{pergunta} (s/n){NORMAL}")
    while True:
        tecla = ler_tecla()
        if tecla in ("s", "n"):
            return tecla == "s"


# ---------- Escolha entre console e janela (Tkinter) ----------
# Cada menu recebe usar_gui=True/False conforme as opções -gui passadas no console.

def ui_escolher(opcoes, nome, usar_gui, cabecalho=None, inicial=0, rodape="", valor_ao_fechar=None):
    if usar_gui:
        return gui.escolher_opcao(nome, opcoes, rodape.strip(), inicial, valor_ao_fechar,
                                  animacao=(nome == "TRACER"))
    if cabecalho is None:
        cabecalho = lambda: titulo(nome)
    return escolher_opcao(opcoes, cabecalho, rodape, inicial)


def ui_confirmar(pergunta, usar_gui):
    if usar_gui:
        return gui.confirmar(pergunta)
    return confirmar(pergunta)


def ui_aviso(texto, usar_gui):
    if usar_gui:
        gui.aviso(texto)
    else:
        limpa_tela()
        print(f"\n  {AMARELO}{texto}{NORMAL}")
        esperar_tecla()


def ui_pedir_texto(nome, pergunta, usar_gui):
    if usar_gui:
        return gui.pedir_texto(nome, pergunta)
    limpa_tela()
    titulo(nome)
    return input(f"  {pergunta} ").strip()


def ui_texto(nome, texto, usar_gui):
    if usar_gui:
        gui.tela_texto(nome, texto)
    else:
        limpa_tela()
        titulo(nome)
        print(texto)
        esperar_tecla()


# ---------- Desenho do tabuleiro ----------

def ligadas(estado, a, b):
    """Verifica se a linha passa diretamente de a para b."""
    caminho = estado["caminho"]
    for i in range(len(caminho) - 1):
        if (caminho[i], caminho[i + 1]) in ((a, b), (b, a)):
            return True
    return False


def desenhar_tabuleiro(estado):
    n = estado["tamanho"]
    ponta = estado["caminho"][-1]
    print("  +" + "───+" * n)
    for l in range(n):
        linha = "  │"
        baixo = "  +"
        for c in range(n):
            cel = (l, c)
            if cel in estado["numeros"]:
                cor = MAGENTA if cel == ponta else (CIANO if cel in estado["caminho"] else AMARELO)
                texto = cor + NEGRITO + str(estado["numeros"][cel]).center(3) + NORMAL
            elif cel == ponta:
                texto = MAGENTA + NEGRITO + " ● " + NORMAL
            elif cel in estado["caminho"]:
                texto = CIANO + " ■ " + NORMAL
            else:
                texto = CINZA + " · " + NORMAL
            linha += texto
            direita = (l, c + 1)
            if c == n - 1 or mecanica.tem_parede(estado, cel, direita):
                linha += "│"
            elif ligadas(estado, cel, direita):
                linha += CIANO + "─" + NORMAL
            else:
                linha += " "
            abaixo = (l + 1, c)
            if l == n - 1 or mecanica.tem_parede(estado, cel, abaixo):
                baixo += "───+"
            elif ligadas(estado, cel, abaixo):
                baixo += " " + CIANO + "│" + NORMAL + " +"
            else:
                baixo += "   +"
        print(linha)
        print(baixo)


def desenhar_jogo(estado, aviso):
    limpa_tela()
    titulo(f"NÍVEL {estado['nivel'] + 1} de {mecanica.total_niveis()}")
    proximo = "—" if mecanica.nivel_completo(estado) else mecanica.proximo_numero(estado)
    print(f"  jogadas: {estado['jogadas']:<4} próximo número: {proximo}")
    print(f"  tempo do nível: {formatar_tempo(estado['tempo_nivel'])}   "
          f"tempo total: {formatar_tempo(estado['tempo_total'])}\n")
    desenhar_tabuleiro(estado)
    print(f"\n{CINZA}  w/a/s/d mover   z desfazer   r recomeçar nível   p pausar{NORMAL}")
    if aviso:
        print(f"\n  {AMARELO}{aviso}{NORMAL}")


# ---------- Telas de texto ----------

def texto_regras():
    return ("""  O objetivo é desenhar uma única linha que passe por TODAS as casas
  do tabuleiro, cada uma exatamente uma vez.

  • A linha começa no número 1 e anda para cima, baixo, esquerda
    ou direita (nunca na diagonal).
  • Os números devem ser visitados em ordem crescente: 1, 2, 3...
  • A linha termina no maior número, depois de cobrir todas as casas.
  • As bordas dentro do tabuleiro são paredes e não podem ser atravessadas.

  São 10 níveis de dificuldade crescente. O jogo termina quando você
  completa o décimo. O tempo e as jogadas de cada nível são registrados.""")


def tela_regras(usar_gui):
    ui_texto("REGRAS", texto_regras(), usar_gui)


def tela_creditos(usar_gui):
    ui_texto("CRÉDITOS", """  Tracer — versão 1.2
  Projeto final de Algoritmos Computacionais (UERJ)
  Autor: Gustavo Martins
  Inspirado no jogo Trace (wordle.global).

  Novidades da versão 1.2:
  • ranking dos melhores tempos e recorde de cada nível
  • logo e ícone do jogo

  Versão 1.1:
  • interface gráfica com Tkinter (-gui, -gui-principal, -gui-pause,
    -gui-arquivos e -gui-jogo)

  Próximas versões:
  • editor para criar novos tabuleiros""", usar_gui)


def tela_historico(usar_gui):
    partidas = arquivos.ler_historico()
    if not partidas:
        texto = "  Nenhuma partida registrada ainda."
    else:
        texto = f"  {'NOME':<6}{'NÍVEIS':>7}{'JOGADAS':>9}{'TEMPO':>8}   DATA\n"
        for p in partidas:
            texto += (f"  {p['nome']:<6}{p['niveis']:>7}{p['jogadas']:>9}"
                      f"{formatar_tempo(p['tempo']):>8}   {p['data']}\n")
    ui_texto("HISTÓRICO DE PARTIDAS", texto, usar_gui)


def tela_ranking(usar_gui):
    ranking = arquivos.ranking_geral()
    texto = "  MELHORES TEMPOS (os 10 níveis, começando do 1)\n\n"
    if not ranking:
        texto += "  Ninguém completou os 10 níveis ainda.\n"
    else:
        texto += f"  {'#':>3}  {'NOME':<6}{'TEMPO':>7}{'JOGADAS':>10}   DATA\n"
        for i in range(len(ranking)):
            p = ranking[i]
            texto += (f"  {i + 1:>2}º  {p['nome']:<6}{formatar_tempo(p['tempo']):>7}"
                      f"{p['jogadas']:>10}   {p['data'][:10]}\n")
    texto += "\n  RECORDE DE CADA NÍVEL\n\n"
    recordes = arquivos.recordes_por_nivel()
    for i in range(len(recordes)):
        r = recordes[i]
        if r is None:
            texto += f"  Nível {i + 1:>2}    --:--\n"
        else:
            texto += f"  Nível {i + 1:>2}    {formatar_tempo(r['tempo'])}   {r['nome']}\n"
    ui_texto("RANKING", texto, usar_gui)


def texto_posicao(posicao):
    """Mensagem sobre a colocação no ranking depois de uma vitória."""
    if posicao is None:
        return "Partidas iniciadas depois do nível 1 não entram no ranking."
    if posicao == 1:
        return "NOVO RECORDE! Você está em 1º lugar no ranking!"
    return f"Você ficou em {posicao}º lugar no ranking."


def pedir_iniciais():
    """Pede as iniciais no estilo dos fliperamas antigos."""
    while True:
        iniciais = input(f"\n  {CIANO}Digite suas iniciais (3 letras): {NORMAL}").strip().upper()
        if len(iniciais) == 3 and iniciais.isalpha():
            return iniciais
        print(f"  {AMARELO}Use exatamente 3 letras.{NORMAL}")


def tela_vitoria(estado):
    limpa_tela()
    titulo("VOCÊ COMPLETOU OS 10 NÍVEIS!")
    # Se o jogo começou num nível acima do 1, os tempos começam a partir dele
    primeiro = mecanica.total_niveis() - len(estado["tempos"])
    for i in range(len(estado["tempos"])):
        print(f"  Nível {primeiro + i + 1:2d}: {formatar_tempo(estado['tempos'][i])}")
    print(f"  {MAGENTA}{'─' * 16}{NORMAL}")
    print(f"  Total   : {NEGRITO}{formatar_tempo(estado['tempo_total'])}{NORMAL}")
    print(f"  Jogadas : {estado['jogadas_total']}")
    estado["nome"] = pedir_iniciais()
    arquivos.registrar_partida(estado)
    print(f"\n  {CIANO}Resultado registrado no histórico, {estado['nome']}!{NORMAL}")
    print(f"  {MAGENTA}{NEGRITO}{texto_posicao(arquivos.posicao_no_ranking(estado))}{NORMAL}")
    esperar_tecla("Pressione qualquer tecla para voltar ao menu.")


# ---------- Menus de arquivos e configurações ----------

def menu_carregar(config):
    """Menu de arquivos no modo carregar. Devolve o estado carregado ou None."""
    usar_gui = config["gui"]["arquivos"]
    while True:
        saves = arquivos.listar_saves()
        opcoes = saves + ["Voltar"]
        rodape = "" if saves else f"\n  {AMARELO}Nenhum save encontrado.{NORMAL}"
        if usar_gui and not saves:
            rodape = "Nenhum save encontrado."
        escolha = ui_escolher(opcoes, "CARREGAR JOGO", usar_gui, rodape=rodape)
        if escolha == len(saves):
            return None
        estado, mensagem = arquivos.carregar_jogo(saves[escolha])
        if estado is not None:
            return estado
        ui_aviso(mensagem, usar_gui)


def menu_salvar(estado, config):
    """Menu de arquivos no modo salvar (regra 3.2.4)."""
    usar_gui = config["gui"]["arquivos"]
    while True:
        saves = arquivos.listar_saves()
        opcoes = ["Criar save novo"] + saves + ["Voltar"]
        escolha = ui_escolher(opcoes, "SALVAR JOGO", usar_gui)
        if escolha == len(opcoes) - 1:
            return
        if escolha == 0:
            nome = ui_pedir_texto("SALVAR JOGO", "Nome do save (sem extensão):", usar_gui)
            if nome == "":
                continue
        else:
            nome = saves[escolha - 1]
        if arquivos.save_existe(nome):
            if not ui_confirmar(f"O save '{nome}' já existe e será SOBRESCRITO. Confirma?", usar_gui):
                continue
        ok, mensagem = arquivos.salvar_jogo(estado, nome)
        ui_aviso(mensagem, usar_gui)
        return


def menu_configuracoes(config):
    usar_gui = config["gui"]["principal"]
    while True:
        opcoes = [f"Nível inicial: {config['nivel'] + 1}",
                  f"Save automático: {config['autosave']}.save",
                  "Voltar"]
        escolha = ui_escolher(opcoes, "CONFIGURAÇÕES", usar_gui)
        if escolha == 0:
            texto = ui_pedir_texto("CONFIGURAÇÕES",
                                   f"Nível inicial (1 a {mecanica.total_niveis()}):", usar_gui)
            if texto.isdigit() and 1 <= int(texto) <= mecanica.total_niveis():
                config["nivel"] = int(texto) - 1
        elif escolha == 1:
            nome = ui_pedir_texto("CONFIGURAÇÕES",
                                  "Nome do arquivo de save automático (sem extensão):", usar_gui)
            if nome != "":
                config["autosave"] = nome
        else:
            return


# ---------- Pause e loop do jogo ----------

def menu_pause(estado, config):
    """
    Menu de pause (regra 3.2.3). Devolve uma ação para o loop do jogo:
    "voltar", "novo", "carregar", "menu" ou "sair".
    """
    usar_gui = config["gui"]["pause"]
    while True:
        opcoes = ["Voltar para o jogo", "Iniciar novo jogo", "Carregar partida de um arquivo",
                  "Salvar partida em um arquivo", "Voltar ao menu principal", "Sair do jogo"]
        escolha = ui_escolher(opcoes, "PAUSA", usar_gui, valor_ao_fechar=0)
        if escolha == 0:
            return "voltar"
        if escolha == 1 and ui_confirmar("A partida atual será encerrada sem salvar. Continuar?",
                                         usar_gui):
            return "novo"
        if escolha == 2:
            return "carregar"
        if escolha == 3:
            menu_salvar(estado, config)
        if escolha == 4:
            return "menu"
        if escolha == 5:
            return "sair"


def novo_jogo(config):
    estado = mecanica.novo_jogo()
    mecanica.carregar_nivel(estado, config["nivel"])
    arquivos.registrar("INICIO", f"novo jogo no nível {config['nivel'] + 1}")
    return estado


def processar_tecla(estado, tecla, config):
    """
    Aplica uma tecla de jogo (w/a/s/d, z ou r), registra e faz o save automático.
    Usada tanto pelo jogo no console quanto pela janela do Tkinter.
    Devolve a mensagem de aviso ("" se não houver).
    """
    nivel = estado["nivel"] + 1
    if tecla in DIRECOES:
        l, c = estado["caminho"][-1]
        dl, dc = DIRECOES[tecla]
        destino = (l + dl, c + dc)
        valido, mensagem = mecanica.fazer_jogada(estado, destino)
        if not valido:
            arquivos.registrar("JOGADA INVÁLIDA", f"nível {nivel}: {destino} — {mensagem}")
            return mensagem
        arquivos.registrar("JOGADA", f"nível {nivel}: ({l}, {c}) -> {destino}")
    elif tecla == "z":
        if not mecanica.desfazer_jogada(estado):
            return ""
        arquivos.registrar("DESFAZER", f"nível {nivel}")
    elif tecla == "r":
        if not mecanica.reiniciar_nivel(estado):
            return ""
        arquivos.registrar("RECOMEÇAR", f"nível {nivel}")
    else:
        return ""
    arquivos.salvar_automatico(estado, config["autosave"])
    return ""


def registrar_nivel_completo(estado):
    arquivos.registrar("NÍVEL COMPLETO", f"nível {estado['nivel'] + 1} em "
                       f"{formatar_tempo(estado['tempos'][-1])}")


def passar_de_nivel(estado, config):
    mecanica.avancar_nivel(estado)
    arquivos.salvar_automatico(estado, config["autosave"])


def tratar_pause(estado, config):
    """Abre o pause e aplica a escolha. Devolve (estado, "continuar"/"menu"/"sair")."""
    acao = menu_pause(estado, config)
    if acao == "novo":
        return novo_jogo(config), "continuar"
    if acao == "carregar":
        carregado = menu_carregar(config)
        if carregado is not None:
            return carregado, "continuar"
    if acao in ("menu", "sair"):
        return estado, acao
    return estado, "continuar"


def loop_do_jogo(estado, config):
    """Loop principal da partida. Devolve "menu" ou "sair"."""
    if config["gui"]["jogo"]:
        while True:
            if gui.jogar(estado, config, processar_tecla) == "menu":
                return "menu"                    # jogo vencido na janela
            estado, acao = tratar_pause(estado, config)
            if acao != "continuar":
                return acao

    aviso = ""
    while True:
        desenhar_jogo(estado, aviso)
        aviso = ""

        inicio = time.time()
        tecla = ler_tecla()
        mecanica.adicionar_tempo(estado, time.time() - inicio)

        if tecla == "p":
            estado, acao = tratar_pause(estado, config)
            if acao != "continuar":
                return acao
        else:
            aviso = processar_tecla(estado, tecla, config)

        if mecanica.nivel_completo(estado):
            if mecanica.jogo_terminou(estado):
                arquivos.registrar("VITÓRIA", f"tempo total {formatar_tempo(estado['tempo_total'])}")
                tela_vitoria(estado)
                return "menu"
            desenhar_jogo(estado, "")
            print(f"\n  {CIANO}{NEGRITO}Nível {estado['nivel'] + 1} completo em "
                  f"{formatar_tempo(estado['tempos'][-1])}!{NORMAL}")
            registrar_nivel_completo(estado)
            esperar_tecla("Pressione qualquer tecla para o próximo nível.")
            passar_de_nivel(estado, config)


# ---------- Menu principal ----------

def menu_principal(config):
    """Menu principal (regra 3.2.2). Termina quando o usuário escolhe sair."""
    opcoes = ["Iniciar jogo", "Carregar jogo", "Histórico de partidas", "Ranking",
              "Configurações", "Ver regras", "Créditos", "Sair"]
    escolha = 0
    while True:
        escolha = ui_escolher(opcoes, "TRACER", config["gui"]["principal"], logo,
                              inicial=escolha, rodape="passe por todas as casas, na ordem certa"
                              if config["gui"]["principal"] else "")   # volta na última opção
        acao = "menu"
        if escolha == 0:
            acao = loop_do_jogo(novo_jogo(config), config)
        elif escolha == 1:
            estado = menu_carregar(config)
            if estado is not None:
                acao = loop_do_jogo(estado, config)
        elif escolha == 2:
            tela_historico(config["gui"]["principal"])
        elif escolha == 3:
            tela_ranking(config["gui"]["principal"])
        elif escolha == 4:
            menu_configuracoes(config)
        elif escolha == 5:
            tela_regras(config["gui"]["principal"])
        elif escolha == 6:
            tela_creditos(config["gui"]["principal"])
        elif escolha == 7:
            acao = "sair"
        if acao == "sair":
            limpa_tela()
            print(f"{CIANO}Até a próxima!{NORMAL}")
            return