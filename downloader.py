import os
import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from urllib.parse import urlsplit
from PyInquirer import prompt, Separator

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
        }
    ]
    return prompt(questions)

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
                'message': 'Digite a posição da URL no "srcset" (0 para a primeira, 1 para a segunda, etc.):',
            }
        ]
        srcset_position = int(prompt(srcset_position_question)['srcset_position'])

    return background_class, srcset_position

def extract_image_url(card, search_type, image_attr, srcset_position, background_class):
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

    if not url_imagem:
        picture_tag = card.find("picture")
        if picture_tag:
            img_tag = picture_tag.find("img")
            if img_tag:
                if image_attr == 'src':
                    url_imagem = img_tag.get("src")
                elif image_attr == 'srcset':
                    srcset = img_tag.get("srcset")
                    if srcset:
                        urls = [src.split()[0] for src in srcset.split(",")]
                        if 0 <= srcset_position < len(urls):
                            url_imagem = urls[srcset_position]
    return url_imagem

def retry_with_new_classes():
    print("Vamos tentar novamente com novas classes ou tags.")
    return ask_questions()

while True:
    answers = ask_questions()
    background_class, srcset_position = ask_additional_questions()

    try:
        response = requests.get(answers['url'], headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erro ao fazer a requisição para a página: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all(class_=answers['class_cards'])

    if not cards:
        print("Nenhum card encontrado na página. Deseja tentar novamente com outras classes?")
        retry = prompt([{
            'type': 'confirm',
            'name': 'retry',
            'message': 'Deseja tentar novamente?',
            'default': True
        }])
        if retry['retry']:
            continue
        else:
            break

    for i, card in enumerate(cards):
        title_tag = card.find(class_=answers['class_or_tag_title'])  # Tenta encontrar a classe
        if not title_tag:  # Se não encontrar a classe, tenta encontrar como tag
            title_tag = card.find(answers['class_or_tag_title'])

        if not title_tag:
            print(f"Título não encontrado para o card {i}. Tentando fallback...")

        if title_tag:
            title = title_tag.text.strip()
            url_imagem = extract_image_url(card, answers['search_type'], answers['image_attr'], srcset_position, background_class)
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
            retry_title_class = prompt([{
                'type': 'confirm',
                'name': 'retry',
                'message': 'Deseja tentar novamente com outra classe ou tag para título?',
                'default': True
            }])
            if retry_title_class['retry']:
                title_class_input = prompt([{
                    'type': 'input',
                    'name': 'class_or_tag_title',
                    'message': 'Por favor, digite uma nova classe ou tag do título dos cards:',
                }])
                answers['class_or_tag_title'] = title_class_input['class_or_tag_title']
                break

    cont = prompt([{
        'type': 'confirm',
        'name': 'continue',
        'message': 'Deseja continuar com mais cards?',
        'default': False
    }])
    if not cont['continue']:
        print("Download concluído! Confira suas imagens na pasta 'get-imagens' dentro de 'Downloads'.")
        break
