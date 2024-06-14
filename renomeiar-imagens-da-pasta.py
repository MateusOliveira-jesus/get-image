import os
import re
from unidecode import unidecode
from pathlib import Path

def normalize_title(title):
    """
    Normaliza o título removendo acentos, caracteres especiais e espaços extras.
    Remove todos os hífens e substitui espaços por hífens.

    Args:
        title (str): O título a ser normalizado.
        
    Returns:
        str: O título normalizado.
    """
    title = unidecode(title)  # Remover acentos
    title = re.sub(r'[^\w\s]', '', title)  # Remover pontuações e caracteres especiais
    normalized_title = re.sub(r'\s+', ' ', title.strip())  # Remover espaços extras e normalizar espaços

    stopwords = {"de", "da", "do", "para", "com", "em", "e", "ou", "a", "o"}
    normalized_title = "-".join(word for word in normalized_title.split() if word.lower() not in stopwords)
    
    # Manter números no título
    normalized_title = re.sub(r'(?<=\d)(?=\D)|(?<=\D)(?=\d)', '-', normalized_title)
    return normalized_title.lower()

def rename_images(folder_path):
    """
    Renomeia os arquivos de imagem dentro de uma pasta para um formato normalizado.
    
    Args:
        folder_path (str): O caminho para a pasta contendo as imagens.
    """
    folder = Path(folder_path)
    
    if not folder.is_dir():
        print("O caminho fornecido não é uma pasta válida.")
        return

    for file_path in folder.iterdir():
        if file_path.is_file():
            file_name = file_path.stem
            file_extension = file_path.suffix

            new_name = f"{normalize_title(file_name)}{file_extension}"

            try:
                file_path.rename(folder.joinpath(new_name))
                print(f"Arquivo '{file_path.name}' renomeado para '{new_name}'")
            except Exception as e:
                print(f"Ocorreu um erro ao tentar renomear o arquivo '{file_path.name}': {e}")

if __name__ == "__main__":
    folder_path = input("Digite o caminho da pasta que contém as imagens que deseja renomear: ")
    rename_images(folder_path)
