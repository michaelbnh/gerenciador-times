from flask import Flask, render_template, request, redirect, jsonify
app = Flask(__name__)

TAMANHO_TIME = 7

fila = []
times = {1: [], 2: []}
historico = []
contador_ordem = 1
contador_partidas = 1

@app.route("/", methods=["GET", "POST"])
def index():
    global contador_ordem

    if request.method == "POST":
        nome = request.form.get("nome")
        if nome:
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

    while len(times[time_perdedor]) < TAMANHO_TIME and fila:
        j = fila.pop(0)
        times[time_perdedor].append(j)
        entrou.append(j)

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

    historico.insert(0, {
        "partida": contador_partidas,
        "vencedor": vencedor_snapshot,
        "perdedor": perdedor_snapshot,
        "entrou": entrou
    })

    contador_partidas += 1
    return redirect("/")

@app.route("/resetar")
def resetar():
    global fila, times, historico, contador_ordem, contador_partidas
    fila = []
    times = {1: [], 2: []}
    historico = []
    contador_ordem = 1
    contador_partidas = 1
    return redirect("/")



@app.route('/mover-jogador', methods=['POST'])
def mover_jogador():
    try:
        data = request.json
        jogador_data = data['jogador']
        destino = data['destino']
        
        ordem = int(jogador_data['ordem'])
        nome = jogador_data['nome']
        origem = jogador_data['origem']
        
        # Encontrar e remover o jogador da origem
        jogador = None
        
        if origem == 'fila':
            # Remover da fila
            for j in fila:
                if j['ordem'] == ordem and j['nome'] == nome:
                    jogador = j
                    fila.remove(j)
                    break
        elif origem == 'team1':
            # Remover do time 1
            for j in times[1]:
                if j['ordem'] == ordem and j['nome'] == nome:
                    jogador = j
                    times[1].remove(j)
                    break
        elif origem == 'team2':
            # Remover do time 2
            for j in times[2]:
                if j['ordem'] == ordem and j['nome'] == nome:
                    jogador = j
                    times[2].remove(j)
                    break
        
        if not jogador:
            return jsonify({'success': False, 'message': 'Jogador não encontrado'})
        
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
                
                return jsonify({
                    'success': False, 
                    'message': f'Time 1 já está completo ({TAMANHO_TIME} jogadores)'
                })
            
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
                
                return jsonify({
                    'success': False, 
                    'message': f'Time 2 já está completo ({TAMANHO_TIME} jogadores)'
                })
            
            # Adicionar ao time 2
            times[2].append(jogador)
        
        return jsonify({'success': True, 'message': 'Jogador movido com sucesso'})
        
    except Exception as e:
        print(f"Erro ao mover jogador: {e}")
        return jsonify({'success': False, 'message': str(e)})



if __name__ == "__main__":
    app.run(debug=True)
