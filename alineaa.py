import typer
import requests
import json

app = typer.Typer()

url = "https://api.itjobs.pt/job/list.json"
api_key = "422295b885ee1bc7fa94f330fbe85de2"

# Adicionando um valor padrão ao User-Agent
headers = {
    "User-Agent": "job-cli/1.0"
}

@app.command()
def trabalhos(limite: int):
    """
    Lista os N trabalhos mais recentes publicados.
    """
    # Verifica se o limite é válido
    if limite <= 0:
        typer.echo("O limite deve ser um número positivo.")
        raise typer.Exit(code=1)

    # Monta os parâmetros da requisição
    params = {
        "api_key": api_key,
        "limit": limite,
    }

    try:
        # Faz a requisição para a API
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Verifica se ocorreu algum erro na requisição

    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro de conexão: {e}")
        raise typer.Exit(code=1)

    # Converte a resposta JSON para um dicionário
    try:
        data = response.json()
    except json.JSONDecodeError:
        typer.echo("Erro ao decodificar a resposta JSON.")
        raise typer.Exit(code=1)

    # Verifica se existem resultados
    if "results" not in data or not data["results"]:
        typer.echo("Nenhuma vaga encontrada.")
        return

    # Exibe as informações de cada vaga
    for job in data["results"]:
        title = job.get("title", "N/A")
        company = job.get("company", "N/A")
        location = job.get("location", "N/A")
        description = job.get("description", "N/A")
        publishedAt = job.get("publishedAt", "N/A")

        # Exibe as informações formatadas
        typer.echo(f"Title: {title}")
        typer.echo(f"Company: {company}")
        typer.echo(f"Location: {location}")
        typer.echo(f"Description: {description}")
        typer.echo(f"Published At: {publishedAt}")
        typer.echo("-" * 40)  # Linha separadora

if __name__ == "__main__":
    app()
