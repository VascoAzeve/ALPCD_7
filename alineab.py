import typer
import requests
import json

app = typer.Typer()

url = "https://api.itjobs.pt/job/search.json"
api_key = "422295b885ee1bc7fa94f330fbe85de2"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

@app.command()
def search(localidade: str, empresa: str, numero_trabalhos: int):
    # Definir os parâmetros da busca
    params = {
        "api_key": api_key,
        "q": empresa,
        "locations": localidade,
        "limit": numero_trabalhos,
        "full_time": "true"  # Filtra apenas vagas full-time
    }

    try:
        # Fazer a requisição à API
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro na requisição: {e}")
        raise typer.Exit(code=1)

    try:
        # Processar a resposta em formato JSON
        data = response.json()
    except ValueError:
        typer.echo("Erro: Resposta não está em formato JSON.")
        raise typer.Exit(code=1)

    # Verificar se há resultados
    if "results" not in data or not data["results"]:
        typer.echo(f"Não foram encontradas vagas para a empresa {empresa} na localidade {localidade}.")
        raise typer.Exit(code=1)

    # Filtrar as vagas e exibir no formato JSON
    vagas = []
    for job in data["results"]:
        job_data = {
            "titulo": job.get("title", "N/A"),
            "empresa": job.get("company", {}).get("name", "N/A"),
            "descricao": job.get("description", "N/A"),
            "data_publicacao": job.get("publishedAt", "N/A"),
            "localizacao": job.get("locations", [{}])[0].get("name", "N/A"),
            "salario": job.get("wage", "N/A")
        }
        vagas.append(job_data)

    # Exibir resultado em formato JSON
    typer.echo(json.dumps(vagas, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    app()
