from solutions import client_instagram as instagram
from solutions import extract_text as processor
from solutions import organizer_prompt as curator

if __name__ == "__main__":

    urls = ['https://www.instagram.com/p/DP2otqEDC-6/', 
            'https://www.instagram.com/p/DPgJE4oEdG9/', 
            'https://www.instagram.com/p/DPOpAuHE2k4/',
            'https://www.instagram.com/p/DPogsYxjpBX/', 
            'https://www.instagram.com/p/DPmnWR6EpPW/', 
            'https://www.instagram.com/p/DPzfC3sDoCP/']

    for url in urls:
        instagram.download_carousel_images(url)

    processor.extract_all_texts(min_length=200)
    curator.organize_prompts(min_length=200)