# SIPp Load Tester Pro — Gerador de Chamadas Simultâneas para Windows

Aplicação Desktop profissional para **Windows** desenvolvida para geração de **chamadas SIP simultâneas com áudio real RTP** (PCAP G.711 a-law), registro de ramais com autenticação Digest (401/407), testes de estresse, simulação de tráfego orgânico/humano e controle de tráfego em tempo real contra servidores **Asterisk**, PBX IP e Gateways SIP.

O aplicativo conta com uma interface gráfica moderna baseada no **Shadcn Luna Dark UI**, motor SIP nativo para Windows embutido (`bin/sipp/sipp.exe`), indicador de status de registro com LED luminoso, console de streaming em tempo real e camada de segurança e sanitização integrada.

---

## 📋 Requisitos de Sistema & Pré-requisitos

- **Sistema Operacional**: Windows 10, Windows 11 ou Windows Server (64-bit).
- **Python**: **Python 3.9 ou superior** (Testado e homologado em **Python 3.10, 3.11, 3.12 e 3.13**).
  > **Nota**: Ao instalar o Python no Windows, certifique-se de marcar a opção **"Add Python to PATH"**.
- **Binários SIPp**: O repositório já inclui os binários portáteis e bibliotecas Cygwin necessárias em `bin/sipp/`.
- **Áudio RTP**: Arquivos PCAP de áudio pré-configurados em `pcap/g711a.pcap`.

---

## 📸 Recursos Principais

- **100% Compatível com Windows**: Binário `sipp.exe` para Windows e bibliotecas de suporte Cygwin integradas na pasta `bin/sipp/` — sem necessidade de compilação ou instalações externas complexas.
- **Gerenciador Central de Caminhos (`core/paths.py`)**: Resolução de caminhos dinâmicos absolutos baseados na raiz do projeto, garantindo funcionamento impecável independente de onde o terminal foi aberto.
- **Interface Gráfica Moderna (CustomTkinter)**: Estética limpa e minimalista inspirada no tema Shadcn Luna, com suporte a DPI awareness no Windows e fontes nativas (`Segoe UI`, `Consolas`).
- **Registro SIP com LED em Tempo Real**: Teste de registro Digest (401/407) com indicador LED colorido (Verde 200 OK com tempo de resposta em segundos, Amarelo em verificação, Vermelho em caso de falha/timeout).
- **Separação de Ramal e Usuário de Autenticação**: Permite cenários em que o Ramal/Caller ID (`[$user]`) difere do Usuário de Autenticação Digest (`-au`).
- **Configurações Avançadas de Rede**: Suporte a Porta Local SIP (`-p`), Porta Base de Mídia RTP (`-mp`) e Seletor dinâmico de Arquivos de Áudio PCAP (`play_pcap_audio`).
- **Estratégias de Discagem & Simulação Humana**:
  - **Regime Constante**: Mantém patamar de N chamadas ativas contínuas (`-l`).
  - **Taxa de Reposição**: Controle de novas chamadas por período (`-r` e `-rp`).
  - **Simulação Humana / Tráfego Orgânico**: Jitter aleatório entre discagens, chance de picos (burst %) e tokens de sessão dinâmicos.
  - **Tabela Ponderada de Destinos**: Configure de 1 até 10 números com pesos relativos (1-100) e cálculo percentual automático em tempo real.
- **Console & Métricas ao Vivo**:
  - 5 Cartões de métricas (Simultâneas Ativas, Total Disparadas, Sucesso 200 OK, Falhas, CPS).
  - Terminal de logs com exportação e cópia.
  - Controles de Pausa (`'p'`), Parada Suave (`'q'`) e Encerramento de Emergência (Kill).
- **Camada de Segurança (Zero Leaks)**: Sanitização estrita contra SIP/Command Injection, mascaramento de senhas em logs, proteção por `.env` e trituração/deleção segura de credenciais temporárias.

---

## 📂 Estrutura de Diretórios do Projeto

```
Chamadas_Externa_Simultaneas_SIPp/
├── app.py                      # Ponto de entrada principal da aplicação GUI
├── iniciar_app.bat             # Inicializador inteligente com auto-setup do .venv
├── instalar_dependencias.bat   # Script dedicado para instalação/reparo de dependências
├── requirements.txt            # Dependências Python com faixas compatíveis (Python 3.9+)
├── config.json                 # Configurações salvas da UI (sanitizado, Zero Leak)
├── .env                        # Credenciais e segredos locais (ignorado no git)
├── .env.example                # Modelo de variáveis de ambiente com documentação
├── .gitignore                  # Higiene de repositório e proteção de credenciais
├── README.md                   # Documentação completa do projeto
├── run.sh                      # Script utilitário em Bash com leitura dinâmica de .env
│
├── bin/                        # Binários e bibliotecas de execução
│   └── sipp/                   # SIPp nativo para Windows (sipp.exe + DLLs Cygwin)
│
├── scenarios/                  # Cenários e templates XML do SIPp
│   ├── register.xml            # Cenário de registro Digest (401/407)
│   ├── call.xml.template       # Template de chamada com suporte a @@PCAP_FILE@@
│   └── call.xml                # Cenário gerado dinamicamente para execução
│
├── pcap/                       # Arquivos de áudio RTP
│   ├── g711a.pcap              # Áudio G.711 a-law (8kHz)
│   └── dtmf_2833_*.pcap        # Tons DTMF RFC 2833 (0-9, *, #)
│
├── core/                       # Regras de negócio e motor backend
│   ├── paths.py                # Gerenciador centralizado de caminhos e ambiente de DLLs
│   ├── config_manager.py       # Gerenciamento de configurações e perfis com suporte .env
│   ├── scenario_builder.py     # Construtor dinâmico de cenários XML e CSVs
│   ├── strategy_manager.py     # Distribuição ponderada e simulação humana
│   ├── security.py             # Validações de segurança, sanitização e mascaramento
│   ├── sipp_engine.py          # Orquestração assíncrona de subprocessos do SIPp
│   └── sipp_downloader.py      # Localizador inteligente do sipp.exe e checagem de versão
│
├── lib/                        # Dependências Python embutidas (100% Offline / Zero-Install)
├── wheels/                     # Pacotes .whl offline pré-baixados (Python 3.9 a 3.13)
│
├── gui/                        # Interface gráfica Desktop (CustomTkinter)
│   ├── main_window.py          # Janela principal e coordenação de abas
│   ├── tab_register.py         # Aba 1: Conexão SIP, Portas/Mídia, Registro com LED e Chamada Única
│   ├── tab_strategy.py         # Aba 2: Estratégia de Discagem, Pesos e Modo Randômico
│   ├── tab_console.py          # Aba 3: Console em tempo real, Métricas e Controles de Carga
│   ├── tab_about.py            # Aba 4: Sobre a aplicação, Topologia e Fluxos SIP
│   └── components/             # Componentes modulares (LED, Métricas, Tabela de Destinos)
│
├── docs/                       # Documentação adicional (PDFs)
└── tests/                      # Suíte de testes automatizados do backend
    └── test_backend.py         # Testes de integração de caminhos, isolamento e cenários
```

---

## 🚀 Como Iniciar em uma Nova Máquina Windows (100% Offline)

O aplicativo é **totalmente autocontido e não requer acesso à internet** na máquina de destino:

### Opção 1: Inicialização em 1 Clique (Recomendado)
Dê um duplo clique no arquivo:
- **`iniciar_app.bat`**

O script:
1. Detecta o Python instalado no Windows.
2. Executa a aplicação imediatamente utilizando as bibliotecas pré-embutidas em `lib/` ou instaladas localmente a partir de `wheels/` (sem precisar baixar nada da internet).
3. Abre a interface gráfica com DPI awareness ajustado.

---

### Opção 2: Instalação Offline de Dependências
Caso queira configurar o ambiente virtual `.venv` localmente sem internet:
1. Dê um duplo clique no arquivo **`instalar_dependencias.bat`** (ele utiliza os arquivos `.whl` da pasta `wheels/`).
2. Em seguida, inicie o app com **`iniciar_app.bat`**.

---

### Opção 3: Pelo Terminal do Windows (PowerShell / CMD)
```powershell
# 1. Clonar o repositório
git clone <URL_DO_REPOSITORIO>
cd Chamadas_Externa_Simultaneas_SIPp

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
.\.venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Criar o arquivo de credenciais local
Copy-Item .env.example .env

# 5. Executar a aplicação
python app.py
```

---

### Opção 4: Executar a Suíte de Testes Automatizados
Para validar se todos os módulos, caminhos e regras de segurança estão 100% operacionais:
```powershell
python tests/test_backend.py
```

---

## 🌐 Topologia de Rede & Fluxo de Comunicação

```
┌─────────────────────────────────────────┐                ┌─────────────────────────────────────────┐
│          CLIENTE GERADOR DE CARGA       │                │          SERVIDOR PBX IP / ASTERISK     │
│        (SIPp Load Tester Pro GUI)       │                │                                         │
│                                         │                │                                         │
│  ┌───────────────────────────────────┐  │                │  ┌───────────────────────────────────┐  │
│  │ Core Engine (Python 3.9 - 3.13)   │  │                │  │ PJSIP / SIP Core Engine           │  │
│  │ - Config & Strategy Manager       │  │                │  │ - Endpoint Registry (AOR)         │  │
│  │ - Security & Masking Layer        │  │                │  │ - Digest Authentication (401/407) │  │
│  │ - Centralized Paths (core/paths)  │  │                │  │ - RTP Media Handler               │  │
│  └─────────────────┬─────────────────┘  │                │  └─────────────────▲─────────────────┘  │
│                    │                    │                │                    │                    │
│  ┌─────────────────▼─────────────────┐  │  SIP (UDP/TCP) │  ┌─────────────────┴─────────────────┐  │
│  │ SIPp Process (bin/sipp/sipp.exe)  ├─┼────────────────┼─►│ Porta SIP 5060                    │  │
│  │ - REGISTER & INVITE Scenarios     │  │  Sinalização   │  │ (From, To, Contact, CSeq, Auth)   │  │
│  └─────────────────┬─────────────────┘  │                │  └─────────────────┬─────────────────┘  │
│                    │                    │                │                    │                    │
│  ┌─────────────────▼─────────────────┐  │   Mídia RTP    │  ┌─────────────────▼─────────────────┐  │
│  │ PCAP RTP Player (pcap/g711a.pcap) ├─┼────────────────┼─►│ RTP Engine (Portas 10000-20000)   │  │
│  │ - G.711 a-law Audio Stream (8kHz) │  │ (Payload PCMA) │  │ - Echo() / URA / Fila Atendimento │  │
│  └───────────────────────────────────┘  │                │  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘                └─────────────────────────────────────────┘
```

---

## ⚙️ Detalhes dos Binários SIPp & DLLs Cygwin no Windows

O projeto acompanha um binário `sipp.exe` compilado com a camada de emulação Cygwin na pasta `bin/sipp/`.
- **Resolução Automática de DLLs**: O módulo [`core/paths.py`](file:///e:/00%20-%20DEV/Chamadas_Externa_Simultaneas_SIPp/core/paths.py) injeta dinamicamente o diretório `bin/sipp` na variável de ambiente `PATH` durante a execução de subprocessos, garantindo que o Windows sempre localize as DLLs `cygwin1.dll`, `cygssl-0.9.8.dll`, `cygcrypto-0.9.8.dll` e `cygncurses-10.dll` sem necessidade de alterar as variáveis de ambiente globais do sistema.
- **Detecção de SIPp do Sistema**: A classe [`SippLocator`](file:///e:/00%20-%20DEV/Chamadas_Externa_Simultaneas_SIPp/core/sipp_downloader.py) também suporta automaticamente binários modernos do SIPp instalados via Chocolatey (`choco install sipp`), Cygwin 64-bit (`C:\cygwin64\bin\sipp.exe`), `C:\Program Files\SIPp\sipp.exe` ou WSL2 (`wsl sipp`).

---

## 📖 Guia de Uso das 4 Abas

### 🔐 Aba 1: Registro & Conexão SIP
- **Alvo Asterisk IP / FQDN**: Endereço de destino na rede (ex: `192.168.1.100`).
- **Porta SIP**: Porta do servidor (padrão `5060`).
- **Transporte**: Selecione `u1 (UDP)` ou `t1 (TCP)`.
- **Domínio SIP**: Domínio da identidade SIP que aparece nos cabeçalhos `From`, `To` e Request-URI.
- **Ramal (Caller ID)**: Número/identidade do ramal (`[$user]`).
- **Usuário de Autenticação (Auth User)**: Usuário enviado no desafio Digest (`-au`).
- **Senha do Ramal**: Senha utilizada no cálculo MD5 da autenticação digest (`-ap`).
- **Portas Locais & Range de Mídia RTP**:
  - **Porta Local SIP (`-p`)**: Fixe uma porta local (ex: `5060`, `5062`) ou deixe em branco para alocação dinâmica.
  - **Porta Base Mídia RTP (`-mp`)**: Porta inicial para o range de sockets RTP (padrão `6000` ou `10000`).
  - **Arquivo de Áudio PCAP**: Caminho do arquivo `.pcap` tocado no início da chamada.
- **Botão "⚡ Testar Registro do Ramal"**: Envia um `REGISTER` com suporte a desafio Digest e atualiza o **LED** luminoso com o resultado (200 OK em X.XXs ou código de erro).
- **Chamada Única Rápida**: Permite discar para um destino específico e desligar a qualquer momento para validar áudio e sinalização.

### 🎯 Aba 2: Estratégia de Discagem & Destinos Ponderados
- **Simultâneas (`-l`)**: Patamar constante de chamadas ativas que o SIPp mantém simultaneamente.
- **Total (`-m`)**: Quantidade total de chamadas a gerar (`0` = Ilimitado / contínuo até você parar).
- **Duração Mínima / Máxima (ms)**: Range de tempo em que cada chamada permanece conectada via `<pause distribution="uniform">`.
- **Duração Fixa**: Checkbox que trava a duração no valor mínimo.
- **Modos de Discagem**:
  - **Taxa Constante (Rate/Period)**: Taxa de novas chamadas por período em milissegundos (`-r` e `-rp`).
  - **Simulação Humana (Orgânico / Randômico)**: Introduz variações realistas de intervalo entre discagens, chance de picos percentuais e prefixos de token para simulação de múltiplos atendentes.
- **Tabela de Destinos (1 a 10)**:
  - Habilite os destinos desejados com caixas de seleção.
  - Ajuste a prioridade/peso de cada destino (1 a 100).
  - O aplicativo calcula e exibe a porcentagem exata de tráfego que cada número receberá.

### 🖥️ Aba 3: Console & Métricas ao Vivo
- **Indicadores em Tempo Real**:
  - 📞 **Simultâneas Ativas**: Chamadas conectadas no momento sobre o teto configurado.
  - 📈 **Total Disparadas**: Quantidade acumulada de chamadas enviadas.
  - ✅ **Atendidas (200 OK)**: Chamadas completadas com sucesso.
  - ❌ **Falhas / Timeouts**: Erros de conexão, ocupado (486), rejeições ou indisponibilidade (503).
  - ⚡ **Taxa Instantânea**: Chamadas por segundo (CPS) em tempo real.
- **Terminal de Logs**: Exibe todas as mensagens trocadas com o processo SIPp, com botões para **Limpar**, **Copiar** e **Exportar** para `.log`.
- **Barra de Controle**:
  - 🚀 **Iniciar Teste de Carga**: Dispara o teste conforme a estratégia configurada.
  - ⏸️ **Pausar ('p')**: Congela a criação de novas chamadas sem derrubar as existentes.
  - 🛑 **Parar Suave ('q')**: Para de gerar chamadas e aguarda as ativas encerrarem naturalmente.
  - 💥 **Derrubar Todas**: Força o encerramento imediato de todos os processos `sipp.exe` ativos.

### 📖 Aba 4: Sobre & Topologia
- Visualização completa da topologia de rede, diagrama de sequência SIP detalhado, boas práticas para Asterisk e especificações técnicas da versão.

---

## 🛡️ Camada de Segurança & Proteção de Segredos (.env)

O projeto adota o padrão ouro de isolamento de credenciais e sanitização contínua:

1. **Isolamento de Credenciais via `.env` (Zero Leaks)**:
   - Senhas e credenciais confidenciais são mantidas exclusivamente no arquivo local `.env` (bloqueado pelo `.gitignore`).
   - O arquivo `config.json` armazena apenas preferências de discagem, pesos e tempos, mantendo a chave `"senha": ""` sempre vazia para evitar vazamentos acidentais em commits do Git.
   - O repositório disponibiliza o `.env.example` para que novos ambientes possam ser configurados rapidamente:
     ```powershell
     copy .env.example .env
     ```
2. **Prevenção contra Injeção de Cabeçalho SIP**:
   - Validação estrita pela classe `SecurityValidator` (`core/security.py`) contra quebras de linha CRLF (`\r`, `\n`) e injeções de comandos nos campos de Host, Porta e Ramal.
3. **Mascaramento Automático em Logs**:
   - Todas as senhas e parâmetros `-ap` são mascarados com `******` nas saídas do console em tempo real.
4. **Trituração Segura de Temporários**:
   - Arquivos CSV de credenciais gerados temporariamente para o SIPp são sobrescritos com zeros binários antes de serem excluídos do disco.
5. **Execução Segura de Subprocessos**:
   - Chamadas ao processo do SIPp utilizam estritamente listas de argumentos sanitizadas, sem `shell=True`.

---

## 📄 Licença

Este software é distribuído sob licença proprietária/MIT para fins de homologação e testes de capacidade em infraestruturas de telecomunicações.
