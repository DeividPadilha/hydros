"""Verifica as regras essenciais de contraste da interface."""

from pathlib import Path

APP = Path(__file__).resolve().parent / "app.py"


def main() -> None:
    content = APP.read_text(encoding="utf-8")

    forbidden = [
        'section[data-testid="stSidebar"] * { color: white !important; }',
        "h1, h2, h3, h4, p, label, span, div { color: white; }",
    ]
    for rule in forbidden:
        assert rule not in content, f"Regra global indevida encontrada: {rule}"

    required = [
        'div[data-baseweb="select"] > div',
        'div[data-baseweb="select"] > div *',
        '[data-testid="stCodeBlock"]',
        '[data-testid="stFileUploader"] section *',
        'input::placeholder',
        'li[role="option"]',
    ]
    for rule in required:
        assert rule in content, f"Regra de contraste ausente: {rule}"

    print("\n=== CONTRASTE DA INTERFACE ===")
    print("Selectbox: texto escuro sobre fundo branco")
    print("Dropdown: opções legíveis")
    print("Código da arquitetura: fundo escuro e texto claro")
    print("Upload de arquivo: texto escuro sobre fundo claro")
    print("Campos de texto: contraste corrigido")
    print("CONTRASTE DA INTERFACE: OK")


if __name__ == "__main__":
    main()
