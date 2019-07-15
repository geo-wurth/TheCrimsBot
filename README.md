# TheCrimsBot
Desenvolvido: George Wurthmann

Email: george.wurthmann@fatec.gov.sp.br

# Bibliotecas necessárias
Necessário instalar as seguintes bibliotecas:

pip install selenium
pip install bs4
pip install lxml
pip install html.parser
pip install playsound

# Chromedriver
Necessário fazer o download do chromedriver pelo endereço abaixo http://chromedriver.chromium.org/downloads

Deve adicionar o caminho do chromedrive à variável do windows no "Path"

# Descrição - Funções
É necessário configurar o arquivo config.py.

O Bot faz o login automático, faz o roubo da gang (se disponível) e posteriormente o roubo solo, vai para a rave para recuperar estamina, entra no banco para guardar o dinheiro e reinicia o ciclo.

O Bot reconhece se você morrer assassinado ou por overdose (não faz diferenciação), se for preso ou se o jogo entrar em update, iniciando um contador que deixa o bot pausado até reiniciar os processos.

Possui uma configuração para fugir do assassinos das raves, quando localizado outra pessoa na balada, saí imediatamente para não morrer, as funções de atacar qualquer um ou atacar apenas pessoas com menor respeito ainda está sendo implementada.

# Importante!!
Por algum motivo a biblioteca playsound não funciona se executada através do MS-DOS, então é necessário rodar o programa pelo Python Launcher que vem junto com a versão do python baixada no site oficial: https://www.python.org/
