import os
import cv2
import time
import json

from paddleocr import PaddleOCR
from deep_translator import GoogleTranslator

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import enums

# ==================================================
# CONFIGURAÇÕES DO PROJETO
# ==================================================

# Pasta onde estão as imagens que serão processadas
PASTA_IMAGENS = "imgs"

# Pasta onde os PDFs finais serão salvos
PASTA_SAIDA = "output"

# Idioma base esperado pelo OCR
IDIOMA_OCR = "en"

# Garante que a pasta de saída exista
os.makedirs(PASTA_SAIDA, exist_ok=True)


# ==================================================
# OCR (RECONHECIMENTO DE TEXTO NA IMAGEM)
# ==================================================

def inicializar_ocr():
    """
    Inicializa o modelo PaddleOCR apenas uma vez
    para melhorar performance.
    """

    print("\nInicializando PaddleOCR...\n")

    return PaddleOCR(
        use_angle_cls=True,  # Corrige textos inclinados/rotacionados
        lang=IDIOMA_OCR      # Otimiza para idioma inglês
    )


def extrair_blocos(ocr, caminho_imagem):
    """
    Executa OCR na imagem e retorna blocos de texto com posição.
    """

    # Lê imagem com OpenCV
    imagem = cv2.imread(caminho_imagem)

    # Validação: imagem precisa existir
    if imagem is None:
        raise FileNotFoundError(f"Imagem inválida ou corrompida: {caminho_imagem}")

    # Executa OCR
    resultado = ocr.ocr(imagem, cls=True)

    # Caso OCR não retorne nada
    if not resultado or not resultado[0]:
        return []

    blocos = []

    # Percorre todos os textos detectados
    for item in resultado[0]:

        # Bounding box do texto (coordenadas)
        bbox = item[0]

        # Texto reconhecido
        texto = item[1][0]

        # Confiança do OCR (0 a 1)
        confianca = item[1][1]

        # Coordenada Y superior (usada para ordenar leitura)
        y_top = min(p[1] for p in bbox)

        blocos.append({
            "texto": texto,
            "y": y_top,
            "confianca": confianca
        })

    return blocos


# ==================================================
# AGRUPAMENTO DE TEXTO EM PARÁGRAFOS
# ==================================================

def agrupar_paragrafos(blocos):
    """
    Agrupa linhas detectadas pelo OCR em parágrafos
    com base na proximidade vertical.
    """

    # Ordena blocos de cima para baixo
    blocos.sort(key=lambda x: x["y"])

    paragrafos = []
    paragrafo_atual = ""
    ultimo_y = None

    # Distância máxima para considerar mesma linha/parágrafo
    DISTANCIA_MAXIMA = 18

    for bloco in blocos:

        texto = bloco["texto"]
        y = bloco["y"]

        # Primeiro elemento
        if ultimo_y is None:
            paragrafo_atual = texto

        # Se estiver próximo verticalmente, junta no mesmo parágrafo
        elif abs(y - ultimo_y) <= DISTANCIA_MAXIMA:
            paragrafo_atual += " " + texto

        # Caso contrário, inicia novo parágrafo
        else:
            paragrafos.append(paragrafo_atual)
            paragrafo_atual = texto

        ultimo_y = y

    # Adiciona último parágrafo
    if paragrafo_atual:
        paragrafos.append(paragrafo_atual)

    return paragrafos


# ==================================================
# TRADUÇÃO AUTOMÁTICA
# ==================================================

def traduzir_paragrafos(paragrafos):
    """
    Traduz cada parágrafo para português usando GoogleTranslator.
    Usa cache para evitar traduções repetidas.
    """

    cache = {}
    resultado = []

    for texto in paragrafos:

        texto = texto.strip()

        # Ignora textos muito curtos
        if len(texto) < 2:
            continue

        # Cache evita chamadas repetidas
        if texto in cache:
            traducao = cache[texto]

        else:
            try:
                traducao = GoogleTranslator(source="auto", target="pt").translate(texto)

            except:
                # fallback: mantém original caso falhe
                traducao = texto

            cache[texto] = traducao

        resultado.append({"original": texto,"traducao": traducao})

        print(f"✓ Tradução: {traducao[:60]}")

    return resultado




# ==================================================
# GERAÇÃO DE PDF
# ==================================================

def gerar_pdf(nome_arquivo, traducoes):
    """
    Gera um PDF final com os textos traduzidos e refinados.
    """

    pdf_saida = os.path.join(PASTA_SAIDA, f"{nome_arquivo}_traduzido.pdf")

    # Cria estrutura do PDF
    doc = SimpleDocTemplate(pdf_saida)

    # Estilos padrão do ReportLab
    styles = getSampleStyleSheet()

    # Estilo de título
    titulo_style = styles["Heading2"]
    titulo_style.alignment = enums.TA_CENTER

    # Estilo de texto normal
    texto_style = styles["BodyText"]
    texto_style.leading = 18  # espaçamento entre linhas

    conteudo = []

    for item in traducoes:

        texto = item["traducao"].strip()

        # Heurística simples para detectar título
        eh_titulo = (len(texto.split()) <= 5 or texto.isupper())

        if eh_titulo:
            conteudo.append(Paragraph(texto, titulo_style))
        else:
            conteudo.append(Paragraph(texto, texto_style))

        # Espaço entre blocos
        conteudo.append(Spacer(1, 10))

    # Gera PDF final
    doc.build(conteudo)

    return pdf_saida


#===================================================
# GERANDO UM ARQUIVO JSON
#===================================================

def gerar_json(nome_arquivo, traducoes):

    # Cria um arquivo JSON contendo texto original e texto traduzido

    caminho_json = os.path.join(PASTA_SAIDA, f"{nome_arquivo}.json")

    with open(caminho_json, "w", encoding="utf-8") as arquivo:
        json.dump(traducoes, arquivo, ensure_ascii=False, indent=4)

    return caminho_json


# ==================================================
# PIPELINE PRINCIPAL
# ==================================================

def processar_documento(ocr, caminho_imagem):
    """
    Pipeline completo para uma imagem:
    OCR → Agrupamento → Tradução → PDF
    """

    inicio = time.time()

    nome = os.path.splitext(os.path.basename(caminho_imagem))[0]

    print("\n============================================================")
    print(f"Processando: {nome}")
    print("============================================================")

    # 1. OCR
    blocos = extrair_blocos(ocr, caminho_imagem)

    # 2. Agrupamento de linhas em parágrafos
    paragrafos = agrupar_paragrafos(blocos)

    # 3. Tradução automática
    traducoes = traduzir_paragrafos(paragrafos)

    # 4. Geração do JSON 
    json = gerar_json(nome,traducoes)

    # 5. Geração do PDF final
    pdf = gerar_pdf(nome, traducoes)


    print(f"PDF gerado: {pdf}")
    print(f"Tempo: {time.time() - inicio:.2f}s")


# ==================================================
# MAIN
# ==================================================

def main():
    """
    Executa o sistema para todas as imagens da pasta.
    """

    inicio_total = time.time()

    # Inicializa OCR uma única vez (otimização importante)
    ocr = inicializar_ocr()

    # Filtra imagens válidas
    imagens = [
        arquivo for arquivo in os.listdir(PASTA_IMAGENS)
        if arquivo.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    # Caso não existam imagens
    if not imagens:
        print("Nenhuma imagem encontrada.")
        return

    # Processa cada imagem individualmente
    for imagem in imagens:
        caminho = os.path.join(PASTA_IMAGENS, imagem)
        processar_documento(ocr, caminho)

    print("\nPROCESSAMENTO FINALIZADO")
    print(f"Tempo total: {time.time() - inicio_total:.2f}s")


# Executa o programa
if __name__ == "__main__":
    main()