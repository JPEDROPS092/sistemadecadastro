from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('senha')
        lembrar = request.form.get('lembrar') == 'on'

        usuario = AuthService.autenticar(username, senha)

        if usuario:
            login_user(usuario, remember=lembrar)
            flash(f'Bem-vindo, {usuario.nome_completo}!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Usuário ou senha inválidos', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/usuarios')
def listar_usuarios():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Acesso negado', 'danger')
        return redirect(url_for('main.index'))

    usuarios = AuthService.listar_usuarios()
    return render_template('auth/usuarios.html', usuarios=usuarios)

@auth_bp.route('/usuarios/novo', methods=['GET', 'POST'])
def novo_usuario():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Acesso negado', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            senha = request.form.get('senha')
            nome_completo = request.form.get('nome_completo')
            email = request.form.get('email')
            tipo = request.form.get('tipo')

            AuthService.criar_usuario(username, senha, nome_completo, email, tipo)
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('auth.listar_usuarios'))
        except Exception as e:
            flash(f'Erro ao criar usuário: {str(e)}', 'error')

    return render_template('auth/form_usuario.html', usuario=None)

@auth_bp.route('/perfil')
def perfil():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('auth/perfil.html')

@auth_bp.route('/alterar-senha', methods=['GET', 'POST'])
def alterar_senha():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual')
        senha_nova = request.form.get('senha_nova')
        senha_confirmacao = request.form.get('senha_confirmacao')

        if not current_user.verificar_senha(senha_atual):
            flash('Senha atual incorreta', 'danger')
        elif senha_nova != senha_confirmacao:
            flash('As senhas não coincidem', 'danger')
        elif len(senha_nova) < 6:
            flash('A senha deve ter no mínimo 6 caracteres', 'danger')
        else:
            AuthService.atualizar_usuario(current_user.id, senha=senha_nova)
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('auth.perfil'))

    return render_template('auth/alterar_senha.html')
