from flask import Flask, render_template, request, redirect, jsonify
import random
from times import GerenciadorTimes
from database import Database
import atexit
import os
import logging

app = Flask(__name__)

# Configurar logging para o Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TAMANHO_TIME = 7

# Inicializa o banco de dados
db = Database()

# Inicializa o gerenciador de times
gerenciador = GerenciadorTimes([], [], [], TAMANHO_TIME)

# Carrega dados do banco
fila, times = db.carregar_jogadores()
historico = db.carregar_historico()
contador_ordem, contador_partidas = db.carregar_estado()

logger.info(f"🚀 INICIANDO APLICAÇÃO - Dados carregados: {len(fila)} jogadores na fila")

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
        logger.info("✅ Dados salvos com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar dados: {e}")

# Registra função para salvar ao encerrar
atexit.register(salvar_tudo)

@app.route("/", methods=["GET", "POST"])
def index():
    global contador_ordem, fila, times, historico, contador_partidas

    if request.method == "POST":
        nome = request.form.get("nome")
        if nome:
            jogador_dict = {"nome": nome, "ordem": contador_ordem}
            contador_ordem += 1
            
            # Adiciona à fila
            gerenciador.fila.append(jogador_dict)
            fila.append(jogador_dict)
            
            logger.info(f"✅ Jogador adicionado: {nome}. Fila agora tem {len(fila)} jogadores")
            
            # VERIFICAÇÃO CRÍTICA - SORTEIO AUTOMÁTICO
            if len(fila) >= 14:
                logger.info("🚀🚀🚀 14 JOGADORES ATINGIDOS! INICIANDO SORTEIO...")
                
                try:
                    # Pega os primeiros 14 da fila
                    jogadores_sorteados = fila[:14]
                    logger.info(f"Jogadores para sorteio: {[j['nome'] for j in jogadores_sorteados]}")
                    
                    # Embaralha
                    random.shuffle(jogadores_sorteados)
                    logger.info(f"Jogadores embaralhados: {[j['nome'] for j in jogadores_sorteados]}")
                    
                    # Remove da fila (os 14 primeiros)
                    fila = fila[14:]
                    logger.info(f"Fila após remoção: {len(fila)} jogadores restantes")
                    
                    # Divide em dois times
                    times[1] = jogadores_sorteados[:7]
                    times[2] = jogadores_sorteados[7:]
                    
                    logger.info(f"🔵 TIME 1: {[j['nome'] for j in times[1]]}")
                    logger.info(f"🟡 TIME 2: {[j['nome'] for j in times[2]]}")
                    
                    # Atualiza gerenciador
                    gerenciador.fila = fila.copy()
                    gerenciador.times = [times[1].copy(), times[2].copy()]
                    
                    # Adiciona ao histórico
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
                    
                    # Salva no banco
                    salvar_tudo()
                    
                    logger.info("🎉🎉🎉 SORTEIO REALIZADO COM SUCESSO!")
                    
                except Exception as e:
                    logger.error(f"❌ ERRO NO SORTEIO: {str(e)}")
            
        return redirect("/")

    return render_template("index.html", fila=fila, times=times, historico=historico, tamanho_time=TAMANHO_TIME)

@app.route("/perdeu/<int:time_perdedor>")
def perdeu(time_perdedor):
    global contador_partidas, fila, times, historico

    time_vencedor = 1 if time_perdedor == 2 else 2

    if len(times[time_perdedor]) != TAMANHO_TIME or len(times[time_vencedor]) != TAMANHO_TIME:
        logger.warning(f"Times incompletos: Time{time_perdedor}={len(times[time_perdedor])}, Time{time_vencedor}={len(times[time_vencedor])}")
        return redirect("/")

    perdedor_snapshot = times[time_perdedor].copy()
    vencedor_snapshot = times[time_vencedor].copy()

    times[time_perdedor] = []
    entrou = []

    # Primeiro: puxa da fila
    while len(times[time_perdedor]) < TAMANHO_TIME and fila:
        j = fila.pop(0)
        times[time_perdedor].append(j)
        entrou.append(j)
    
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

    historico.insert(0, {
        "partida": contador_partidas,
        "vencedor": vencedor_snapshot,
        "perdedor": perdedor_snapshot,
        "entrou": entrou,
        "sorteio": False
    })

    contador_partidas += 1
    
    # Salva após cada modificação
    salvar_tudo()
    
    if len(fila) >= 14:
        logger.info("🔄 Redirecionando para sorteio automático após partida")
        return redirect("/sortear-automatico")
    
    return redirect("/")

@app.route("/sortear-automatico")
def sortear_automatico():
    """Rota para sorteio automático quando tem 14 jogadores"""
    global fila, times, contador_partidas, historico
    
    logger.info("🔄 Rota /sortear-automatico chamada")
    logger.info(f"Tamanho da fila: {len(fila)}")
    
    if len(fila) >= 14:
        logger.info("🚀 Iniciando sorteio...")
        
        try:
            # Pega os primeiros 14
            jogadores_sorteados = fila[:14]
            logger.info(f"Jogadores para sorteio: {[j['nome'] for j in jogadores_sorteados]}")
            
            # Embaralha
            random.shuffle(jogadores_sorteados)
            
            # Remove da fila
            fila = fila[14:]
            
            # Cria os times
            times[1] = jogadores_sorteados[:7]
            times[2] = jogadores_sorteados[7:]
            
            logger.info(f"Time 1: {[j['nome'] for j in times[1]]}")
            logger.info(f"Time 2: {[j['nome'] for j in times[2]]}")
            
            # Atualiza gerenciador
            gerenciador.fila = fila.copy()
            gerenciador.times = [times[1].copy(), times[2].copy()]
            
            # Adiciona ao histórico
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
            
            # Salva no banco
            salvar_tudo()
            
            logger.info("✅ Sorteio concluído com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro no sorteio: {str(e)}")
    else:
        logger.warning(f"❌ Fila insuficiente: {len(fila)}/14")
    
    return redirect("/")

@app.route("/resetar")
def resetar():
    global fila, times, historico, contador_ordem, contador_partidas, gerenciador
    
    logger.info("🔄 Resetando toda a aplicação")
    
    fila = []
    times = {1: [], 2: []}
    historico = []
    contador_ordem = 1
    contador_partidas = 1
    gerenciador = GerenciadorTimes([], [], [], TAMANHO_TIME)
    
    # Salva estado resetado
    salvar_tudo()
    
    logger.info("✅ Aplicação resetada com sucesso")
    
    return redirect("/")

@app.route("/editar", methods=["POST"])
def editar():
    ordem = int(request.form["ordem"])
    novo_nome = request.form["nome"]

    for lista in [gerenciador.fila, gerenciador.times[0] if len(gerenciador.times) > 0 else [], 
                  gerenciador.times[1] if len(gerenciador.times) > 1 else []]:
        for j in lista:
            if isinstance(j, dict) and j.get("ordem") == ordem:
                logger.info(f"Editando jogador {j['nome']} para {novo_nome}")
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
        logger.info(f"Arrastando jogador {jogador['nome']} para time {destino}")
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

@app.route('/mover-jogador', methods=['POST'])
def mover_jogador():
    try:
        data = request.json
        jogador_data = data['jogador']
        destino = data['destino']
        
        ordem = int(jogador_data['ordem'])
        nome = jogador_data['nome']
        origem = jogador_data['origem']
        
        jogador = None
        
        if origem == 'fila':
            for j in fila:
                if j['ordem'] == ordem and j['nome'] == nome:
                    jogador = j
                    fila.remove(j)
                    if j in gerenciador.fila:
                        gerenciador.fila.remove(j)
                    break
        elif origem == 'team1':
            for j in times[1]:
                if j['ordem'] == ordem and j['nome'] == nome:
                    jogador = j
                    times[1].remove(j)
                    if len(gerenciador.times) > 0 and j in gerenciador.times[0]:
                        gerenciador.times[0].remove(j)
                    break
        elif origem == 'team2':
            for j in times[2]:
                if j['ordem'] == ordem and j['nome'] == nome:
                    jogador = j
                    times[2].remove(j)
                    if len(gerenciador.times) > 1 and j in gerenciador.times[1]:
                        gerenciador.times[1].remove(j)
                    break
        
        if not jogador:
            return jsonify({'success': False, 'message': 'Jogador não encontrado'})
        
        logger.info(f"Movendo jogador {jogador['nome']} de {origem} para {destino}")
        
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
                
                return jsonify({
                    'success': False, 
                    'message': f'Time 1 já está completo ({TAMANHO_TIME} jogadores)'
                })
            
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
                
                return jsonify({
                    'success': False, 
                    'message': f'Time 2 já está completo ({TAMANHO_TIME} jogadores)'
                })
            
            times[2].append(jogador)
            if len(gerenciador.times) < 2:
                gerenciador.times.append([])
            gerenciador.times[1].append(jogador)
        
        # Salva após mover
        salvar_tudo()
        
        return jsonify({'success': True, 'message': 'Jogador movido com sucesso'})
        
    except Exception as e:
        logger.error(f"Erro ao mover jogador: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route("/status")
def status():
    return jsonify({
        'fila': len(fila),
        'time1': len(times[1]),
        'time2': len(times[2]),
        'pode_sortear': len(fila) >= 14
    })

@app.route("/testar-sorteio")
def testar_sorteio():
    """Rota para testar o sorteio manualmente"""
    global fila, times, contador_partidas, historico
    
    logger.info("🧪 Rota /testar-sorteio chamada")
    
    if len(fila) >= 14:
        logger.info("✅ Fila tem 14+ jogadores, redirecionando para sorteio")
        return redirect("/sortear-automatico")
    else:
        msg = f"❌ Fila tem apenas {len(fila)} jogadores. Precisa de 14."
        logger.warning(msg)
        return msg

@app.route("/teste-sorteio-forcado")
def teste_sorteio_forcado():
    """Rota para forçar um sorteio com dados de teste"""
    global fila, times, contador_partidas, historico, contador_ordem
    
    logger.info("🧪🧪🧪 TESTE FORÇADO INICIADO")
    
    # Limpa tudo
    fila = []
    times = {1: [], 2: []}
    
    # Cria 14 jogadores de teste
    for i in range(1, 15):
        jogador = {"nome": f"Teste{i}", "ordem": contador_ordem}
        contador_ordem += 1
        fila.append(jogador)
    
    logger.info(f"✅ 14 jogadores de teste criados: {[j['nome'] for j in fila]}")
    
    # Força o sorteio
    jogadores_sorteados = fila[:14]
    random.shuffle(jogadores_sorteados)
    
    fila = fila[14:]
    
    times[1] = jogadores_sorteados[:7]
    times[2] = jogadores_sorteados[7:]
    
    logger.info(f"🔵 TIME 1 (teste): {[j['nome'] for j in times[1]]}")
    logger.info(f"🟡 TIME 2 (teste): {[j['nome'] for j in times[2]]}")
    
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
    salvar_tudo()
    
    logger.info("🎉🎉🎉 TESTE FORÇADO CONCLUÍDO COM SUCESSO!")
    
    return redirect("/")

@app.route("/debug-db")
def debug_db():
    """Rota para debug - mostra estatísticas do banco"""
    try:
        import sqlite3
        
        # Tenta conectar no banco
        db_path = '/data/gerenciador.db' if os.path.exists('/data') else 'gerenciador.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Estatísticas
        cursor.execute("SELECT COUNT(*) FROM jogadores")
        total_jogadores = cursor.fetchone()[0]
        
        cursor.execute("SELECT localizacao, COUNT(*) FROM jogadores GROUP BY localizacao")
        localizacoes = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM historico")
        total_partidas = cursor.fetchone()[0]
        
        conn.close()
        
        return f"""
        <html>
        <head><title>Debug DB</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h2>🔍 Debug do Banco de Dados</h2>
            <p><strong>Caminho:</strong> {db_path}</p>
            <p><strong>Arquivo existe?</strong> {os.path.exists(db_path)}</p>
            <p><strong>Total de jogadores:</strong> {total_jogadores}</p>
            <p><strong>Por localização:</strong> {localizacoes}</p>
            <p><strong>Partidas no histórico:</strong> {total_partidas}</p>
            <p><strong>Fila atual (memória):</strong> {len(fila)} jogadores</p>
            <p><strong>Time 1:</strong> {len(times[1])} jogadores</p>
            <p><strong>Time 2:</strong> {len(times[2])} jogadores</p>
            <p><a href="/">⬅️ Voltar</a> | <a href="/teste-sorteio-forcado">🧪 Forçar teste</a></p>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h2>Erro</h2><p>{str(e)}</p>"

@app.route("/logs")
def ver_logs():
    """Rota simples para ver os logs recentes (últimas 50 linhas)"""
    return """
    <html>
    <head><title>Logs</title></head>
    <body style="font-family: monospace; padding: 20px;">
        <h2>📋 Logs da Aplicação</h2>
        <p>Para ver os logs completos, acesse o dashboard do Render.</p>
        <p><a href="/">⬅️ Voltar</a></p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)