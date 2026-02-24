import os
import re
import sys
import argparse
from pathlib import Path

def fix_content(content):
    """
    Procura por tags {{ }}, {% %} e {# #} que se espalham por várias linhas
    e remove as quebras de linha contidas nelas.
    """
    def format_match(match):
        # Pega a tag inteira (que pode estar quebrada em várias linhas)
        text = match.group(0)
        # Substitui quebras de linha e retornos de carro por um espaço simples
        text = text.replace('\n', ' ').replace('\r', '')
        # Removemos espaços em branco excessivos criados pela formatação dentro da tag
        text = re.sub(r'\s+', ' ', text)
        return text

    # re.DOTALL permite que o '.' também coincida com quebras de linha ('\n')
    new_content = re.sub(r'\{\{.*?\}\}', format_match, content, flags=re.DOTALL)
    new_content = re.sub(r'\{%.*?%\}', format_match, new_content, flags=re.DOTALL)
    new_content = re.sub(r'\{#.*?#\}', format_match, new_content, flags=re.DOTALL)
    
    return new_content

def validate_templates(templates_dir, auto_fix=False):
    """
    Percorre a pasta de templates e verifica (ou corrige) se há tags do Django mal formatadas
    ou que não fecham na mesma linha.
    """
    templates_path = Path(templates_dir)
    if not templates_path.exists() or not templates_path.is_dir():
        print(f"Erro: O diretório '{templates_dir}' não foi encontrado.")
        sys.exit(1)

    # Expressões regulares para encontrar tags perfeitamente formadas NA MESMA LINHA
    regex_variavel_ok = re.compile(r'\{\{.*?\}\}')
    regex_bloco_ok = re.compile(r'\{%.*?%\}')
    regex_comentario_ok = re.compile(r'\{#.*?#\}')

    # Expressão regular para detectar qualquer abertura ou fechamento órfão ou quebrado na CHECAGEM linha a linha
    regex_quebrada = re.compile(r'(\{\{|\}\}|\{%|%\}|\{#|#\})')

    erros_encontrados = False
    arquivos_verificados = 0
    arquivos_corrigidos = 0

    print(f"Iniciando {'CORREÇÃO' if auto_fix else 'VALIDAÇÃO'} de templates no diretório: {templates_path.resolve()}")

    for ext in ['*.html', '*.txt', '*.email']:
        for filepath in templates_path.rglob(ext):
            arquivos_verificados += 1
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Se auto_fix estiver ativado, aplicamos a correção no conteúdo completo
                if auto_fix:
                    novo_conteudo = fix_content(content)
                    if novo_conteudo != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(novo_conteudo)
                        print(f"✅ Arquivo corrigido: {filepath}")
                        arquivos_corrigidos += 1
                    continue # Pula para a checagem do próximo arquivo

                # Modo de validação (linha por linha, estrito)
                lines = content.splitlines()
                for line_number, line in enumerate(lines, start=1):
                    clean_line = line
                    # Remove as tags que estão perfeitamente contidas na mesma linha
                    clean_line = regex_variavel_ok.sub('', clean_line)
                    clean_line = regex_bloco_ok.sub('', clean_line)
                    clean_line = regex_comentario_ok.sub('', clean_line)

                    # Se restou algo como {{, }}, {% etc., é porque existe sintaxe irregular 
                    # (quebrada em várias linhas ou mal fechada)
                    if regex_quebrada.search(clean_line):
                        erros_encontrados = True
                        print(f"❌ Erro encontrado no arquivo: {filepath}")
                        print(f"   Linha {line_number}: Tag de template mal formatada ou quebrada.")
                        print(f"   Conteúdo: {line.strip()}")
                        print("-" * 60)
            except Exception as e:
                print(f"Erro ao processar o arquivo {filepath}: {e}")
                erros_encontrados = True

    print(f"\nResumo da {'Correção' if auto_fix else 'Validação'}:")
    print(f"Arquivos verificados: {arquivos_verificados}")

    if auto_fix:
        print(f"Arquivos corrigidos: {arquivos_corrigidos}")
        print("✅ Correção finalizada! Execute o script novamente sem --fix para validar.")
        sys.exit(0)
    else:
        if erros_encontrados:
            print("❌ A validação falhou! Corrija os erros apontados acima antes do deploy ou use a flag --fix.")
            sys.exit(1)
        else:
            print("✅ Nenhum erro de formatação de tags de template encontrado. Tudo pronto!")
            sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validador e formatador de tags de template do Django.")
    parser.add_argument(
        '--fix',
        action='store_true',
        help="Aplica a correção automática em tags divididas em múltiplas linhas."
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    templates_dir = project_root / 'templates'

    validate_templates(templates_dir, auto_fix=args.fix)
