
import sqlite3
from contextlib import closing
from pathlib import Path

from modelos import Cliente, Endereco
from validacoes import normalizar_cpf


class CadastroClientes:
    def __init__(self):
        self.caminho_banco = (
            Path(__file__).resolve().parent / 'clientes.db'
        )
        self.criar_tabelas()

    def conectar(self):
        conexao = sqlite3.connect(self.caminho_banco)
        conexao.row_factory = sqlite3.Row
        conexao.execute('PRAGMA foreign_keys = ON')
        return conexao

    def criar_tabelas(self):
        with closing(self.conectar()) as conexao:
            with conexao:
                conexao.execute('''
                    CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        ano_nascimento INTEGER NOT NULL,
                        cpf TEXT NOT NULL UNIQUE,
                        telefone TEXT NOT NULL DEFAULT '',
                        email TEXT NOT NULL DEFAULT ''
                    )
                ''')

                conexao.execute('''
                    CREATE TABLE IF NOT EXISTS enderecos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente_id INTEGER NOT NULL,
                        rua TEXT NOT NULL,
                        numero TEXT NOT NULL,
                        FOREIGN KEY (cliente_id)
                            REFERENCES clientes(id)
                            ON DELETE CASCADE
                    )
                ''')

                colunas = {
                    coluna['name']
                    for coluna in conexao.execute(
                        'PRAGMA table_info(clientes)'
                    ).fetchall()
                }

                if 'telefone' not in colunas:
                    conexao.execute('''
                        ALTER TABLE clientes
                        ADD COLUMN telefone TEXT NOT NULL DEFAULT ''
                    ''')

                if 'email' not in colunas:
                    conexao.execute('''
                        ALTER TABLE clientes
                        ADD COLUMN email TEXT NOT NULL DEFAULT ''
                    ''')

    def montar_cliente(self, conexao, registro):
        cliente = Cliente(
            registro['nome'],
            registro['ano_nascimento'],
            registro['cpf'],
            registro['telefone'],
            registro['email']
        )

        cliente.id = registro['id']

        enderecos = conexao.execute(
            '''
            SELECT id, rua, numero
            FROM enderecos
            WHERE cliente_id = ?
            ORDER BY id
            ''',
            (cliente.id,)
        ).fetchall()

        for dados in enderecos:
            endereco = Endereco(
                dados['rua'],
                dados['numero']
            )
            endereco.id = dados['id']
            cliente.enderecos.append(endereco)

        return cliente

    def cadastrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise TypeError('O objeto deve ser um Cliente.')

        validado = Cliente(
            cliente.nome,
            cliente.ano_nascimento,
            cliente.cpf,
            cliente.telefone,
            cliente.email
        )

        with closing(self.conectar()) as conexao:
            try:
                with conexao:
                    cursor = conexao.execute(
                        '''
                        INSERT INTO clientes (
                            nome, ano_nascimento, cpf,
                            telefone, email
                        )
                        VALUES (?, ?, ?, ?, ?)
                        ''',
                        (
                            validado.nome,
                            validado.ano_nascimento,
                            validado.cpf,
                            validado.telefone,
                            validado.email
                        )
                    )

                    cliente_id = cursor.lastrowid

                    for endereco in cliente.enderecos:
                        novo = Endereco(
                            endereco.rua,
                            endereco.numero
                        )

                        conexao.execute(
                            '''
                            INSERT INTO enderecos (
                                cliente_id, rua, numero
                            )
                            VALUES (?, ?, ?)
                            ''',
                            (
                                cliente_id,
                                novo.rua,
                                novo.numero
                            )
                        )

            except sqlite3.IntegrityError as erro:
                raise ValueError(
                    'CPF já cadastrado ou dados inválidos.'
                ) from erro

            cliente.id = cliente_id

    def buscar_cliente(self, cpf):
        cpf = normalizar_cpf(cpf)

        with closing(self.conectar()) as conexao:
            registro = conexao.execute(
                'SELECT * FROM clientes WHERE cpf = ?',
                (cpf,)
            ).fetchone()

            if registro is None:
                return None

            return self.montar_cliente(conexao, registro)

    def buscar_por_id(self, cliente_id):
        with closing(self.conectar()) as conexao:
            registro = conexao.execute(
                'SELECT * FROM clientes WHERE id = ?',
                (cliente_id,)
            ).fetchone()

            if registro is None:
                return None

            return self.montar_cliente(conexao, registro)

    def listar_todos(self):
        with closing(self.conectar()) as conexao:
            registros = conexao.execute(
                'SELECT * FROM clientes ORDER BY id'
            ).fetchall()

            return [
                self.montar_cliente(conexao, registro)
                for registro in registros
            ]

    def listar_clientes(self):
        clientes = self.listar_todos()

        if not clientes:
            print('Nenhum cliente cadastrado.')
            return

        for cliente in clientes:
            print(f'Código: {cliente.id}')
            cliente.emitir_dados()
            print('-' * 30)

    def listar_clientes_numerados(self):
        clientes = self.listar_todos()

        if not clientes:
            print('Nenhum cliente cadastrado.')
            return False

        for indice, cliente in enumerate(clientes, start=1):
            print(f'{indice} - {cliente.nome}')

        return True

    def selecionar_cliente(self, numero):
        clientes = self.listar_todos()

        if not 1 <= numero <= len(clientes):
            raise ValueError('Cliente não encontrado.')

        return clientes[numero - 1]

    def alterar_titular(
        self,
        cpf_atual,
        nome,
        ano_nascimento,
        cpf_novo,
        telefone=None,
        email=None
    ):
        cliente = self.buscar_cliente(cpf_atual)

        if cliente is None:
            raise ValueError('Cliente não encontrado.')

        novo = Cliente(
            nome,
            ano_nascimento,
            cpf_novo,
            cliente.telefone if telefone is None else telefone,
            cliente.email if email is None else email
        )

        with closing(self.conectar()) as conexao:
            try:
                with conexao:
                    conexao.execute(
                        '''
                        UPDATE clientes
                        SET nome = ?,
                            ano_nascimento = ?,
                            cpf = ?,
                            telefone = ?,
                            email = ?
                        WHERE id = ?
                        ''',
                        (
                            novo.nome,
                            novo.ano_nascimento,
                            novo.cpf,
                            novo.telefone,
                            novo.email,
                            cliente.id
                        )
                    )
            except sqlite3.IntegrityError as erro:
                raise ValueError(
                    'CPF já cadastrado em outro cliente.'
                ) from erro

        return self.buscar_por_id(cliente.id)

    def adicionar_endereco(self, cliente_id, rua, numero):
        endereco = Endereco(rua, numero)

        with closing(self.conectar()) as conexao:
            with conexao:
                existe = conexao.execute(
                    'SELECT id FROM clientes WHERE id = ?',
                    (cliente_id,)
                ).fetchone()

                if existe is None:
                    raise ValueError('Cliente não encontrado.')

                conexao.execute(
                    '''
                    INSERT INTO enderecos (
                        cliente_id, rua, numero
                    )
                    VALUES (?, ?, ?)
                    ''',
                    (
                        cliente_id,
                        endereco.rua,
                        endereco.numero
                    )
                )

    def alterar_endereco(
        self,
        cliente_id,
        endereco_id,
        nova_rua,
        novo_numero
    ):
        novo = Endereco(nova_rua, novo_numero)

        with closing(self.conectar()) as conexao:
            with conexao:
                cursor = conexao.execute(
                    '''
                    UPDATE enderecos
                    SET rua = ?, numero = ?
                    WHERE id = ? AND cliente_id = ?
                    ''',
                    (
                        novo.rua,
                        novo.numero,
                        endereco_id,
                        cliente_id
                    )
                )

                if cursor.rowcount == 0:
                    raise ValueError('Endereço não encontrado.')

    def excluir_endereco(self, cliente_id, endereco_id):
        with closing(self.conectar()) as conexao:
            with conexao:
                cursor = conexao.execute(
                    '''
                    DELETE FROM enderecos
                    WHERE id = ? AND cliente_id = ?
                    ''',
                    (endereco_id, cliente_id)
                )

                if cursor.rowcount == 0:
                    raise ValueError('Endereço não encontrado.')

    def excluir_cliente(self, cliente_id):
        with closing(self.conectar()) as conexao:
            with conexao:
                cursor = conexao.execute(
                    'DELETE FROM clientes WHERE id = ?',
                    (cliente_id,)
                )

                if cursor.rowcount == 0:
                    raise ValueError('Cliente não encontrado.')
