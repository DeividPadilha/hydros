"""Valida os escores por ação e o estado operacional do AMDH."""

from src.agents.amdh_agent import AMDHAgent


def evidence(name: str, level: str):
    return {
        name: level,
        "evidencia": level,
        "criticidade": level,
        "confianca": 1.0,
        "completude": 1.0,
        "indice_conflito": 0.0,
    }


def run_case(
    title: str,
    ehc: str,
    earg: str,
    eaps: str,
    active: bool,
    expected: str,
):
    agent = AMDHAgent()
    result = agent.decidir(
        evidence("Earg", earg),
        evidence("Ehc", ehc),
        evidence("Eaps", eaps),
        contexto_atual={
            "irrigacao_ativa": active,
            "irrigacao_aplicada": 10.0 if active else 0.0,
            "origem_estado_irrigacao": "teste_explicito",
        },
    )

    print(f"\n{title}")
    print("Estado:", result["estado_irrigacao"]["state"])
    print("Ações bloqueadas:", result["acoes_bloqueadas"])
    print("Escores válidos:", result["escores_acoes_validos"])
    print("Decisão:", result["D(Ui)"])

    assert result["criterio_selecao"] == "argmax_d S(d)"
    assert result["D(Ui)"] == expected
    assert result["escores_acoes"][expected] is not None
    assert result["estado_irrigacao"]["source"] == "teste_explicito"


def main():
    print("\n=== ESCORES DE AÇÃO DO AMDH ===")

    run_case(
        "1. Irrigação ativa e condição adequada",
        ehc="baixo",
        earg="baixo",
        eaps="baixo",
        active=True,
        expected="finalizar_irrigacao",
    )
    run_case(
        "2. Irrigação ativa e baixa necessidade",
        ehc="moderado",
        earg="moderado",
        eaps="baixo",
        active=True,
        expected="reduzir_irrigacao",
    )
    run_case(
        "3. Irrigação ativa e condição moderada",
        ehc="moderado",
        earg="moderado",
        eaps="moderado",
        active=True,
        expected="manter_irrigacao",
    )
    run_case(
        "4. Irrigação inativa e condição crítica",
        ehc="critico",
        earg="critico",
        eaps="alto",
        active=False,
        expected="iniciar_irrigacao",
    )
    run_case(
        "5. Irrigação ativa e condição crítica",
        ehc="critico",
        earg="critico",
        eaps="alto",
        active=True,
        expected="aumentar_irrigacao",
    )

    print("\nAMDH POR AÇÃO: OK")


if __name__ == "__main__":
    main()
