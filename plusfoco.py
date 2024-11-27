import os
import time
import threading

class Cliente:
    def __init__(self, nome):
        self.nome = nome

class Compra:
    def __init__(self, cliente, valor_itens):
        self.cliente = cliente
        self.valor_itens = valor_itens

# Variáveis globais
pomodoro_running = False
pomodoro_paused = False
pomodoro_lock = threading.Lock()
carteira = 0.0

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def carregar_carteira():
    global carteira
    try:
        with open("carteira.txt", "r") as arquivo:
            carteira = float(arquivo.read().strip())
            print(f"\nSaldo carregado: \033[1;32mR${carteira:.2f}\033[0m")
    except FileNotFoundError:
        print("\n\033[1;33mNenhum saldo encontrado, iniciando com R$0.00.\033[0m")
    except ValueError:
        print("\n\033[1;31mErro ao ler o saldo, iniciando com R$0.00.\033[0m")

def salvar_carteira():
    global carteira
    with open("carteira.txt", "w") as arquivo:
        arquivo.write(f"{carteira:.2f}")

def pomodoro_timer():
    global pomodoro_running, pomodoro_paused, carteira
    while pomodoro_running:
        print("\n\033[1;34mPomodoro iniciado! Ciclo: 25 minutos de trabalho e 5 minutos de descanso.\033[0m")
        print("\033[1;33mPressione 's' e confirme em seguida para sair.\nOBS: Os Pontos resgatados no relógio pomodoro são de 10 por minuto.\n\033[0m")
        for minutes, label in [(25, "Trabalho"), (5, "Descanso")]:
            for second in range(minutes * 60, 0, -1):
                with pomodoro_lock:
                    if not pomodoro_running:
                        return
                    while pomodoro_paused:
                        time.sleep(1)
                    mins, secs = divmod(second, 60)
                    print(f"{label} - Tempo restante: {mins:02d}:{secs:02d}", end="\r", flush=True)
                    if secs == 0 and label == "Trabalho":
                        carteira += 10.0
                        salvar_carteira()  # Salva o novo saldo ao final de cada ciclo de trabalho
                    time.sleep(1)
        print("\n\033[1;32mCiclo completo! Reiniciando Pomodoro...\033[0m")

def pomodoro_menu():
    global pomodoro_running, pomodoro_paused
    if not pomodoro_running:
        pomodoro_running = True
        threading.Thread(target=pomodoro_timer, daemon=True).start()
    else:
        print("\033[1;33mO Pomodoro já está em execução.\033[0m")

    while pomodoro_running:
        cmd = input("\nComando (s: sair): ").lower()
        if cmd == 's':
            with pomodoro_lock:
                pomodoro_running = False
            print("\033[1;31mPomodoro encerrado. Voltando ao Menu Principal.\033[0m")
            break

def cadastrar_recompensas():
    num_recompensas = int(input("\033[1;36mQuantas Recompensas deseja cadastrar?\033[0m "))
    while num_recompensas <= 0:
        print("\033[1;31mQuantidade inválida. Insira um valor maior que zero.\033[0m")
        num_recompensas = int(input("Quantas Recompensas deseja cadastrar? "))

    with open("registros.txt", "a") as bd:
        for i in range(num_recompensas):
            print(f"\n\033[1;35mProsseguindo para a Recompensa {i + 1} de {num_recompensas}.\033[0m")
            nome = input("\nExemplo: Jogar por 15 minutos\nInsira a Recompensa: ").strip()
            while len(nome) < 3:
                print("\033[1;31mNome inválido. Mínimo 3 caracteres.\033[0m")
                nome = input("Insira a Recompensa: ").strip()

            valor_itens = float(input("\n\033[1;33mOBS: Os Pontos resgatados no relógio pomodoro são de 10 por minuto.\nInsira o valor de Resgate: R$\033[0m"))
            while valor_itens <= 0:
                print("\033[1;31mValor inválido.\033[0m")
                valor_itens = float(input("Insira o valor de Resgate: R$"))

            cliente = Cliente(nome)
            compra = Compra(cliente, valor_itens)

            bd.write(f"{cliente.nome} {compra.valor_itens:.2f}\n")
            print(f"\033[1;32mCadastro efetivado para a Recompensa {i + 1} de {num_recompensas}!\033[0m\n")

def mostrar_todas_recompensas():
    print("\n==== \033[1;36mRecompensas Disponíveis\033[0m ====\n")
    try:
        with open("registros.txt", "r") as bd:
            linhas = bd.readlines()
            if linhas:
                for i, linha in enumerate(linhas, start=1):
                    *nome_parts, valor = linha.strip().split()
                    nome = " ".join(nome_parts)
                    print(f"{i}. Recompensa: {nome} | Valor: R${valor}")
            else:
                print("\033[1;33mNenhuma recompensa cadastrada.\033[0m")
    except FileNotFoundError:
        print("\033[1;33mNenhuma recompensa cadastrada.\033[0m")
    print("\n=========================================")

def resgatar_recompensa():
    global carteira
    try:
        with open("registros.txt", "r") as bd:
            linhas = bd.readlines()
            if not linhas:
                print("\n\033[1;33mNenhuma recompensa disponível para resgate.\033[0m\n")
                return
            print(f"\n==== \033[1;36mCarteira de Pontos\033[0m ====\n\nSaldo atual: \033[1;32mR${carteira:.2f}\033[0m\n\n===========================")
            recompensas = []
            for i, linha in enumerate(linhas, start=1):
                *nome_parts, valor = linha.strip().split()
                nome = " ".join(nome_parts)
                recompensas.append((nome, float(valor)))
                print(f"{i}. {nome} | R${valor}")
            escolha = input("\nDigite o número da recompensa ou 'c' para cancelar: ").strip().lower()
            if escolha == 'c':
                print("\n\033[1;33mResgate cancelado.\033[0m")
                return
            escolha_idx = int(escolha) - 1
            nome_resgate, valor_resgate = recompensas[escolha_idx]
            if carteira < valor_resgate:
                print(f"\n\033[1;31mSaldo insuficiente! Sua carteira possui R${carteira:.2f}.\033[0m\n")
                return
            confirmar = input(f"\nConfirma o resgate de '{nome_resgate}'? (s/n): ").strip().lower()
            if confirmar == 's':
                carteira -= valor_resgate
                salvar_carteira()
                del linhas[escolha_idx]
                with open("registros.txt", "w") as bd:
                    bd.writelines(linhas)
                print(f"\n\033[1;32mResgate realizado! Saldo Atualizado: R${carteira:.2f}\033[0m")
            else:
                print("\n\033[1;33mResgate cancelado.\033[0m\n")
    except FileNotFoundError:
        print("\n\033[1;33mNenhuma recompensa cadastrada.\033[0m\n")
    except Exception as e:
        print(f"\n\033[1;31mErro: {e}\033[0m\n")

def main():
    carregar_carteira()
    while True:
        print("\n======\t\033[1;36m+ FOCO\033[0m\t======\n")
        print("1 - Cadastro de Recompensas;")
        print("2 - Mostrar todas as Recompensas;")
        print("3 - Resgate de Recompensas;")
        print("4 - Relógio Pomodoro;")
        print("5 - Sair;")
        print(f"\n==== \033[1;36mCarteira de Pontos\033[0m ====\n\nSaldo atual: \033[1;32mR${carteira:.2f}\033[0m\n\n===========================")
        op_menu = input("\nInsira a sua opção: ").strip()
        limpar_terminal()

        if op_menu == '1':
            cadastrar_recompensas()
        elif op_menu == '2':
            mostrar_todas_recompensas()
        elif op_menu == '3':
            resgatar_recompensa()
        elif op_menu == '4':
            pomodoro_menu()
        elif op_menu == '5':
            if input("Tem certeza que quer sair? (s/n): ").strip().lower() == 's':
                salvar_carteira()
                print("\n\033[1;32mSistema Encerrado.\033[0m")
                break
        else:
            print("\033[1;31mOpção inválida.\033[0m")

if __name__ == "__main__":
    main()

