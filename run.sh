#!/usr/bin/env bash
# ============================================================
#  run.sh - Teste de 100 chamadas simultaneas com SIPp
#  Alvo: Asterisk | Audio real via RTP (PCAP G.711 a-law)
#  L5 Networks
# ============================================================
set -euo pipefail

# ------------------------------------------------------------
# 1) AJUSTE ESTAS VARIAVEIS
# ------------------------------------------------------------
ASTERISK_IP="192.168.68.205"      # IP ou FQDN do seu Asterisk (alvo de REDE)
ASTERISK_PORT="5060"            # Porta SIP (5060 UDP tipico)
TRANSPORT="u1"                  # u1=UDP  t1=TCP  (passado como: -t u1)

SIP_DOMAIN="192.168.68.205"
                                # Dominio SIP da IDENTIDADE (From/To/Request-URI).
                                # Separado do alvo de rede acima de proposito:
                                # o SIPp resolve ASTERISK_IP para um IP, e usar
                                # [remote_ip] nos headers quebra o match de
                                # dominio no registrar. Injetado nos cenarios
                                # como [$domain] via -set (NAO -key: -key
                                # alimenta [keyword], -set alimenta [$var]).

RAMAL="108\$1002"               # Ramal (usuario SIP) registrado
SENHA="<*L5-Callbox*>"          # Senha do ramal
DESTINO="22221864"              # Numero/ramal de destino que sera chamado
                                # (ex.: uma URA, um Echo() no dialplan, etc.)

LOCAL_IP=""                     # Deixe vazio p/ autodetectar, ou fixe o IP
                                # da placa que fala com o Asterisk.

# ------------------------------------------------------------
# 2) PARAMETROS DO TESTE
# ------------------------------------------------------------
SIMULTANEAS=100                 # Teto de chamadas ativas ao mesmo tempo (-l).
                                # O SIPp MANTEM esse patamar: assim que uma
                                # chamada termina, cria outra para repor.

TOTAL=0                         # Total de chamadas a criar (-m).
                                # 0 = ILIMITADO: roda em regime constante ate
                                # voce parar (tecla 'q' ou Ctrl+C).
                                # Qualquer valor > 0 encerra o teste ao
                                # atingir esse total.

RATE=50                         # Novas chamadas por RATE_PERIOD (-r).
RATE_PERIOD=1000                # Periodo da taxa em ms (-rp).
                                # A taxa limita a VELOCIDADE DE REPOSICAO das
                                # vagas. Se muitas chamadas terminarem juntas,
                                # um RATE baixo demora para recompor o teto -
                                # mantenha-o folgado (>= SIMULTANEAS/2 por
                                # segundo) para o patamar ficar estavel.

# Duracao da chamada APOS atendida: sorteada por chamada (distribuicao
# uniforme) dentro do range abaixo. Para duracao FIXA, use o mesmo valor
# nos dois campos.
DURACAO_MIN_MS=10000            # piso do range (10s)
DURACAO_MAX_MS=60000            # teto do range (60s)

PCAP_MS=7000                    # Duracao do pcap/g711a.pcap em ms (informativo).
                                # O audio toca UMA vez no inicio da chamada;
                                # o resto do tempo o canal fica aberto sem RTP.
                                # Nao afeta a duracao da chamada.

# ------------------------------------------------------------
# 3) DESCOBRE O BINARIO E OS ARGS COMUNS
# ------------------------------------------------------------
SIPP_BIN="$(command -v sipp || true)"
if [[ -z "${SIPP_BIN}" ]]; then
  echo "ERRO: sipp nao encontrado no PATH. Instale o SIPp (com pcapplay)." >&2
  exit 1
fi

# Descobre onde estao os PCAPs do SIPp caso o relativo "pcap/" nao exista.
if [[ ! -f "pcap/g711a.pcap" ]]; then
  for d in /usr/share/sip-tester /usr/share/sipp/pcap /usr/share/doc/sipp/pcap ./pcap; do
    if [[ -f "$d/g711a.pcap" ]]; then
      mkdir -p pcap && cp -f "$d/g711a.pcap" pcap/ && echo "PCAP copiado de $d"
      break
    fi
  done
fi
if [[ ! -f "pcap/g711a.pcap" ]]; then
  echo "AVISO: pcap/g711a.pcap nao encontrado. O playback de audio vai falhar." >&2
  echo "       Copie o g711a.pcap da instalacao do SIPp para ./pcap/" >&2
fi

# Expandido adiante como ${LOCAL_ARG[@]+"${LOCAL_ARG[@]}"}: em bash <= 4.3,
# "${array[@]}" vazio sob 'set -u' aborta com "unbound variable".
LOCAL_ARG=()
if [[ -n "${LOCAL_IP}" ]]; then
  LOCAL_ARG=(-i "${LOCAL_IP}")
fi

TARGET="${ASTERISK_IP}:${ASTERISK_PORT}"

# TOTAL=0 -> omite o -m, e o SIPp roda indefinidamente mantendo o patamar
# de SIMULTANEAS. Sem -m nao existe condicao de parada: encerre com 'q'.
TOTAL_ARG=()
if [[ "${TOTAL}" -gt 0 ]]; then
  TOTAL_ARG=(-m "${TOTAL}")
fi

if [[ ${DURACAO_MIN_MS} -gt ${DURACAO_MAX_MS} ]]; then
  echo "ERRO: DURACAO_MIN_MS (${DURACAO_MIN_MS}) > DURACAO_MAX_MS (${DURACAO_MAX_MS})." >&2
  exit 1
fi

# Gera call.xml a partir do template. <pause milliseconds> e <test value> sao
# lidos no parse do cenario, antes das variaveis [$...] existirem - por isso
# precisam ser literais, substituidos aqui.
TEMPLATE="scenarios/call.xml.template"
if [[ ! -f "${TEMPLATE}" ]]; then
  TEMPLATE="call.xml.template"
fi

if [[ ! -f "${TEMPLATE}" ]]; then
  echo "ERRO: call.xml.template nao encontrado em scenarios/ ou raiz." >&2
  exit 1
fi

CALL_XML="scenarios/call.xml"
sed -e "s/@@DURACAO_MIN_MS@@/${DURACAO_MIN_MS}/g" \
    -e "s/@@DURACAO_MAX_MS@@/${DURACAO_MAX_MS}/g" \
    -e "s/@@PCAP_FILE@@/pcap\/g711a.pcap/g" \
    "${TEMPLATE}" > "${CALL_XML}"

# Guard: se sobrou algum placeholder, o cenario esta inconsistente com o script.
if grep -q '@@' "${CALL_XML}"; then
  echo "ERRO: placeholder nao substituido em ${CALL_XML}:" >&2
  grep -n '@@' "${CALL_XML}" >&2
  exit 1
fi

# CSV de credenciais/destino injetado via [field0]=ramal [field1]=senha [field2]=destino
CSV="credenciais.csv"
cat > "${CSV}" <<EOF
SEQUENTIAL
${RAMAL};${SENHA};${DESTINO}
EOF

echo "=============================================="
echo " Alvo Asterisk : ${TARGET} (${TRANSPORT})"
echo " Dominio SIP   : ${SIP_DOMAIN}"
echo " Ramal         : ${RAMAL}  ->  Destino: ${DESTINO}"
if [[ "${TOTAL}" -gt 0 ]]; then
  MODO_TXT="Total: ${TOTAL}"
else
  MODO_TXT="Total: ILIMITADO (pare com 'q')"
fi
echo " Simultaneas   : ${SIMULTANEAS} | ${MODO_TXT} | Taxa: ${RATE}/${RATE_PERIOD}ms"
echo " Duracao/chamada: aleatoria ${DURACAO_MIN_MS}-${DURACAO_MAX_MS}ms (audio nos primeiros $((PCAP_MS / 1000))s)"
echo "=============================================="

# ------------------------------------------------------------
# 4) REGISTRA O RAMAL (uma vez)
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
  -au "${RAMAL}" \
  -ap "${SENHA}" \
  -m 1 \
  -r 1 \
  -trace_err \
  ${LOCAL_ARG[@]+"${LOCAL_ARG[@]}"} \
  || { echo "ERRO no registro. Verifique IP/ramal/senha." >&2; exit 1; }

echo ">> Ramal registrado. Aguardando 1s..."
sleep 1

# ------------------------------------------------------------
# 5) DISPARA AS CHAMADAS COM AUDIO
# ------------------------------------------------------------
if [[ "${TOTAL}" -gt 0 ]]; then
  echo ">> Disparando ${TOTAL} chamadas (ate ${SIMULTANEAS} simultaneas)..."
else
  echo ">> Regime constante: mantendo ${SIMULTANEAS} chamadas ativas."
  echo "   Pare com 'q' (saida suave, aguarda chamadas terminarem) ou Ctrl+C."
fi
"${SIPP_BIN}" "${TARGET}" \
  -sf "${CALL_XML}" \
  -inf "${CSV}" \
  -t "${TRANSPORT}" \
  -set domain "${SIP_DOMAIN}" \
  -set user "${RAMAL}" \
  -set dest "${DESTINO}" \
  -au "${RAMAL}" -ap "${SENHA}" \
  ${LOCAL_ARG[@]+"${LOCAL_ARG[@]}"} \
  -l "${SIMULTANEAS}" \
  ${TOTAL_ARG[@]+"${TOTAL_ARG[@]}"} \
  -r "${RATE}" -rp "${RATE_PERIOD}" \
  -trace_err \
  -trace_stat -stf stats.csv \
  -fd 1s \
  || RC=$?

# O SIPp sai com codigo != 0 quando houve chamadas falhadas ou quando foi
# interrompido - ambos esperados aqui. Sem este guard, 'set -e' abortaria o
# script antes da mensagem final.
RC=${RC:-0}
if [[ ${RC} -ne 0 ]]; then
  echo ">> SIPp encerrou com codigo ${RC} (falhas ou interrupcao)."
fi

echo ">> Teste concluido. Estatisticas em stats.csv (e *_errors.log se houver falhas)."
