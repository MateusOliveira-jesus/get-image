import os

def rename_images_in_folder(folder_path):
    # Verifica se o caminho é válido
    if not os.path.isdir(folder_path):
        print(f"O caminho '{folder_path}' não é uma pasta válida.")
        return
    
    # Obtém o nome da pasta
    folder_name = os.path.basename(os.path.normpath(folder_path))
    
    # Lista todos os arquivos na pasta
    files = os.listdir(folder_path)
    
    # Extensões de imagem comuns
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp']
    
    # Filtra apenas arquivos de imagem
    images = [f for f in files if any(f.lower().endswith(ext) for ext in image_extensions)]
    
    # Ordena as imagens para manter a consistência
    images.sort()
    
    # Renomeia os arquivos
    for i, image in enumerate(images, start=1):
        # Obtém a extensão do arquivo
        file_extension = os.path.splitext(image)[1].lower()
        
        # Construir o novo nome com o nome da pasta e um índice de dois dígitos
        new_name = f"{folder_name}-{i:02d}{file_extension}"
        
        # Caminho completo dos arquivos antigo e novo
        old_file_path = os.path.join(folder_path, image)
        new_file_path = os.path.join(folder_path, new_name)
        
        # Renomeia o arquivo
        os.rename(old_file_path, new_file_path)
        
        print(f"Renomeado '{old_file_path}' para '{new_file_path}'")

if __name__ == "__main__":
    folder_path = input("Digite o caminho da pasta onde estão as imagens: ").strip()
    rename_images_in_folder(folder_path)
