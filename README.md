uzosms
======

Uma ferramenta para enviar sms grátis através do site [uzo.pt](http://www.uzo.pt) directamente da linha de comandos

Utiliza técnicas de machine learning para resolver automaticamente o CAPTCHA na página de envio.

Uma vez que usa o [scikit-learn](http://scikit-learn.org/stable/) é um bocado pesado em termos de dependências

Como utilizar
-------------
1. `git clone https://github.com/jotinha/uzosms.git`
2. `python setup.py install`
3. Guardar o login/password com `uzo login <number> <password>`
4. Enviar sms com `uzo send 960000000 olá mundo`
5. Para apagar o login fazer `uzo logout`

Comandos
--------

#### `uzo login <number> <password>`
Gravar ou substituir novas credenciais. Tem de ser usado antes de qualquer outro comando

#### `uzo logout`
Apaga as credenciais actuais

#### `uzo send <number> <msg>`
Enviar mensagem `<msg>` para o número de telefone `<number>`

#### `uzo check`
Devolve o número de mensagens ainda disponíveis no mês actual

#### `uzo train`
Re-treina o modelo com os captchas previamente resolvidos

#### `uzo grab [n]`
Faz o download de `n` novos captchas (default 10) que devem ser resolvidos manualmente mudando o nome do ficheiro de
imagem `<timestamp>.xml` para `yyyyyy.jpg` onde `yyy` é o conjunto de 6 algarismos que correspondem à imagem      
