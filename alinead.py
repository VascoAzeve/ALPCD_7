import typer
import requests
import csv
from datetime import datetime

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
                    title = job.get("title", "N/A")
                    company = job.get("company", "N/A")
                    description = " ".join(company.get("description", "N/A").splitlines()).strip()
                    locations = job.get("locations", "N/A")
                    if locations != "N/A":
                        location_name = locations[0].get("name", "N/A")
                    else:
                        location_name = locations
                    wage = job.get("wage", "N/A") or "N/A"

                    typer.echo(f"Title: {title}")
                    typer.echo(f"Company: {company['name']}")
                    typer.echo(f"Location: {location_name}")
                    typer.echo(f"Description: {description}")
                    typer.echo(f"Published At: {published_at_str}")
                    typer.echo(f"Wage: {wage}")
                    typer.echo("-" * 40)

                    #guardar vaga para o csv
                    vagas.append({
                        "titulo": title,
                        "empresa": company["name"],
                        "descricao": description,
                        "data_publicacao": published_at_str,
                        "salario": wage,
                        "localizacao": location_name
                    })

            except ValueError:
                typer.echo(f"Data inválida ou em formato inesperado: {published_at_str}")
                continue

        page += 1

    if not encontrou_vaga:
        typer.echo("Nenhuma vaga encontrada com as skills e datas informadas.")

    guardar_csv = input("Deseja guardar as vagas em um arquivo CSV? (1 para guardar; 2 para não guardar)")
    while True: 
        if guardar_csv == "1":
            with open("vagas_por_skills.csv", mode="a", newline='', encoding="utf-8") as csvfile:
                fieldnames = ["titulo", "empresa", "descricao", "data_publicacao", "salario", "localizacao"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(vagas)
            typer.echo("Vagas exportadas para o arquivo 'vagas_filtradas.csv'.")
            break
        elif guardar_csv == "2": 
            break
        else: 
            guardar_csv = input("Opção inválida. Por favor, digite 1 para guardar e 2 para não guardar.")
        

if __name__ == "__main__":
    app()
