#!/bin/bash
# =============================================================
# fix_templates.sh
# Valida e corrige quebras de linha em arquivos .html
# dentro do diretório templates/.
#
# Uso:
#   ./scripts/fix_templates.sh          # Apenas valida (dry-run)
#   ./scripts/fix_templates.sh --fix    # Corrige os arquivos
# =============================================================

set -euo pipefail

TEMPLATES_DIR="$(cd "$(dirname "$0")/.." && pwd)/templates"
FIX_MODE=false
HAS_ISSUES=false

if [[ "${1:-}" == "--fix" ]]; then
    FIX_MODE=true
fi

echo "======================================"
echo " HelpDesk — Template Line Validator"
echo "======================================"
echo ""
echo "Diretório: $TEMPLATES_DIR"
echo "Modo: $(if $FIX_MODE; then echo 'CORRIGIR'; else echo 'VALIDAR (dry-run)'; fi)"
echo ""

find "$TEMPLATES_DIR" -name "*.html" -type f | sort | while read -r file; do
    rel_path="${file#$TEMPLATES_DIR/}"
    line_count=$(wc -l < "$file" | tr -d ' ')

    if [[ "$line_count" -gt 1 ]]; then
        HAS_ISSUES=true
        echo "❌  $rel_path ($line_count linhas)"

        if $FIX_MODE; then
            # Remove todas as quebras de linha, compactando espaços extras
            # Preserva espaços dentro de tags Django {% %}
            content=$(tr '\n' ' ' < "$file" | sed 's/  */ /g' | sed 's/> </></g')
            # Restaura espaços ao redor de == dentro de {% if ... %}
            content=$(echo "$content" | sed 's/{%\([^%]*\)==\([^%]*\)%}/{%\1 == \2%}/g')
            content=$(echo "$content" | sed 's/{%\([^%]*\)==\([^%]*\)%}/{%\1 == \2%}/g')
            echo "$content" > "$file"
            new_count=$(wc -l < "$file" | tr -d ' ')
            echo "   ✅  Corrigido → $new_count linha"
        fi
    else
        echo "✅  $rel_path (1 linha)"
    fi
done

echo ""
if ! $FIX_MODE; then
    echo "Para corrigir automaticamente, execute:"
    echo "  ./scripts/fix_templates.sh --fix"
fi
echo "Concluído."
