# Tutorial: Passos necessários para criar e configurar certificados **`SSL/TLS`**  para comunicação segura entre um **Broker MQTT** e **Clients** usando OpenSSL.

### Estrutura de Diretórios

Antes de iniciar, vamos organizar os arquivos em uma estrutura de diretórios:

```
certs/
├── broker/
│   ├── broker.crt
│   ├── broker.key
│   └── broker.csr
└── client/
    ├── client.crt
    ├── client.key
    └── client.csr
```

### Passo 1: Gerar Certificados da Autoridade Certificadora (CA)

#### 1.1. Gerar a chave privada da CA

Primeiro, gere a chave privada da CA:

```bash
openssl genrsa -out certs/ca.key 2048
```

#### 1.2. Gerar o certificado da CA

Agora, crie o certificado autoassinado para a CA:

```bash
openssl req -x509 -new -nodes -key certs/ca.key -sha256 -days 3650 -out certs/ca.crt
```

Preencha os detalhes solicitados, como o **Common Name (CN)**, que pode ser algo como "Minha Autoridade Certificadora".

---

### Passo 2: Gerar Certificados para o Broker MQTT

#### 2.1. Gerar a chave privada do broker

Execute o comando abaixo para gerar a chave privada do broker MQTT:

```bash
openssl genrsa -out certs/broker/broker.key 2048
```

#### 2.2. Gerar a Solicitação de Assinatura de Certificado (CSR) para o Broker

Agora, crie a solicitação de certificado para o broker:

```bash
openssl req -new -key certs/broker/broker.key -out certs/broker/broker.csr
```

Preencha os detalhes, sendo importante definir o **Common Name (CN)** como o nome do domínio ou o IP do broker (por exemplo, `mqtt.exemplo.com` ou `192.168.1.100`).

#### 2.3. Assinar o Certificado do Broker com a Chave da CA

Assine o certificado do broker usando a chave da CA:

```bash
openssl x509 -req -in certs/broker/broker.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial -out certs/broker/broker.crt -days 365 -sha256
```

Isso criará o **certificado do broker** (`broker.crt`) assinado pela sua CA.

---

### Passo 3: Gerar Certificados para o Cliente MQTT

#### 3.1. Gerar a chave privada do cliente

Execute o comando abaixo para gerar a chave privada do cliente:

```bash
openssl genrsa -out certs/client/client.key 2048
```

#### 3.2. Gerar a Solicitação de Assinatura de Certificado (CSR) para o Cliente

Crie a solicitação de certificado para o cliente:

```bash
openssl req -new -key certs/client/client.key -out certs/client/client.csr
```

Preencha os detalhes do cliente. O **Common Name (CN)** pode ser o nome do cliente, como "cliente_1".

#### 3.3. Assinar o Certificado do Cliente com a Chave da CA

Assine o certificado do cliente com a chave da CA:

```bash
openssl x509 -req -in certs/client/client.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial -out certs/client/client.crt -days 365 -sha256
```

Isso criará o **certificado do cliente** (`client.crt`), assinado pela sua CA.

---

### Arquivos Gerados

Após executar os comandos acima, você terá os seguintes arquivos na estrutura de diretórios:

#### Para o **Broker** (na pasta `certs/broker/`):
- **`certs/broker/broker.crt`**: Certificado assinado da CA.
- **`certs/broker/broker.key`**: Chave privada do broker.
- **`certs/broker/broker.csr`**: Solicitação de assinatura de certificado (CSR) do broker.

#### Para o **Cliente** (na pasta `certs/client/`):
- **`certs/client/client.crt`**: Certificado assinado do cliente.
- **`certs/client/client.key`**: Chave privada do cliente.
- **`certs/client/client.csr`**: Solicitação de assinatura de certificado (CSR) do cliente.
- **`certs/ca.crt`**: Certificado da CA (para validar o broker).

---

### Passo 4: Configurar o Broker MQTT para Usar TLS

Para configurar o **Mosquitto** (ou outro broker MQTT) para usar TLS, edite o arquivo de configuração `mosquitto.conf` com os seguintes parâmetros:

```bash
# Caminhos dos arquivos TLS
cafile /caminho/para/certs/ca.crt            # Certificado da CA
certfile /caminho/para/certs/broker/broker.crt  # Certificado do servidor
keyfile /caminho/para/certs/broker/broker.key   # Chave privada do servidor

# Porta segura para comunicação TLS
listener 8883
cafile /caminho/para/certs/ca.crt
certfile /caminho/para/certs/broker/broker.crt
keyfile /caminho/para/certs/broker/broker.key

# Habilitar TLS
tlsv1.2 true
```

- **Porta TLS**: A porta `8883` é a padrão para comunicação MQTT segura via TLS.

---

### Passo 5: Configurar o Cliente MQTT para Usar TLS

Para que o cliente se conecte com segurança ao broker usando TLS, ele precisará configurar a conexão para usar:

- **Certificado do Cliente** (`client.crt`).
- **Chave Privada do Cliente** (`client.key`).
- **Certificado da CA** (`ca.crt`) para validar o broker.

Aqui está um exemplo de como configurar o cliente com **paho-mqtt** (em Python):

```python
import paho.mqtt.client as mqtt

# Configuração TLS do cliente
client = mqtt.Client()

# Definir os arquivos de certificado
client.tls_set(ca_certs="certs/ca.crt", certfile="certs/client/client.crt", keyfile="certs/client/client.key")

# Conectar ao broker MQTT com TLS
client.connect("mqtt.exemplo.com", port=8883)

# Iniciar a comunicação MQTT
client.loop_start()
```

---

### CERTIFICADO:

- Testar se o certificado é valido:
  
`Comando`: openssl verify -CAfile certs/ca.crt certs/broker/broker.crt

`Retorno`: certs/broker/broker.crt: OK    

- Verficar oque tem no certificado:
  
`Comando`: openssl x509 -in certs/broker/broker.crt -text -noout  

`Retorno`: 
```
Certificate:                                                                                                                                             
    Data:                                                                                                                                                  
        Version: 3 (0x2)
        Serial Number:
            20:42:f3:ad:fa:f6:e9:eb:47:d6:dd:c2:61:a2:1d:ac:a3:a0:77:5e
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: C=BR, ST=RS, L=Pelotas, O=AllCode, OU=SD, CN=Minha Autoridade Certificadora
        Validity
            Not Before: Dec 19 23:41:35 2024 GMT
            Not After : Dec 19 23:41:35 2025 GMT
        Subject: C=BR, ST=RS, L=Pelotas, O=AllCode, OU=SD, CN=localhost
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public-Key: (2048 bit)
                Modulus:
                    00:da:ad:c5:01:76:33:74:02:3f:e4:91:f7:c6:58:
                    cd:df:6c:27:81:e6:16:87:11:ff:c6:b2:20:8e:1b:
                    34:48:a0:72:d9:57:9d:ba:14:7a:b1:73:c5:cb:d7:
                    f1:1d:dc:10:15:39:62:ed:68:eb:c7:8d:15:dc:58:
                    0b:2e:b6:a0:f9:53:44:22:ea:5c:8b:c1:0e:a7:34:
                    88:12:9c:87:e5:f2:6a:d6:c5:d1:29:28:56:2d:60:
                    89:d0:39:84:53:e3:e3:4c:e2:0e:f3:54:3d:10:50:
                    75:4b:a7:e7:9c:5c:48:df:75:cf:00:36:20:11:93:
                    3a:ec:ea:3b:e1:ad:f8:45:1c:d3:0d:e2:2a:41:f2:
                    85:02:76:ed:f1:41:46:55:6f:91:40:21:5e:49:74:
                    7e:a5:fb:52:da:41:bb:72:6b:17:c4:da:f8:6f:05:
                    92:d1:be:88:70:3f:ee:4b:6c:f8:ce:a4:0b:46:10:
                    35:f5:65:9b:64:d6:b5:88:b2:6f:b8:31:b9:0b:47:
                    51:41:32:c4:04:73:99:9e:d8:e1:1a:56:5b:ac:a2:
                    ff:6c:26:fc:61:3a:08:b9:d5:d3:79:b6:09:a1:bf:
                    e3:a7:0d:d2:5d:d1:5a:c2:75:0f:a4:d3:e2:ac:44:
                    ab:5f:06:e9:5f:71:bd:10:19:31:9b:ac:0e:1e:67:
                    40:37
                Exponent: 65537 (0x10001)
        X509v3 extensions:
            X509v3 Subject Key Identifier:
                BC:D6:94:59:97:2C:96:23:FC:CD:8A:14:4D:56:96:DA:EF:3C:9D:CC
            X509v3 Authority Key Identifier:
                F1:66:B3:7A:3C:83:6E:73:55:B0:50:95:28:D8:DA:48:77:9D:D3:3F
    Signature Algorithm: sha256WithRSAEncryption
    Signature Value:
        8a:d2:cd:5c:df:39:26:35:89:52:e3:29:3c:53:ac:3e:2a:2d:
        96:48:a2:5e:c1:58:53:22:56:e0:9a:ae:77:00:34:ac:6a:2d:
        49:4a:98:52:bb:df:34:05:f2:19:fb:76:ed:18:51:15:39:7e:
        fb:73:d3:b5:5a:20:3a:15:e8:8a:fe:38:ac:80:6d:72:31:94:
        2c:02:fd:ba:9c:4a:33:8c:f2:82:58:f3:53:f4:14:78:09:be:
        3d:b6:55:dd:9d:cd:bf:78:10:95:ad:6f:67:14:1f:af:40:90:
        02:d7:65:34:03:4a:08:6a:17:dc:16:11:f3:46:9f:a7:83:5e:
        a7:06:e3:c6:4d:e8:6b:bc:fe:87:53:8d:64:0b:73:f4:e3:c9:
        3f:52:42:d9:20:b6:54:11:b6:40:01:d7:a7:2f:04:88:eb:72:
        6e:6b:ae:b9:62:43:dd:12:dd:53:61:0d:68:4c:a3:11:1b:ec:
        3e:eb:f6:cf:3d:9b:c7:e0:a0:15:b5:cc:95:6a:34:01:0e:59:
        64:2d:88:dd:e5:a7:48:55:7d:e7:7c:ff:9d:ea:65:d1:5d:d2:
        d9:6d:41:2a:b3:0e:70:54:e6:07:c7:dc:76:35:9f:0f:53:e3:
        0b:38:aa:43:cb:e3:33:01:45:59:cb:a0:9f:90:2d:06:4e:73:
        ad:e2:19:ca

```

- Verificar especificamente o domínio (Subject):
  
  `Comando`: openssl x509 -in certs/broker/broker.crt -subject -noout
  
  `Retorno`: subject=C=BR, ST=RS, L=Pelotas, O=AllCode, OU=SD CN=localhost          


### Conclusão

Agora você tem uma comunicação segura via TLS entre o broker MQTT e os clientes, utilizando certificados SSL/TLS. Os passos descritos aqui foram organizados para facilitar a geração e a configuração dos certificados, garantindo que tanto o broker quanto os clientes possam se autenticar e criptografar os dados trocados.

Se você tiver dúvidas ou precisar de ajustes na configuração, sinta-se à vontade para voltar e perguntar!



