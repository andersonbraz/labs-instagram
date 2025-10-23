import os
import logging
from typing import List, Optional
from PIL import Image
import pytesseract

# Configura logging para output claro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_tesseract_path() -> None:
    """
    Configura o caminho do Tesseract se necessário (ajuste para o seu sistema).
    No Windows, pode ser algo como: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    """
    # Descomente e ajuste se o Tesseract não for detectado automaticamente
    # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Exemplo Linux/macOS
    pass

def extract_text_from_image(image_path: str) -> str:
    """
    Extrai texto de uma imagem usando OCR.
    
    Args:
        image_path: Caminho para a imagem.
    
    Returns:
        Texto extraído (string vazia se nada for detectado).
    """
    try:
        # Abre a imagem com Pillow
        img = Image.open(image_path)
        
        # Configurações OCR: lang='por' para português (ajuste para 'eng' se inglês)
        # --psm 6 para texto uniforme (bom para posts IG)
        text = pytesseract.image_to_string(img, lang='por', config='--psm 6')
        
        # Limpa texto (remove quebras de linha extras e espaços)
        text = ' '.join(text.split()).strip()
        
        logger.info(f"Texto extraído de '{os.path.basename(image_path)}': {text[:50]}..." if text else f"Nenhum texto em '{os.path.basename(image_path)}'.")
        return text
        
    except Exception as e:
        logger.error(f"Erro ao processar {image_path}: {e}")
        return ""

def get_image_files(input_dir: str) -> List[str]:
    """
    Lista todos os arquivos de imagem no diretório.
    Suporta: .jpg, .jpeg, .png, .bmp, .tiff.
    """
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    image_files = []
    
    for filename in os.listdir(input_dir):
        if any(filename.lower().endswith(ext) for ext in supported_extensions):
            image_files.append(os.path.join(input_dir, filename))
    
    if not image_files:
        logger.warning(f"Nenhuma imagem encontrada em '{input_dir}'.")
    
    return image_files

def save_contentss(image_texts: List[tuple[str, str]], output_dir: str, min_length: int = 25) -> None:
    """
    Salva textos extraídos: um TXT por imagem (só se len(text) > min_length) + um consolidado.
    
    Args:
        image_texts: Lista de tuplas (caminho_imagem, texto_extraido).
        output_dir: Diretório de output.
        min_length: Comprimento mínimo para salvar arquivo individual.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Arquivo consolidado (inclui todos, com marcação para curtos)
    consolidated_path = os.path.join(output_dir, 'all_contentss.txt')
    with open(consolidated_path, 'w', encoding='utf-8') as f:
        f.write("=== TEXTOS EXTRAÍDOS DE IMAGENS ===\n")
        f.write(f"(Filtros: Arquivos individuais só para textos > {min_length} chars)\n\n")
        for img_path, text in image_texts:
            if text:
                img_name = os.path.basename(img_path)
                if len(text) > min_length:
                    f.write(f"--- {img_name} (Relevante) ---\n{text}\n\n")
                else:
                    f.write(f"--- {img_name} (Texto curto: <{min_length} chars) ---\n{text}\n\n")
            else:
                f.write(f"--- {img_name} (Sem texto) ---\n\n")
    
    logger.info(f"Resumo salvo em '{consolidated_path}'.")
    
    # Arquivos individuais (só se texto relevante)
    relevant_count = 0
    for img_path, text in image_texts:
        if text and len(text) > min_length:
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            txt_path = os.path.join(output_dir, f"{base_name}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"Arquivo individual salvo: '{txt_path}'.")
            relevant_count += 1
    
    if relevant_count == 0:
        logger.info("Nenhum arquivo individual salvo (todos os textos curtos ou vazios).")

def extract_all_texts(input_dir: str = "images", output_dir: str = "contents", min_length: int = 25) -> None:
    """
    Função principal: Extrai texto de todas as imagens no input_dir.
    
    Args:
        input_dir: Diretório com imagens.
        output_dir: Diretório para salvar textos extraídos.
        min_length: Comprimento mínimo para arquivos individuais.
    """
    setup_tesseract_path()  # Configura Tesseract se preciso
    
    # Lista imagens
    image_files = get_image_files(input_dir)
    if not image_files:
        return
    
    logger.info(f"Processando {len(image_files)} imagem(ns) de '{input_dir}' (filtro: >{min_length} chars para arquivos individuais).")
    
    # Extrai textos
    image_texts = []
    for img_path in image_files:
        text = extract_text_from_image(img_path)
        image_texts.append((img_path, text))
    
    # Salva resultados
    save_contentss(image_texts, output_dir, min_length)
    
    # Estatísticas
    total_with_text = sum(1 for _, text in image_texts if text)
    relevant_count = sum(1 for _, text in image_texts if text and len(text) > min_length)
    logger.info(f"Processamento concluído! {relevant_count} imagem(ns) com texto relevante (>{min_length} chars) / {total_with_text} com texto detectado (total).")
