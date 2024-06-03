import os
import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

def normalize_title(title):
    # Remover acentos
    title = unidecode(title)
    # Remover pontuações e caracteres especiais
    title = re.sub(r'[^\w\s-]', '', title)
    # Substituir espaços por hífens
    normalized_title = title.replace(" ", "-")
    # Substituir múltiplos hífens por apenas um hífen
    normalized_title = re.sub(r'-{2,}', '-', normalized_title)
    # Remover preposições, artigos e outras palavras curtas
    stopwords = ["de", "da", "do", "para", "com", "em", "e", "ou", "a", "o"]
    normalized_title = "-".join(word for word in normalized_title.split("-") if word.lower() not in stopwords)
    # Remover números e sublinhados restantes
    normalized_title = re.sub(r'[\d_]', '', normalized_title)
    return normalized_title.lower()

# Função para obter a extensão da imagem a partir do cabeçalho do conteúdo
def get_image_extension(response):
    content_type = response.headers['Content-Type']
    if 'image/jpeg' in content_type:
        return '.jpg'
    elif 'image/png' in content_type:
        return '.png'
    elif 'image/gif' in content_type:
        return '.gif'
    else:
        return '.jpg'  # Padrão para jpg se não conseguir determinar

# Cabeçalhos para simular um navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Caminho onde deseja salvar as imagens
caminho_base = "c:\\Users\\mateus.jesus\\Downloads"
pasta_imagens = "get-imagens"
caminho_salvar = os.path.join(caminho_base, pasta_imagens)

print('Bem vindo ao Get Images!  \né aqui aonde a mágica acontece! 🥷')
# Verificar se o diretório de imagens existe, senão criar
print('\n')
if not os.path.exists(caminho_salvar):
    os.makedirs(caminho_salvar)
    print(f"Diretório '{pasta_imagens}' criado em '{caminho_base}'.\n")

# Perguntar ao usuário sobre a classe dos cards, classe do título e link
class_cards = input("Por favor, digite o nome da classe dos cards: ") 
print('\n')
class_title = input("Por favor, digite o nome da classe ou tag do título dos cards: ")
print('\n')
url = input("Por favor, digite o link da página da web onde os cards estão localizados: ")
print('\n')

# Perguntar se o usuário deseja buscar imagens pela tag img ou pelo background
search_type = input("Deseja buscar imagens pela tag img? (sim/não): ").strip().lower()
print('\n')

background_class = None
if search_type == 'não':
    background_class = input("Por favor, digite o nome da classe do background: ")

# Fazer a requisição HTTP para a página
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Isso irá gerar um erro se a requisição falhar
except requests.RequestException as e:
    print(f"Erro ao fazer a requisição para a página: {e}")
    exit()

# Parsear o HTML com BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Encontrar todas as tags de classe dos cards na página
cards = soup.find_all(class_=class_cards)

# Verificar se foram encontrados cards na página
if not cards:
    print("Nenhum card encontrado na página.")
    exit()

# ...

# Iterar sobre os cards e extrair o URL da imagem e o título
for i, card in enumerate(cards):
    # Encontrar a tag do título dentro do card
    title_tag = card.find(class_=class_title) or card.find(class_=class_title, href=True) or card.find("a", class_=class_title)
    if title_tag:
        title = title_tag.text.strip()
        url_imagem = None

        if search_type == 'sim':
            img_tag = card.find("img")
            if img_tag:
                url_imagem = img_tag.get("src")
            else:
                print(f"Imagem não encontrada para o card {i}.")
                continue
        else:
            background_div = card.find(class_=background_class)
            if background_div:
                style = background_div.get('style', '')
                print(f"Card {i} - Style encontrado: {style}")  # Adicionado para depuração
                match = re.search(r'background(?:-image)?:\s*url\(["\']?(.*?)["\']?\)', style)
                if match:
                    url_imagem = match.group(1).strip('\'"')
                    # Corrigir a URL se necessário (remover parâmetros de dimensionamento)
                    url_imagem = re.sub(r'\?.*$', '', url_imagem)
                    print(f"Card {i} - URL da imagem de fundo encontrado: {url_imagem}")  # Adicionado para depuração
                else:
                    print(f"Background não encontrado para o card {i}.")
                    continue
            else:
                print(f"Div de background não encontrada para o card {i}.")
                continue

        # Baixar a imagem
        try:
            response_imagem = requests.get(url_imagem, headers=headers, stream=True)
            response_imagem.raise_for_status()  # Isso irá gerar um erro se a requisição falhar
            # Obter a extensão da imagem
            extensao = get_image_extension(response_imagem)
        except requests.RequestException as e:
            print(f"Erro ao baixar a imagem do card {i}: {e}")
            continue

        # Normalizar o título para o padrão desejado
        nome_arquivo = normalize_title(title)

        # Construir o caminho completo para salvar a imagem
        caminho_completo = os.path.join(caminho_salvar, f"{nome_arquivo}{extensao}")
        with open(caminho_completo, "wb") as file:
            for chunk in response_imagem.iter_content(1024):
                file.write(chunk)

        print(f"Imagem do card {title} => ( {nome_arquivo}{extensao} )")
    else:
        print("Título não encontrado para o card {i}.")

# Mensagem de conclusão
print(f"\nDownload concluído! Foram baixadas {len(cards)} imagens. Confira suas imagens na pasta 'get-imagens' dentro de 'Downloads'. 🎉")
