"""Valida governança do APS fora do domínio no AMDH."""

from src.agents.amdh_agent import AMDHAgent
from src.core.irrigation_state import IrrigationState


def evidencia(nome: str, valor: str, confianca: float = 1.0) -> dict:
    return {
        nome: valor,
        "confianca": confianca,
        "completude": 1.0,
        "indice_conflito": 0.0,
    }


def main() -> None:
    amdh = AMDHAgent()
    estado_inativo = IrrigationState(
        active=False,
        state="inativa",
        source="teste_explicito",
        confidence=1.0,
        applied_mm=0.0,
        explicit=True,
    )

    # Caso 1: o APS está fora do domínio, mas sua retirada não altera a ação.
    resultado_estavel = amdh.decidir(
        evidencia("Earg", "critico"),
        evidencia("Ehc", "critico"),
        {
            **evidencia("Eaps", "baixo", confianca=0.05),
            "status_dominio": "fora_dominio",
            "fora_dominio": True,
            "avisos": ["categoria desconhecida"],
        },
        contexto_atual={"irrigacao_ativa": False},
        estado_irrigacao=estado_inativo,
    )

    dependencia_estavel = resultado_estavel["dependencia_aps"]
    assert resultado_estavel["decisao_final"] == "iniciar_irrigacao"
    assert dependencia_estavel["decisao_sem_aps"] == "iniciar_irrigacao"
    assert dependencia_estavel["influencia_material"] is False
    assert "aps_fora_ou_parcialmente_fora_do_dominio" in resultado_estavel[
        "avisos_governanca"
    ]
    assert "decisao_dependente_de_aps_fora_do_dominio" not in resultado_estavel[
        "motivos_revisao_humana"
    ]

    # Caso 2: o APS fora do domínio altera a decisão no teste contrafactual.
    resultado_dependente = amdh.decidir(
        evidencia("Earg", "moderado"),
        evidencia("Ehc", "alto"),
        {
            **evidencia("Eaps", "alto", confianca=0.8),
            "status_dominio": "fora_dominio",
            "fora_dominio": True,
            "avisos": ["categoria desconhecida"],
        },
        contexto_atual={"irrigacao_ativa": False},
        estado_irrigacao=estado_inativo,
    )

    dependencia_material = resultado_dependente["dependencia_aps"]
    assert dependencia_material["influencia_material"] is True
    assert resultado_dependente["revisao_humana_requerida"] is True
    assert "decisao_dependente_de_aps_fora_do_dominio" in resultado_dependente[
        "motivos_revisao_humana"
    ]

    # Caso 3: recomendação conservadora com APS fora do domínio gera aviso,
    # mas não revisão especial apenas por baixa confiança global.
    resultado_conservador = amdh.decidir(
        evidencia("Earg", "moderado", confianca=0.55),
        evidencia("Ehc", "moderado", confianca=0.55),
        {
            **evidencia("Eaps", "moderado", confianca=0.2),
            "status_dominio": "fora_dominio",
            "fora_dominio": True,
            "avisos": ["categoria desconhecida"],
        },
        contexto_atual={"irrigacao_ativa": False},
        estado_irrigacao=estado_inativo,
    )

    assert resultado_conservador["decisao_final"] == "manter_irrigacao"
    assert resultado_conservador["revisao_humana_requerida"] is False
    assert "aps_fora_ou_parcialmente_fora_do_dominio" in resultado_conservador[
        "avisos_governanca"
    ]

    print("\n=== GOVERNANÇA DO APS ===")
    print("Caso estável:")
    print("  Decisão com APS:", dependencia_estavel["decisao_com_aps"])
    print("  Decisão sem APS:", dependencia_estavel["decisao_sem_aps"])
    print("  Influência material:", dependencia_estavel["influencia_material"])
    print("  Revisão especial:", resultado_estavel["revisao_humana_requerida"])
    print("Caso dependente:")
    print("  Decisão com APS:", dependencia_material["decisao_com_aps"])
    print("  Decisão sem APS:", dependencia_material["decisao_sem_aps"])
    print("  Influência material:", dependencia_material["influencia_material"])
    print("  Revisão especial:", resultado_dependente["revisao_humana_requerida"])
    print("Caso conservador:")
    print("  Decisão:", resultado_conservador["decisao_final"])
    print("  Avisos:", resultado_conservador["avisos_governanca"])
    print("  Revisão especial:", resultado_conservador["revisao_humana_requerida"])
    print("GOVERNANÇA DO APS: OK")


if __name__ == "__main__":
    main()
