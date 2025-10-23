import os
import logging
from typing import Optional
import instaloader

# Configura logging para output claro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_instagram_session(login_username: Optional[str] = None, login_password: Optional[str] = None) -> instaloader.Instaloader:
    """
    Cria uma sessão do Instaloader, com login opcional para posts privados ou mais robustez.
    """
    L = instaloader.Instaloader(
        download_pictures=True,
        download_video_thumbnails=False,  # Só imagens, sem vídeos
        download_geotags=False,
        download_comments=False,
        save_metadata=False,  # Foco só em imagens
        compress_json=False,
        filename_pattern='{shortcode}'  # Nomeia arquivos pelo shortcode do post
    )
    
    if login_username and login_password:
        try:
            L.login(login_username, login_password)
            logger.info("Login realizado com sucesso.")
        except Exception as e:
            logger.error(f"Erro no login: {e}. Continuando sem autenticação (apenas para posts públicos).")
    
    return L

def extract_shortcode_from_url(url: str) -> Optional[str]:
    """
    Extrai o shortcode da URL do post Instagram.
    Ex: https://www.instagram.com/p/ABC123def/ -> ABC123def
    """
    if '/p/' not in url:
        raise ValueError("URL inválida: deve conter '/p/' para posts.")
    
    shortcode = url.split('/p/')[1].split('/')[0].split('?')[0]  # Remove query params
    if len(shortcode) < 5:  # Shortcode típico tem ~11 chars
        raise ValueError("Shortcode inválido extraído da URL.")
    
    return shortcode

def download_carousel_images(post_url: str, target_dir: str = "images", 
                             login_username: Optional[str] = None, 
                             login_password: Optional[str] = None) -> None:
    """
    Baixa todas as imagens de um post carrossel para o diretório target_dir.
    
    Args:
        post_url: URL do post Instagram (ex: https://www.instagram.com/p/ABC123def/).
        target_dir: Diretório de destino para as imagens.
        login_username: Username para login (opcional).
        login_password: Password para login (opcional).
    """
    try:
        # Extrai shortcode
        shortcode = extract_shortcode_from_url(post_url)
        logger.info(f"Shortcode extraído: {shortcode}")
        
        # Cria sessão
        L = create_instagram_session(login_username, login_password)
        
        # Cria diretório se não existir
        os.makedirs(target_dir, exist_ok=True)
        
        # Baixa o post (instaloader detecta carrossel e baixa todas as sidecars)
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=target_dir)
        
        # Conta imagens baixadas (carrossel pode ter 2+)
        num_images = len([f for f in os.listdir(target_dir) if f.startswith(shortcode) and f.endswith(('.jpg', '.png'))])
        logger.info(f"Download concluído! {num_images} imagem(ns) salva(s) em '{target_dir}'.")
        
    except ValueError as e:
        logger.error(f"Erro na URL/shortcode: {e}")
    except instaloader.exceptions.ProfileNotExistsException:
        logger.error("Post não encontrado ou perfil privado sem login.")
    except instaloader.exceptions.ConnectionException as e:
        logger.error(f"Erro de conexão: {e}. Tente com login ou verifique rate limits.")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
