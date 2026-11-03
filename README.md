# CadastroPro 🐍

Aplicação web para cadastro e gerenciamento de clientes, desenvolvida com **Python, Flask, Jinja2 e SQLite3** como projeto de estudos em desenvolvimento backend.

## 📖 Sobre o projeto

O CadastroPro nasceu como um exercício de **Programação Orientada a Objetos (POO)**, com classes, herança e composição. Ao longo dos estudos, evoluiu para uma aplicação web com interface visual, gerenciamento de dados, autenticação administrativa e persistência em banco de dados.

O projeto representa uma etapa do meu aprendizado: integrar regras de negócio escritas em Python a rotas Flask, templates HTML e um banco SQLite.

## ✨ Funcionalidades

- Login e logout de administrador.
- Cadastro e listagem de clientes.
- Consulta, edição e exclusão de cadastros.
- Dados de clientes: nome, ano de nascimento, CPF, telefone e e-mail.
- Cadastro, alteração e exclusão de endereços vinculados a clientes.
- Validação de CPF e impedimento de CPF duplicado.
- Painel administrativo para personalizar nome do sistema, empresa, cores, tema e logotipo.
- Mensagens de confirmação e erro na interface.

## 🧰 Tecnologias utilizadas

- **Python** — lógica de negócio e modelos orientados a objetos.
- **Flask** — aplicação e rotas web.
- **Jinja2** — renderização dos templates HTML.
- **SQLite3** — armazenamento local dos cadastros e endereços.
- **Flask-WTF** — proteção CSRF dos formulários.
- **Werkzeug** — geração e verificação de hash da senha administrativa.
- **HTML e CSS** — estrutura e estilos da interface.

## 🔐 Acesso administrativo

As páginas de gerenciamento exigem autenticação de administrador. O projeto utiliza hash de senha, sessão com duração configurada de 30 minutos, proteção CSRF e um decorador para restringir o acesso às rotas administrativas.

A configuração administrativa é gerada **localmente** no primeiro uso. Não publique o arquivo `admin_config.json` nem dados reais de clientes.

> **Atenção:** esta é uma aplicação de estudos preparada para execução local. As configurações atuais não devem ser consideradas prontas para hospedagem pública em produção.

## 📁 Estrutura do projeto

```text
cadastro_cliente/
├── static/
│   ├── uploads/
│   ├── admin.css
│   ├── style.css
│   └── tema.css
├── templates/
│   ├── base.html
│   ├── cliente.html
│   ├── configuracoes.html
│   ├── index.html
│   └── login.html
├── .gitignore
├── app.py
├── cadastro_cliente.py
├── configuracoes.py
├── interface.py
├── main.py
├── modelos.py
├── requirements.txt
├── setup_admin.py
├── validacoes.py
└── README.md
```

Os arquivos locais de configuração, banco de dados e ambiente virtual são criados ou utilizados na execução, mas **não devem fazer parte do repositório público**.

## ▶️ Como executar localmente

### 1. Clone o projeto

Substitua `SEU-USUARIO` pelo nome da sua conta no GitHub:

```bash
git clone https://github.com/SEU-USUARIO/CadastroPro.git
cd CadastroPro
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

Ative o ambiente no **PowerShell (Windows)**:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Instale as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Configure o administrador

```bash
python setup_admin.py
```

Informe um nome de usuário e uma senha de pelo menos 12 caracteres. O script criará o arquivo local `admin_config.json`, contendo o hash da senha e a chave secreta da aplicação.

### 5. Inicie a aplicação

```bash
python app.py
```

Abra no navegador:

**http://127.0.0.1:5000**

A aplicação cria as tabelas de clientes e endereços no banco SQLite local quando a classe de gerenciamento é inicializada.

> **Observação:** os comandos acima consideram Windows/PowerShell, Python e suas dependências corretamente instalados. A execução em uma instalação limpa ainda deve ser testada antes da publicação.

## 🧠 Aprendizados

Neste projeto, pratiquei conceitos de **POO, herança, composição, validação de dados, organização em módulos, integração entre backend e templates HTML, rotas web e persistência com SQLite**. Também utilizei ferramentas de IA como apoio na implementação, investigação de erros e evolução da aplicação.

## 📷 Demonstração

Uma demonstração em vídeo do CadastroPro acompanha a publicação do projeto no LinkedIn. Capturas de tela poderão ser adicionadas a este repositório.

## 👨‍💻 Autor

**Maycon Junio Santos Carvalho**  
Projeto desenvolvido durante meus estudos de Python e desenvolvimento backend.
