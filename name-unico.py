import os
import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from urllib.parse import urlsplit
    # srset 1

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

# Cabeçalhos para simular um navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Caminho onde deseja salvar as imagens
caminho_base = "c:\\Users\\mateus.jesus\\Downloads"
pasta_imagens = "get-imagens"
caminho_salvar = os.path.join(caminho_base, pasta_imagens)

print('Bem vindo ao Get Images!  \né aqui aonde a mágica acontece! 🥷')
print('\n')

# Perguntar ao usuário se deseja nomear todas as imagens com um único título
usar_titulo_unico = input("Deseja nomear todas as imagens com um único título? (sim/não): ").strip().lower()
titulo_unico = None
if usar_titulo_unico == "sim":
    titulo_unico = input("Por favor, digite o título único para as imagens: ")
    titulo_unico = normalize_title(titulo_unico)  # Normaliza o título único

# Se o usuário optar por usar um título único, pedir apenas o link da página
if usar_titulo_unico == "sim":
    url = input("Por favor, digite o link da página da web onde as imagens estão localizadas: ").strip()
else:
    # Perguntar ao usuário sobre a classe dos cards e a classe ou tag do título
    class_cards = input("Por favor, digite o nome da classe dos cards: ").strip()
    class_title = input("Por favor, digite o nome da classe ou tag do título dos cards: ").strip()
    url = input("Por favor, digite o link da página da web onde os cards estão localizados: ").strip()

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

# Encontrar todas as imagens da página
if usar_titulo_unico == "sim":
    imagens = soup.find_all('img')
else:
    imagens = soup.find_all('img', class_=class_cards)

# Verificar se foram encontradas imagens na página
if not imagens:
    print("Nenhuma imagem encontrada na página.")
    exit()

# Contador para numerar as imagens se for título único
contador_imagens = 1

# Iterar sobre as imagens e extrair o URL da primeira imagem da srcset e o título
for i, img_tag in enumerate(imagens):
    srcset = img_tag.get("srcset")

    # Verificar se a srcset está vazia ou nula
    if not srcset:
        print(f"Erro ao baixar a imagem {i}: srcset vazia ou nula.")
        continue

    # Pegar a primeira URL da lista srcset
    url_imagem = srcset.split(",")[0].split()[0]

    # Baixar a imagem
    try:
        response_imagem = requests.get(url_imagem, headers=headers, stream=True)
        response_imagem.raise_for_status()  # Isso irá gerar um erro se a requisição falhar
    except requests.RequestException as e:
        print(f"Erro ao baixar a imagem {i}: {e}")
        continue

    # Normalizar o título para o padrão desejado
    if usar_titulo_unico == "sim":
        # Adiciona um número ao título único no formato de dois dígitos
        nome_arquivo = f"{titulo_unico}-{contador_imagens:02d}"
        contador_imagens += 1
    else:
        title = img_tag.get("alt", f"Imagem_{i+1}")  # Se não houver alt, usa uma numeração simples
        nome_arquivo = normalize_title(title)

    # Obter a extensão da imagem diretamente do URL
    extensao = os.path.splitext(urlsplit(url_imagem).path)[1]
    
    # Construir o caminho completo para salvar a imagem
    caminho_completo = os.path.join(caminho_salvar, f"{nome_arquivo}{extensao}")
    with open(caminho_completo, "wb") as file:
        for chunk in response_imagem.iter_content(1024):
            file.write(chunk)

    print(f"Imagem {i+1} => ( {nome_arquivo}{extensao} )")

# Mensagem de conclusão
print(f"\nDownload concluído! Foram baixadas {len(imagens)} imagens. Confira suas imagens na pasta 'get-imagens' dentro de 'Downloads'. 🎉")
