
import json
import hmac
from datetime import timedelta
from functools import wraps
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, abort
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash
from werkzeug.exceptions import RequestEntityTooLarge

from cadastro_cliente import CadastroClientes
from configuracoes import Configuracoes
from modelos import Cliente


BASE = Path(__file__).resolve().parent
CONFIG = BASE / 'admin_config.json'

if not CONFIG.exists():
    raise RuntimeError(
        'Configure o administrador: python setup_admin.py'
    )

with CONFIG.open(encoding='utf-8') as arquivo:
    admin = json.load(arquivo)

app = Flask(__name__)

app.config.update(
    SECRET_KEY=admin['secret_key'],
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    MAX_CONTENT_LENGTH=2 * 1024 * 1024 + 100_000
)

CSRFProtect(app)

sistema = CadastroClientes()
aparencia = Configuracoes()


@app.context_processor
def carregar_aparencia():
    return {'visual': aparencia.obter()}


@app.after_request
def evitar_cache_privado(resposta):
    resposta.headers['Cache-Control'] = 'no-store'
    return resposta


@app.errorhandler(RequestEntityTooLarge)
def arquivo_grande(erro):
    flash('Arquivo muito grande. Use uma imagem de até 2 MB.', 'erro')
    return redirect(url_for('pagina_configuracoes')), 303


def admin_required(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        if session.get('admin') is not True:
            return redirect(url_for('login'))
        return funcao(*args, **kwargs)
    return protegida


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin') is True:
        return redirect(url_for('pagina_inicial'))

    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '')

        usuario_correto = hmac.compare_digest(
            usuario.encode('utf-8'),
            admin['usuario'].encode('utf-8')
        )

        senha_correta = check_password_hash(
            admin['senha_hash'],
            senha
        )

        if usuario_correto and senha_correta:
            session.clear()
            session.permanent = True
            session['admin'] = True
            return redirect(url_for('pagina_inicial'))

        flash('Usuário ou senha incorretos.', 'erro')

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@admin_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@admin_required
def pagina_inicial():
    clientes = sistema.listar_todos()

    return render_template(
        'index.html',
        clientes=clientes,
        total_clientes=len(clientes),
        total_enderecos=sum(
            len(cliente.enderecos)
            for cliente in clientes
        )
    )


@app.route('/clientes/cadastrar', methods=['POST'])
@admin_required
def cadastrar_cliente():
    try:
        nome = request.form.get('nome', '').strip()
        ano = int(request.form.get('ano_nascimento', ''))
        cpf = request.form.get('cpf', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        rua = request.form.get('rua', '').strip()
        numero = request.form.get('numero', '').strip()

        if not telefone or not email:
            raise ValueError('Telefone e e-mail são obrigatórios.')

        cliente = Cliente(nome, ano, cpf, telefone, email)
        cliente.inserir_endereco(rua, numero)
        sistema.cadastrar_cliente(cliente)

        flash('Cliente cadastrado com sucesso!', 'sucesso')
        return redirect(
            url_for('detalhes_cliente', cliente_id=cliente.id)
        )

    except ValueError as erro:
        flash(f'Erro ao cadastrar: {erro}', 'erro')
        return redirect(url_for('pagina_inicial'))


@app.route('/clientes/<int:cliente_id>')
@admin_required
def detalhes_cliente(cliente_id):
    cliente = sistema.buscar_por_id(cliente_id)

    if cliente is None:
        abort(404)

    return render_template('cliente.html', cliente=cliente)


@app.route('/clientes/<int:cliente_id>/editar', methods=['POST'])
@admin_required
def editar_cliente(cliente_id):
    cliente = sistema.buscar_por_id(cliente_id)

    if cliente is None:
        abort(404)

    try:
        sistema.alterar_titular(
            cliente.cpf,
            request.form.get('nome', '').strip(),
            int(request.form.get('ano_nascimento', '')),
            request.form.get('cpf', '').strip(),
            request.form.get('telefone', '').strip(),
            request.form.get('email', '').strip()
        )
        flash('Titular atualizado!', 'sucesso')

    except ValueError as erro:
        flash(str(erro), 'erro')

    return redirect(
        url_for('detalhes_cliente', cliente_id=cliente_id)
    )


@app.route('/clientes/<int:cliente_id>/enderecos', methods=['POST'])
@admin_required
def adicionar_endereco(cliente_id):
    if sistema.buscar_por_id(cliente_id) is None:
        abort(404)

    try:
        sistema.adicionar_endereco(
            cliente_id,
            request.form.get('rua', ''),
            request.form.get('numero', '')
        )
        flash('Endereço adicionado!', 'sucesso')
    except ValueError as erro:
        flash(str(erro), 'erro')

    return redirect(
        url_for('detalhes_cliente', cliente_id=cliente_id)
    )


@app.route(
    '/clientes/<int:cliente_id>/enderecos/<int:endereco_id>/editar',
    methods=['POST']
)
@admin_required
def editar_endereco(cliente_id, endereco_id):
    if sistema.buscar_por_id(cliente_id) is None:
        abort(404)

    try:
        sistema.alterar_endereco(
            cliente_id,
            endereco_id,
            request.form.get('rua', ''),
            request.form.get('numero', '')
        )
        flash('Endereço atualizado!', 'sucesso')
    except ValueError as erro:
        flash(str(erro), 'erro')

    return redirect(
        url_for('detalhes_cliente', cliente_id=cliente_id)
    )


@app.route(
    '/clientes/<int:cliente_id>/enderecos/<int:endereco_id>/excluir',
    methods=['POST']
)
@admin_required
def excluir_endereco(cliente_id, endereco_id):
    if sistema.buscar_por_id(cliente_id) is None:
        abort(404)

    try:
        sistema.excluir_endereco(cliente_id, endereco_id)
        flash('Endereço excluído!', 'sucesso')
    except ValueError as erro:
        flash(str(erro), 'erro')

    return redirect(
        url_for('detalhes_cliente', cliente_id=cliente_id)
    )


@app.route('/clientes/<int:cliente_id>/excluir', methods=['POST'])
@admin_required
def excluir_cliente(cliente_id):
    if sistema.buscar_por_id(cliente_id) is None:
        abort(404)

    if request.form.get('confirmacao') != 'EXCLUIR':
        flash('Confirmação de exclusão incorreta.', 'erro')
        return redirect(
            url_for('detalhes_cliente', cliente_id=cliente_id)
        )

    sistema.excluir_cliente(cliente_id)
    flash('Cliente excluído com sucesso!', 'sucesso')
    return redirect(url_for('pagina_inicial'))


# ===== PAINEL DE PERSONALIZAÇÃO =====

@app.route('/admin/configuracoes')
@admin_required
def pagina_configuracoes():
    return render_template('configuracoes.html')


@app.route('/admin/configuracoes/salvar', methods=['POST'])
@admin_required
def salvar_configuracoes():
    try:
        aparencia.salvar(
            request.form.get('nome_sistema', ''),
            request.form.get('nome_empresa', ''),
            request.form.get('cor_principal', ''),
            request.form.get('cor_lateral', ''),
            request.form.get('tema', '')
        )
        flash('Aparência atualizada com sucesso!', 'sucesso')
    except ValueError as erro:
        flash(str(erro), 'erro')

    return redirect(url_for('pagina_configuracoes'))


@app.route('/admin/configuracoes/logo', methods=['POST'])
@admin_required
def enviar_logo():
    try:
        aparencia.salvar_logo(request.files.get('logo'))
        flash('Logotipo atualizado com sucesso!', 'sucesso')
    except ValueError as erro:
        flash(str(erro), 'erro')

    return redirect(url_for('pagina_configuracoes'))


@app.route('/admin/configuracoes/restaurar', methods=['POST'])
@admin_required
def restaurar_configuracoes():
    aparencia.restaurar()
    flash('Visual padrão restaurado!', 'sucesso')
    return redirect(url_for('pagina_configuracoes'))


if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False
    )
