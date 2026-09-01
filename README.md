# SIPp Load Tester Pro — Gerador de Chamadas Simultâneas para Windows

[![GitHub Releases](https://img.shields.io/github/v/release/ocfcorrea/TestSIPpWindows?label=Download%20.EXE%20Release&color=0284c7&logo=github)](https://github.com/ocfcorrea/TestSIPpWindows/releases)
[![Versão](https://img.shields.io/badge/Versão-v2.0_Pro_Auto--SemVer-0284c7.svg)](https://github.com/ocfcorrea/TestSIPpWindows/releases)
[![Plataforma](https://img.shields.io/badge/Plataforma-Windows_10_|_11_|_Server-38bdf8.svg)](#-requisitos-de-sistema)
[![Sinalização](https://img.shields.io/badge/SIP-RFC_3261_|_RFC_2617_MD5-10b981.svg)](#-como-funciona-a-transmissão-de-áudio-rtp-pcap)
[![Segurança](https://img.shields.io/badge/Segurança-Zero_Leaks_with_.env-emerald.svg)](#-camada-de-segurança--isolamento-de-credenciais-env)
[![Operação](https://img.shields.io/badge/Operação-100%25_Offline-purple.svg)](#-como-iniciar-no-windows)

Aplicação Desktop profissional para **Windows** desenvolvida para geração de **chamadas SIP simultâneas de alta performance com áudio real RTP** (PCAP G.711 a-law), registro de ramais com autenticação Digest (RFC 3261 / RFC 2617), testes de estresse, simulação de tráfego orgânico/humano e controle de capacidade em tempo real contra servidores **Asterisk**, PBX IP, FreePBX, Issabel, OpenSIPS, Kamailio e Gateways SIP.

O aplicativo conta com uma interface gráfica moderna em **Slate Dark UI**, motor SIP nativo em Python com **autenticação Digest MD5 integrada** e streaming RTP, indicador de status de registro com **LED luminoso**, console de eventos em tempo real, métricas contínuas, **links diretos para releases** e **100% de operação offline** no Windows.

---

> [!TIP]
> ### 📦 Download Rápido da Release Pronta (.EXE)
> Você pode baixar a versão executável standalone compilada mais recente diretamente na página de [**GitHub Releases**](https://github.com/ocfcorrea/TestSIPpWindows/releases). Não é necessário instalar Python, dependências ou SIPp para rodar o `.exe`.

---

## 📋 Sumário
1. [Requisitos de Sistema & Pré-requisitos](#-requisitos-de-sistema--pré-requisitos)
2. [Como Iniciar no Windows](#-como-iniciar-no-windows)
3. [Versionamento e Geração de Releases Executáveis (.EXE)](#-versionamento-e-geração-de-releases-executáveis-exe)
4. [Publicação Automática de Releases no GitHub (CI/CD)](#-publicação-automática-de-releases-no-github-cicd)
5. [Guia Completo de Todas as Abas da Aplicação](#-guia-completo-de-todas-as-abas-da-aplicação)
   - [Aba 1: Registro SIP & Conexão](#-aba-1-registro-sip--conexão)
   - [Aba 2: Estratégia de Discagem, Pesos & Simulação Humana](#-aba-2-estratégia-de-discagem-pesos--simulação-humana)
   - [Aba 3: Console em Tempo Real, Métricas & Controles](#-aba-3-console-em-tempo-real-métricas--controles)
   - [Aba 4: Sobre & Topologia Técnica](#-aba-4-sobre--topologia-técnica)
6. [Transmissão de Áudio RTP (PCAP)](#-transmissão-de-áudio-rtp-pcap)
7. [Segurança & Isolamento de Credenciais (.env)](#-segurança--isolamento-de-credenciais-env)
8. [Suíte de Testes Automatizados](#-suíte-de-testes-automatizados)
9. [Perguntas Frequentes & Resolução de Problemas](#-perguntas-frequentes--resolução-de-problemas)

---

## 💻 Requisitos de Sistema & Pré-requisitos

- **Sistema Operacional**: Windows 10, Windows 11 ou Windows Server (64-bit).
- **Executável Standalone (.exe)**: **Não requer Python nem SIPp instalados**. Basta baixar o binário da [página de Releases](https://github.com/ocfcorrea/TestSIPpWindows/releases) e executar.
- **Execução via Código Fonte**:
  - Python 3.9+ (homologado em Python 3.10, 3.11, 3.12 e 3.13).
  - Todas as dependências externas já vêm embutidas offline na pasta `lib/`.
- **Áudio RTP**: Áudio pré-configurado em `pcap/g711a.pcap`.

---

## 🚀 Como Iniciar no Windows

### Opção 1: Executável Standalone Versionado (Distribuição / Produção)
Se você baixou a release oficial do GitHub ou compilou localmente:
- Dê um duplo clique em **`dist\SIPp_Load_Tester_Pro_v<VERSAO>.exe`** (ou `dist\SIPp_Load_Tester_Pro.exe`).
- O aplicativo abre instantaneamente em qualquer máquina Windows sem necessidade de instalar dependências.

---

### Opção 2: Inicialização em 1 Clique via Script Batch (Desenvolvimento / Ambiente Local)
Dê um duplo clique no arquivo:
- **`iniciar_app.bat`**

O script:
1. Detecta o Python instalado no sistema.
2. Injeta as bibliotecas da pasta `lib/`.
3. Ajusta o DPI awareness no Windows para renderização perfeita em monitores Full HD e 4K.
4. Abre a interface gráfica imediatamente.

---

### Opção 3: Inicialização via Terminal (PowerShell / Prompt de Comando)
```powershell
# 1. Navegue até a pasta do projeto
cd "e:\00 - DEV\Chamadas_Externa_Simultaneas_SIPp"

# 2. Inicie a aplicação
python app.py
```

---

## 📦 Versionamento e Geração de Releases Executáveis (.EXE)

O projeto conta com um pipeline inteligente de versionamento semântico integrado ao Git:

### Como Funciona a Release Numérica por Commit (SemVer Dinâmico)
1. O módulo central [`core/version.py`](file:///e:/00%20-%20DEV/Chamadas_Externa_Simultaneas_SIPp/core/version.py) consulta a contagem total de commits do repositório Git (`git rev-list --count HEAD`).
2. A versão é formatada automaticamente como: `v2.0.<NUMERO_DO_COMMIT>` (exemplo: commit 11 gera `v2.0.11`).
3. Toda vez que você faz um novo commit no Git e compila o projeto, a versão numérica sobe automaticamente sem precisar editar nenhum arquivo manual.

---

### 🔨 Passo a Passo para Gerar um Novo Executável Versionado:

#### Método Automático (Recomendado):
Dê um duplo clique no arquivo:
- **`gerar_executavel.bat`**

O script executa automaticamente as seguintes etapas:
1. Verifica o Python e a presença do PyInstaller.
2. Extrai e grava a versão atual em `version.json`.
3. Executa o PyInstaller com a spec [`SIPp_Load_Tester_Pro.spec`](file:///e:/00%20-%20DEV/Chamadas_Externa_Simultaneas_SIPp/SIPp_Load_Tester_Pro.spec), embutindo todas as dependências, cenários XML, áudios PCAP e motor SIP em um único arquivo standalone.
4. Gera dois binários na pasta `dist\`:
   - **`dist\SIPp_Load_Tester_Pro_v<VERSAO>.exe`**: Cópia versionada da release para histórico e controle de versão (ex: `SIPp_Load_Tester_Pro_v2.0.11.exe`).
   - **`dist\SIPp_Load_Tester_Pro.exe`**: Executável principal padrão.

---

#### Método Manual via Terminal:
```powershell
# 1. Salva e registra a versão atual do commit
python -c "from core.version import save_version_file; print('Versão salva:', save_version_file())"

# 2. Executa a compilação com PyInstaller
pyinstaller --noconfirm SIPp_Load_Tester_Pro.spec

# 3. Cria a cópia versionada da release
python -c "import shutil, os; from core.version import get_version_tag; tag = get_version_tag(); shutil.copy2('dist/SIPp_Load_Tester_Pro.exe', f'dist/SIPp_Load_Tester_Pro_{tag}.exe')"
```

---

## 🚀 Publicação Automática de Releases no GitHub (CI/CD)

O repositório possui uma GitHub Action configurada em [`.github/workflows/release.yml`](file:///e:/00%20-%20DEV/Chamadas_Externa_Simultaneas_SIPp/.github/workflows/release.yml) para gerar e publicar releases automaticamente no GitHub.

### Para publicar uma nova release oficial:
```powershell
# 1. Obtenha a tag da versão atual
$TAG = python -c "from core.version import get_version_tag; print(get_version_tag())"

# 2. Crie e envie a tag para o GitHub
git tag $TAG
git push origin $TAG
```

A GitHub Action irá:
1. Configurar o ambiente Windows Runner com Python 3.12.
2. Gerar a versão dinâmica baseada no Git.
3. Compilar o executável `.exe` standalone com PyInstaller.
4. Criar a Release oficial no GitHub e anexar os binários `SIPp_Load_Tester_Pro_v*.exe` e `SIPp_Load_Tester_Pro.exe` prontos para download.

---

## 📖 Guia Completo de Todas as Abas da Aplicação

---

### 📡 Aba 1: Registro SIP & Conexão

Esta aba é o centro de parametrização de conectividade com o seu PBX Asterisk, além de oferecer diagnósticos rápidos com LED e Chamada Única.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 📡 PARÂMETROS DE CONEXÃO & IDENTIDADE SIP                                              │
│ • Alvo Asterisk IP / FQDN: 192.168.0.1     │ • Porta SIP: 5060  | Transporte: UDP (u1)  │
│ • Domínio SIP: 192.168.0.1                 │ • IP Local: (vazio = autodetectar)         │
│ • Ramal (Identidade): 1001                 │ • Usuário Digest (Auth User): 1001         │
│ • Senha do Ramal: ••••••••                 │ • Executável SIPp: bin/sipp/sipp.exe       │
├────────────────────────────────────────────┴───────────────────────────────────────────┤
│ 🎧 PORTAS LOCAIS & MÍDIA RTP / ÁUDIO PCAP                                              │
│ • Porta Local SIP (-p): (opcional/vazio)   │ • Porta Base RTP (-mp): 10000              │
│ • Arquivo de Áudio RTP: pcap/g711a.pcap                                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 🚦 STATUS DO REGISTRO SIP (TEMPO REAL)                                                 │
│ 🟢 LED: 200 OK — Registrado (0.01s)                                                    │
│ [ ⚡ Testar Registro do Ramal ]   [ 💾 Salvar Parâmetros de Conexão ]                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 📞 TESTE DE CHAMADA ÚNICA (DIAGNÓSTICO)                                                │
│ • Número de Destino de Teste: 22223333     │ [ ▶️ Disparar Chamada ]  [ ⏹️ Encerrar ]   │
│ Status: 200 OK — Em conversação (transmitindo áudio RTP)                               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 📌 Explicação de Cada Campo da Aba 1:

1. **Alvo Asterisk IP / FQDN**:
   - Endereço IPv4 ou nome DNS do servidor Asterisk/PBX (padrão de teste: `192.168.0.1`).
2. **Porta SIP**:
   - Porta onde o Asterisk escuta sinalização SIP (padrão mundial `5060`).
3. **Transporte**:
   - `u1 (UDP)`: Transporte padrão mais utilizado em telefonia IP (menor latência).
   - `t1 (TCP)`: Transporte orientado a conexão (para redes que exigem pacotes TCP).
4. **Domínio SIP (Identidade)**:
   - Domínio da identidade SIP presente nos cabeçalhos `From`, `To` e `Request-URI` (padrão: `192.168.0.1`).
5. **IP Local (Interface)**:
   - Deixe em branco para autodetecção automática da placa de rede ativa, ou fixe o IP local da sua máquina.
6. **Ramal e Usuário de Autenticação**:
   - **Ramal**: Número de identificação do ramal (ex: `1001`).
   - **Usuário Digest**: Nome de usuário exigido pelo Asterisk no desafio 401/407.
7. **Senha do Ramal**:
   - Senha secreta do ramal. Armazenada de forma protegida no `.env` (Zero Leaks).
8. **Porta Base Mídia RTP (`-mp`)**:
   - Porta base para os canais de áudio RTP (padrão `10000`).
9. **Número de Destino de Teste (Chamada Única)**:
   - Número de extensão ou URA para teste prévio de áudio (padrão: `22223333`).

#### 💡 Ações da Aba 1:
- **⚡ Testar Registro do Ramal**:
  - Envia pacote `REGISTER`, recebe desafio `401 Unauthorized`, calcula o hash MD5 e envia o `REGISTER` autenticado.
  - **LED Luminoso**:
    - 🟢 **Verde**: Registrado com sucesso (`200 OK`) com latência em segundos.
    - 🟡 **Amarelo**: Enviando REGISTER / aguardando resposta.
    - 🔴 **Vermelho**: Falha de autenticação ou PBX inacessível.
- **▶️ Disparar Chamada Única**:
  - Disca para o número de teste `22223333`, autentica, recebe `200 OK` e inicia o streaming contínuo de áudio RTP do PCAP para teste de voz.

---

### 🎲 Aba 2: Estratégia de Discagem, Pesos & Simulação Humana

Nesta aba você configura a inteligência do teste: quantas chamadas manter simultaneamente, quanto tempo cada uma dura, a velocidade de disparo e a distribuição entre múltiplos destinos.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ⚙️ CAPACIDADE & DURAÇÃO DAS CHAMADAS                                                    │
│ • Simultâneas (-l): 30                     │ • Total (-m) [0=Ilimitado]: 0              │
│ • Duração Mínima: 60000 ms (60s)           │ • Duração Máxima: 70000 ms (70s)           │
│ [ ] Duração Fixa (ignora teto máximo e fixa no valor mínimo)                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 🎲 MODO DE DISCAGEM & PADRÃO DE DISPARO                                                │
│ [ ⚡ Taxa Constante (Rate/Period) ]        │ [ 👥 Simulação Humana (Orgânico/Randômico) ]│
│ • Intervalo Mín: 200ms | Intervalo Máx: 1500ms | Chance de Pico: 15% | Prefixo: AGENT_ │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 🎯 TABELA DE DESTINOS & PRIORIDADES DE DISCAGEM (1 A 10)                               │
│ [x] 1. Número: 22223333 | Descrição: Ex. Texto para Identificar | Peso: 10 | Tráfego: 100%│
│ [ ] 2. Número: 22223333 | Descrição: Ex. Texto para Identificar | Peso: 10 | Tráfego: 0.0%│
│ [ ] 3. Número: 22223333 | Descrição: Ex. Texto para Identificar | Peso: 10 | Tráfego: 0.0%│
│ [ ] 4 até 10...                                                                        │
│ [ ⚖️ Distribuir Pesos ]   [ 🧹 Limpar Desmarcados ]   [ 💾 Salvar Estratégia ]          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 📌 Explicação Detalhada de Cada Parâmetro da Aba 2:

1. **Simultâneas (`-l`)**:
   - É o **teto máximo de chamadas ativas conectadas ao mesmo tempo** no Asterisk.
2. **Total (`-m`)**:
   - Quantidade total acumulada de chamadas a gerar antes de encerrar o teste (`0` = Ilimitado / contínuo).
3. **Duração Mínima e Máxima (ms)**:
   - Define a faixa de tempo (em milissegundos) em que cada chamada permanecerá conectada no Asterisk. Cada ligação sorteia uma duração aleatória dentro dessa faixa para simular comportamento realista.
4. **Checkbox "Duração Fixa"**:
   - Se marcada, todas as chamadas durarão rigorosamente o tempo mínimo estipulado.
5. **Modos de Discagem**:
   - ⚡ **Taxa Constante**: Dispara em cadência uniforme (`-r` chamadas por período `-rp`).
   - 👥 **Simulação Humana**: Introduz variações realistas, intervalos orgânicos e chances de rajadas (*bursts*).
6. **Tabela de 10 Destinos Ponderados**:
   - Suporta até 10 destinos com números, descrições e pesos individuais (1 a 100).
   - O tráfego percentual é recalculado e exibido em tempo real.
   - Padrão inicial: 10 linhas configuradas com `22223333` e `Ex. Texto para Identificar`, com **apenas a 1ª linha marcada como ativa**.

---

### 🖥️ Aba 3: Console em Tempo Real, Métricas & Controles

Painel de comando operacional do teste de carga e geração de simultâneas.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 📊 PAINEL DE MÉTRICAS EM TEMPO REAL                                                    │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│ │ SIMULTÂNEAS  │ │  DISPARADAS  │ │  ATENDIDAS   │ │    FALHAS    │ │     CPS      │   │
│ │    30 / 30   │ │     180      │ │     150      │ │      0       │ │   1.5 cps    │   │
│ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 💻 TERMINAL DE LOGS E EVENTOS SIP EM TEMPO REAL                                        │
│ [00:48:10] [HEADER] 🚀 INICIANDO TESTE DE CARGA (MOTOR SIP PRO MD5)                   │
│ [00:48:10] [INFO]   Alvo PBX: 192.168.0.1:5060 (UDP) | Domínio: 192.168.0.1            │
│ [00:48:10] [INFO]   Teto de Simultâneas: 30 | Duração: 60000ms a 70000ms               │
│ [00:48:10] [INFO] ➔ [DISPARO] Chamada #1 para 22223333 (Alvo: 30 simultâneas)          │
│ [00:48:10] [SUCCESS] 🎉 [PBX] Chamada #1 ➔ 22223333 atendida (200 OK)! Mantida por 64s │
│ [00:48:10] [INFO] 🎵 Transmitindo áudio G.711a do PCAP para 192.168.0.1:10000...      │
│ [00:48:12] [INFO] 📊 [PAINEL] Simultâneas: 30/30 | Disparadas: 30 | Atendidas: 30      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [ 🚀 INICIAR TESTE DE CARGA ] [ ⏸️ PAUSAR ] [ 🛑 PARAR SUAVE ] [ 💥 DERRUBAR TODAS ]   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 📌 Cartões de Métricas:
- 📞 **Simultâneas**: Canais conectados simultaneamente sobre o limite configurado (ex: `30 / 30`).
- 📈 **Disparadas**: Total acumulado de ligações enviadas.
- ✅ **Atendidas**: Ligações atendidas com sucesso (`200 OK`).
- ❌ **Falhas**: Ligações recusadas (403, 404, 486, 503, etc.).
- ⚡ **CPS**: Novas chamadas por segundo em tempo real.

#### 🎮 Controles Operacionais:
- **🚀 INICIAR TESTE DE CARGA**: Inicia a geração contínua de chamadas.
- **⏸️ PAUSAR / RETOMAR**: Congela novos disparos mantendo as chamadas ativas conectadas.
- **🛑 PARAR SUAVE**: Não abre novas chamadas e aguarda as ativas encerrarem normalmente.
- **💥 DERRUBAR TODAS (Kill Switch)**: Derruba todas as chamadas ativas instantaneamente via pacote `BYE`.
- **Botão de Emergência no Cabeçalho**: Disponível em qualquer aba para encerramento imediato.

---

### 📖 Aba 4: Sobre & Topologia Técnica

Apresenta detalhes da versão ativa, links de download de releases, repositório GitHub, topologia de sinalização SIP e fluxo de áudio RTP:

```text
┌─────────────────────────────────────────┐                ┌─────────────────────────────────────────┐
│        CLIENTE GERADOR DE CARGA         │                │        SERVIDOR PBX IP / ASTERISK       │
│        (SIPp Load Tester Pro GUI)       │                │                                         │
│                                         │                │                                         │
│  ┌───────────────────────────────────┐  │                │  ┌───────────────────────────────────┐  │
│  │ Core Engine & SipClient (Python)  │  │                │  │ PJSIP / SIP Core Engine           │  │
│  │ - Config & Strategy Manager       │  │                │  │ - Endpoint Registry (AOR)         │  │
│  │ - Security & Masking Layer        │  │                │  │ - Digest Authentication (401/407) │  │
│  └─────────────────┬─────────────────┘  │                │  └─────────────────▲─────────────────┘  │
│                    │                    │                │                    │                    │
│  ┌─────────────────▼─────────────────┐  │  SIP (UDP/TCP) │  ┌─────────────────┴─────────────────┐  │
│  │ SIPp Process / Native SipClient   ├─┼────────────────┼─►│ Porta SIP 5060                    │  │
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

## 🎙️ Transmissão de Áudio RTP (`.pcap`)

1. **Negociação SDP**: Ao receber o `200 OK` do Asterisk, o cliente analisa o cabeçalho SDP e extrai o IP e a porta de áudio abertos pelo PBX (`c=IN IP4` e `m=audio`).
2. **Cache em RAM**: O arquivo `pcap/g711a.pcap` é decodificado e mantido em memória RAM.
3. **Injeção RTP com Cadência de 20ms**: Os pacotes de voz G.711 a-law (PCMA 8kHz) são transmitidos a cada 20ms (50 pacotes/segundo), garantindo áudio fluído sem sobrecarga de CPU.

---

## 🛡️ Segurança & Isolamento de Credenciais (.env)

- **Zero Leaks**: As senhas de ramais são armazenadas no arquivo local `.env` (ignorado pelo Git). O arquivo `config.json` armazena apenas preferências de interface mantendo `"senha": ""` sempre em branco.
- **Sanitização SIP**: Prevenção contra injeção de caracteres de quebra de linha CRLF (`\r`, `\n`) em campos de texto.
- **Mascaramento em Logs**: Senhas são mascaradas automaticamente como `******` em todas as telas de log.

---

## 🧪 Suíte de Testes Automatizados

Para validar todos os módulos, caminhos, segurança, cálculos de Digest MD5 e integridade da GUI:
```powershell
python tests/test_backend.py
```

Saída esperada:
```text
-> Testando core.paths...                  [OK] core.paths validado!
-> Testando core.version...                [OK] core.version validado! (Versão detectada: v2.0.x)
-> Testando ConfigManager e .env...        [OK] ConfigManager e isolamento .env validados com sucesso!
-> Testando StrategyManager...             [OK] StrategyManager validado!
-> Testando ScenarioBuilder...             [OK] ScenarioBuilder validado!
-> Testando SecurityValidator...           [OK] SecurityValidator validado com sucesso!
-> Testando SippLocator e binário Win...   [OK] SippLocator encontrou executável SIPp!
-> Testando SipClient e Digest MD5...      [OK] SipClient, Digest MD5 e Chamada Única validados com sucesso!
-> Testando imports da GUI...              [OK] Módulos da GUI importados com sucesso!

[SUCCESS] TODOS OS TESTES PASSARAM COM SUCESSO!
```

---

## ❓ Perguntas Frequentes & Resolução de Problemas

### 1. "Como baixar ou gerar uma release versionada para distribuir aos clientes?"
- **Download direto**: Acesse [GitHub Releases](https://github.com/ocfcorrea/TestSIPpWindows/releases) e baixe o binário compilado `.exe`.
- **Compilação local**: Execute o arquivo `gerar_executavel.bat`. Ele criará o executável standalone na pasta `dist/` com a tag de versão numérica (ex: `SIPp_Load_Tester_Pro_v2.0.11.exe`). Você pode copiar esse arquivo para qualquer computador com Windows sem instalar nada.

### 2. "Como funciona o loop contínuo de chamadas simultâneas?"
Se você configurar **30 Simultâneas** e **Total = 0**, o aplicativo manterá **30 chamadas ativas conectadas o tempo todo**. Quando uma chamada atingir sua duração (ex: 60s) e desligar, outra chamada será iniciada imediatamente no mesmo instante para repor a vaga, mantendo o PBX permanentemente sob a carga desejada.

### 3. "O aplicativo funciona sem acesso à internet?"
**Sim, 100% offline.** Todas as bibliotecas Python e arquivos de mídia necessários já estão embutidos.
