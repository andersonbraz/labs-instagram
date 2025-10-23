from solutions import client_instagram as instagram
from solutions import extract_text as capture

if __name__ == "__main__":

    urls = ['https://www.instagram.com/p/DP2otqEDC-6/', 
            'https://www.instagram.com/p/DPgJE4oEdG9/', 
            'https://www.instagram.com/p/DPOpAuHE2k4/',
            'https://www.instagram.com/p/DPogsYxjpBX/', 
            'https://www.instagram.com/p/DPmnWR6EpPW/', 
            'https://www.instagram.com/p/DPzfC3sDoCP/']

    for url in urls:
        instagram.download_carousel_images(url)

    capture.extract_all_texts(output_dir='texts', min_length=150)