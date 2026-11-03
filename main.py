
from cadastro_cliente import CadastroClientes
from interface import executar_menu


def main():
    sistema = CadastroClientes()
    executar_menu(sistema)


if __name__ == '__main__':
    main()
