# DivideAi Backend

## Integrantes

- Guilherme Ponce 2011179

## Descricao do projeto

O backend do DivideAi fornece autenticacao JWT, CRUD de grupos, CRUD de despesas e um endpoint de saldos por grupo. Cada usuario autenticado acessa apenas grupos dos quais participa, e as despesas tambem ficam limitadas aos grupos do usuario.

## Tecnologias utilizadas

- Python
- Django
- Django REST Framework
- Simple JWT
- drf-spectacular
- django-cors-headers
- SQLite

## Instalacao local

1. Clonar o repositorio:
   
   git clone https://github.com/GuilhermePonce/ProjetoWeb2-Back
   cd divideai-backend


2. Criar e ativar ambiente virtual:

   python -m venv .venv
   .venv\Scripts\activate

3. Instalar dependencias:

   pip install -r requirements.txt

4. Rodar migrations:
   python manage.py migrate
   
5. Criar superusuario:
   python manage.py createsuperuser
   
6. Rodar o servidor:
   python manage.py runserver
  
## Como usar

Principais endpoints:

- `POST /api/auth/register/` cria usuario.
- `POST /api/auth/login/` retorna tokens JWT.
- `POST /api/auth/refresh/` renova token.
- `GET /api/auth/me/` retorna o usuario autenticado.
- `POST /api/auth/change-password/` altera senha do usuario logado.
- `POST /api/auth/password-reset/` simula solicitacao de redefinicao.
- `GET|POST /api/groups/` lista e cria grupos.
- `GET|PUT|PATCH|DELETE /api/groups/{id}/` consulta, atualiza e exclui grupos.
- `GET|POST /api/expenses/` lista e cria despesas.
- `GET|PUT|PATCH|DELETE /api/expenses/{id}/` consulta, atualiza e exclui despesas.
- `GET /api/groups/{id}/balances/` calcula totais pagos, valores devidos, saldo final e pagamentos sugeridos.

Todos os endpoints principais exigem token no cabecalho:

```txt
Authorization: Bearer SEU_ACCESS_TOKEN
```

## Documentacao Swagger

Com o servidor local em execucao, acesse:

- `/api/schema/`
- `/api/docs/`

A tela Swagger permite consultar e testar a API.

## Manual do usuario

1. Registre uma conta em `/api/auth/register/`.
2. Faca login em `/api/auth/login/` e copie o `access token`.
3. Crie um grupo em `/api/groups/`.
4. Adicione membros ao grupo pelo campo `members`, usando IDs de usuarios.
5. Cadastre despesas em `/api/expenses/`, informando grupo, pagador e participantes.
6. Consulte `/api/groups/{id}/balances/` para ver quem pagou, quem deve e os pagamentos sugeridos.
7. Use `/api/auth/change-password/` para alterar a senha.

## Deploy

Sugestoes de hospedagem: Render, Railway, PythonAnywhere ou AWS.

Passos gerais:

1. Criar o servico Python no provedor escolhido.
2. Configurar variaveis `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` e `CORS_ALLOWED_ORIGINS`.
3. Instalar dependencias com `pip install -r requirements.txt`.
4. Executar `python manage.py migrate`.
5. Rodar com Gunicorn, por exemplo:
   ```bash
   gunicorn divideai.wsgi
   ```

Link do backend publicado: `INSERIR_LINK_DO_DEPLOY_BACKEND`

## O que foi desenvolvido

- Projeto Django separado do frontend.
- API REST com Django REST Framework.
- Autenticacao JWT com Simple JWT.
- Registro, login, refresh, dados do usuario, troca de senha e reset simulado.
- CRUD completo de grupos e despesas.
- Permissoes por participacao no grupo.
- Calculo dinamico de saldos e pagamentos sugeridos.
- Swagger com drf-spectacular.
- Testes basicos de autenticacao, escopo por usuario e saldos.

## O que funcionou

- Registro de usuario.
- Login com JWT.
- Protecao de endpoints sem token.
- Criacao e listagem de grupos por usuario.
- Criacao de despesas.
- Separacao de dados entre usuarios diferentes.
- Calculo de saldo e settlements.
- Documentacao Swagger.

