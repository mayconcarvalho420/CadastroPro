
import io
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from PIL import Image, UnidentifiedImageError


BASE = Path(__file__).resolve().parent
BANCO = BASE / 'clientes.db'
PASTA_LOGO = BASE / 'static' / 'uploads'
PASTA_LOGO.mkdir(parents=True, exist_ok=True)

PADRAO = {
    'nome_sistema': 'CadastroPro',
    'nome_empresa': 'Sistema de Gestão de Clientes',
    'cor_principal': '#2563eb',
    'cor_lateral': '#101a2e',
    'tema': 'claro',
    'logo': ''
}


class Configuracoes:
    def __init__(self):
        self.criar_tabela()

    def conectar(self):
        return sqlite3.connect(BANCO)

    def criar_tabela(self):
        with closing(self.conectar()) as conexao:
            with conexao:
                conexao.execute('''
                    CREATE TABLE IF NOT EXISTS configuracoes (
                        chave TEXT PRIMARY KEY,
                        valor TEXT NOT NULL
                    )
                ''')

                for chave, valor in PADRAO.items():
                    conexao.execute(
                        '''
                        INSERT OR IGNORE INTO configuracoes
                        (chave, valor) VALUES (?, ?)
                        ''',
                        (chave, valor)
                    )

    def obter(self):
        with closing(self.conectar()) as conexao:
            registros = conexao.execute(
                'SELECT chave, valor FROM configuracoes'
            ).fetchall()

        dados = PADRAO.copy()
        dados.update(dict(registros))
        return dados

    def validar_cor(self, cor):
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', cor):
            raise ValueError('Cor hexadecimal inválida.')
        return cor.lower()

    def salvar(self, nome, empresa, cor, lateral, tema):
        nome = nome.strip()
        empresa = empresa.strip()

        if not 2 <= len(nome) <= 50:
            raise ValueError(
                'O nome deve ter entre 2 e 50 caracteres.'
            )

        if not 2 <= len(empresa) <= 80:
            raise ValueError(
                'O nome da empresa deve ter entre 2 e 80 caracteres.'
            )

        cor = self.validar_cor(cor)
        lateral = self.validar_cor(lateral)

        if tema not in ('claro', 'escuro'):
            raise ValueError('Tema inválido.')

        alteracoes = {
            'nome_sistema': nome,
            'nome_empresa': empresa,
            'cor_principal': cor,
            'cor_lateral': lateral,
            'tema': tema
        }

        with closing(self.conectar()) as conexao:
            with conexao:
                for chave, valor in alteracoes.items():
                    conexao.execute(
                        '''
                        UPDATE configuracoes
                        SET valor = ?
                        WHERE chave = ?
                        ''',
                        (valor, chave)
                    )

    def salvar_logo(self, arquivo):
        if arquivo is None or not arquivo.filename:
            raise ValueError('Selecione uma imagem.')

        dados = arquivo.read()

        if not dados or len(dados) > 2 * 1024 * 1024:
            raise ValueError('A imagem deve ter até 2 MB.')

        try:
            with Image.open(io.BytesIO(dados)) as imagem:
                if imagem.format not in ('PNG', 'JPEG'):
                    raise ValueError('Use somente PNG ou JPG.')

                largura, altura = imagem.size

                if largura > 3000 or altura > 3000:
                    raise ValueError(
                        'A imagem deve ter no máximo 3000 x 3000 pixels.'
                    )

                imagem.load()
                imagem = imagem.copy()

        except (UnidentifiedImageError, OSError) as erro:
            raise ValueError('Arquivo de imagem inválido.') from erro

        # Converte para PNG padronizado
        if imagem.mode not in ('RGB', 'RGBA'):
            imagem = imagem.convert('RGBA')

        destino = PASTA_LOGO / 'logo.png'
        temporario = PASTA_LOGO / 'logo.tmp'

        imagem.save(temporario, format='PNG')
        temporario.replace(destino)

        with closing(self.conectar()) as conexao:
            with conexao:
                conexao.execute(
                    '''
                    UPDATE configuracoes
                    SET valor = 'uploads/logo.png'
                    WHERE chave = 'logo'
                    '''
                )

    def restaurar(self):
        with closing(self.conectar()) as conexao:
            with conexao:
                for chave, valor in PADRAO.items():
                    conexao.execute(
                        '''
                        UPDATE configuracoes
                        SET valor = ?
                        WHERE chave = ?
                        ''',
                        (valor, chave)
                    )
