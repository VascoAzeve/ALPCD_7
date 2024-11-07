import typer
import requests
from datetime import datetime
from time import sleep

app = typer.Typer()

url = "https://api.itjobs.pt/job/search.json"
api_key = "422295b885ee1bc7fa94f330fbe85de2"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

@app.command()
def skills(skills: list[str], data_inicial: str, data_final: str):
    skill_query = ",".join(skills)
    data_inicial_dt = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final_dt = datetime.strptime(data_final, "%Y-%m-%d")

    page = 1
    encontrou_vaga = False

    while True:
        params = {
            "api_key": api_key,
            "q": skill_query,
            "page": page,
            "limit": 999
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            typer.echo(f"Erro na requisição: {e}")
            raise typer.Exit(code=1)

        try:
            data = response.json()
        except ValueError:
            typer.echo("Erro: Resposta não está em formato JSON.")
            raise typer.Exit(code=1)

        # Se não houver resultados, pare o loop
        if "results" not in data or not data["results"]:
            typer.echo("Nenhuma vaga encontrada em páginas adicionais.")
            break

        # Processa cada resultado
        for job in data["results"]:
            published_at_str = job.get("publishedAt", "N/A")
            try:
                published_at_dt = datetime.strptime(published_at_str, "%Y-%m-%d %H:%M:%S")
                if data_inicial_dt <= published_at_dt <= data_final_dt:
                    encontrou_vaga = True
                    title = job.get("title", "N/A")
                    company = job.get("company", "N/A")
                    location = job.get("location", "N/A")
                    description = job.get("description", "N/A")

                    typer.echo(f"Title: {title}")
                    typer.echo(f"Company: {company}")
                    typer.echo(f"Location: {location}")
                    typer.echo(f"Description: {description}")
                    typer.echo(f"Published At: {published_at_str}")
                    typer.echo("-" * 40)
            except ValueError:
                typer.echo(f"Data inválida ou em formato inesperado: {published_at_str}")
                continue

        page += 1
        sleep(0.5)  # Intervalo entre requisições para evitar limite da API (ajuste se necessário)

    if not encontrou_vaga:
        typer.echo("Estas são as vagas encontrada com as skills e datas informadas.")

if __name__ == "__main__":
    app()
