import os
import logging
from pathlib import Path
from typing import List

# Configura logging para output claro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_txt_files(input_dir: str) -> List[Path]:
    """
    Lista todos os arquivos .txt no diretório, ordenados alfabeticamente.
    Ignora explicitamente 'all_extracted_texts.txt'.
    
    Args:
        input_dir: Diretório de input (ex: 'contents').
    
    Returns:
        Lista de Paths para os arquivos .txt.
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        logger.warning(f"Diretório '{input_dir}' não encontrado.")
        return []
    
    txt_files = []
    for f in input_path.iterdir():
        if f.suffix == '.txt':
            if f.name == 'all_extracted_texts.txt':
                logger.info(f"Ignorando arquivo consolidado: '{f.name}'.")
                continue
            txt_files.append(f)
    
    txt_files = sorted(txt_files)
    if not txt_files:
        logger.warning(f"Nenhum arquivo .txt relevante encontrado em '{input_dir}' (após filtros).")
    
    return txt_files

def read_file_content(file_path: Path) -> str:
    """
    Lê o conteúdo de um arquivo .txt.
    
    Args:
        file_path: Path do arquivo.
    
    Returns:
        Conteúdo como string (vazio se erro ou vazio).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                logger.warning(f"Arquivo '{file_path.name}' está vazio.")
            return content
    except Exception as e:
        logger.error(f"Erro ao ler '{file_path.name}': {e}")
        return ""

def generate_prompts_md(txt_files: List[Path], output_file: str, min_length: int = 150) -> None:
    """
    Gera o arquivo Markdown com a estrutura solicitada, filtrando por min_length.
    
    Args:
        txt_files: Lista de arquivos .txt.
        output_file: Caminho do output (ex: 'guide/prompts.md').
        min_length: Comprimento mínimo para incluir no MD.
    """
    output_path = Path(output_file)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    included_count = 0
    with open(output_path, 'w', encoding='utf-8') as md_file:
        md_file.write("# Prompts\n\n")
        md_file.write(f"(Filtros: Apenas prompts > {min_length} chars; arquivos consolidados ignorados)\n\n")
        
        for txt_file in txt_files:
            content = read_file_content(txt_file)
            if content and len(content) > min_length:
                # Subtítulo: nome sem .txt
                subtitle = txt_file.stem
                md_file.write(f"## {subtitle}\n\n")
                md_file.write("```\n")
                md_file.write(content)
                md_file.write("\n```\n\n")
                logger.info(f"Adicionado prompt relevante de '{subtitle}' ({len(content)} chars) ao MD.")
                included_count += 1
            else:
                logger.info(f"Ignorado '{txt_file.name}' (conteúdo vazio ou < {min_length} chars: {len(content) if content else 0}).")
    
    logger.info(f"Arquivo Markdown gerado: '{output_file}' com {included_count} prompts relevantes.")

def organize_prompts(input_dir: str = "contents", output_file: str = "guide/prompts.md", min_length: int = 150) -> None:
    """
    Função principal: Organiza prompts em MD, com filtro de comprimento e ignorando consolidados.
    
    Args:
        input_dir: Diretório com .txt.
        output_file: Caminho do MD de output.
        min_length: Comprimento mínimo para incluir.
    """
    txt_files = get_txt_files(input_dir)
    if txt_files:
        logger.info(f"Processando {len(txt_files)} arquivos .txt relevantes (filtro: >{min_length} chars).")
        generate_prompts_md(txt_files, output_file, min_length)
    else:
        logger.warning("Nada a processar. Verifique o diretório de input.")

