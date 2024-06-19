import os
import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from urllib.parse import urlsplit
from PyInquirer import prompt
from PIL import Image, ImageFilter  # Importar Pillow

# Função de normalização de título
def normalize_title(title, keep_numbers=False):
    title = unidecode(title)  # Remove acentos
    title = re.sub(r'[^\w\s-]', '', title)  # Remove pontuações e caracteres especiais
    title = re.sub(r'\s+', '-', title)  # Substitui espaços por hífens
    stopwords = ["de", "da", "do", "para", "com", "em", "e", "ou", "a", "o"]
    normalized_title = "-".join(word for word in title.split("-") if word.lower() not in stopwords)
    
    if keep_numbers == 'não':
        normalized_title = re.sub(r'[\d_]', '', normalized_title)  # Remove números e sublinhados
    
    normalized_title = re.sub(r'-{2,}', '-', normalized_title)  # Substitui múltiplos hífens por um único
    normalized_title = normalized_title.strip('-')  # Remove hífens no início ou fim
    return normalized_title.lower()

# Função para obter caminho de arquivo único
def get_unique_filename(base_path, filename, extension):
    file_path = os.path.join(base_path, f"{filename}{extension}")
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(base_path, f"{filename}-{counter:02d}{extension}")
        counter += 1
    return file_path

# Função para melhorar e converter a imagem para WebP
def enhance_and_convert_image(image_path):
    try:
        # Abre a imagem usando PIL
        image = Image.open(image_path)

        # Aplica um filtro de suavização
        image = image.filter(ImageFilter.SMOOTH_MORE)

        # Converte para WebP
        webp_path = os.path.splitext(image_path)[0] + '.webp'
        image.save(webp_path, 'WEBP')
        print(f"Imagem convertida para WebP: {webp_path}")

        # Remove a imagem original
        os.remove(image_path)
        return webp_path
    except Exception as e:
        print(f"Erro ao melhorar e converter a imagem: {e}")
        return None

# Cabeçalhos para simular um navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Configurações de caminho e pasta para salvar imagens
caminho_base = "C:\\Users\\mateu\\Downloads"
pasta_imagens = "get-imagens"
caminho_salvar = os.path.join(caminho_base, pasta_imagens)

def print_get_image_banner():
    banner = """
𝕸𝖆𝖙𝖊𝖚𝖘 𝕺𝖑𝖎𝖛𝖊𝖎𝖗𝖆

  ____    ___  ______                 ____  ___ ___   ____   ____    ___
 /    T  /  _]|      T               l    j|   T   T /    T /    T  /  _]
Y   __j /  [_ |      |     _____      |  T | _   _ |Y  o  |Y   __j /  [_
|  T  |Y    _]l_j  l_j    |     |     |  | |  \_/  ||     ||  T  |Y    _]
|  l_ ||   [_   |  |      l_____j     |  | |   |   ||  _  ||  l_ ||   [_
|     ||     T  |  |                  j  l |   |   ||  |  ||     ||     T
l___,_jl_____j  l__j                 |____jl___j___jl__j__jl___,_jl_____j
    """
    print(banner)

# Chamada da função para exibir o banner no início do script
print_get_image_banner()

# Verifica se o diretório de salvamento existe, se não, cria
if not os.path.exists(caminho_salvar):
    os.makedirs(caminho_salvar)

# Lista para armazenar os dados de título e URL das imagens
vetGetImage = []

# Função para fazer perguntas interativas ao usuário
def ask_questions():
    questions = [
        {
            'type': 'input',
            'name': 'class_cards',
            'message': 'Por favor, digite o nome da classe dos cards:',
        },
        {
            'type': 'input',
            'name': 'class_or_tag_title',
            'message': 'Por favor, digite o nome da classe ou tag do título dos cards:',
        },
        {
            'type': 'input',
            'name': 'url',
            'message': 'Por favor, digite o link da página da web onde os cards estão localizados:',
        },
        {
            'type': 'list',
            'name': 'search_type',
            'message': 'Deseja buscar imagens pela tag img?',
            'choices': [
                'sim',
                'não'
            ]
        },
        {
            'type': 'list',
            'name': 'image_attr',
            'message': 'Deseja buscar a URL da imagem em "src" ou "srcset"?',
            'choices': [
                'src',
                'srcset'
            ]
        },
        {
            'type': 'list',
            'name': 'keep_numbers',
            'message': 'Deseja manter a numeração no título da URL da imagem?',
            'choices': [
                'não',
                'sim'
            ]
        },
        {
            'type': 'list',
            'name': 'enhance_image',
            'message': 'Deseja melhorar a qualidade das imagens?',
            'choices': [
                'sim',
                'não'
            ]
        }
    ]
    return prompt(questions)

# Função para extrair URL da imagem de acordo com o tipo de busca
def extract_image_url(card, search_type, image_attr, srcset_position, background_class, base_url):
    url_imagem = None
    if search_type == 'sim':
        img_tag = card.find("img")
        if img_tag:
            if image_attr == 'src':
                url_imagem = img_tag.get("src")
            elif image_attr == 'srcset':
                srcset = img_tag.get("srcset")
                if srcset:
                    urls = [src.split()[0] for src in srcset.split(",")]
                    if 0 <= srcset_position < len(urls):
                        url_imagem = urls[srcset_position]
    else:
        background_div = card.find(class_=background_class)
        if background_div:
            style = background_div.get('style', '')
            match = re.search(r'background(?:-image)?:\s*url\(["\']?(.*?)["\']?\)', style)
            if match:
                url_imagem = match.group(1).strip('\'"')
                url_imagem = re.sub(r'\?.*$', '', url_imagem)

    if url_imagem:
        # Verifica se a URL não possui um esquema (http:// ou https://)
        if not url_imagem.startswith(('http://', 'https://')):
            # Verifica se a URL é relativa (começa com /) e adiciona o domínio base
            if url_imagem.startswith('/'):
                url_imagem = base_url + url_imagem
            else:
                # Se não for relativa e não tiver um esquema, adiciona http:// como padrão
                url_imagem = 'http://' + url_imagem

    return url_imagem

# Função para perguntar se deseja tentar novamente com novas classes ou tags
def retry_with_new_classes():
    print("Vamos tentar novamente com novas classes ou tags.")
    return ask_questions()

# Função para perguntar classes ou tags adicionais baseado nas respostas
def ask_additional_questions():
    background_class = None
    srcset_position = None

    if answers['search_type'] == 'não':
        background_class_question = [
            {
                'type': 'input',
                'name': 'background_class',
                'message': 'Por favor, digite o nome da classe do background:',
            }
        ]
        background_class = prompt(background_class_question)['background_class']

    if answers['image_attr'] == 'srcset':
        srcset_position_question = [
            {
                'type': 'input',
                'name': 'srcset_position',
                'message': 'Por favor, digite a posição da imagem desejada no "srcset" (0 para a primeira, 1 para a segunda, etc.):',
            }
        ]
        srcset_position = int(prompt(srcset_position_question)['srcset_position'])

    return background_class, srcset_position

# Executa as perguntas para o usuário
answers = ask_questions()

# Extrai informações das respostas do usuário
class_cards = answers['class_cards']
class_or_tag_title = answers['class_or_tag_title']
url = answers['url']
search_type = answers['search_type']
image_attr = answers['image_attr']
keep_numbers = answers['keep_numbers']
enhance_image = answers['enhance_image']  # Nova variável para guardar a escolha do usuário

background_class, srcset_position = ask_additional_questions()

# Faz a solicitação HTTP à página
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Divide a URL para obter o domínio base
url_parts = urlsplit(url)
base_url = f"{url_parts.scheme}://{url_parts.netloc}"

# Extrai todos os cards da página
cards = soup.find_all(class_=class_cards)

# Verifica se foram encontrados cards
if not cards:
    print("Nenhum card encontrado com a classe fornecida.")
    retry_with_new_classes()
else:
    # Itera sobre cada card para extrair as imagens
    for i, card in enumerate(cards, start=1):
        # Extrai o título do card
        title_element = card.find(class_=class_or_tag_title)
        title = title_element.get_text(strip=True) if title_element else f"Imagem_{i}"
        normalized_title = normalize_title(title, keep_numbers)

        # Extrai a URL da imagem
        url_imagem = extract_image_url(card, search_type, image_attr, srcset_position, background_class, base_url)
        if url_imagem:
            try:
                # Faz o download da imagem
                img_data = requests.get(url_imagem, headers=headers).content
                # Gera um caminho único para salvar a imagem
                img_path = get_unique_filename(caminho_salvar, normalized_title, '.jpg')
                # Salva a imagem
                with open(img_path, 'wb') as img_file:
                    img_file.write(img_data)

                print(f"Imagem salva: {img_path}")
                
                # Se o usuário optou por melhorar a imagem
                if enhance_image == 'sim':
                    enhanced_image_path = enhance_and_convert_image(img_path)
                    if enhanced_image_path:
                        print(f"Imagem melhorada e salva como WebP: {enhanced_image_path}")
                        vetGetImage.append(enhanced_image_path)
                else:
                    vetGetImage.append(img_path)
            except Exception as e:
                print(f"Erro ao salvar a imagem {url_imagem}: {e}")

print("Processo concluído!")
print(f"Imagens salvas: {vetGetImage}")
