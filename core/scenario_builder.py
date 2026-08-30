"""
Scenario Builder - Constrói os cenários XML e arquivos CSV para o SIPp.
Substitui variáveis de template e gera arquivos de credenciais compatíveis.
"""

import os
from typing import List, Tuple


class ScenarioBuilder:
    """Responsável por ler templates XML e gerar os cenários executáveis e CSVs."""

    @staticmethod
    def resolve_scenario_path(filename: str) -> str:
        """Resolve o caminho do arquivo procurando na pasta scenarios/ ou raiz."""
        candidates = [
            os.path.join("scenarios", filename),
            filename,
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "scenarios", filename),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return os.path.join("scenarios", filename)

    @staticmethod
    def generate_call_xml(
        template_path: str = "call.xml.template",
        output_path: str = "call.xml",
        duracao_min_ms: int = 10000,
        duracao_max_ms: int = 60000,
        duracao_fixa: bool = False,
        pcap_file: str = "pcap/g711a.pcap"
    ) -> Tuple[bool, str]:
        """
        Lê call.xml.template e substitui @@DURACAO_MIN_MS@@, @@DURACAO_MAX_MS@@ e @@PCAP_FILE@@.
        Se duracao_fixa for True, usa duracao_min_ms em ambos.
        """
        actual_template = ScenarioBuilder.resolve_scenario_path(template_path)
        if not os.path.exists(actual_template):
            return False, f"Arquivo de template '{template_path}' não encontrado em {actual_template}."

        try:
            with open(actual_template, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            min_ms = int(duracao_min_ms)
            max_ms = int(duracao_min_ms) if duracao_fixa else int(duracao_max_ms)

            if min_ms > max_ms:
                min_ms, max_ms = max_ms, min_ms

            pcap_clean = pcap_file.replace("\\", "/").strip() if pcap_file else "pcap/g711a.pcap"

            content = content.replace("@@DURACAO_MIN_MS@@", str(min_ms))
            content = content.replace("@@DURACAO_MAX_MS@@", str(max_ms))
            content = content.replace("@@PCAP_FILE@@", pcap_clean)

            if "@@" in content:
                return False, "Aviso: Ainda existem placeholders '@@' não substituídos no template."

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True, f"Cenário '{output_path}' gerado com sucesso (Duração: {min_ms}ms - {max_ms}ms, PCAP: {pcap_clean})."
        except Exception as e:
            return False, f"Erro ao gerar '{output_path}': {e}"

    @staticmethod
    def generate_single_call_xml(
        template_path: str = "call.xml.template",
        output_path: str = "single_call.xml",
        duracao_ms: int = 10000,
        pcap_file: str = "pcap/g711a.pcap"
    ) -> Tuple[bool, str]:
        """Gera um cenário dedicado para chamada única de teste com duração fixa."""
        return ScenarioBuilder.generate_call_xml(
            template_path=template_path,
            output_path=output_path,
            duracao_min_ms=duracao_ms,
            duracao_max_ms=duracao_ms,
            duracao_fixa=True,
            pcap_file=pcap_file
        )

    @staticmethod
    def generate_credentials_csv(
        pool: List[Tuple[str, str, str]],
        output_path: str = "credenciais.csv",
        mode: str = "SEQUENTIAL"
    ) -> Tuple[bool, str]:
        """
        Grava o arquivo CSV de credenciais lido pelo SIPp via -inf.
        Formato:
        SEQUENTIAL ou RANDOM
        ramal;senha;destino
        """
        try:
            with open(output_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(f"{mode}\n")
                for ramal, senha, destino in pool:
                    f.write(f"{ramal};{senha};{destino}\n")
            return True, f"Arquivo '{output_path}' gerado com {len(pool)} registros."
        except Exception as e:
            return False, f"Erro ao gerar '{output_path}': {e}"
