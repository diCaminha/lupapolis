import json

import requests
import base64
import io
from PIL import Image
import pdf2image
from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import date

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))
modelo = "gpt-4o"

def process_file(url):
    response = requests.get(url)
    response.raise_for_status()

    # Verifica o tipo do arquivo pela header ou pela extensão
    content_type = response.headers.get('content-type', '')
    if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
        # Converte PDF para imagem (primeira página)
        images = pdf2image.convert_from_bytes(response.content)
        image = images[0]
    else:
        # Trata como imagem
        image = Image.open(io.BytesIO(response.content))

    # Converte a imagem para bytes (formato PNG)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    # Codifica os bytes da imagem em Base64
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    return img_base64


def ask_gpt_about_image(img_base64, question):
    messages = [
        {"role": "system", "content": "Você é um excelente analisador de imagens de comprovantes de despesas e identificador de anomalia em gastos de verbas de deputados federais do brasil."},
        {"role": "user", "content": f"Pergunta: {question}\nImagem (base64): {img_base64}"}
    ]

    response = client.chat.completions.create(
        model=modelo,
        temperature=0.1,
        messages=messages
    )
    return json.loads(response.choices[0].message.content)


def ask_gpt_about_expense(question):
    messages = [
        {"role": "system", "content": "Você é um excelente analisador de despesas e identificador de anomalia em gastos com verbas de deputados federais dom brasil."},
        {"role": "user", "content": f"Pergunta: {question}"}
    ]

    response = client.chat.completions.create(
        model=modelo,
        temperature=0.1,
        messages=messages
    )
    return json.loads(response.choices[0].message.content)


def run_llm(despesa):
    pergunta = f""""
                Analise essa despesa para verificar se há a possibilidade de anomalia ou erro nessa despesa.
                info sobre a despesa: {despesa}
                deve ser analisado o valor pago na despesa (valorLiquido) e o tipo da despesa, verificando se faz sentido esse valor para esse tipo.
                Segue a imagem do comprovante da despesa. Caso nao contenham a imagem, leve em conta apenas nos dados da despesa informados.
                porém se a imagem existir, analise se está tudo ok com o comprovante, se há algo estranho com os valores e descrições.
                Não é pra analisar nada alem dessas coisas que informei.
                Expected output:
                Quero que voce responda no formato json com apenas as informacoes 
                "is_anomaly" => true ou false 
                "description" => explicação do seu parecer dando detalhes da analise.  
                
                Por favor, ao gerar a resposta, evite inserir caracteres de formatação ou delimitação, como as marcações de bloco (ex.: ``` ou ''' ou quebra de linha), e retorne o conteúdo sem essas formatações adicionais
                """
    pergunta_sem_image = f""""
        Analise a seguinte despesa para identificar se há evidências de erro ou anomalia. Considere os itens abaixo:
- Valor pago (valorLiquido): verifique se o valor é compatível com o esperado para o tipo da despesa.
- Tipo da despesa: confirme se o valor condiz com o tipo informado.
- Data do documento: valide se a data do documento (dataDocumento) corresponde ao ano e mês da despesa, considerando que a data de hoje é {date.today()} – use essa data como referência para evitar análises equivocadas sobre datas futuras.
- Campo urlDocumento: verifique se este campo está preenchido. Caso não esteja, inclua essa observação na descrição, mas sem necessariamente considerar como uma anomalia.

Apenas classifique a despesa como anômala ("is_anomaly": true) se houver evidências extremamente fortes (pelo menos 90% de certeza) de que algo está errado. Se não houver esse alto grau de certeza, retorne "is_anomaly": false.

Responda estritamente no formato JSON com as seguintes chaves:
"is_anomaly": true ou false  
"description": explicação detalhada da análise, mencionando os itens verificados e quaisquer observações relevantes.

Por favor, não utilize caracteres de formatação ou delimitação (como ``` ou ''' ou quebras de linha extras) na resposta.
Despesa: {despesa}

        """
    result = ask_gpt_about_expense(pergunta_sem_image)

    return result
