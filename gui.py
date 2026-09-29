# Interface gráfica do Tracer com Tkinter (pontuação extra, seção 6 da descrição).
# Faz parte do módulo de interface: é chamado pela interface.py quando as opções -gui estão ativas.
# Código adaptado de sugestão gerada com o Claude (Anthropic), acessado em 28/09/2026.
import os
import time
import tkinter as tk
import mecanica
import arquivos

FUNDO = "#070B1F"
PAINEL = "#0E1433"
CIANO = "#3DF5FF"
CIANO_ESCURO = "#1B5E7A"
MAGENTA = "#FF3D9A"
TEXTO = "#C9D6FF"
FONTE = "Bahnschrift"
PASTA_IMAGENS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagens")


def carregar_imagem(janela, nome):
    """Abre uma imagem da pasta 'imagens'. Devolve None se ela não existir."""
    try:
        return tk.PhotoImage(master=janela, file=os.path.join(PASTA_IMAGENS, nome))
    except tk.TclError:
        return None


# ---------- Base das janelas ----------
# Cada tela é uma janela própria: ela abre, espera a escolha do usuário, fecha e
# devolve o resultado. Assim cada parte do jogo pode ser gráfica ou de console
# de forma independente (-gui-principal, -gui-pause, -gui-arquivos, -gui-jogo).

def nova_janela(titulo):
    """
    Cria uma janela em tela cheia (F11 alterna entre tela cheia e janela).
    O conteúdo de cada tela vai em janela.conteudo, que fica centralizado.
    """
    janela = tk.Tk()
    janela.title(titulo_da_janela(titulo))
    janela.configure(bg=FUNDO)
    # Ocupa a tela toda mesmo em sistemas que ignoram o modo tela cheia
    janela.geometry(f"{janela.winfo_screenwidth()}x{janela.winfo_screenheight()}+0+0")
    janela.attributes("-fullscreen", True)
    janela.bind("<F11>", lambda e: alternar_tela_cheia(janela))
    icone = carregar_imagem(janela, "icone64.png")
    if icone is not None:
        janela.iconphoto(True, icone)
        janela.icone = icone            # guarda a referência para a imagem não sumir
    janela.conteudo = tk.Frame(janela, bg=FUNDO, padx=30, pady=24)
    janela.conteudo.pack(expand=True)   # expand centraliza o quadro na tela
    return janela


def titulo_da_janela(titulo):
    """Texto da barra de título: "Tracer - Menu", "Tracer - Pausa", "Tracer - Carregar jogo"..."""
    if titulo == "TRACER":
        nome = "Menu"
    else:
        nome = titulo.capitalize()
    return "Tracer - " + nome


def alternar_tela_cheia(janela):
    janela.attributes("-fullscreen", not janela.attributes("-fullscreen"))


def abrir(janela):
    """Traz a janela para frente, com o foco do teclado, e espera ela fechar."""
    janela.lift()
    janela.focus_force()
    janela.mainloop()


def rotulo(pai, texto, tamanho=12, cor=TEXTO, negrito=False, fonte=FONTE):
    estilo = (fonte, tamanho, "bold") if negrito else (fonte, tamanho)
    return tk.Label(pai, text=texto, font=estilo, fg=cor, bg=FUNDO, justify="left")


def botao(pai, texto, comando, largura=26):
    """Botão com borda de 1 pixel e efeito ao passar o mouse."""
    borda = tk.Frame(pai, bg=CIANO_ESCURO, padx=1, pady=1)
    b = tk.Button(borda, text=texto, command=comando, font=(FONTE, 13), fg=CIANO, bg=PAINEL,
                  activebackground=CIANO, activeforeground=FUNDO, relief="flat", bd=0,
                  cursor="hand2", width=largura, anchor="w", padx=14, pady=6)
    b.pack()
    b.bind("<Enter>", lambda e: marcar(b, borda, True))
    b.bind("<Leave>", lambda e: marcar(b, borda, False))
    return borda, b


def marcar(b, borda, ativo):
    if ativo:
        b.config(bg=CIANO_ESCURO, fg="white")
        borda.config(bg=CIANO)
    else:
        b.config(bg=PAINEL, fg=CIANO)
        borda.config(bg=CIANO_ESCURO)


def cabecalho(janela, titulo, subtitulo="", imagem=None):
    if imagem is not None:
        tk.Label(janela, image=imagem, bg=FUNDO, bd=0).pack(anchor="w")
    else:
        rotulo(janela, titulo, 30, CIANO, True).pack(anchor="w")
    if subtitulo:
        rotulo(janela, subtitulo, 12).pack(anchor="w")
    tk.Frame(janela, bg=MAGENTA, height=2, width=260).pack(anchor="w", pady=(10, 18))


# ---------- Telas genéricas ----------

def escolher_opcao(titulo, opcoes, subtitulo="", inicial=0, valor_ao_fechar=None, animacao=False):
    """
    Menu com um botão por opção. Também aceita w/s, setas e Enter.
    Fechar a janela no X devolve 'valor_ao_fechar' (por padrão, a última opção).
    """
    if valor_ao_fechar is None:
        valor_ao_fechar = len(opcoes) - 1
    resultado = {"valor": valor_ao_fechar, "marcada": inicial, "animacao": None}
    janela = nova_janela(titulo)

    def fechar(valor):
        resultado["valor"] = valor
        if resultado["animacao"] is not None:
            janela.after_cancel(resultado["animacao"])
        janela.destroy()

    corpo = tk.Frame(janela.conteudo, bg=FUNDO)
    corpo.pack()
    if animacao:
        tabuleiro_animado(corpo, janela, resultado).grid(row=0, column=0, padx=(0, 30))
    lado = tk.Frame(corpo, bg=FUNDO)
    lado.grid(row=0, column=1)
    logo = carregar_imagem(janela, "titulo.png") if animacao else None
    cabecalho(lado, titulo, subtitulo, logo)

    botoes = []
    for i in range(len(opcoes)):
        borda, b = botao(lado, opcoes[i], lambda i=i: fechar(i))
        borda.pack(anchor="w", pady=4)
        botoes.append((b, borda))
    rotulo(lado, "w/s ou setas e Enter também funcionam   F11: tela cheia", 9, CIANO_ESCURO).pack(anchor="w", pady=(12, 0))

    def atualizar_marca():
        for i in range(len(botoes)):
            marcar(botoes[i][0], botoes[i][1], i == resultado["marcada"])

    def tecla(evento):
        nome = evento.keysym.lower()
        if nome in ("s", "down"):
            resultado["marcada"] = (resultado["marcada"] + 1) % len(opcoes)
        elif nome in ("w", "up"):
            resultado["marcada"] = (resultado["marcada"] - 1) % len(opcoes)
        elif nome == "return":
            fechar(resultado["marcada"])
            return
        atualizar_marca()

    janela.bind("<Key>", tecla)
    janela.protocol("WM_DELETE_WINDOW", lambda: fechar(valor_ao_fechar))
    atualizar_marca()
    abrir(janela)
    return resultado["valor"]


def tabuleiro_animado(pai, janela, resultado):
    """Pequeno tabuleiro 4x4 onde uma linha vai se desenhando em espiral (menu principal)."""
    lado, margem = 56, 10
    tela = tk.Canvas(pai, width=4 * lado + 2 * margem, height=4 * lado + 2 * margem,
                     bg=FUNDO, highlightthickness=0)
    espiral = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (3, 3), (3, 2),
               (3, 1), (3, 0), (2, 0), (1, 0), (1, 1), (1, 2), (2, 2), (2, 1)]
    centro = lambda c: (margem + c[1] * lado + lado / 2, margem + c[0] * lado + lado / 2)
    passo = {"i": 0}

    def quadro():
        tela.delete("all")
        for l in range(4):
            for c in range(4):
                x, y = margem + c * lado, margem + l * lado
                tela.create_rectangle(x + 3, y + 3, x + lado - 3, y + lado - 3,
                                      fill=PAINEL, outline=CIANO_ESCURO)
        feitos = espiral[:min(passo["i"], len(espiral) - 1) + 1]
        for i in range(len(feitos) - 1):
            x1, y1 = centro(feitos[i])
            x2, y2 = centro(feitos[i + 1])
            tela.create_line(x1, y1, x2, y2, fill=CIANO, width=12, capstyle="round")
        x, y = centro(feitos[-1])
        tela.create_oval(x - 11, y - 11, x + 11, y + 11, fill=MAGENTA, outline="")
        passo["i"] = (passo["i"] + 1) % (len(espiral) + 6)   # para um pouco no fim e recomeça
        resultado["animacao"] = janela.after(160, quadro)

    quadro()
    return tela


def tela_texto(titulo, texto):
    janela = nova_janela(titulo)
    cabecalho(janela.conteudo, titulo)
    rotulo(janela.conteudo, texto, 11, fonte="Consolas").pack(anchor="w")
    borda, _ = botao(janela.conteudo, "Voltar", janela.destroy, 12)
    borda.pack(anchor="w", pady=(18, 0))
    janela.bind("<Key>", lambda e: janela.destroy())
    abrir(janela)


def aviso(texto):
    tela_texto("AVISO", texto)


def confirmar(pergunta):
    return escolher_opcao("CONFIRMAR", ["Sim", "Não"], pergunta, inicial=1, valor_ao_fechar=1) == 0


def pedir_texto(titulo, pergunta):
    """Pede um texto numa caixa de digitação. Devolve "" se o usuário cancelar."""
    resultado = {"texto": ""}
    janela = nova_janela(titulo)
    cabecalho(janela.conteudo, titulo)
    rotulo(janela.conteudo, pergunta).pack(anchor="w")
    campo = tk.Entry(janela.conteudo, font=(FONTE, 14), bg=PAINEL, fg="white", insertbackground=CIANO,
                     relief="flat", width=24)
    campo.pack(anchor="w", pady=10, ipady=6)

    def ok(evento=None):
        resultado["texto"] = campo.get().strip()
        janela.destroy()

    linha = tk.Frame(janela.conteudo, bg=FUNDO)
    linha.pack(anchor="w")
    borda, _ = botao(linha, "Confirmar", ok, 10)
    borda.grid(row=0, column=0, padx=(0, 10))
    borda, _ = botao(linha, "Cancelar", janela.destroy, 10)
    borda.grid(row=0, column=1)
    campo.bind("<Return>", ok)
    janela.after(100, campo.focus_force)
    abrir(janela)
    return resultado["texto"]


# ---------- Jogo ----------

def formatar_tempo(segundos):
    segundos = int(segundos)
    return f"{segundos // 60:02d}:{segundos % 60:02d}"


def jogar(estado, config, processar_tecla):
    """
    Janela do jogo (-gui-jogo). Usa a mesma função processar_tecla da interface
    de console, então as regras, o registro e o save automático são os mesmos.
    Devolve "pausa" (tecla p ou janela fechada) ou "menu" (jogo vencido).
    """
    resultado = {"acao": "pausa", "ultimo": time.time(), "aguardando": False, "relogio": None}
    janela = nova_janela("Jogo")

    topo = tk.Frame(janela.conteudo, bg=FUNDO)
    topo.pack(fill="x")
    titulo = rotulo(topo, "", 22, CIANO, True)
    titulo.pack(anchor="w")
    info = rotulo(topo, "", 11)
    info.pack(anchor="w")
    relogio = rotulo(topo, "", 11, CIANO)
    relogio.pack(anchor="w", pady=(0, 10))

    tela = tk.Canvas(janela.conteudo, bg=FUNDO, highlightthickness=0)
    tela.pack()
    mensagem = rotulo(janela.conteudo, "", 12, MAGENTA)
    mensagem.pack(anchor="w", pady=(10, 0))
    rotulo(janela.conteudo, "w/a/s/d ou setas: mover   clique: andar/voltar   z: desfazer   "
                   "r: recomeçar   p: pausar   F11: tela cheia", 9, CIANO_ESCURO).pack(anchor="w", pady=(6, 0))

    def medidas():
        n = estado["tamanho"]
        # As casas crescem conforme a altura da tela (entre 40 e 110 pixels)
        lado = max(40, min(110, (janela.winfo_screenheight() - 300) // n))
        return n, lado, 14

    def centro(cel, lado, margem):
        return margem + cel[1] * lado + lado / 2, margem + cel[0] * lado + lado / 2

    def desenhar():
        n, lado, m = medidas()
        tela.config(width=n * lado + 2 * m, height=n * lado + 2 * m)
        tela.delete("all")
        titulo.config(text=f"NÍVEL {estado['nivel'] + 1} de {mecanica.total_niveis()}")
        janela.title(f"Tracer - Nível {estado['nivel'] + 1}")
        proximo = "—" if mecanica.nivel_completo(estado) else mecanica.proximo_numero(estado)
        info.config(text=f"jogadas: {estado['jogadas']}    próximo número: {proximo}")
        for l in range(n):
            for c in range(n):
                x, y = m + c * lado, m + l * lado
                cor = "#10284A" if (l, c) in estado["caminho"] else PAINEL
                tela.create_rectangle(x, y, x + lado, y + lado, fill=cor, outline=CIANO_ESCURO)
        caminho = estado["caminho"]
        for i in range(len(caminho) - 1):
            x1, y1 = centro(caminho[i], lado, m)
            x2, y2 = centro(caminho[i + 1], lado, m)
            tela.create_line(x1, y1, x2, y2, fill=CIANO, width=lado // 4, capstyle="round")
        for a, b in estado["paredes"]:
            if a[0] == b[0]:        # vizinhas na mesma linha: parede vertical
                x = m + max(a[1], b[1]) * lado
                y = m + a[0] * lado
                tela.create_line(x, y, x, y + lado, fill=TEXTO, width=6, capstyle="round")
            else:                   # vizinhas na mesma coluna: parede horizontal
                x = m + a[1] * lado
                y = m + max(a[0], b[0]) * lado
                tela.create_line(x, y, x + lado, y, fill=TEXTO, width=6, capstyle="round")
        tela.create_rectangle(m, m, m + n * lado, m + n * lado, outline=TEXTO, width=4)
        raio = lado * 0.3
        for cel in estado["numeros"]:
            x, y = centro(cel, lado, m)
            alcancado = cel in caminho
            tela.create_oval(x - raio, y - raio, x + raio, y + raio,
                             fill=CIANO if alcancado else CIANO_ESCURO, outline=CIANO, width=2)
            tela.create_text(x, y, text=str(estado["numeros"][cel]),
                             fill=FUNDO if alcancado else "white", font=(FONTE, int(lado / 4), "bold"))
        x, y = centro(caminho[-1], lado, m)
        r = lado * 0.14
        tela.create_oval(x - r, y - r, x + r, y + r, fill=MAGENTA, outline="")

    def atualizar_relogio():
        extra = 0 if resultado["aguardando"] else time.time() - resultado["ultimo"]
        relogio.config(text=f"tempo do nível: {formatar_tempo(estado['tempo_nivel'] + extra)}"
                            f"    tempo total: {formatar_tempo(estado['tempo_total'] + extra)}")
        resultado["relogio"] = janela.after(250, atualizar_relogio)

    def contar_tempo():
        agora = time.time()
        mecanica.adicionar_tempo(estado, agora - resultado["ultimo"])
        resultado["ultimo"] = agora

    def fechar(acao):
        resultado["acao"] = acao
        if resultado["relogio"] is not None:
            janela.after_cancel(resultado["relogio"])
        janela.destroy()

    def executar(tecla):
        if resultado["aguardando"]:
            return
        contar_tempo()
        if tecla == "p":
            fechar("pausa")
            return
        mensagem.config(text=processar_tecla(estado, tecla, config))
        if mecanica.nivel_completo(estado):
            concluir_nivel()
        desenhar()

    def concluir_nivel():
        resultado["aguardando"] = True
        if mecanica.jogo_terminou(estado):
            desenhar()
            janela.after(400, vitoria)
            return
        from interface import registrar_nivel_completo
        registrar_nivel_completo(estado)
        mensagem.config(text=f"Nível {estado['nivel'] + 1} completo em "
                             f"{formatar_tempo(estado['tempos'][-1])}!  Enter para continuar")

    def continuar():
        from interface import passar_de_nivel
        passar_de_nivel(estado, config)
        resultado["aguardando"] = False
        resultado["ultimo"] = time.time()
        mensagem.config(text="")
        desenhar()

    def vitoria():
        arquivos.registrar("VITÓRIA", f"tempo total {formatar_tempo(estado['tempo_total'])}")
        for filho in janela.conteudo.winfo_children():
            filho.destroy()
        cabecalho(janela.conteudo, "VOCÊ VENCEU!", "os 10 níveis foram completados")
        primeiro = mecanica.total_niveis() - len(estado["tempos"])
        linhas = ""
        for i in range(len(estado["tempos"])):
            linhas += f"Nível {primeiro + i + 1:2d}   {formatar_tempo(estado['tempos'][i])}\n"
        linhas += f"\nTotal      {formatar_tempo(estado['tempo_total'])}\n"
        linhas += f"Jogadas    {estado['jogadas_total']}"
        rotulo(janela.conteudo, linhas, 12, fonte="Consolas").pack(anchor="w")
        rotulo(janela.conteudo, "\nDigite suas iniciais (3 letras):", 12, CIANO).pack(anchor="w")
        campo = tk.Entry(janela.conteudo, font=(FONTE, 18), bg=PAINEL, fg="white", width=5,
                         insertbackground=CIANO, relief="flat", justify="center")
        campo.pack(anchor="w", pady=8, ipady=4)
        erro = rotulo(janela.conteudo, "", 10, MAGENTA)
        erro.pack(anchor="w")

        def registrar(evento=None):
            iniciais = campo.get().strip().upper()
            if len(iniciais) == 3 and iniciais.isalpha():
                estado["nome"] = iniciais
                arquivos.registrar_partida(estado)
                resultado["posicao"] = arquivos.posicao_no_ranking(estado)
                resultado["vitoria"] = True
                fechar("menu")
            else:
                erro.config(text="Use exatamente 3 letras.")

        borda, _ = botao(janela.conteudo, "Registrar no histórico", registrar, 22)
        borda.pack(anchor="w", pady=(8, 0))
        janela.unbind("<Key>")
        campo.bind("<Return>", registrar)
        janela.protocol("WM_DELETE_WINDOW", registrar)
        campo.focus_force()

    def tecla(evento):
        nome = evento.keysym.lower()
        if resultado["aguardando"] and nome == "return":
            continuar()
            return
        nome = {"up": "w", "down": "s", "left": "a", "right": "d"}.get(nome, nome)
        if nome in ("w", "a", "s", "d", "z", "r", "p"):
            executar(nome)

    def clique(evento):
        n, lado, m = medidas()
        cel = (int((evento.y - m) // lado), int((evento.x - m) // lado))
        ponta = estado["caminho"][-1]
        if len(estado["caminho"]) > 1 and cel == estado["caminho"][-2]:
            executar("z")
            return
        direcoes = {(-1, 0): "w", (1, 0): "s", (0, -1): "a", (0, 1): "d"}
        passo = (cel[0] - ponta[0], cel[1] - ponta[1])
        if passo in direcoes:
            executar(direcoes[passo])

    janela.bind("<Key>", tecla)
    tela.bind("<Button-1>", clique)
    def fechar_no_x():
        if resultado["aguardando"]:
            continuar()
        executar("p")

    janela.protocol("WM_DELETE_WINDOW", fechar_no_x)
    desenhar()
    atualizar_relogio()
    abrir(janela)
    if resultado.get("vitoria"):
        from interface import texto_posicao
        aviso(f"Resultado registrado no histórico, {estado['nome']}!\n\n"
              f"{texto_posicao(resultado['posicao'])}")
    return resultado["acao"]