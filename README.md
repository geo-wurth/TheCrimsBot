# TheCrimsBot

## Informações Gerais
Desenvolvido: George Wurthmann

Email: george.wurthmann@fatec.gov.sp.br

## Bibliotecas necessárias
Necessário instalar as seguintes bibliotecas:
```
pip install selenium
pip install bs4
pip install lxml
pip install html.parser
pip install playsound
```

## Chromedriver
Necessário fazer o download do chromedriver pelo link: [Chromedrive](http://chromedriver.chromium.org/downloads)

Deve adicionar o caminho do chromedrive à variável do windows no "Path"

## Descrição
### Configuração
É necessário configurar o arquivo config.py. O arquivo possi comentários para facilitar o entedimento.

### Login
O bot faz o login automático conforme os dados fornecidos no arquivo config.py

### Roubos
O bot faz roubo da gangue (se disponível) e posteriormente o roubo solo conforme os parâmetros no arquivo config.py

### Estamina
Quando a estamina estiver menor que o definido pelo roubo solo, o bot vai para a vida noturna, entra no primeiro estabelecimento de balada que conseguir, o bot vai tentando até identificar que está dentro da balada, então mesmo se não conseguir entrar devido ao limite de respeito, ele pula para o próximo. Não fiz a tratativa caso não entre em nenhuma balada pois as chances são mínimas.

Após entrar na balada ele verifica qual a melhor droga para consumir (custo x recuperação de estamina), caso for necessário compara mais de 99 unidades (máximo permitido pelo campo), o bot comprará em partes.

> Ex: Comprar 153 cervas - Primeiro comprará 99 e depois 54.

### Caça
O bot possui três configurações para verificar pessoas na balada. Quando localizado outra pessoa na balada ele pode:

1. Sair imediatamente para não morrer;
2. Atacar a pessoa, independente do nível dela;
3. Verifica se o respeito da pessoa é menor que o seu, em caso positivo ataca, em caso negativo foge. (Esta função ainda não foi implementada!)

### Detox
Após atingir o nível máximo de vício permitido, o bot irá para o hospital e utilizará a função "Detox por dinheiro", caso não possua dinheiro na mão suficiente, o bot irá até o banco sacar a diferença. É importante ter algum dinheiro com você, pois se não tiver dinheiro suficiente o bot ficará em loop.

### Mortes / Prisão / Atualização
O Bot reconhece se você morrer (seja assassinado ou por overdose, ele não faz diferenciação), se for preso ou se o jogo entrar em update diário, iniciando um contador que deixa o bot pausado até reiniciar os processos. O tempo calculado é o tempo informado com uma variação aleatório conforme determinado no config.py (limite máximo em %).

# Importante!!
Por algum motivo a biblioteca playsound não funciona se executada através do MS-DOS, então é necessário rodar o programa pelo Python Launcher que vem junto com a versão do python baixada no site oficial: [Python](https://www.python.org/)
