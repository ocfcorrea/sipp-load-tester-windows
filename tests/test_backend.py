"""
Testes unitários e de integração para os módulos do SIPp Load Tester Pro.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.paths import (
    BASE_DIR,
    CORE_DIR,
    GUI_DIR,
    SIPP_DIR,
    SCENARIOS_DIR,
    PCAP_DIR,
    ENV_EXAMPLE_FILE,
    get_project_path,
    resolve_scenario,
    resolve_pcap,
    get_subprocess_env
)
from core.config_manager import ConfigManager, DEFAULT_CONFIG
from core.strategy_manager import StrategyManager
from core.scenario_builder import ScenarioBuilder
from core.sipp_downloader import SippLocator
from core.security import SecurityValidator


def test_paths():
    print("-> Testando core.paths...")
    assert os.path.exists(BASE_DIR)
    assert os.path.exists(CORE_DIR)
    assert os.path.exists(GUI_DIR)
    assert os.path.exists(SCENARIOS_DIR)
    assert os.path.exists(PCAP_DIR)
    assert os.path.exists(ENV_EXAMPLE_FILE)

    resolved_scen = resolve_scenario("register.xml")
    assert os.path.exists(resolved_scen)
    assert "register.xml" in resolved_scen

    resolved_pcap_file = resolve_pcap("g711a.pcap")
    assert os.path.exists(resolved_pcap_file)
    assert "g711a.pcap" in resolved_pcap_file

    env = get_subprocess_env()
    assert "PATH" in env
    if sys.platform == "win32" and os.path.exists(SIPP_DIR):
        assert SIPP_DIR in env["PATH"]

    print("  [OK] core.paths validado!")


def test_config_manager():
    print("-> Testando ConfigManager e isolamento .env...")
    test_cfg = get_project_path("test_config.json")
    test_env = get_project_path("test.env")
    
    mgr = ConfigManager(test_cfg, test_env)
    assert mgr.get("asterisk_ip") == DEFAULT_CONFIG["asterisk_ip"]
    assert mgr.get("usuario_auth") == DEFAULT_CONFIG["usuario_auth"]
    assert len(mgr.get("destinations")) == 10
    
    mgr.set("simultaneas", 200)
    mgr.set("usuario_auth", "user1002")
    mgr.set("senha", "SegredoUltra123")
    mgr.save_config()
    
    # 1. Verifica se no arquivo JSON a senha ficou vazia (Zero Leak)
    import json
    with open(test_cfg, "r", encoding="utf-8") as f:
        saved_json = json.load(f)
    assert saved_json.get("senha") == ""
    assert saved_json.get("simultaneas") == 200

    # 2. Verifica se no test.env a senha foi salva corretamente
    with open(test_env, "r", encoding="utf-8") as f:
        env_text = f.read()
    assert "SIP_SENHA=SegredoUltra123" in env_text

    # 3. Recarrega o ConfigManager e verifica se a senha é recuperada do .env
    mgr2 = ConfigManager(test_cfg, test_env)
    assert mgr2.get("simultaneas") == 200
    assert mgr2.get("usuario_auth") == "user1002"
    assert mgr2.get("senha") == "SegredoUltra123"
    
    for f_clean in [test_cfg, test_env]:
        if os.path.exists(f_clean):
            os.remove(f_clean)
    print("  [OK] ConfigManager e isolamento .env validados com sucesso!")


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
    
    token = StrategyManager.generate_session_token("AGENT")
    assert token.startswith("AGENT_")
    
    interval = StrategyManager.get_random_human_interval(200, 1500, 20)
    assert interval >= 50
    print("  [OK] StrategyManager validado!")


def test_scenario_builder():
    print("-> Testando ScenarioBuilder...")
    test_call_xml = get_project_path("test_call.xml")
    ok, msg = ScenarioBuilder.generate_call_xml(
        template_path="call.xml.template",
        output_path=test_call_xml,
        duracao_min_ms=15000,
        duracao_max_ms=45000,
        pcap_file="pcap/custom_audio.pcap"
    )
    assert ok is True
    assert os.path.exists(test_call_xml)
    
    with open(test_call_xml, "r", encoding="utf-8") as f:
        content = f.read()
        assert 'min="15000"' in content
        assert 'max="45000"' in content
        assert "@@" not in content
        
    os.remove(test_call_xml)
    
    # Testa CSV
    test_cred_csv = get_project_path("test_cred.csv")
    ok_csv, msg_csv = ScenarioBuilder.generate_credentials_csv(
        [("1002", "pass", "22221864"), ("1002", "pass", "9999")],
        output_path=test_cred_csv
    )
    assert ok_csv is True
    assert os.path.exists(test_cred_csv)
    os.remove(test_cred_csv)
    print("  [OK] ScenarioBuilder validado!")


def test_security_validator():
    print("-> Testando SecurityValidator...")
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
    assert all([ctk, LedIndicator, MetricCard, DestinationTable, TabRegister, TabStrategy, TabConsole, TabAbout, MainWindow])
    print("  [OK] Módulos da GUI importados com sucesso!")


def test_sip_client():
    print("-> Testando SipClient e cálculo nativo de Digest MD5...")
    from core.sip_client import SipClient
    h = SipClient.compute_digest_response(
        username="1002",
        realm="asterisk",
        password="secretpassword",
        method="REGISTER",
        uri="sip:192.168.1.100",
        nonce="4d2f8a",
        qop="auth",
        nc="00000001",
        cnonce="abcd1234"
    )
    assert len(h) == 32
    assert isinstance(h, str)
    
    # Testa parsing de desafio WWW-Authenticate
    sample_hdr = 'Digest realm="asterisk", nonce="5a6b7c", qop="auth", algorithm=MD5'
    params = SipClient.parse_auth_challenge(sample_hdr)
    assert params.get("realm") == "asterisk"
    assert params.get("nonce") == "5a6b7c"
    assert params.get("qop") == "auth"

    # Testa cálculo de Digest para INVITE (Chamada Única)
    h_invite = SipClient.compute_digest_response(
        username="1002",
        realm="asterisk",
        password="secretpassword",
        method="INVITE",
        uri="sip:22221864@192.168.1.100",
        nonce="5a6b7c",
        qop="auth",
        nc="00000001",
        cnonce="abcd1234"
    )
    assert len(h_invite) == 32
    assert isinstance(h_invite, str)
    print("  [OK] SipClient, Digest MD5 e Chamada Única validados com sucesso!")


def test_version():
    print("-> Testando core.version...")
    from core.version import get_version_info, get_version, get_version_tag, get_app_title
    info = get_version_info()
    assert "version" in info
    assert "release_tag" in info
    assert info["major"] == 2
    assert info["minor"] == 0
    assert isinstance(info["build"], int)
    assert get_version() == f"2.0.{info['build']}"
    assert get_version_tag() == f"v2.0.{info['build']}"
    assert "SIPp Load Tester Pro" in get_app_title()
    print(f"  [OK] core.version validado! (Versão detectada: {get_version_tag()})")


if __name__ == "__main__":
    test_paths()
    test_version()
    test_config_manager()
    test_strategy_manager()
    test_scenario_builder()
    test_security_validator()
    test_sipp_locator()
    test_sip_client()
    test_gui_imports()
    print("\n[SUCCESS] TODOS OS TESTES PASSARAM COM SUCESSO!")

