
<summary> <strong>📚 Sumário</strong>

- [1 - Métodos de Autenticação no Mosquitto](#1---métodos-de-autenticação-no-mosquitto)
  - [Versões do Mosquitto](#versões-do-mosquitto)
  - [Opções de Autenticação](#opções-de-autenticação)
  - [Arquivos de Senha](#arquivos-de-senha)
    - [Criando um arquivo de senhas](#criando-um-arquivo-de-senhas)
    - [Configurando o broker](#configurando-o-broker)
  - [Plugins de Autenticação](#plugins-de-autenticação)
    - [Configurando o plugin](#configurando-o-plugin)
    - [Plugins disponíveis](#plugins-disponíveis)
  - [Acesso Não Autenticado](#acesso-não-autenticado)
- [2 - Uso de mosquitto\_passwd](#2---uso-de-mosquitto_passwd)
  - [mosquitto\_passwd — gerencia arquivos de senha para o mosquitto](#mosquitto_passwd--gerencia-arquivos-de-senha-para-o-mosquitto)
  - [Comando](#comando)
  - [Descrição](#descrição)
  - [Opções](#opções)
  - [Códigos de Saída](#códigos-de-saída)
    - [Códigos CONNACK MQTT v3.1.1:](#códigos-connack-mqtt-v311)
    - [Códigos MQTT v5:](#códigos-mqtt-v5)
  - [Exemplos](#exemplos)
- [3 - MOSQUITTO-TLS](#3---mosquitto-tls)
  - [mosquitto-tls — Configura suporte SSL/TLS para o Mosquitto](#mosquitto-tls--configura-suporte-ssltls-para-o-mosquitto)
  - [Descrição](#descrição-1)
  - [Observação importante](#observação-importante)
  - [Gerando certificados](#gerando-certificados)
    - [Autoridade Certificadora (CA)](#autoridade-certificadora-ca)
    - [Servidor](#servidor)
    - [Cliente](#cliente)
  - [`Dicas importantes`](#dicas-importantes)
  
</summary>
<br>

# 1 - Métodos de Autenticação no Mosquitto

É importante configurar a autenticação em sua instância do Mosquitto para que clientes não autorizados não possam se conectar.

## Versões do Mosquitto
- **Mosquitto 2.0 e superiores**: Você deve escolher explicitamente as opções de autenticação antes que os clientes possam se conectar.
- **Versões anteriores**: O padrão é permitir que clientes se conectem sem autenticação.

## Opções de Autenticação
Existem três escolhas para autenticação:
1. Arquivos de senha
2. Plugins de autenticação
3. Acesso não autorizado/anônimo

É possível usar uma combinação de todas as três opções.

Você pode ter listeners diferentes usando métodos de autenticação diferentes configurando per_listener_settings true no seu arquivo de configuração.

Além da autenticação, você também deve considerar alguma forma de controle de acesso para determinar quais clientes podem acessar quais tópicos.

## Arquivos de Senha
Arquivos de senha são um mecanismo simples para armazenar nomes de usuário e senhas em um único arquivo. Eles são bons se você tem um número relativamente pequeno de usuários bastante estáticos.

Se você fizer alterações no arquivo de senhas, deve solicitar que o broker recarregue o arquivo enviando um sinal SIGHUP:

``` bash
kill -HUP <ID do processo do mosquitto>
```
### Criando um arquivo de senhas
Para criar um arquivo de senhas, use o utilitário mosquitto_passwd. Você será solicitado a informar a senha. Observe que -c significa que um arquivo existente será sobrescrito:

``` bash
mosquitto_passwd -c <arquivo de senhas> <nome de usuário>
```

Para adicionar mais usuários a um arquivo de senhas existente ou alterar a senha de um usuário existente, omita o argumento -c:

``` bash
mosquitto_passwd <arquivo de senhas> <nome de usuário>
```

Para remover um usuário de um arquivo de senhas:
``` bash
mosquitto_passwd -D <arquivo de senhas> <nome de usuário>
```

Você também pode adicionar/atualizar um nome de usuário e senha em uma única linha, mas esteja ciente de que isso significa que a senha ficará visível na linha de comando e em qualquer histórico de comandos:

``` bash
mosquitto_passwd <arquivo de senhas> <nome de usuário> <senha>
``` 

### Configurando o broker
Para começar a usar seu arquivo de senhas, você deve adicionar a opção password_file ao seu arquivo de configuração:

``` conf
password_file <caminho para o arquivo de configuração>
``` 

O arquivo de senhas deve poder ser lido pelo usuário sob o qual o Mosquitto está sendo executado. Em sistemas Linux/POSIX, isso normalmente será o usuário mosquitto, e /etc/mosquitto/password_file é um bom local para o arquivo.

Se você estiver usando a opção per_listener_settings true para ter configurações de segurança separadas por listener, você deve colocar a opção do arquivo de senhas após o listener ao qual ela se aplica:

``` conf
listener 1883
password_file /etc/mosquitto/password_file
``` 

## Plugins de Autenticação
Se você deseja mais controle sobre a autenticação de seus usuários do que o oferecido por um arquivo de senhas, então um plugin de autenticação pode ser adequado para você. Os recursos oferecidos dependem de qual plugin você usa.

### Configurando o plugin
A configuração de um plugin varia dependendo da versão da interface de plugin do Mosquitto para a qual o plugin foi escrito: versão 2.0 e superiores ou 1.6.x e anteriores.

Para 1.6.x e anteriores, use a opção auth_plugin. Esses plugins também são suportados pela versão 2.0:

``` conf
listener 1883
auth_plugin <caminho para o plugin>
```

Alguns plugins requerem configuração adicional que será descrita em sua documentação.

Para 2.0 e superiores, use a opção plugin:

``` conf
listener 1883
plugin <caminho para o plugin>
```

### Plugins disponíveis
- **Dynamic security**: Apenas para 2.0 e superiores, fornecido pelo projeto Mosquitto para oferecer clientes, grupos e funções flexíveis no broker que podem ser administrados remotamente.
- **mosquitto-go-auth**: Oferece o uso de vários backends para armazenar dados de usuário, como mysql, jwt ou redis.

## Acesso Não Autenticado
Para configurar o acesso não autenticado, use a opção allow_anonymous:

``` conf
listener 1883
allow_anonymous true
```

É válido permitir acesso anônimo e autenticado no mesmo broker. Em particular, o plugin dynamic security permite que você atribua direitos diferentes a usuários anônimos em relação aos usuários autenticados, o que pode ser útil para acesso somente leitura a dados, por exemplo.

<br>


# 2 - Uso de mosquitto_passwd

## mosquitto_passwd — gerencia arquivos de senha para o mosquitto

## Comando
mosquitto_passwd [ -H hash ] [ -c | -D ] arquivo_senha usuario
mosquitto_passwd [ -H hash ] -b arquivo_senha usuario senha
mosquitto_passwd -U arquivo_senha


## Descrição
mosquitto_passwd é uma ferramenta para gerenciar arquivos de senha para o servidor MQTT mosquitto.

Nomes de usuário não podem conter ":". As senhas são armazenadas em um formato similar ao crypt(3).

## Opções
**-b**  ➡️ Modo batch. Permite informar a senha diretamente na linha de comando (útil, mas deve ser usado com cuidado pois a senha ficará visível no histórico de comandos).

**-c**  ➡️ Cria um novo arquivo de senhas. Se o arquivo já existir, será sobrescrito.

**-D**  ➡️ Remove o usuário especificado do arquivo de senhas.

**-H**  ➡️ Seleciona o algoritmo de hash. 
Pode ser:
  - sha512-pbkdf2 (padrão)
  - sha512 (para compatibilidade com Mosquitto 1.6 e versões anteriores)

**-U**  ➡️ Atualiza/converte um arquivo de senhas com texto puro para usar hashes. Modifica o arquivo especificado.  

**`Atenção`**: Não detecta se as senhas já estão hasheadas - usar em arquivos já hasheados tornará o arquivo inutilizável.

**arquivo_senha** ➡️O arquivo de senhas a ser modificado.

**usuario** ➡️O usuário a ser adicionado/atualizado/removido.

**senha** ➡️A senha a ser usada no modo batch.

## Códigos de Saída
Retorna 0 em caso de sucesso ou valores não-zero em caso de erro.

### Códigos CONNACK MQTT v3.1.1:
- 0 ➡️ Sucesso
- 1 ➡️ Versão de protocolo inválida
- 2 ➡️ Identificador rejeitado
- 3 ➡️ Servidor indisponível
- 4 ➡️ Usuário/senha inválidos
- 5 ➡️ Não autorizado

### Códigos MQTT v5:
- 0 ➡️ Sucesso
- 128-162 ➡️ Diversos códigos de erro específicos (vide original para lista completa)

## Exemplos
Adicionar um usuário a um novo arquivo passwd:
``` bash
mosquitto_passwd -c /etc/mosquitto/passwd fulano
``` 

Remover um usuário:
``` bash
mosquitto_passwd -D /etc/mosquitto/passwd fulano
``` 

<br>

# 3 - MOSQUITTO-TLS

## mosquitto-tls — Configura suporte SSL/TLS para o Mosquitto

## Descrição
O Mosquitto fornece suporte SSL para conexões de rede criptografadas e autenticação. Este manual descreve como criar os arquivos necessários.

## Observação importante
É fundamental usar parâmetros distintos (subject) para os certificados da CA, servidor e clientes. Se os certificados parecerem idênticos, mesmo que gerados separadamente, o broker/cliente não conseguirá distingui-los e você enfrentará erros difíceis de diagnosticar.

## Gerando certificados
As seções abaixo mostram os comandos openssl para gerar certificados. Para um tutorial completo, consulte:  
https://asciinema.org/a/201826

### Autoridade Certificadora (CA)
Gerar certificado e chave da CA:
bash
openssl req -new -x509 -days <duração> -extensions v3_ca -keyout ca.key -out ca.crt


### Servidor
Gerar chave do servidor (com criptografia):
```bash
openssl genrsa -aes256 -out server.key 2048
```

Gerar chave do servidor (sem criptografia):
```bash
openssl genrsa -out server.key 2048
```

Gerar solicitação de assinatura de certificado (CSR):
```bash
openssl req -out server.csr -key server.key -new
```

**`Atenção`**: Quando solicitado o CN (Common Name), informe o hostname ou domínio do seu servidor/broker.

Assinar o CSR com a chave da CA:
```bash
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days <duração>
```

### Cliente
Gerar chave do cliente:
```bash
openssl genrsa -aes256 -out client.key 2048
```

Gerar CSR do cliente:
```bash
openssl req -out client.csr -key client.key -new
```

Assinar o CSR do cliente:
```bash
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days <duração>
``` 

## `Dicas importantes`
1. ➡️ **Substitua <duração> pelo número de dias de validade dos certificados**
2. ➡️ **Para ambientes de produção, recomenda-se sempre usar chaves criptografadas**
3. ➡️ **Mantenha a chave da CA (ca.key) em local extremamente seguro**
4. ➡️ **Revogue certificados comprometidos imediatamente**


