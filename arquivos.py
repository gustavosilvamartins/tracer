# Módulo de arquivos do Tracer.
# Código adaptado de sugestão gerada com o Claude (Anthropic), acessado em 28/09/2026.
import os
import time
import mecanica

PASTA_SAVES = "saves"
PASTA_HISTORICO = "historico"
PASTA_LOGS = "logs"
ARQUIVO_HISTORICO = os.path.join(PASTA_HISTORICO, "historico.txt")
ARQUIVO_REGISTRO = os.path.join(PASTA_LOGS, "registro.log")


def data_hora():
    """Data e hora atuais em texto, para o histórico e o registro."""
    return time.strftime("%d/%m/%Y %H:%M:%S")


def caminho_save(nome):
    """Caminho completo de um save a partir do nome sem extensão (regras 3.3.3 e 3.3.4)."""
    return os.path.join(PASTA_SAVES, nome + ".save")


def preparar_pasta(pasta=PASTA_SAVES):
    """Cria a pasta se ela ainda não existir (por padrão, a de saves, regra 3.3.1)."""
    if not os.path.exists(pasta):
        os.mkdir(pasta)


# ---------- Registro de jogadas e erros (regra 3.1.1.4) ----------

def registrar(tipo, texto):
    """Acrescenta uma linha ao registro. O arquivo só cresce, nunca é sobrescrito."""
    try:
        preparar_pasta(PASTA_LOGS)
        with open(ARQUIVO_REGISTRO, "a", encoding="utf-8") as arquivo:
            arquivo.write(f"[{data_hora()}] {tipo}: {texto}\n")
    except OSError:
        pass  # se nem o registro puder ser escrito, o jogo continua mesmo assim


# ---------- Saves ----------

def estado_para_texto(estado):
    """
    Converte o estado em linhas "chave=valor".
    O tabuleiro (números e paredes) não é salvo: ele vem do nível, na mecanica.py.
    """
    celulas = []
    for linha, coluna in estado["caminho"]:
        celulas.append(f"{linha},{coluna}")
    return (f"nivel={estado['nivel']}\n"
            f"caminho={';'.join(celulas)}\n"
            f"jogadas={estado['jogadas']}\n"
            f"jogadas_total={estado['jogadas_total']}\n"
            f"tempo_nivel={estado['tempo_nivel']}\n"
            f"tempo_total={estado['tempo_total']}\n"
            f"tempos={';'.join(str(t) for t in estado['tempos'])}\n"
            f"nome={estado['nome']}\n")


def texto_para_estado(texto):
    """
    Reconstrói o estado a partir do texto de um save.
    Refaz o caminho jogada por jogada com a mecanica.py, o que também garante
    que um arquivo alterado à mão não gere um estado impossível.
    Lança ValueError se o conteúdo for inválido.
    """
    dados = {}
    for linha in texto.splitlines():
        if "=" in linha:
            chave, valor = linha.split("=", 1)
            dados[chave] = valor

    nivel = int(dados["nivel"])
    if not (0 <= nivel < mecanica.total_niveis()):
        raise ValueError("nível inexistente")

    estado = mecanica.novo_jogo()
    mecanica.carregar_nivel(estado, nivel)

    celulas = dados["caminho"].split(";")
    for i in range(1, len(celulas)):        # a primeira célula é o número 1
        linha, coluna = celulas[i].split(",")
        valido, mensagem = mecanica.fazer_jogada(estado, (int(linha), int(coluna)))
        if not valido:
            raise ValueError(mensagem)

    estado["jogadas"] = int(dados["jogadas"])
    estado["jogadas_total"] = int(dados["jogadas_total"])
    estado["tempo_nivel"] = float(dados["tempo_nivel"])
    estado["tempo_total"] = float(dados["tempo_total"])
    estado["tempos"] = []
    if dados["tempos"] != "":
        for t in dados["tempos"].split(";"):
            estado["tempos"].append(float(t))
    estado["nome"] = dados.get("nome", "")
    return estado


def salvar_jogo(estado, nome):
    """Salva o estado em saves/<nome>.save. Devolve (True/False, mensagem)."""
    try:
        preparar_pasta()
        with open(caminho_save(nome), "w", encoding="utf-8") as arquivo:
            arquivo.write(estado_para_texto(estado))
        return True, f"Jogo salvo em {caminho_save(nome)}."
    except OSError as erro:
        registrar("ERRO", f"falha ao salvar '{nome}': {erro}")
        return False, "Não foi possível salvar o jogo."


def carregar_jogo(nome):
    """Carrega saves/<nome>.save. Devolve (estado ou None, mensagem)."""
    try:
        with open(caminho_save(nome), "r", encoding="utf-8") as arquivo:
            estado = texto_para_estado(arquivo.read())
        # Um save de partida já vencida (por exemplo, o autosave feito na última jogada)
        # não pode ser jogado de novo, senão a vitória seria registrada outra vez
        if mecanica.jogo_terminou(estado):
            registrar("AVISO", f"save '{nome}' é de uma partida já concluída")
            return None, f"O save '{nome}' é de uma partida já concluída. Comece um novo jogo."
        registrar("CARREGAR", f"save '{nome}' carregado")
        return estado, f"Save '{nome}' carregado."
    except FileNotFoundError:
        registrar("ERRO", f"save '{nome}' não encontrado")
        return None, f"O save '{nome}' não existe."
    except (KeyError, ValueError) as erro:
        registrar("ERRO", f"save '{nome}' inválido: {erro}")
        return None, f"O save '{nome}' está corrompido."
    except OSError as erro:
        registrar("ERRO", f"falha ao ler '{nome}': {erro}")
        return None, "Não foi possível ler o save."


def save_existe(nome):
    """Verifica se já existe um save com esse nome (para avisar da sobrescrita)."""
    return os.path.exists(caminho_save(nome))


def listar_saves():
    """Lista os nomes (sem extensão) de todos os saves da pasta (regra 3.2.4a)."""
    preparar_pasta()
    nomes = []
    for arquivo in sorted(os.listdir(PASTA_SAVES)):
        if arquivo.endswith(".save"):
            nomes.append(arquivo[:-len(".save")])
    return nomes


def salvar_automatico(estado, nome_autosave):
    """Save automático após cada jogada, em arquivo próprio (regra 3.3.2)."""
    return salvar_jogo(estado, nome_autosave)


# ---------- Histórico de partidas (regra 3.3.5) ----------

def registrar_partida(estado):
    """Acrescenta uma linha ao histórico quando uma partida termina."""
    niveis = estado["nivel"] + 1 if mecanica.nivel_completo(estado) else estado["nivel"]
    tempos = ",".join(str(int(t)) for t in estado["tempos"])
    linha = (f"{estado['nome']};{niveis};{estado['jogadas_total']};"
             f"{int(estado['tempo_total'])};{tempos};{data_hora()}\n")
    try:
        preparar_pasta(PASTA_HISTORICO)
        with open(ARQUIVO_HISTORICO, "a", encoding="utf-8") as arquivo:
            arquivo.write(linha)
        registrar("FIM", f"partida de {estado['nome']} registrada no histórico")
        return True
    except OSError as erro:
        registrar("ERRO", f"falha ao gravar o histórico: {erro}")
        return False


def ler_historico():
    """
    Devolve a lista de partidas passadas, cada uma como dicionário.
    Linhas com defeito são ignoradas (e anotadas no registro).
    """
    partidas = []
    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as arquivo:
            for linha in arquivo.readlines():
                partes = linha.strip().split(";")
                if len(partes) != 6:
                    continue
                try:
                    tempos = []
                    if partes[4] != "":
                        for t in partes[4].split(","):
                            tempos.append(int(t))
                    partidas.append({"nome": partes[0],
                                     "niveis": int(partes[1]),
                                     "jogadas": int(partes[2]),
                                     "tempo": int(partes[3]),
                                     "tempos": tempos,
                                     "data": partes[5]})
                except ValueError:
                    registrar("ERRO", f"linha inválida no histórico: {linha.strip()}")
    except FileNotFoundError:
        pass  # nenhuma partida registrada ainda
    return partidas