# Código adaptado de sugestão gerada com o Claude (Anthropic), acessado em 28/09/2026,
# a partir do exemplo argumentos_console_argparse.py visto em aula.
import sys
import argparse
import arquivos
import interface
import mecanica


def init_parser():
    parser = argparse.ArgumentParser(prog='tracer',
                                     description='''Tracer: desenhe uma linha que passa
                                     por todas as células, visitando os números em ordem.''')

    # 3.2.1.1 - começar um jogo novo sem passar por menus
    parser.add_argument('-novo',
                        action='store_true',
                        help='inicia um jogo novo direto, sem passar pelo menu.')

    # 3.2.1.2 - carregar um jogo sem passar por menus
    parser.add_argument('-carregar',
                        type=str,
                        metavar='NOME',
                        help='carrega o save NOME.save da pasta de saves.')

    # 3.2.1.3 - escolher o arquivo de save automático
    parser.add_argument('-autosave',
                        type=str,
                        default='autosave',
                        metavar='NOME',
                        help='arquivo usado nos saves automáticos (padrão: autosave).')

    # 3.2.1.4 - opções do menu de configurações (exemplo: ajustar às do jogo)
    parser.add_argument('-nivel',
                        type=int,
                        default=1,
                        metavar='N',
                        help='nível em que o jogo começa, de 1 a 10 (padrão: 1).')

    # Seção 6 - interfaces gráficas (pontuação extra)
    parser.add_argument('-gui', action='store_true',
                        help='todo o jogo em interface gráfica.')
    parser.add_argument('-gui-principal', action='store_true',
                        help='só o menu principal em interface gráfica.')
    parser.add_argument('-gui-pause', action='store_true',
                        help='só o menu de pause em interface gráfica.')
    parser.add_argument('-gui-arquivos', action='store_true',
                        help='só o menu de arquivos em interface gráfica.')
    parser.add_argument('-gui-jogo', action='store_true',
                        help='só o jogo em interface gráfica.')

    return parser


def ler_argumentos(parser, args):
    argumentos = parser.parse_args(args[1:])

    # -gui equivale a todas as outras opções de GUI juntas
    if argumentos.gui:
        argumentos.gui_principal = True
        argumentos.gui_pause = True
        argumentos.gui_arquivos = True
        argumentos.gui_jogo = True

    if argumentos.novo and argumentos.carregar is not None:
        parser.error('use -novo ou -carregar, não os dois juntos.')

    if not (1 <= argumentos.nivel <= mecanica.total_niveis()):
        parser.error(f'o nível deve estar entre 1 e {mecanica.total_niveis()}.')

    return argumentos


def main(args=sys.argv):
    parser = init_parser()                    # argparse é o primeiro passo (3.2.1)
    argumentos = ler_argumentos(parser, args)

    # Configurações do jogo, que também podem ser mudadas no menu (regra 3.2.1.4)
    config = {"nivel": argumentos.nivel - 1, "autosave": argumentos.autosave}

    acao = "menu"
    if argumentos.carregar is not None:
        estado, mensagem = arquivos.carregar_jogo(argumentos.carregar)
        if estado is not None:
            acao = interface.loop_do_jogo(estado, config)
        else:
            print(mensagem)
            interface.esperar_tecla("Pressione qualquer tecla para abrir o menu.")
    elif argumentos.novo:
        acao = interface.loop_do_jogo(interface.novo_jogo(config), config)

    if acao != "sair":
        interface.menu_principal(config)

if __name__ == "__main__":
    main()