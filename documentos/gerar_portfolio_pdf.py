"""Gera documentos/portfolio.pdf a partir do README.md do repositório.

O README é convertido em HTML pela API de markdown do GitHub, para que o PDF
reproduza a página do repositório, e o HTML é impresso em A4 pelo WeasyPrint,
com as margens do Trabalho de Graduação. Todos os toggles <details> ficam
abertos, de modo que os diagramas de arquitetura aparecem no PDF.

Requisitos: GitHub CLI (`gh`) autenticado e WeasyPrint (`pip install weasyprint`).

Uso, a partir da raiz do repositório:
    python documentos/gerar_portfolio_pdf.py

Depois de gerar o PDF, recompile o documento ABNT para atualizar o Apêndice A:
    cd documentos && latexmk -pdf -outdir=build portfolio-abnt.tex
"""
import re
import subprocess
from pathlib import Path

import weasyprint

RAIZ = Path(__file__).resolve().parent.parent
README = RAIZ / "README.md"
SAIDA = RAIZ / "documentos" / "portfolio.pdf"

CSS = """
@page {
  size: A4;
  margin: 3cm 2cm 2cm 3cm;
}
html { font-family: "Liberation Sans", "DejaVu Sans", "Noto Color Emoji", sans-serif; font-size: 10pt; line-height: 1.45; color: #1f2328; }
h1 { font-size: 18pt; border-bottom: 1px solid #d1d9e0; padding-bottom: 4pt; }
h2 { font-size: 15pt; border-bottom: 1px solid #d1d9e0; padding-bottom: 3pt; margin-top: 18pt; }
h3 { font-size: 13pt; margin-top: 14pt; }
h4 { font-size: 11pt; margin-top: 12pt; }
h5 { font-size: 10pt; margin-top: 10pt; }
h1, h2, h3, h4, h5 { break-after: avoid; }
p, li { orphans: 3; widows: 3; }
a { color: #0969da; text-decoration: none; }
img { max-width: 100%; }
img[align="left"] { float: left; width: 3.5cm; height: auto; margin: 0 14pt 8pt 0; }
p[align="center"] img { max-height: 5cm; width: auto; }
table { border-collapse: collapse; margin: 8pt 0; font-size: 9pt; width: 100%; break-inside: auto; }
th, td { border: 1px solid #d1d9e0; padding: 3pt 6pt; text-align: left; vertical-align: top; }
tr { break-inside: avoid; }
th { background: #f6f8fa; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.5pt; background: #f6f8fa; padding: 0 2pt; }
details { margin: 10pt 0; }
details > summary { font-weight: bold; font-size: 12pt; list-style: none; border-bottom: 1px solid #d1d9e0; margin-bottom: 6pt; }
details details > summary { font-size: 10pt; border-bottom: none; }
details:not(details details) { break-before: page; }
"""


def readme_em_html() -> str:
    """Converte o README em HTML com a API de markdown do GitHub (modo documento)."""
    resultado = subprocess.run(
        ["gh", "api", "markdown", "-f", "mode=markdown", "-f", f"text={README.read_text(encoding='utf-8')}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return resultado.stdout


def main() -> None:
    corpo = readme_em_html()
    # Os toggles ficam abertos no PDF, para que todo o conteúdo apareça.
    corpo = corpo.replace("<details>", "<details open>")
    # O GitHub insere âncoras vazias nos títulos, que não têm função no PDF.
    corpo = re.sub(r'<a id="user-content-[^"]*" class="anchor"[^>]*>.*?</a>', "", corpo, flags=re.S)

    documento = (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        "<title>Portfólio - Pedro Felipe Sousa Garcia</title>"
        f"<style>{CSS}</style></head><body>{corpo}</body></html>"
    )
    weasyprint.HTML(string=documento, base_url=f"{RAIZ}/").write_pdf(SAIDA)
    print(f"PDF gerado em {SAIDA}")


if __name__ == "__main__":
    main()
