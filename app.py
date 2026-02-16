from flask import Flask, render_template, request, redirect, jsonify
<<<<<<< HEAD
import random
from times import GerenciadorTimes
from database import Database
import atexit

=======
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
app = Flask(__name__)

TAMANHO_TIME = 7

<<<<<<< HEAD
# Inicializa o banco de dados
db = Database()

# Inicializa o gerenciador de times
gerenciador = GerenciadorTimes([], [], [], TAMANHO_TIME)

# Carrega dados do banco
fila, times = db.carregar_jogadores()
historico = db.carregar_historico()
contador_ordem, contador_partidas = db.carregar_estado()

# Atualiza o gerenciador com os dados carregados
gerenciador.fila = fila.copy()
if times[1] and times[2]:
    gerenciador.times = [times[1].copy(), times[2].copy()]

def sincronizar_com_gerenciador():
    """Sincroniza as variáveis locais com o gerenciador"""
    global fila, times
    
    if gerenciador.fila and isinstance(gerenciador.fila[0], dict):
        fila = gerenciador.fila.copy()
    else:
        fila = [{"nome": j, "ordem": i+1} for i, j in enumerate(gerenciador.fila)]
    
    if len(gerenciador.times) >= 2:
        if gerenciador.times[0] and isinstance(gerenciador.times[0][0], dict):
            times[1] = gerenciador.times[0].copy()
            times[2] = gerenciador.times[1].copy()
        else:
            times[1] = [{"nome": j, "ordem": i+1} for i, j in enumerate(gerenciador.times[0])]
            times[2] = [{"nome": j, "ordem": i+1+len(gerenciador.times[0])} for i, j in enumerate(gerenciador.times[1])]

def salvar_tudo():
    """Salva todo o estado no banco de dados"""
    try:
        db.salvar_jogadores(fila, times)
        db.salvar_estado(contador_ordem, contador_partidas)
        db.salvar_historico(historico)
        print("✅ Dados salvos com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")

# Registra função para salvar ao encerrar
atexit.register(salvar_tudo)

@app.route("/", methods=["GET", "POST"])
def index():
    global contador_ordem, fila, times, historico, contador_partidas
=======
fila = []
times = {1: [], 2: []}
historico = []
contador_ordem = 1
contador_partidas = 1

@app.route("/", methods=["GET", "POST"])
def index():
    global contador_ordem
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639

    if request.method == "POST":
        nome = request.form.get("nome")
        if nome:
<<<<<<< HEAD
            jogador_dict = {"nome": nome, "ordem": contador_ordem}
            contador_ordem += 1
            
            gerenciador.fila.append(jogador_dict)
            fila.append(jogador_dict)
            
            if len(fila) >= 14:
                jogadores_sorteados = fila[:14]
                random.shuffle(jogadores_sorteados)
                
                fila = fila[14:]
                gerenciador.fila = fila.copy()
                
                times[1] = jogadores_sorteados[:7]
                times[2] = jogadores_sorteados[7:]
                
                gerenciador.times = [times[1].copy(), times[2].copy()]
                
                historico.insert(0, {
                    "partida": contador_partidas,
                    "vencedor": [],
                    "perdedor": [],
                    "entrou": [],
                    "sorteio": True,
                    "time1": times[1].copy(),
                    "time2": times[2].copy()
                })
                
                contador_partidas += 1
            
            # Salva após cada modificação
            salvar_tudo()
            
        return redirect("/")

    return render_template("index.html", fila=fila, times=times, historico=historico, tamanho_time=TAMANHO_TIME)

@app.route("/perdeu/<int:time_perdedor>")
def perdeu(time_perdedor):
    global contador_partidas, fila, times, historico

    time_vencedor = 1 if time_perdedor == 2 else 2

    if len(times[time_perdedor]) != TAMANHO_TIME or len(times[time_vencedor]) != TAMANHO_TIME:
        return redirect("/")

    perdedor_snapshot = times[time_perdedor].copy()
    vencedor_snapshot = times[time_vencedor].copy()

    times[time_perdedor] = []
    entrou = []

    # Primeiro: puxa da fila
=======
            fila.append({"nome": nome, "ordem": contador_ordem})
            contador_ordem += 1
        return redirect("/")

    return render_template("index.html", fila=fila, times=times, historico=historico)

@app.route("/editar", methods=["POST"])
def editar():
    ordem = int(request.form["ordem"])
    novo_nome = request.form["nome"]

    for lista in [fila, times[1], times[2]]:
        for j in lista:
            if j["ordem"] == ordem:
                j["nome"] = novo_nome
                break

    return redirect("/")

@app.route("/drag", methods=["POST"])
def drag():
    ordem = int(request.form["ordem"])
    destino = int(request.form["destino"])

    if len(times[destino]) >= TAMANHO_TIME:
        return redirect("/")

    jogador = None
    for j in fila:
        if j["ordem"] == ordem:
            jogador = j
            fila.remove(j)
            break

    if jogador:
        times[destino].append(jogador)

    return redirect("/")

@app.route("/perdeu/<int:time_perdedor>")
def perdeu(time_perdedor):
    global contador_partidas

    time_vencedor = 1 if time_perdedor == 2 else 2

    perdedor_snapshot = times[time_perdedor].copy()
    vencedor_snapshot = times[time_vencedor].copy()

    if len(perdedor_snapshot) != TAMANHO_TIME or len(vencedor_snapshot) != TAMANHO_TIME:
        return redirect("/")

    times[time_perdedor] = []
    entrou = []

>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
    while len(times[time_perdedor]) < TAMANHO_TIME and fila:
        j = fila.pop(0)
        times[time_perdedor].append(j)
        entrou.append(j)
<<<<<<< HEAD
    
    # Segundo: completa com perdedores se necessário
    perdedores_ordenados = sorted(perdedor_snapshot, key=lambda x: x["ordem"])
    for j in perdedores_ordenados:
        if len(times[time_perdedor]) < TAMANHO_TIME:
            if j not in times[time_perdedor]:
                times[time_perdedor].append(j)
        else:
            if j not in times[time_perdedor]:
                fila.append(j)
    
    # Terceiro: perdedores restantes vão para fila
    for j in perdedor_snapshot:
        if j not in times[time_perdedor] and j not in fila:
            fila.append(j)
    
    fila.sort(key=lambda x: x["ordem"])
    
    # Atualiza gerenciador
    gerenciador.fila = fila.copy()
    if len(gerenciador.times) >= 2:
        gerenciador.times[time_perdedor-1] = times[time_perdedor].copy()
        gerenciador.times[time_vencedor-1] = times[time_vencedor].copy()
=======

    usados = set(j["ordem"] for j in times[time_perdedor])

    perdedores_ordenados = sorted(perdedor_snapshot, key=lambda x: x["ordem"])
    for j in perdedores_ordenados:
        if len(times[time_perdedor]) < TAMANHO_TIME:
            times[time_perdedor].append(j)
            usados.add(j["ordem"])

    for j in perdedor_snapshot:
        if j["ordem"] not in usados:
            fila.append(j)

    fila.sort(key=lambda x: x["ordem"])
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639

    historico.insert(0, {
        "partida": contador_partidas,
        "vencedor": vencedor_snapshot,
        "perdedor": perdedor_snapshot,
<<<<<<< HEAD
        "entrou": entrou,
        "sorteio": False
    })

    contador_partidas += 1
    
    # Salva após cada modificação
    salvar_tudo()
    
    if len(fila) >= 14:
        return redirect("/sortear-automatico")
    
    return redirect("/")

@app.route("/sortear-automatico")
def sortear_automatico():
    global fila, times, contador_partidas, historico
    
    if len(fila) >= 14:
        jogadores_sorteados = fila[:14]
        random.shuffle(jogadores_sorteados)
        
        fila = fila[14:]
        
        times[1] = jogadores_sorteados[:7]
        times[2] = jogadores_sorteados[7:]
        
        gerenciador.fila = fila.copy()
        gerenciador.times = [times[1].copy(), times[2].copy()]
        
        historico.insert(0, {
            "partida": contador_partidas,
            "vencedor": [],
            "perdedor": [],
            "entrou": [],
            "sorteio": True,
            "time1": times[1].copy(),
            "time2": times[2].copy()
        })
        
        contador_partidas += 1
        
        # Salva após sorteio
        salvar_tudo()
    
=======
        "entrou": entrou
    })

    contador_partidas += 1
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
    return redirect("/")

@app.route("/resetar")
def resetar():
<<<<<<< HEAD
    global fila, times, historico, contador_ordem, contador_partidas, gerenciador
    
=======
    global fila, times, historico, contador_ordem, contador_partidas
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
    fila = []
    times = {1: [], 2: []}
    historico = []
    contador_ordem = 1
    contador_partidas = 1
<<<<<<< HEAD
    gerenciador = GerenciadorTimes([], [], [], TAMANHO_TIME)
    
    # Salva estado resetado
    salvar_tudo()
    
    return redirect("/")

@app.route("/editar", methods=["POST"])
def editar():
    ordem = int(request.form["ordem"])
    novo_nome = request.form["nome"]

    for lista in [gerenciador.fila, gerenciador.times[0] if len(gerenciador.times) > 0 else [], 
                  gerenciador.times[1] if len(gerenciador.times) > 1 else []]:
        for j in lista:
            if isinstance(j, dict) and j.get("ordem") == ordem:
                j["nome"] = novo_nome
                break

    sincronizar_com_gerenciador()
    salvar_tudo()
    return redirect("/")

@app.route("/drag", methods=["POST"])
def drag():
    ordem = int(request.form["ordem"])
    destino = int(request.form["destino"])

    if len(times[destino]) >= TAMANHO_TIME:
        return redirect("/")

    jogador = None
    for j in fila:
        if j["ordem"] == ordem:
            jogador = j
            fila.remove(j)
            if jogador in gerenciador.fila:
                gerenciador.fila.remove(jogador)
            break

    if jogador:
        times[destino].append(jogador)
        if destino == 1:
            if len(gerenciador.times) == 0:
                gerenciador.times.append([])
            if len(gerenciador.times) < 2:
                gerenciador.times.append([])
            gerenciador.times[0].append(jogador)
        else:
            if len(gerenciador.times) < 2:
                gerenciador.times.append([])
            gerenciador.times[1].append(jogador)

    salvar_tudo()
    return redirect("/")
=======
    return redirect("/")


>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639

@app.route('/mover-jogador', methods=['POST'])
def mover_jogador():
    try:
        data = request.json
        jogador_data = data['jogador']
        destino = data['destino']
        
        ordem = int(jogador_data['ordem'])
        nome = jogador_data['nome']
        origem = jogador_data['origem']
        
<<<<<<< HEAD
        jogador = None
        
        if origem == 'fila':
=======
        # Encontrar e remover o jogador da origem
        jogador = None
        
        if origem == 'fila':
            # Remover da fila
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
            for j in fila:
                if j['ordem'] == ordem and j['nome'] == nome:
                    jogador = j
                    fila.remove(j)
<<<<<<< HEAD
                    if j in gerenciador.fila:
                        gerenciador.fila.remove(j)
                    break
        elif origem == 'team1':
=======
                    break
        elif origem == 'team1':
            # Remover do time 1
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
            for j in times[1]:
                if j['ordem'] == ordem and j['nome'] == nome:
                    jogador = j
                    times[1].remove(j)
<<<<<<< HEAD
                    if len(gerenciador.times) > 0 and j in gerenciador.times[0]:
                        gerenciador.times[0].remove(j)
                    break
        elif origem == 'team2':
=======
                    break
        elif origem == 'team2':
            # Remover do time 2
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
            for j in times[2]:
                if j['ordem'] == ordem and j['nome'] == nome:
                    jogador = j
                    times[2].remove(j)
<<<<<<< HEAD
                    if len(gerenciador.times) > 1 and j in gerenciador.times[1]:
                        gerenciador.times[1].remove(j)
=======
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
                    break
        
        if not jogador:
            return jsonify({'success': False, 'message': 'Jogador não encontrado'})
        
<<<<<<< HEAD
        if destino == 'fila':
            if jogador not in fila:
                fila.append(jogador)
                gerenciador.fila.append(jogador)
                fila.sort(key=lambda x: x['ordem'])
                gerenciador.fila.sort(key=lambda x: x['ordem'])
                
        elif destino == '1':
            if len(times[1]) >= TAMANHO_TIME:
                if origem == 'fila':
                    fila.append(jogador)
                    gerenciador.fila.append(jogador)
                elif origem == 'team2':
                    times[2].append(jogador)
                    if len(gerenciador.times) > 1:
                        gerenciador.times[1].append(jogador)
=======
        # Adicionar ao destino
        if destino == 'fila':
            # Verificar se já está na fila (não deveria acontecer)
            if jogador not in fila:
                fila.append(jogador)
                # Ordenar fila por ordem
                fila.sort(key=lambda x: x['ordem'])
                
        elif destino == '1':
            # Verificar se o time já está cheio
            if len(times[1]) >= TAMANHO_TIME:
                # Devolver jogador à origem
                if origem == 'fila':
                    fila.append(jogador)
                    fila.sort(key=lambda x: x['ordem'])
                elif origem == 'team2':
                    times[2].append(jogador)
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
                
                return jsonify({
                    'success': False, 
                    'message': f'Time 1 já está completo ({TAMANHO_TIME} jogadores)'
                })
            
<<<<<<< HEAD
            times[1].append(jogador)
            if len(gerenciador.times) < 1:
                gerenciador.times.append([])
            if len(gerenciador.times) < 2:
                gerenciador.times.append([])
            gerenciador.times[0].append(jogador)
            
        elif destino == '2':
            if len(times[2]) >= TAMANHO_TIME:
                if origem == 'fila':
                    fila.append(jogador)
                    gerenciador.fila.append(jogador)
                elif origem == 'team1':
                    times[1].append(jogador)
                    if len(gerenciador.times) > 0:
                        gerenciador.times[0].append(jogador)
=======
            # Adicionar ao time 1
            times[1].append(jogador)
            
        elif destino == '2':
            # Verificar se o time já está cheio
            if len(times[2]) >= TAMANHO_TIME:
                # Devolver jogador à origem
                if origem == 'fila':
                    fila.append(jogador)
                    fila.sort(key=lambda x: x['ordem'])
                elif origem == 'team1':
                    times[1].append(jogador)
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
                
                return jsonify({
                    'success': False, 
                    'message': f'Time 2 já está completo ({TAMANHO_TIME} jogadores)'
                })
            
<<<<<<< HEAD
            times[2].append(jogador)
            if len(gerenciador.times) < 2:
                gerenciador.times.append([])
            gerenciador.times[1].append(jogador)
        
        # Salva após mover
        salvar_tudo()
=======
            # Adicionar ao time 2
            times[2].append(jogador)
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
        
        return jsonify({'success': True, 'message': 'Jogador movido com sucesso'})
        
    except Exception as e:
        print(f"Erro ao mover jogador: {e}")
        return jsonify({'success': False, 'message': str(e)})

<<<<<<< HEAD
@app.route("/status")
def status():
    return jsonify({
        'fila': len(fila),
        'time1': len(times[1]),
        'time2': len(times[2]),
        'pode_sortear': len(fila) >= 14
    })

if __name__ == "__main__":
    app.run(debug=True)
=======


if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> 8859576d84ec504ccac5afffba7c8a5171bae639
