import typer
import requests
import re

app = typer.Typer()

url = "https://api.itjobs.pt/job/get.json"
apikey = "422295b885ee1bc7fa94f330fbe85de2"

# Adicionando um valor padrão ao User-Agent
headers = {
    "User-Agent": "job-cli/1.0"
}

@app.command()
def salary(job_id: str):
    """
    Extrai o salário oferecido por um job_id específico.
    """

    # Monta a URL para o job específico

    params = {
        "api_key": apikey,
        "id": job_id,
    }

    try:
        # Faz a requisição para a API
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro de conexão: {e}")
        raise typer.Exit(code=1)

    # Converte a resposta JSON para um dicionário
    try:
        job_data = response.json()
    except json.JSONDecodeError:
        typer.echo("Erro ao decodificar a resposta JSON.")
        raise typer.Exit(code=1)

    # Verifica se existe o campo 'wage' e tenta extrair o salário
    wage = job_data.get("wage")
    if wage:
        typer.echo(wage)
    else:
        # Tenta extrair salário usando expressões regulares em outros campos
        description = job_data.get("description", "")
        # Procurar valores numéricos seguidos de "€" ou "euros"
        match = re.search(r"(\d{3,6})(?:\s?€|\s?euros?)", description, re.IGNORECASE)
        
        if match:
            salario_extraido = match.group(1)
            typer.echo(salario_extraido)
        else:
            typer.echo("Salário não especificado.")

if __name__ == "__main__":
    app()

