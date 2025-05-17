import subprocess
import time
import os

# Configurações de SSH
server_user = "root"
server_ip = "144.76.99.247"
remote_script_path = "monitor_resources.py"
remote_python_path = "python3"

def run_test(duration, threads, ramp_time, database, query_type):
    print("\n🛰️ Iniciando monitoramento remoto no servidor...")

    # Inicia o monitoramento com duracao limitada (test_duration)
    ssh_command = (
        f'ssh {server_user}@{server_ip} '
        f'"tcc && '
        f'systemctl {'restart postgresql && sudo systemctl stop mongod' if database == 'pg' else 'restart mongod && sudo systemctl stop postgresql'} && {remote_python_path} {remote_script_path} '
        f'--duration {duration} --threads {threads} --ramp {ramp_time} '
        f'--database {database} --type {query_type}" &'
    )
    subprocess.run(ssh_command, shell=True)

    print("⏳ Aguardando inicialização do monitoramento...")
    time.sleep(5)

    print("🚀 Executando teste de carga com JMeter...")
    database_folder_name = "postgres" if database == "pg" else "mongo"
    jmx_file = f'./test-plans/{database_folder_name}/{database}-{query_type}-workload.jmx'
    output_dir = f'./output/{database}/{duration}_seconds_duration/{ramp_time}_seconds_ramp/{threads}_threads/{query_type}_workload'
    web_dir = f'./web/{database}/{duration}_seconds_duration/{ramp_time}_seconds_ramp/{threads}_threads/{query_type}_workload'

    if os.path.exists(output_dir):
        subprocess.run(["rm", "-rf", output_dir])
    if os.path.exists(web_dir):
        subprocess.run(["rm", "-rf", web_dir])
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(web_dir, exist_ok=True)

    jmeter_cmd = [
        "jmeter",
        "-n",
        "-t", jmx_file,
        "-l", f"{output_dir}/results.csv",
        "-e",
        "-o", web_dir,
        f"-Jduration={duration}",
        f"-Jnumber_of_threads={threads}",
        f"-Jramp_time={ramp_time}"
    ]

    subprocess.run(jmeter_cmd)
    print("✅ Teste finalizado com sucesso!")


if __name__ == "__main__":
    test_scenarios = [
        # PostgreSQL
        (1800, 100, 60, 'pg', 'insert'),
        (1800, 100, 60, 'pg', 'read'),
        (1800, 100, 60, 'pg', 'update'),
        (1800, 100, 60, 'pg', 'mixed'),

        (1800, 200, 120, 'pg', 'insert'),
        (1800, 200, 120, 'pg', 'read'),
        (1800, 200, 120, 'pg', 'update'),
        (1800, 200, 120, 'pg', 'mixed'),

        (1800, 400, 240, 'pg', 'insert'),
        (1800, 400, 240, 'pg', 'read'),
        (1800, 400, 240, 'pg', 'update'),
        (1800, 400, 240, 'pg', 'mixed'),

        # MongoDB
        (1800, 100, 60, 'mongo', 'insert'),
        (1800, 100, 60, 'mongo', 'read'),
        (1800, 100, 60, 'mongo', 'update'),
        (1800, 100, 60, 'mongo', 'mixed'),

        (1800, 200, 120, 'mongo', 'insert'),
        (1800, 200, 120, 'mongo', 'read'),
        (1800, 200, 120, 'mongo', 'update'),
        (1800, 200, 120, 'mongo', 'mixed'),

        (1800, 400, 240, 'mongo', 'insert'),
        (1800, 400, 240, 'mongo', 'read'),
        (1800, 400, 240, 'mongo', 'update'),
        (1800, 400, 240, 'mongo', 'mixed'),
    ]

    for i, (duration, threads, ramp_time, database, query_type) in enumerate(test_scenarios):
        print(f"\n--- Running Test {i+1}/{len(test_scenarios)} ---")
        run_test(duration, threads, ramp_time, database, query_type)

        if i < len(test_scenarios) - 1:
            print("⏸️ Aguardando 5 minutos antes do próximo teste...")
            time.sleep(300)

    print("🎉 Todos os testes foram executados!")