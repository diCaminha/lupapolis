import csv
import requests

from teste import run_model


class Despesa:
    def __init__(self, ano, mes, tipoDespesa, codDocumento, tipoDocumento, codTipoDocumento,
                 dataDocumento, numDocumento, valorDocumento, urlDocumento, nomeFornecedor,
                 cnpjCpfFornecedor, valorLiquido, valorGlosa, numRessarcimento, codLote, parcela):
        self.ano = ano
        self.mes = mes
        self.tipoDespesa = tipoDespesa
        self.codDocumento = codDocumento
        self.tipoDocumento = tipoDocumento
        self.codTipoDocumento = codTipoDocumento
        self.dataDocumento = dataDocumento
        self.numDocumento = numDocumento
        self.valorDocumento = valorDocumento
        self.urlDocumento = urlDocumento
        self.nomeFornecedor = nomeFornecedor
        self.cnpjCpfFornecedor = cnpjCpfFornecedor
        self.valorLiquido = valorLiquido
        self.valorGlosa = valorGlosa
        self.numRessarcimento = numRessarcimento
        self.codLote = codLote
        self.parcela = parcela


class Deputado:
    def __init__(self, id, name, urlPhoto, email):
        self.id = id
        self.name = name
        self.urlPhoto = urlPhoto
        self.email = email

    def __str__(self):
        return f"Deputado {self.id}: {self.name} ({self.urlPhoto})"


def get_deputados_data_from_file():
    deputados = []
    filename = 'files/deputados.csv'  # Replace with your CSV file name or path
    with open(filename, mode='r', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            deputado = Deputado(
                id=row['id'],
                name=row['nome'],
                urlPhoto=row['urlFoto'],
                email=row['email']
            )
            deputados.append(deputado)

    for deputado in deputados:
        url_despesas = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{deputado.id}/despesas?ordem=desc&ordenarPor=dataDocumento"
        try:
            response = requests.get(url_despesas)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Parse JSON payload
            content = response.json()
            despesas = content["dados"]

            for despesa in despesas:
                run_model(despesa)
                return

        except requests.RequestException as error:
            print("An error occurred while fetching data:", error)

if __name__ == '__main__':
    get_deputados_data_from_file()