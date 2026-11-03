
from modelos import Cliente


def exibir_menu():
    print('\n===== CADASTRO DE CLIENTES =====')
    print('1 - Cadastrar cliente')
    print('2 - Listar clientes')
    print('3 - Alterar titular')
    print('4 - Alterar endereço')
    print('5 - Excluir cliente')
    print('0 - Sair')

    return input('Escolha uma opção: ').strip()


def cadastrar_novo_cliente(sistema):
    print('\n===== NOVO CLIENTE =====')

    nome = input('Nome: ').strip()

    try:
        ano = int(input('Ano de nascimento: '))
        cpf = input('CPF: ').strip()
        rua = input('Rua: ').strip()
        numero = input('Número: ').strip()

        cliente = Cliente(nome, ano, cpf)
        cliente.inserir_endereco(rua, numero)

        sistema.cadastrar_cliente(cliente)

        print('\nCliente cadastrado com sucesso!')
        print(f'Código do cliente: {cliente.id}')

    except ValueError as erro:
        print(f'Erro ao cadastrar: {erro}')


def alterar_titular_interface(sistema):
    print('\n===== ALTERAR TITULAR =====')

    cpf_atual = input('CPF do titular atual: ').strip()

    try:
        cliente = sistema.buscar_cliente(cpf_atual)

        if cliente is None:
            print('Cliente não encontrado.')
            return

        print('\n===== DADOS ATUAIS =====')
        cliente.emitir_dados()

        print('\n===== NOVOS DADOS =====')

        novo_nome = input('Novo nome: ').strip()
        novo_ano = int(input('Novo ano de nascimento: '))
        novo_cpf = input('Novo CPF: ').strip()

        confirmar = input(
            'Confirmar alteração do titular? (S/N): '
        ).strip().upper()

        if confirmar != 'S':
            print('Alteração cancelada.')
            return

        atualizado = sistema.alterar_titular(
            cpf_atual,
            novo_nome,
            novo_ano,
            novo_cpf
        )

        print('\nTitular alterado com sucesso!')
        atualizado.emitir_dados()

    except ValueError as erro:
        print(f'Erro ao alterar titular: {erro}')


def alterar_endereco_interface(sistema):
    print('\n===== ALTERAR ENDEREÇO =====')

    if not sistema.listar_clientes_numerados():
        return

    try:
        opcao = int(
            input('\nSelecione o cliente (0 para voltar): ')
        )

        if opcao == 0:
            return

        cliente = sistema.selecionar_cliente(opcao)

        print(f'\nCliente: {cliente.nome}')

        if not cliente.enderecos:
            print('Nenhum endereço cadastrado.')
            return

        print('\n===== ENDEREÇOS =====')

        for indice, endereco in enumerate(
            cliente.enderecos, start=1
        ):
            print(
                f'{indice} - {endereco.rua}, '
                f'Nº {endereco.numero}'
            )

        escolha = int(
            input('\nSelecione o endereço (0 para voltar): ')
        )

        if escolha == 0:
            return

        if not 1 <= escolha <= len(cliente.enderecos):
            print('Endereço inválido.')
            return

        endereco = cliente.enderecos[escolha - 1]

        nova_rua = input('Nova rua: ').strip()
        novo_numero = input('Novo número: ').strip()

        confirmar = input(
            'Confirmar alteração do endereço? (S/N): '
        ).strip().upper()

        if confirmar != 'S':
            print('Alteração cancelada.')
            return

        sistema.alterar_endereco(
            cliente.id,
            endereco.id,
            nova_rua,
            novo_numero
        )

        print('\nEndereço alterado com sucesso!')

    except ValueError as erro:
        print(f'Erro ao alterar endereço: {erro}')


def excluir_cliente_interface(sistema):
    print('\n===== EXCLUIR CLIENTE =====')

    if not sistema.listar_clientes_numerados():
        return

    try:
        opcao = int(
            input('\nSelecione o cliente (0 para voltar): ')
        )

        if opcao == 0:
            return

        cliente = sistema.selecionar_cliente(opcao)

        print('\n===== CLIENTE SELECIONADO =====')
        print(f'Código: {cliente.id}')
        cliente.emitir_dados()

        print('\nATENÇÃO!')
        print('O cliente e todos os seus endereços serão excluídos.')

        confirmar = input(
            'Digite EXCLUIR para confirmar: '
        ).strip()

        if confirmar != 'EXCLUIR':
            print('Exclusão cancelada.')
            return

        sistema.excluir_cliente(cliente.id)

        print('\nCliente excluído com sucesso!')

    except ValueError as erro:
        print(f'Erro ao excluir cliente: {erro}')


def executar_menu(sistema):
    while True:
        opcao = exibir_menu()

        if opcao == '1':
            cadastrar_novo_cliente(sistema)

        elif opcao == '2':
            sistema.listar_clientes()

        elif opcao == '3':
            alterar_titular_interface(sistema)

        elif opcao == '4':
            alterar_endereco_interface(sistema)

        elif opcao == '5':
            excluir_cliente_interface(sistema)

        elif opcao == '0':
            print('Encerrando sistema...')
            break

        else:
            print('Opção inválida ou ainda não implementada.')
