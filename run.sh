#!/usr/bin/env bash
# ============================================================
#  run.sh - Teste de 100 chamadas simultâneas com SIPp
#  Alvo: Asterisk | Áudio real via RTP (PCAP G.711 a-law)
#  L5 Networks
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# ------------------------------------------------------------
# 1) CARREGAMENTO AUTOMÁTICO DO ARQUIVO .env (SE EXISTIR)
# ------------------------------------------------------------
if [[ -f ".env" ]]; then
  echo ">> Carregando configurações do arquivo .env..."
  # Exporta variáveis do .env ignorando comentários e linhas vazias
  set -a
  # shellcheck disable=SC1091
  source <(grep -E -v '^#|^$' .env)
  set +a
elif [[ -f ".env.example" && ! -f ".env" ]]; then
  echo ">> Arquivo .env não encontrado. Copiando de .env.example..."
  cp .env.example .env
fi

# ------------------------------------------------------------
# 2) CONFIGURAÇÃO DOS PARÂMETROS SIP (com fallback seguro)
# ------------------------------------------------------------
ASTERISK_IP="${SIP_ASTERISK_IP:-192.168.1.100}"    # IP ou FQDN do seu Asterisk (alvo de REDE)
ASTERISK_PORT="${SIP_ASTERISK_PORT:-5060}"        # Porta SIP (5060 UDP típico)
TRANSPORT="${SIP_TRANSPORT:-u1}"                  # u1=UDP  t1=TCP  (passado como: -t u1)

SIP_DOMAIN="${SIP_DOMAIN:-$ASTERISK_IP}"          # Domínio SIP da IDENTIDADE (From/To/Request-URI)
RAMAL="${SIP_RAMAL:-1002}"                        # Ramal (usuário SIP) registrado
AUTH_USER="${SIP_USUARIO_AUTH:-$RAMAL}"           # Usuário de autenticação Digest
SENHA="${SIP_SENHA:-sua_senha_aqui}"              # Senha do ramal (definida no .env)
DESTINO="${SIP_DESTINO:-22221864}"                # Número/ramal de destino chamado

LOCAL_IP="${SIP_LOCAL_IP:-}"                      # Interface local (vazio = autodetectar)

# ------------------------------------------------------------
# 3) PARÂMETROS DO TESTE DE CARGA
# ------------------------------------------------------------
SIMULTANEAS=100                 # Teto de chamadas ativas ao mesmo tempo (-l)
TOTAL=0                         # Total de chamadas a criar (-m) [0 = ilimitado]
RATE=50                         # Novas chamadas por RATE_PERIOD (-r)
RATE_PERIOD=1000                # Período da taxa em ms (-rp)

DURACAO_MIN_MS=10000            # Piso do range de duração (10s)
DURACAO_MAX_MS=60000            # Teto do range de duração (60s)
PCAP_MS=7000                    # Duração do pcap/g711a.pcap em ms (informativo)

# ------------------------------------------------------------
# 4) LOCALIZAÇÃO DO BINÁRIO SIPP E ARQUIVOS PCAP
# ------------------------------------------------------------
SIPP_BIN=""
if [[ -f "bin/sipp/sipp.exe" ]]; then
  SIPP_BIN="bin/sipp/sipp.exe"
elif command -v sipp >/dev/null 2>&1; then
  SIPP_BIN="$(command -v sipp)"
elif [[ -f "/usr/bin/sipp" ]]; then
  SIPP_BIN="/usr/bin/sipp"
elif [[ -f "/usr/local/bin/sipp" ]]; then
  SIPP_BIN="/usr/local/bin/sipp"
fi

if [[ -z "${SIPP_BIN}" ]]; then
  echo "ERRO: sipp não encontrado no PATH ou em bin/sipp/sipp.exe. Instale o SIPp." >&2
  exit 1
fi

# Garante a existência do arquivo PCAP
if [[ ! -f "pcap/g711a.pcap" ]]; then
  for d in /usr/share/sip-tester /usr/share/sipp/pcap /usr/share/doc/sipp/pcap ./pcap; do
    if [[ -f "$d/g711a.pcap" ]]; then
      mkdir -p pcap && cp -f "$d/g711a.pcap" pcap/ && echo "PCAP copiado de $d"
      break
    fi
  done
fi

if [[ ! -f "pcap/g711a.pcap" ]]; then
  echo "AVISO: pcap/g711a.pcap não encontrado. O playback de áudio RTP pode falhar." >&2
fi

LOCAL_ARG=()
if [[ -n "${LOCAL_IP}" ]]; then
  LOCAL_ARG=(-i "${LOCAL_IP}")
fi

TARGET="${ASTERISK_IP}:${ASTERISK_PORT}"

TOTAL_ARG=()
if [[ "${TOTAL}" -gt 0 ]]; then
  TOTAL_ARG=(-m "${TOTAL}")
fi

if [[ ${DURACAO_MIN_MS} -gt ${DURACAO_MAX_MS} ]]; then
  echo "ERRO: DURACAO_MIN_MS (${DURACAO_MIN_MS}) > DURACAO_MAX_MS (${DURACAO_MAX_MS})." >&2
  exit 1
fi

# Gera call.xml a partir do template
TEMPLATE="scenarios/call.xml.template"
if [[ ! -f "${TEMPLATE}" ]]; then
  TEMPLATE="call.xml.template"
fi

if [[ ! -f "${TEMPLATE}" ]]; then
  echo "ERRO: call.xml.template não encontrado em scenarios/ ou raiz." >&2
  exit 1
fi

CALL_XML="scenarios/call.xml"
sed -e "s/@@DURACAO_MIN_MS@@/${DURACAO_MIN_MS}/g" \
    -e "s/@@DURACAO_MAX_MS@@/${DURACAO_MAX_MS}/g" \
    -e "s/@@PCAP_FILE@@/pcap\/g711a.pcap/g" \
    "${TEMPLATE}" > "${CALL_XML}"

if grep -q '@@' "${CALL_XML}"; then
  echo "ERRO: placeholder não substituído em ${CALL_XML}:" >&2
  grep -n '@@' "${CALL_XML}" >&2
  exit 1
fi

# CSV de credenciais/destino (field0=AUTH_USER, field1=SENHA, field2=DESTINO)
CSV="credenciais.csv"
cat > "${CSV}" <<EOF
SEQUENTIAL
${AUTH_USER};${SENHA};${DESTINO}
EOF

# Função de limpeza segura ao sair
cleanup() {
  if [[ -f "${CSV}" ]]; then
    rm -f "${CSV}"
  fi
}
trap cleanup EXIT

echo "=============================================="
echo " Alvo Asterisk : ${TARGET} (${TRANSPORT})"
echo " Domínio SIP   : ${SIP_DOMAIN}"
echo " Ramal         : ${RAMAL} (Auth: ${AUTH_USER}) -> Destino: ${DESTINO}"
if [[ "${TOTAL}" -gt 0 ]]; then
  MODO_TXT="Total: ${TOTAL}"
else
  MODO_TXT="Total: ILIMITADO (pare com 'q')"
fi
echo " Simultâneas   : ${SIMULTANEAS} | ${MODO_TXT} | Taxa: ${RATE}/${RATE_PERIOD}ms"
echo " Duração       : ${DURACAO_MIN_MS}-${DURACAO_MAX_MS}ms (áudio PCAP nos primeiros $((PCAP_MS / 1000))s)"
echo "=============================================="

# ------------------------------------------------------------
# 5) REGISTRA O RAMAL (Digest 401/407)
# ------------------------------------------------------------
echo ">> Registrando o ramal ${RAMAL}..."
REG_XML="scenarios/register.xml"
if [[ ! -f "${REG_XML}" ]]; then
  REG_XML="register.xml"
fi

"${SIPP_BIN}" "${TARGET}" \
  -sf "${REG_XML}" \
  -inf "${CSV}" \
  -t "${TRANSPORT}" \
  -set domain "${SIP_DOMAIN}" \
  -set user "${RAMAL}" \
  -m 1 \
  -r 1 \
  -trace_err \
  ${LOCAL_ARG[@]+"${LOCAL_ARG[@]}"} \
  || { echo "ERRO no registro. Verifique IP/ramal/senha no .env." >&2; exit 1; }

echo ">> Ramal registrado com sucesso. Aguardando 1s..."
sleep 1

# ------------------------------------------------------------
# 6) DISPARA AS CHAMADAS DE CARGA
# ------------------------------------------------------------
if [[ "${TOTAL}" -gt 0 ]]; then
  echo ">> Disparando ${TOTAL} chamadas (até ${SIMULTANEAS} simultâneas)..."
else
  echo ">> Regime constante: mantendo ${SIMULTANEAS} chamadas ativas."
  echo "   Pare com 'q' (saída suave) ou Ctrl+C."
fi

"${SIPP_BIN}" "${TARGET}" \
  -sf "${CALL_XML}" \
  -inf "${CSV}" \
  -t "${TRANSPORT}" \
  -set domain "${SIP_DOMAIN}" \
  -set user "${RAMAL}" \
  -set dest "${DESTINO}" \
  ${LOCAL_ARG[@]+"${LOCAL_ARG[@]}"} \
  -l "${SIMULTANEAS}" \
  ${TOTAL_ARG[@]+"${TOTAL_ARG[@]}"} \
  -r "${RATE}" -rp "${RATE_PERIOD}" \
  -trace_err \
  -trace_stat -stf stats.csv \
  -fd 1s \
  || RC=$?

RC=${RC:-0}
if [[ ${RC} -ne 0 ]]; then
  echo ">> SIPp encerrou com código ${RC} (falhas ou interrupção)."
fi

echo ">> Teste concluído. Estatísticas em stats.csv (e *_errors.log se houver falhas)."
