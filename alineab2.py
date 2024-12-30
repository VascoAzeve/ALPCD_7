import requests
import csv
import typer

app = typer.Typer()
api_key = "422295b885ee1bc7fa94f330fbe85de2"

headers_api = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

# 2 b)  estatisticas zona cargo nr
def save_statistics(data):
    stats = {}

    for job in data:
        zone = job.get("locations", [{"name": "Desconhecida"}])[0]["name"]
        job_type = job.get("title", "Desconhecido")

        if zone not in stats:
            stats[zone] = {}

        if job_type not in stats[zone]:
            stats[zone][job_type] = 0

        stats[zone][job_type] += 1

    return stats

# 2 b) guardar csv
def save_detailed_to_csv(stats, filename="job_statistics.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Cabeçalho com 3 colunas
        writer.writerow(["Zona", "Tipo de Trabalho", "Nº de vagas"])

        # Iterar pelos dados detalhados e escrever no CSV
        for zone, job_types in stats.items():
            for job_type, count in job_types.items():
                writer.writerow([zone, job_type, count])

    print(f"Ficheiro de exportação criado com sucesso: {filename}")

# 2 b) comando csv estatisticas
@app.command()
def statistics():
    print("A guardar dados de trabalho...")
    page = 1
    all_jobs = []

    while True:
        url = "https://api.itjobs.pt/job/search.json"
        params = {
            "api_key": api_key,
            "page": page,
        }

        try:
            response = requests.get(url, params=params, headers=headers_api)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            typer.echo(f"Erro na requisição: {e}")
            raise typer.Exit(code=1)

        data = response.json()

        # Verifique se 'results' está presente na resposta e se não está vazio
        if 'results' not in data or not data['results']:
            break

        all_jobs.extend(data['results'])
        page += 1

    
    print("Guardar estatísticas detalhadas...")
    stats = save_statistics(all_jobs)
    save_detailed_to_csv(stats)

    print("Ficheiro csv criado com sucesso!")

if __name__ == "__main__":
    app()