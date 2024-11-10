import typer
import requests
import csv
import re
from datetime import datetime

app = typer.Typer()
api_key = "422295b885ee1bc7fa94f330fbe85de2"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

def imprimir_vagas_guardar_csv(data, nome_comando):
    vagas = []
    for job in data["results"]:
        publishedAt = job.get("publishedAt", "N/A")
        title = job.get("title", "N/A")
        company = job.get("company", "N/A")
        description = " ".join(company.get("description", "N/A").splitlines()).strip()
        locations = job.get("locations", "N/A")
        if locations != "N/A":
            location_name = locations[0].get("name", "N/A")
        else:
            location_name = locations
        wage = job.get("wage", "N/A") or "N/A"

        typer.echo(f"Titulo: {title}")
        typer.echo(f"Empresa: {company['name']}")
        typer.echo(f"Localização: {location_name}")
        typer.echo(f"Descrição da empresa: {description}")
        typer.echo(f"Publicado em: {publishedAt}")
        typer.echo(f"Salário: {wage}")
        typer.echo("-" * 40)

        
        vagas.append({
            "titulo": title,
            "empresa": company["name"],
            "descricao": description,
            "data_publicacao": publishedAt,
            "salario": wage,
            "localizacao": location_name
        })

    guardar_csv = input("Deseja guardar as vagas em um arquivo CSV? (1 para guardar; 2 para não guardar)")
    while True: 
        if guardar_csv == "1":
            ficheiro = f"{nome_comando}.csv"
            with open(ficheiro, mode="a", newline='', encoding="utf-8") as csvfile:
                fieldnames = ["titulo", "empresa", "descricao", "data_publicacao", "salario", "localizacao"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(vagas)
            typer.echo(f"Vagas exportadas para o arquivo '{ficheiro}'.")
            break
        elif guardar_csv == "2": 
            break
        else: 
            guardar_csv = input("Opção inválida. Por favor, digite 1 para guardar e 2 para não guardar.")

#alinea a
@app.command()
def top(limite: int):
    url = "https://api.itjobs.pt/job/list.json"
    vagas = []
    if limite <= 0:
        typer.echo("O limite deve ser um número positivo.")
        raise typer.Exit(code=1)

    
    params = {
        "api_key": api_key,
        "limit": limite,
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

    if "results" not in data or not data["results"]:
        typer.echo("Nenhuma vaga encontrada.")
        return

    imprimir_vagas_guardar_csv(data, "job")

#alinea b
@app.command()
def search(localidade: str, empresa: str, numero_trabalhos: int):
    params = {
        "api_key": api_key,
        "q": empresa,
        "locations": localidade,
        "limit": numero_trabalhos,
        "full_time": "true"  #filtra apenas vagas full-time
    }

    url = "https://api.itjobs.pt/job/search.json"

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

    if "results" not in data or not data["results"]:
        typer.echo(f"Não foram encontradas vagas para a empresa {empresa} na localidade {localidade}.")
        raise typer.Exit(code=1)

    imprimir_vagas_guardar_csv(data, "search")

#alinea c
@app.command()
def salary(job_id: str):
    params = {
        "api_key": api_key,
        "id": job_id,
    }

    url = "https://api.itjobs.pt/job/get.json"

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
    

    wage = data.get("wage")
    if wage:
        typer.echo(wage)
    else:
        #tenta extrair salário usando expressões regulares em outros campos
        body = data.get("body", "")
        #procurar valores numéricos seguidos de "€" ou "euros"
        match = re.findall(r"(\d{1,3}(?:[.,]\d{3})*(?:-\d{1,3}(?:[.,]\d{3})*)?)\s?(€|euros?)", body, re.IGNORECASE)
        
        if match:
            #salario_extraido = match.group(1)
            typer.echo(match)
        else:
            typer.echo("Salário não especificado.")
            
#alinea d 
@app.command()
def skills(skills: list[str], data_inicial: str, data_final: str):
    url = "https://api.itjobs.pt/job/search.json"
    skill_query = ",".join(skills)
    data_inicial_dt = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final_dt = datetime.strptime(data_final, "%Y-%m-%d")

    page = 1
    encontrou_vaga = False
    vagas = []

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
            typer.echo("Estas são as vagas encontradas com as skills e datas informadas.")
            break

        # Processa cada resultado
        for job in data["results"]:
            published_at_str = job.get("publishedAt", "N/A")
            try:
                published_at_dt = datetime.strptime(published_at_str, "%Y-%m-%d %H:%M:%S")
                if data_inicial_dt <= published_at_dt <= data_final_dt:
                    encontrou_vaga = True
                    imprimir_vagas_guardar_csv(data, "skills")
            except ValueError:
                typer.echo(f"Data inválida ou em formato inesperado: {published_at_str}")
                continue
        page += 1
    if not encontrou_vaga:
        typer.echo("Nenhuma vaga encontrada com as skills e datas informadas.")

        
if __name__ == "__main__":
    app()
