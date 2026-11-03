
import re
from datetime import date

from validacoes import validar_cpf, normalizar_cpf


def normalizar_telefone(telefone):
    telefone = str(telefone or '').strip()

    if not telefone:
        return ''

    if not re.fullmatch(r'[\d\s()+-]+', telefone):
        raise ValueError('Telefone contém caracteres inválidos.')

    digitos = re.sub(r'\D', '', telefone)

    if len(digitos) not in (10, 11):
        raise ValueError(
            'Informe um telefone com DDD, de 10 ou 11 dígitos.'
        )

    if digitos[:2] == '00' or digitos[:2] == '0' * 2:
        raise ValueError('DDD inválido.')

    return digitos


def normalizar_email(email):
    email = str(email or '').strip().lower()

    if not email:
        return ''

    formato = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'

    if len(email) > 254 or not re.fullmatch(formato, email):
        raise ValueError('E-mail inválido.')

    return email


class Pessoa:
    def __init__(self, nome, ano_nascimento):
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError('Nome inválido.')

        ano_atual = date.today().year

        if (
            not isinstance(ano_nascimento, int)
            or isinstance(ano_nascimento, bool)
            or not 1900 <= ano_nascimento <= ano_atual
        ):
            raise ValueError('Ano de nascimento inválido.')

        self.nome = nome.strip()
        self.ano_nascimento = ano_nascimento

    @property
    def idade(self):
        return date.today().year - self.ano_nascimento

    def emitir_dados(self):
        print(f'Nome: {self.nome}')
        print(f'Ano de nascimento: {self.ano_nascimento}')
        print(f'Idade aproximada: {self.idade}')


class Endereco:
    def __init__(self, rua, numero):
        if not str(rua).strip() or not str(numero).strip():
            raise ValueError('Rua e número são obrigatórios.')

        self.id = None
        self.rua = str(rua).strip()
        self.numero = str(numero).strip()


class Cliente(Pessoa):
    def __init__(
        self,
        nome,
        ano_nascimento,
        cpf,
        telefone='',
        email=''
    ):
        if not validar_cpf(cpf):
            raise ValueError('CPF inválido!')

        super().__init__(nome, ano_nascimento)

        self.id = None
        self.cpf = normalizar_cpf(cpf)
        self.telefone = normalizar_telefone(telefone)
        self.email = normalizar_email(email)
        self.enderecos = []

    def inserir_endereco(self, rua, numero):
        endereco = Endereco(rua, numero)
        self.enderecos.append(endereco)

    def listar_enderecos(self):
        if not self.enderecos:
            print('Nenhum endereço cadastrado.')
            return

        for endereco in self.enderecos:
            print(
                f'Endereço: {endereco.rua}, '
                f'Nº {endereco.numero}'
            )

    def emitir_dados(self):
        super().emitir_dados()
        print(f'CPF: {self.cpf}')
        print(f'Telefone: {self.telefone or "Não informado"}')
        print(f'E-mail: {self.email or "Não informado"}')
        self.listar_enderecos()

    def alterar_endereco(self, indice, nova_rua, novo_numero):
        if not 0 <= indice < len(self.enderecos):
            raise ValueError('Endereço não encontrado.')

        self.enderecos[indice] = Endereco(
            nova_rua,
            novo_numero
        )
