# Módulo de interface com o usuário do Tracer (tudo que é mostrado ou pedido).
# Código adaptado de sugestão gerada com o Claude (Anthropic), acessado em 28/09/2026.
# Leitura de teclas e limpeza de tela baseadas no getch_teste.py visto em aula.
from sys import platform
import os
import time
import mecanica
import arquivos

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
    print(f"  jogadas: {estado['jogadas']:<4} próximo número: {mecanica.proximo_numero(estado)}")
    print(f"  tempo do nível: {formatar_tempo(estado['tempo_nivel'])}   "
          f"tempo total: {formatar_tempo(estado['tempo_total'])}\n")
    desenhar_tabuleiro(estado)
    print(f"\n{CINZA}  w/a/s/d mover   z desfazer   r recomeçar nível   p pausar{NORMAL}")
    if aviso:
        print(f"\n  {AMARELO}{aviso}{NORMAL}")


# ---------- Telas de texto ----------

def tela_regras():
    limpa_tela()
    titulo("REGRAS")
    print("""  O objetivo é desenhar uma única linha que passe por TODAS as casas
  do tabuleiro, cada uma exatamente uma vez.

  • A linha começa no número 1 e anda para cima, baixo, esquerda
    ou direita (nunca na diagonal).
  • Os números devem ser visitados em ordem crescente: 1, 2, 3...
  • A linha termina no maior número, depois de cobrir todas as casas.
  • As bordas dentro do tabuleiro são paredes e não podem ser atravessadas.

  São 10 níveis de dificuldade crescente. O jogo termina quando você
  completa o décimo. O tempo e as jogadas de cada nível são registrados.""")
    esperar_tecla()


def tela_creditos():
    limpa_tela()
    titulo("CRÉDITOS")
    print("""  Tracer — versão 1.0
  Projeto final de Algoritmos Computacionais (UERJ)
  Autor: Gustavo Martins
  Inspirado no jogo Trace (wordle.global).

  Próximas versões:
  • interface gráfica com Tkinter (-gui)
  • ranking com os melhores tempos por nível
  • editor para criar novos tabuleiros""")
    esperar_tecla()


def tela_historico():
    limpa_tela()
    titulo("HISTÓRICO DE PARTIDAS")
    partidas = arquivos.ler_historico()
    if not partidas:
        print("  Nenhuma partida registrada ainda.")
    else:
        print(f"  {'NOME':<6}{'NÍVEIS':>7}{'JOGADAS':>9}{'TEMPO':>8}   DATA")
        for p in partidas:
            print(f"  {p['nome']:<6}{p['niveis']:>7}{p['jogadas']:>9}"
                  f"{formatar_tempo(p['tempo']):>8}   {p['data']}")
    esperar_tecla()


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
    esperar_tecla("Pressione qualquer tecla para voltar ao menu.")


# ---------- Menus de arquivos e configurações ----------

def menu_carregar():
    """Menu de arquivos no modo carregar. Devolve o estado carregado ou None."""
    while True:
        saves = arquivos.listar_saves()
        opcoes = saves + ["Voltar"]
        escolha = escolher_opcao(opcoes, lambda: titulo("CARREGAR JOGO"),
                                 "" if saves else f"\n  {AMARELO}Nenhum save encontrado.{NORMAL}")
        if escolha == len(saves):
            return None
        estado, mensagem = arquivos.carregar_jogo(saves[escolha])
        if estado is not None:
            return estado
        limpa_tela()
        print(f"\n  {AMARELO}{mensagem}{NORMAL}")
        esperar_tecla()


def menu_salvar(estado):
    """Menu de arquivos no modo salvar (regra 3.2.4)."""
    while True:
        saves = arquivos.listar_saves()
        opcoes = ["Criar save novo"] + saves + ["Voltar"]
        escolha = escolher_opcao(opcoes, lambda: titulo("SALVAR JOGO"))
        if escolha == len(opcoes) - 1:
            return
        if escolha == 0:
            limpa_tela()
            titulo("SALVAR JOGO")
            nome = input("  Nome do save (sem extensão): ").strip()
            if nome == "":
                continue
        else:
            nome = saves[escolha - 1]
        if arquivos.save_existe(nome):
            if not confirmar(f"O save '{nome}' já existe e será SOBRESCRITO. Confirma?"):
                continue
        ok, mensagem = arquivos.salvar_jogo(estado, nome)
        limpa_tela()
        print(f"\n  {CIANO if ok else AMARELO}{mensagem}{NORMAL}")
        esperar_tecla()
        return


def menu_configuracoes(config):
    while True:
        opcoes = [f"Nível inicial: {config['nivel'] + 1}",
                  f"Arquivo de save automático: {config['autosave']}.save",
                  "Voltar"]
        escolha = escolher_opcao(opcoes, lambda: titulo("CONFIGURAÇÕES"))
        if escolha == 0:
            limpa_tela()
            titulo("CONFIGURAÇÕES")
            texto = input(f"  Nível inicial (1 a {mecanica.total_niveis()}): ").strip()
            if texto.isdigit() and 1 <= int(texto) <= mecanica.total_niveis():
                config["nivel"] = int(texto) - 1
        elif escolha == 1:
            limpa_tela()
            titulo("CONFIGURAÇÕES")
            nome = input("  Nome do arquivo de save automático (sem extensão): ").strip()
            if nome != "":
                config["autosave"] = nome
        else:
            return


# ---------- Pause e loop do jogo ----------

def menu_pause(estado):
    """
    Menu de pause (regra 3.2.3). Devolve uma ação para o loop do jogo:
    "voltar", "novo", "carregar", "menu" ou "sair".
    """
    while True:
        opcoes = ["Voltar para o jogo", "Iniciar novo jogo", "Carregar partida de um arquivo",
                  "Salvar partida em um arquivo", "Voltar ao menu principal", "Sair do jogo"]
        escolha = escolher_opcao(opcoes, lambda: titulo("PAUSA"))
        if escolha == 0:
            return "voltar"
        if escolha == 1 and confirmar("A partida atual será encerrada sem salvar. Continuar?"):
            return "novo"
        if escolha == 2:
            return "carregar"
        if escolha == 3:
            menu_salvar(estado)
        if escolha == 4:
            return "menu"
        if escolha == 5:
            return "sair"


def novo_jogo(config):
    estado = mecanica.novo_jogo()
    mecanica.carregar_nivel(estado, config["nivel"])
    arquivos.registrar("INICIO", f"novo jogo no nível {config['nivel'] + 1}")
    return estado


def loop_do_jogo(estado, config):
    """Loop principal da partida. Devolve "menu" ou "sair"."""
    aviso = ""
    while True:
        desenhar_jogo(estado, aviso)
        aviso = ""

        inicio = time.time()
        tecla = ler_tecla()
        mecanica.adicionar_tempo(estado, time.time() - inicio)

        if tecla in DIRECOES:
            l, c = estado["caminho"][-1]
            dl, dc = DIRECOES[tecla]
            destino = (l + dl, c + dc)
            valido, mensagem = mecanica.fazer_jogada(estado, destino)
            if valido:
                arquivos.registrar("JOGADA", f"nível {estado['nivel'] + 1}: ({l}, {c}) -> {destino}")
                arquivos.salvar_automatico(estado, config["autosave"])
            else:
                aviso = mensagem
                arquivos.registrar("JOGADA INVÁLIDA", f"nível {estado['nivel'] + 1}: {destino} — {mensagem}")
        elif tecla == "z":
            if mecanica.desfazer_jogada(estado):
                arquivos.registrar("DESFAZER", f"nível {estado['nivel'] + 1}")
                arquivos.salvar_automatico(estado, config["autosave"])
        elif tecla == "r":
            if mecanica.reiniciar_nivel(estado):
                arquivos.registrar("RECOMEÇAR", f"nível {estado['nivel'] + 1}")
                arquivos.salvar_automatico(estado, config["autosave"])
        elif tecla == "p":
            acao = menu_pause(estado)
            if acao == "novo":
                estado = novo_jogo(config)
            elif acao == "carregar":
                carregado = menu_carregar()
                if carregado is not None:
                    estado = carregado
            elif acao in ("menu", "sair"):
                return acao

        if mecanica.nivel_completo(estado):
            if mecanica.jogo_terminou(estado):
                arquivos.registrar("VITÓRIA", f"tempo total {formatar_tempo(estado['tempo_total'])}")
                tela_vitoria(estado)
                return "menu"
            desenhar_jogo(estado, "")
            print(f"\n  {CIANO}{NEGRITO}Nível {estado['nivel'] + 1} completo em "
                  f"{formatar_tempo(estado['tempos'][-1])}!{NORMAL}")
            arquivos.registrar("NÍVEL COMPLETO", f"nível {estado['nivel'] + 1} em "
                               f"{formatar_tempo(estado['tempos'][-1])}")
            esperar_tecla("Pressione qualquer tecla para o próximo nível.")
            mecanica.avancar_nivel(estado)
            arquivos.salvar_automatico(estado, config["autosave"])


# ---------- Menu principal ----------

def menu_principal(config):
    """Menu principal (regra 3.2.2). Termina quando o usuário escolhe sair."""
    opcoes = ["Iniciar jogo", "Carregar jogo", "Histórico de partidas",
              "Configurações", "Ver regras", "Créditos", "Sair"]
    escolha = 0
    while True:
        escolha = escolher_opcao(opcoes, logo, inicial=escolha)   # volta na última opção usada
        acao = "menu"
        if escolha == 0:
            acao = loop_do_jogo(novo_jogo(config), config)
        elif escolha == 1:
            estado = menu_carregar()
            if estado is not None:
                acao = loop_do_jogo(estado, config)
        elif escolha == 2:
            tela_historico()
        elif escolha == 3:
            menu_configuracoes(config)
        elif escolha == 4:
            tela_regras()
        elif escolha == 5:
            tela_creditos()
        elif escolha == 6:
            acao = "sair"
        if acao == "sair":
            limpa_tela()
            print(f"{CIANO}Até a próxima!{NORMAL}")
            return