"""
Strategy Manager - Gerenciador de estratégias de discagem e cálculo de pesos dos destinos.
Suporta distribuição ponderada de destinos e simulação randômica de tráfego humano.
"""

import random
import uuid
from typing import List, Dict, Any, Tuple


class StrategyManager:
    """Gerencia a distribuição de destinos ponderados e as regras de discagem."""

    @staticmethod
    def calculate_weights_percentage(destinations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcula a porcentagem que cada destino ativo representa sobre o total de pesos.
        Retorna a lista atualizada com a chave 'percentage'.
        """
        active = [
            d for d in destinations
            if d.get("enabled", False) and str(d.get("number", "")).strip()
        ]
        
        total_weight = sum(int(d.get("weight", 1)) for d in active)
        
        result = []
        for d in destinations:
            item = dict(d)
            if item.get("enabled", False) and str(item.get("number", "")).strip() and total_weight > 0:
                w = int(item.get("weight", 1))
                item["percentage"] = round((w / total_weight) * 100.0, 1)
            else:
                item["percentage"] = 0.0
            result.append(item)
            
        return result

    @staticmethod
    def validate_destinations(destinations: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Verifica se há pelo menos 1 destino ativo e válido."""
        active = [
            d for d in destinations
            if d.get("enabled", False) and str(d.get("number", "")).strip()
        ]
        if not active:
            return False, "É necessário configurar pelo menos 1 destino habilitado com número válido."
        
        for d in active:
            try:
                w = int(d.get("weight", 0))
                if w <= 0:
                    return False, f"O peso para o número {d.get('number')} deve ser maior que 0."
            except ValueError:
                return False, f"Peso inválido para o número {d.get('number')}."
                
        return True, ""

    @staticmethod
    def generate_weighted_destination_pool(
        destinations: List[Dict[str, Any]],
        ramal: str,
        senha: str,
        pool_size: int = 1000,
        token_prefix: str = "L5_"
    ) -> List[Tuple[str, str, str]]:
        """
        Gera uma lista de tuplas (ramal, senha, destino) para o arquivo CSV de credenciais do SIPp,
        respeitando a proporção exata de pesos de cada destino.
        """
        active = [
            d for d in destinations
            if d.get("enabled", False) and str(d.get("number", "")).strip()
        ]
        if not active:
            return [(ramal, senha, "22221864")]

        numbers = [str(d.get("number")).strip() for d in active]
        weights = [max(1, int(d.get("weight", 1))) for d in active]
        
        # Gera uma amostragem ponderada aleatória
        sampled_destinations = random.choices(numbers, weights=weights, k=pool_size)
        
        # Cria tuplas para o SIPp: [field0]=ramal; [field1]=senha; [field2]=destino
        return [(ramal, senha, dest) for dest in sampled_destinations]

    @staticmethod
    def generate_session_token(prefix: str = "AGENT") -> str:
        """Gera um identificador/token único de chamada para rastreamento."""
        uid = uuid.uuid4().hex[:8].upper()
        return f"{prefix}_{uid}"

    @staticmethod
    def get_random_human_interval(min_ms: int, max_ms: int, burst_chance: int) -> int:
        """
        Simula intervalo humano entre discagens com chance de rajada (burst).
        Se cair na chance de burst, reduz o intervalo para simular múltiplas pessoas ligando juntas.
        """
        min_ms = max(50, min_ms)
        max_ms = max(min_ms, max_ms)
        
        is_burst = random.randint(1, 100) <= burst_chance
        if is_burst:
            # Em momento de rajada, disca muito rápido (50ms a 200ms)
            return random.randint(50, min(200, max_ms))
        else:
            return random.randint(min_ms, max_ms)
