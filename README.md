# SIPp Load Tester Pro — Gerador de Chamadas Simultâneas para Windows

Aplicação Desktop profissional para **Windows** desenvolvida para geração de **chamadas SIP simultâneas com áudio real RTP** (PCAP G.711 a-law), registro de ramais com autenticação Digest (401/407), testes de estresse, simulação de tráfego orgânico/humano e controle de tráfego em tempo real contra servidores **Asterisk**, PBX IP e Gateways SIP.

O aplicativo conta com uma interface gráfica moderna baseada no **Shadcn Luna Dark UI**, motor SIP nativo para Windows embutido (`bin/sipp/sipp.exe`), indicador de status de registro com LED luminoso, console de streaming em tempo real e camada de segurança e sanitização integrada.

---

## 📸 Recursos Principais

- **100% Compatível com Windows**: Binário `sipp.exe` para Windows e bibliotecas de suporte Cygwin integradas na pasta `bin/sipp/` — sem necessidade de compilação ou instalações externas complexas.
- **Interface Gráfica Moderna (CustomTkinter)**: Estética limpa e minimalista inspirada no tema Shadcn Luna, com suporte a DPI awareness no Windows.
- **Registro SIP com LED em Tempo Real**: Teste de registro Digest (401/407) com indicador LED colorido (Verde 200 OK com tempo de resposta em segundos, Amarelo em verificação, Vermelho em caso de falha/timeout).
- **Separação de Ramal e Usuário de Autenticação**: Permite cenários em que o Ramal/Caller ID (`[$user]`) difere do Usuário de Autenticação Digest (`-au`).
- **Configurações Avançadas de Rede**: Suporte a Porta Local SIP (`-p`), Porta Base de Mídia RTP (`-mp`) e Seletor dinâmico de Arquivos de Áudio PCAP (`play_pcap_audio`).
- **Estratégias de Discagem & Simulação Humana**:
  - Regime Constante: Mantém patamar de N chamadas ativas contínuas (`-l`).
  - Taxa de Reposição: Controle de novas chamadas por período (`-r` e `-rp`).
  - Simulação Humana / Tráfego Orgânico: Jitter aleatório entre discagens, chance de picos (burst %) e tokens de sessão dinâmicos.
  - Tabela Ponderada de Destinos: Configure de 1 até 10 números com pesos relativos (1-100) e cálculo percentual automático em tempo real.
- **Console & Métricas ao Vivo**:
  - 5 Cartões de métricas (Simultâneas Ativas, Total Disparadas, Sucesso 200 OK, Falhas, CPS).
  - Terminal de logs com exportação e cópia.
  - Controles de Pausa (`'p'`), Parada Suave (`'q'`) e Encerramento de Emergência (Kill).
- **Camada de Segurança**: Sanitização estrita contra SIP/Command Injection, mascaramento de senhas em logs e trituração/deleção segura de credenciais temporárias.

---

## 📂 Estrutura de Diretórios do Projeto

```
Chamadas_Externa_Simultaneas_SIPp/
├── app.py                      # Ponto de entrada principal da aplicação GUI
├── iniciar_app.bat             # Inicializador rápido de 1 clique para Windows
├── requirements.txt            # Dependências Python fixadas
├── config.json                 # Configurações salvas (conexão, portas, estratégias)
├── .gitignore                  # Higiene de repositório e proteção de arquivos temporários
├── README.md                   # Documentação completa do projeto
├── run.sh                      # Script utilitário em Bash (compatível com WSL/Git Bash)
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
│   ├── config_manager.py       # Gerenciamento de configurações e perfis
│   ├── scenario_builder.py     # Construtor dinâmico de cenários XML e CSVs
│   ├── strategy_manager.py     # Distribuição ponderada e simulação humana
│   ├── security.py             # Validações de segurança, sanitização e mascaramento
│   ├── sipp_engine.py          # Orquestração assíncrona de subprocessos do SIPp
│   └── sipp_downloader.py      # Localizador inteligente do bin/sipp/sipp.exe
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
```

---

## 🚀 Como Iniciar no Windows

### Opção 1: Inicialização em 1 Clique (Recomendado)
Dê um duplo clique no arquivo:
- **`iniciar_app.bat`**

O script detecta automaticamente o ambiente virtual Python (`.venv`), instala as dependências se necessário e abre a interface gráfica.

### Opção 2: Pelo Terminal do Windows (PowerShell / Prompt de Comando)
```powershell
# Ativar o ambiente virtual e executar
.\.venv\Scripts\python.exe app.py
```

### Opção 3: Executar a Suíte de Testes Automatizados
```powershell
.\.venv\Scripts\python.exe tests\test_backend.py
```

---

## 🌐 Topologia de Rede & Fluxo de Comunicação

```
┌─────────────────────────────────────────┐                ┌─────────────────────────────────────────┐
│          CLIENTE GERADOR DE CARGA       │                │          SERVIDOR PBX IP / ASTERISK     │
│        (SIPp Load Tester Pro GUI)       │                │                                         │
│                                         │                │                                         │
│  ┌───────────────────────────────────┐  │                │  ┌───────────────────────────────────┐  │
│  │ Core Engine (Python 3.12)         │  │                │  │ PJSIP / SIP Core Engine           │  │
│  │ - Config & Strategy Manager       │  │                │  │ - Endpoint Registry (AOR)         │  │
│  │ - Security & Masking Layer        │  │                │  │ - Digest Authentication (401/407) │  │
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

## 📖 Guia de Uso das 4 Abas

### 🔐 Aba 1: Registro & Conexão SIP
- **Alvo Asterisk IP / FQDN**: Endereço de destino na rede (ex: `192.168.68.205`).
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

## 🛠️ Cuidados e Boas Práticas no Asterisk

1. **Limite de Chamadas por Endpoint (`pjsip.conf`)**:
   Para permitir que um único ramal gere 50, 100 ou mais chamadas simultâneas, desative a trava de device state no Asterisk:
   ```ini
   [1002]
   type=endpoint
   device_state_busy_at=0        ; 0 = sem limite de chamadas simultâneas
   max_contacts=100
   qualify_frequency=0           ; desabilita qualify OPTIONS durante o teste de carga
   allow=!all,alaw,ulaw
   ```

2. **Destino que Atende e Sustenta Mídia (`extensions.conf`)**:
   O número discado deve atender e manter o canal aberto para sustentar o fluxo RTP:
   ```asterisk
   exten => 9999,1,Answer()
    same => n,Echo()             ; devolve o áudio RTP nos dois sentidos
    same => n,Hangup()
   ```

3. **Faixa de Portas RTP (`rtp.conf`)**:
   Para suportar 100 chamadas simultâneas, configure um range de no mínimo 200 portas RTP no Asterisk (ex: `10000` a `20000`).

---

## 🛡️ Camada de Segurança Integrada

O projeto conta com a classe `SecurityValidator` (`core/security.py`):
- **Prevenção contra Injeção de Cabeçalho SIP**: Validação estrita de hosts, portas e ramais contra caracteres CRLF (`\r`, `\n`) e injeções maliciosas.
- **Proteção de Credenciais**: Mascaramento automático de senhas (`******`) em todos os logs gerados na tela.
- **Trituração Segura de Temporários**: Arquivos CSV de credenciais gerados para o SIPp são sobrescritos com zeros binários antes de serem removidos do disco.
- **Execução Segura**: Chamadas de subprocessos utilizam listas de argumentos sanitizadas sem uso de `shell=True`.

---

## 📄 Licença

Este software é distribuído sob licença proprietária/MIT para fins de homologação e testes de capacidade em infraestruturas de telecomunicações.
