import typer
import requests
import json

app = typer.Typer()

url = "https://api.itjobs.pt/job/search.json"
apikey = "422295b885ee1bc7fa94f330fbe85de2" 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}

@app.command()
def search(locality: str = typer.Argument(...), company: str = typer.Argument(...), limit: int = typer.Argument(...)):
    # Monta os parâmetros da requisição
    params = {
        "api_key": apikey,
        "q": company,  # Realiza busca pela empresa
        "limit": limit,  # Número de resultados a mostrar
        "page": 1,  # Página inicial (pode ser ajustada se necessário)
        "type": "1",  # Filtra apenas trabalhos Full-time (id 1 corresponde a Full-time)
        "contract": "2",  # Exclui outros contratos, filtrando para contratos sem termo
    }

    # Adiciona o filtro de localidade, se fornecido
    if locality:
        params["location"] = locality

    # Faz a requisição para a API
    response = requests.get(url, params=params, headers=headers)

    # Verifica o status da resposta
    if response.status_code != 200:
        typer.echo(f"Erro na requisição: {response.status_code} - {response.text}")
        raise typer.Exit(code=1)

    # Converte a resposta JSON para um dicionário
    data = response.json()

    # Verifica se há resultados
    if "results" in data and len(data["results"]) > 0:
        # Exibe os resultados em formato JSON
        output = []
        for job in data["results"]:
            job_data = {
                "id": job.get("id", "N/A"),
                "company": job.get("company", {}).get("name", "N/A"),
                "title": job.get("title", "N/A"),
                "location": [loc["name"] for loc in job.get("locations", [])],  # Lista de localidades
                "publishedAt": job.get("publishedAt", "N/A"),
                "description": job.get("body", "N/A")
            }
            output.append(job_data)

        # Exibe os resultados no formato JSON
        typer.echo(json.dumps(output, indent=4))
    else:
        typer.echo("Nenhuma vaga encontrada para os critérios fornecidos.")

if __name__ == "__main__":
    app()