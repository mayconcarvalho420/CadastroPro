
import json
import secrets
from getpass import getpass
from pathlib import Path

from werkzeug.security import generate_password_hash


CONFIG = Path(__file__).resolve().parent / 'admin_config.json'


def configurar_admin():
    if CONFIG.exists():
        print('Administrador já configurado.')
        print('A configuração existente não foi alterada.')
        return

    print('===== CONFIGURAR ADMINISTRADOR =====')

    usuario = input('Usuário administrador: ').strip()

    if not usuario:
        print('Informe um nome de usuário.')
        return

    senha = getpass('Crie uma senha (mínimo 12 caracteres): ')
    confirmar = getpass('Confirme a senha: ')

    if len(senha) < 12:
        print('A senha precisa ter pelo menos 12 caracteres.')
        return

    if senha != confirmar:
        print('As senhas não coincidem.')
        return

    dados = {
        'usuario': usuario,
        'senha_hash': generate_password_hash(senha),
        'secret_key': secrets.token_hex(32)
    }

    try:
        with CONFIG.open('x', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo, indent=2)
    except FileExistsError:
        print('Administrador já configurado.')
        return

    print('Administrador criado com sucesso!')
    print('Guarde sua senha em local seguro.')


if __name__ == '__main__':
    configurar_admin()
