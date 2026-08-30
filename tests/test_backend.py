"""
Testes unitários e de integração para os módulos do SIPp Load Tester Pro.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_manager import ConfigManager, DEFAULT_CONFIG
from core.strategy_manager import StrategyManager
from core.scenario_builder import ScenarioBuilder
from core.sipp_downloader import SippLocator
from core.sipp_engine import SippEngine


def test_config_manager():
    print("-> Testando ConfigManager...")
    mgr = ConfigManager("test_config.json")
    assert mgr.get("asterisk_ip") == DEFAULT_CONFIG["asterisk_ip"]
    assert mgr.get("usuario_auth") == DEFAULT_CONFIG["usuario_auth"]
    assert len(mgr.get("destinations")) == 10
    
    mgr.set("simultaneas", 200)
    mgr.set("usuario_auth", "user1002")
    mgr.save_config()
    
    mgr2 = ConfigManager("test_config.json")
    assert mgr2.get("simultaneas") == 200
    assert mgr2.get("usuario_auth") == "user1002"
    
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    print("  [OK] ConfigManager validado!")


def test_strategy_manager():
    print("-> Testando StrategyManager...")
    dests = [
        {"enabled": True, "number": "1001", "description": "URA", "weight": 50},
        {"enabled": True, "number": "1002", "description": "Echo", "weight": 50},
        {"enabled": False, "number": "1003", "description": "Desabilitado", "weight": 100},
    ]
    
    valid, msg = StrategyManager.validate_destinations(dests)
    assert valid is True
    
    calculated = StrategyManager.calculate_weights_percentage(dests)
    assert calculated[0]["percentage"] == 50.0
    assert calculated[1]["percentage"] == 50.0
    assert calculated[2]["percentage"] == 0.0
    
    pool = StrategyManager.generate_weighted_destination_pool(dests, ramal="1002", senha="pass", pool_size=100)
    assert len(pool) == 100
    assert pool[0][0] == "1002"
    assert pool[0][1] == "pass"
    assert pool[0][2] in ["1001", "1002"]
    
    token = StrategyManager.generate_session_token("L5")
    assert token.startswith("L5_")
    
    interval = StrategyManager.get_random_human_interval(200, 1500, 20)
    assert interval >= 50
    print("  [OK] StrategyManager validado!")


def test_scenario_builder():
    print("-> Testando ScenarioBuilder...")
    ok, msg = ScenarioBuilder.generate_call_xml(
        template_path="call.xml.template",
        output_path="test_call.xml",
        duracao_min_ms=15000,
        duracao_max_ms=45000,
        pcap_file="pcap/custom_audio.pcap"
    )
    assert ok is True
    assert os.path.exists("test_call.xml")
    
    with open("test_call.xml", "r", encoding="utf-8") as f:
        content = f.read()
        assert 'min="15000"' in content
        assert 'max="45000"' in content
        assert 'play_pcap_audio="pcap/custom_audio.pcap"' in content
        assert "@@" not in content
        
    os.remove("test_call.xml")
    
    # Testa CSV
    ok_csv, msg_csv = ScenarioBuilder.generate_credentials_csv(
        [("1002", "pass", "22221864"), ("1002", "pass", "9999")],
        output_path="test_cred.csv"
    )
    assert ok_csv is True
    assert os.path.exists("test_cred.csv")
    os.remove("test_cred.csv")
    print("  [OK] ScenarioBuilder validado!")


def test_security_validator():
    print("-> Testando SecurityValidator...")
    from core.security import SecurityValidator
    
    # Host
    ok, _ = SecurityValidator.validate_host("192.168.1.100")
    assert ok is True
    ok, _ = SecurityValidator.validate_host("pbx.empresa.com.br")
    assert ok is True
    ok, _ = SecurityValidator.validate_host("192.168.1.1; rm -rf /")
    assert ok is False
    ok, _ = SecurityValidator.validate_host("192.168.1.1\r\nInjected-Header: 1")
    assert ok is False

    # Port
    ok, p = SecurityValidator.validate_port(5060)
    assert ok is True and p == 5060
    ok, _ = SecurityValidator.validate_port(99999)
    assert ok is False

    # User
    ok, u = SecurityValidator.validate_sip_user("108$1002")
    assert ok is True and u == "108$1002"
    ok, _ = SecurityValidator.validate_sip_user("1002\r\nVia: hacker")
    assert ok is False

    # Password Masking
    masked = SecurityValidator.mask_credentials("sipp 192.168.1.1 -ap MinhaSenhaSecreta123", "MinhaSenhaSecreta123")
    assert "MinhaSenhaSecreta123" not in masked
    assert "******" in masked

    print("  [OK] SecurityValidator validado com sucesso!")


def test_sipp_locator():
    print("-> Testando SippLocator e binário Windows...")
    sipp_path = SippLocator.find_sipp()
    assert sipp_path is not None
    assert "sipp.exe" in sipp_path.lower()
    
    ok, ver_msg = SippLocator.check_sipp_version(sipp_path)
    assert ok is True
    print(f"  [OK] SippLocator encontrou: {sipp_path} ({ver_msg})")


def test_gui_imports():
    print("-> Testando imports da GUI...")
    import customtkinter as ctk
    from gui.components.led_indicator import LedIndicator
    from gui.components.metric_card import MetricCard
    from gui.components.destination_table import DestinationTable
    from gui.tab_register import TabRegister
    from gui.tab_strategy import TabStrategy
    from gui.tab_console import TabConsole
    from gui.tab_about import TabAbout
    from gui.main_window import MainWindow
    print("  [OK] Módulos da GUI importados com sucesso!")


if __name__ == "__main__":
    test_config_manager()
    test_strategy_manager()
    test_scenario_builder()
    test_security_validator()
    test_sipp_locator()
    test_gui_imports()
    print("\n[SUCCESS] TODOS OS TESTES PASSARAM COM SUCESSO!")
