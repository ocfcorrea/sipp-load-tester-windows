# AGENTS.md — Diretrizes e Contexto do Projeto

Este arquivo contém o contexto arquitetural, regras de desenvolvimento, convenções de código e comandos de suporte para assistentes de IA (e desenvolvedores) que operam no repositório **SIPp Load Tester Pro**.

---

## 🎯 Visão Geral do Projeto

O **SIPp Load Tester Pro** é uma aplicação desktop para Windows desenvolvida em Python (CustomTkinter) com motor SIP nativo e integração ao SIPp. Foi projetada para testes de estresse, validação de carga, simulação de tráfego humano e chamadas externas simultâneas com áudio RTP real (G.711 a-law) contra servidores PBX IP (Asterisk, FreePBX, Issabel, OpenSIPS, Kamailio, etc.).

### Principais Capacidades:
- **Autenticação Digest MD5 Nativa:** Registro e autenticação SIP (RFC 3261 / RFC 2617) diretamente no motor Python sem depender exclusivamente do SIPp para handshake inicial.
- **Transmissão de Áudio RTP:** Injeção de áudio real via streaming PCAP (`pcap/g711a.pcap`).
- **Simulação Orgânica/Humana:** Controle de CPS (chamadas por segundo), jitter de tempo de fala, pausas e pesos de discagem.
- **Interface Gráfica Moderna:** UI em Slate Dark Mode (CustomTkinter) com indicador de LED luminoso em tempo real para status de registro.
- **Distribuição Standalone (.EXE):** Empacotamento via PyInstaller com resolução dinâmica de caminhos (`_MEIPASS` vs runtime local) e versionamento SemVer baseado em commits Git.

---

## 🏗️ Arquitetura do Repositório

```text
├── app.py                      # Ponto de entrada principal da GUI (DPI-aware, lib injection)
├── config.json                 # Configurações gerais da aplicação (sem credenciais)
├── version.json                # Metadados de versão da release
├── .env / .env.example         # Isolamento estrito de credenciais SIP (IP, usuário, senha)
├── requirements.txt            # Dependências Python mínimas
├── SIPp_Load_Tester_Pro.spec   # Especificação PyInstaller para build .EXE
│
├── core/                       # Camada de Negócio e Motores SIP
│   ├── sip_client.py           # Cliente SIP UDP nativo (Digest MD5, LED status, threads)
│   ├── sipp_engine.py          # Orquestrador do processo CLI do SIPp
│   ├── scenario_builder.py     # Gerador dinâmico de cenários XML para SIPp
│   ├── config_manager.py       # Gerenciamento de config.json e variáveis .env
│   ├── security.py             # Validação defensiva e sanitização de credenciais em logs
│   ├── paths.py                # Resolução de diretórios (modo script vs executável PyInstaller)
│   ├── strategy_manager.py     # Lógica de distribuição de carga e simulação humana
│   ├── version.py              # SemVer dinâmico via contagem de commits Git
│   └── sipp_downloader.py      # Localizador/download de binários SIPp para Windows
│
├── gui/                        # Camada de Interface Gráfica (CustomTkinter)
│   ├── main_window.py          # Janela principal e alternância de abas
│   ├── tab_register.py         # Aba 1: Registro SIP & Conexão (LED de status)
│   ├── tab_strategy.py         # Aba 2: Estratégias de Discagem & Carga
│   ├── tab_console.py          # Aba 3: Terminal de Logs em tempo real & Controles
│   ├── tab_about.py            # Aba 4: Topologia Técnica e Links de Release
│   └── components/             # Componentes visuais reutilizáveis
│
├── scenarios/                  # Modelos de cenários SIPp em XML (UAC, UAS, Register)
├── pcap/                       # Capturas de áudio RTP para injeção (ex: g711a.pcap)
├── bin/                        # Binários auxiliares (ex: sipp.exe para Windows)
├── lib/                        # Dependências Python offline pré-instaladas
├── tests/                      # Suíte de testes automatizados
│   └── test_backend.py         # Testes unitários de caminhos, config, segurança e SIP
│
├── iniciar_app.bat             # Inicialização rápida da GUI no Windows
├── instalar_dependencias.bat   # Instalação de dependências no ambiente virtual
└── gerar_executavel.bat        # Compilação do .EXE versionado via PyInstaller
```

---

## 🔒 Regras de Segurança e Isolamento de Credenciais

1. **Zero Leaks de Credenciais:**
   - **NUNCA** salve senhas ou tokens dentro de `config.json` ou arquivos versionados no Git.
   - Credenciais SIP sensíveis (`SIP_HOST`, `SIP_PORT`, `SIP_USER`, `SIP_PASSWORD`, `SIP_DOMAIN`) devem residir exclusivamente no `.env`.
   - Sempre utilize `core.security.SecurityValidator` para sanitizar saídas antes de exibir em logs ou consoles.
2. **Compatibilidade com .env.example:**
   - Ao introduzir novas variáveis de ambiente, atualize imediatamente o arquivo `.env.example` com valores fictícios/placeholders.

---

## ⚙️ Convenções de Código e Boas Práticas

### Python & Backend
- **Compatibilidade:** Suporte a Python 3.9+ em Windows (64-bit).
- **Tratamento de Caminhos:** Utilize SEMPRE `core.paths.get_project_path()` ou funções de resolução de `core.paths` em vez de `os.getcwd()` ou caminhos hardcoded, garantindo funcionamento correto tanto no modo script quanto empacotado no PyInstaller (`sys._MEIPASS`).
- **Concorrência e Threads:** Métodos que realizam chamadas SIP de longa duração ou I/O de rede devem rodar em threads separadas (`threading.Thread(daemon=True)`) para nunca travar o loop de eventos da UI.
- **Tratamento de Exceções:** Todas as chamadas de socket UDP SIP devem ter tratamento explícito de timeouts (`socket.timeout`) e tratamento gracioso de erros de rede.

### Interface Gráfica (CustomTkinter)
- **Tema:** Dark Mode padronizado (Slate Dark).
- **Atualização de UI via Threads:** Sempre use `widget.after(0, callback)` ou despache atualizações para a thread principal do Tkinter ao modificar componentes visuais a partir de threads de background.
- **Responsividade:** Layout baseado em grid/pack responsivo com suporte a DPI Scaling do Windows.

---

## 🛠️ Comandos Mais Utilizados

### Executar a aplicação (Desenvolvimento)
```powershell
# Opção 1: Direto via Python
python app.py

# Opção 2: Via script Batch
.\iniciar_app.bat
```

### Executar a suíte de testes automatizados
```powershell
python -m unittest tests/test_backend.py
# ou execução direta do script de teste:
python tests/test_backend.py
```

### Gerar executável único (.EXE) versionado
```powershell
# Executar o script de build automatizado
.\gerar_executavel.bat
```
*O executável resultante é salvo em `dist/SIPp_Load_Tester_Pro_v<VERSAO>.exe`.*

---

## 📌 Diretrizes para Modificações Futuras

- **Adicionar Novo Cenário XML:** Adicione o arquivo em `scenarios/` e registre a opção correspondente em `core/scenario_builder.py` e na UI `gui/tab_strategy.py`.
- **Adicionar Novo Arquivo de Áudio:** Insira o `.pcap` em `pcap/` e valide a inclusão no arquivo `SIPp_Load_Tester_Pro.spec` (datas) para que seja empacotado no executável.
- **Alterações de Versionamento:** Não altere a versão manualmente em arquivos estáticos sem necessidade; a versão é derivada via `core/version.py` a partir do histórico Git.
