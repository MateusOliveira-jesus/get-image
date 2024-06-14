import os
import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from urllib.parse import urlsplit

def normalize_title(title):
    title = unidecode(title)  # Remove acentos
    title = re.sub(r'[^\w\s-]', '', title)  # Remove pontuações e caracteres especiais
    title = re.sub(r'\s+', '-', title)  # Substitui espaços por hífens
    stopwords = ["de", "da", "do", "para", "com", "em", "e", "ou", "a", "o"]
    normalized_title = "-".join(word for word in title.split("-") if word.lower() not in stopwords)
    normalized_title = re.sub(r'[\d_]', '', normalized_title)  # Remove números e sublinhados
    normalized_title = re.sub(r'-{2,}', '-', normalized_title)  # Substitui múltiplos hífens por um único
    normalized_title = normalized_title.strip('-')  # Remove hífens no início ou fim
    return normalized_title.lower()

def get_unique_filename(base_path, filename, extension):
    file_path = os.path.join(base_path, f"{filename}{extension}")
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(base_path, f"{filename}-{counter:02d}{extension}")
        counter += 1
    return file_path

# Cabeçalhos para simular um navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

caminho_base = "c:\\Users\\mateus.jesus\\Downloads"
pasta_imagens = "get-imagens"
caminho_salvar = os.path.join(caminho_base, pasta_imagens)

if not os.path.exists(caminho_salvar):
    os.makedirs(caminho_salvar)

class_cards = input("Por favor, digite o nome da classe dos cards: ")
class_title = input("Por favor, digite o nome da classe ou tag do título dos cards: ")
url = input("Por favor, digite o link da página da web onde os cards estão localizados: ")

search_type = input("Deseja buscar imagens pela tag img? (sim/não): ").strip().lower()
background_class = None
if search_type == 'não':
    background_class = input("Por favor, digite o nome da classe do background: ")

# Fazer a requisição HTTP para a página
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Erro ao fazer a requisição para a página: {e}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")
cards = soup.find_all(class_=class_cards)

if not cards:
    print("Nenhum card encontrado na página.")
    exit()

# Função para extrair URL da imagem de diferentes tipos de cards
def extract_image_url(card):
    url_imagem = None
    if search_type == 'sim':
        img_tag = card.find("img")
        if img_tag:
            url_imagem = img_tag.get("src")
    else:
        background_div = card.find(class_=background_class)
        if background_div:
            style = background_div.get('style', '')
            match = re.search(r'background(?:-image)?:\s*url\(["\']?(.*?)["\']?\)', style)
            if match:
                url_imagem = match.group(1).strip('\'"')
                url_imagem = re.sub(r'\?.*$', '', url_imagem)

    # Tentativa adicional de encontrar imagem dentro de `<picture>`
    if not url_imagem:
        picture_tag = card.find("picture")
        if picture_tag:
            img_tag = picture_tag.find("img")
            if img_tag:
                url_imagem = img_tag.get("src")
    return url_imagem

for i, card in enumerate(cards):
    title_tag = card.find(class_=class_title) or card.find("a", class_=class_title)
    if not title_tag:
        title_tag = card.find("div", {"data-hook": "item-title"})
    if title_tag:
        title = title_tag.text.strip()
        url_imagem = extract_image_url(card)
        if url_imagem:
            try:
                response_imagem = requests.get(url_imagem, headers=headers, stream=True)
                response_imagem.raise_for_status()
            except requests.RequestException as e:
                print(f"Erro ao baixar a imagem do card {i}: {e}")
                continue

            nome_arquivo = normalize_title(title)
            extensao = os.path.splitext(urlsplit(url_imagem).path)[1]
            caminho_completo = get_unique_filename(caminho_salvar, nome_arquivo, extensao)
            with open(caminho_completo, "wb") as file:
                for chunk in response_imagem.iter_content(1024):
                    file.write(chunk)

            print(f"Imagem do card {title} => ({os.path.basename(caminho_completo)})")
        else:
            print(f"URL da imagem não encontrada para o card {i}.")
    else:
        print(f"Título não encontrado para o card {i}.")

print(f"\nDownload concluído! Confira suas imagens na pasta 'get-imagens' dentro de 'Downloads'. 🎉")
