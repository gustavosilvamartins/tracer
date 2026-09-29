# Tracer

Jogo de lógica para o terminal, feito em Python como projeto final da disciplina de **Algoritmos Computacionais** (UERJ). Inspirado no jogo [Trace](https://wordle.global/ltg/trace).

> Versão 1.0: jogo completo no console.

## Como se joga

O objetivo é desenhar **uma única linha** que passe por **todas as casas** do tabuleiro, cada uma exatamente uma vez.

- A linha começa no número **1** e anda para cima, baixo, esquerda ou direita (nunca na diagonal).
- Os números devem ser visitados em **ordem crescente**: 1, 2, 3...
- A linha termina no **maior número**, depois de cobrir todas as casas.
- As bordas dentro do tabuleiro são **paredes** e não podem ser atravessadas.

São **10 níveis** de dificuldade crescente, de tabuleiros 4x4 até 7x7. Cada tabuleiro tem uma única solução. O jogo termina ao completar o décimo nível, e o tempo e as jogadas de cada nível ficam registrados no histórico.

```
  NÍVEL 2 de 10
  ─────────────

  jogadas: 0    próximo número: 2
  tempo do nível: 00:00   tempo total: 00:00

  +───+───+───+───+
  │ ·   1   4   · │
  +   +   +   +   +
  │ ·   2 │ ·   · │
  +   +   +   +   +
  │ ·   ·   3   · │
  +   +   +   +   +
  │ ·   ·   ·   · │
  +───+───+───+───+
```

## Requisitos

- Python 3
- **Windows:** nada a instalar.
- **Linux:** a biblioteca `getch`, usada para ler as teclas sem precisar apertar Enter:

```
pip install getch
```

## Como executar

```
git clone https://github.com/gustavosilvamartins/tracer.git
cd tracer
python tracer.py
```

Rode sempre num terminal de verdade (Prompt de Comando, PowerShell ou o terminal integrado do VS Code). A leitura de teclas não funciona no IDLE nem na aba "Output" do VS Code.

### Argumentos de console

É possível pular os menus usando argumentos:

| Argumento | O que faz |
|---|---|
| `-novo` | Começa um jogo novo direto, sem passar pelo menu |
| `-carregar NOME` | Carrega o save `saves/NOME.save` direto |
| `-autosave NOME` | Usa `saves/NOME.save` como arquivo de save automático (padrão: `autosave`) |
| `-nivel N` | Define o nível inicial, de 1 a 10 (padrão: 1) |
| `-h` | Mostra a ajuda com todos os argumentos |

Exemplos:

```
python tracer.py -novo
python tracer.py -novo -nivel 5
python tracer.py -carregar minha_partida
```

## Controles

| Tecla | No jogo | Nos menus |
|---|---|---|
| `w` `a` `s` `d` (ou setas, no Windows) | Move a linha | `w`/`s` escolhem a opção |
| `Enter` | | Confirma a opção |
| `z` | Desfaz o último passo | |
| `r` | Recomeça o nível atual | |
| `p` | Abre o menu de pausa | |

## Menus

- **Menu principal:** iniciar jogo, carregar jogo, histórico de partidas, configurações, regras, créditos e sair.
- **Pausa:** voltar ao jogo, iniciar novo jogo, carregar, salvar, voltar ao menu principal e sair.
- **Arquivos:** lista os saves existentes, cria saves novos e pede confirmação antes de sobrescrever um save.
- **Configurações:** nível inicial e nome do arquivo de save automático.

Ao completar os 10 níveis, o jogo mostra o tempo de cada nível e o total, e pede as suas iniciais de três letras, no estilo dos fliperamas antigos, para registrar a partida no histórico.

## Arquivos gerados

As pastas abaixo são criadas automaticamente na primeira vez que o jogo precisa delas:

| Pasta | Conteúdo |
|---|---|
| `saves/` | Saves manuais e o save automático, feito depois de cada jogada |
| `historico/` | `historico.txt`, com uma linha por partida vencida |
| `logs/` | `registro.log`, com todas as jogadas e erros (só é ampliado, nunca sobrescrito) |

## Estrutura do código

| Arquivo | Responsabilidade |
|---|---|
| `tracer.py` | Ponto de entrada: lê os argumentos com `argparse` e decide se abre o menu, começa um jogo ou carrega um save |
| `mecanica.py` | Regras do jogo: os 10 tabuleiros, o dicionário de estado, validação das jogadas e verificação de fim de nível e de jogo |
| `interface.py` | Tudo o que é mostrado ou pedido ao jogador: menus, desenho do tabuleiro e loop do jogo |
| `arquivos.py` | Saves, save automático, histórico de partidas e registro de jogadas e erros |

## Créditos

- **Autor:** Gustavo Martins
- **Disciplina:** Algoritmos Computacionais, UERJ
- **Inspiração:** Trace ([wordle.global](https://wordle.global/ltg/trace))
- Partes do código foram desenvolvidas com auxílio do Claude (Anthropic), como indicado nos comentários de cada arquivo.
