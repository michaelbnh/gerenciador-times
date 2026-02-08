from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

jogadores = []
times = []
fila = []
historico = []

jogo_iniciado = False
TAMANHO_TIME = 7
contador_partidas = 0

@app.route("/", methods=["GET", "POST"])
def index():
    global jogadores, times, fila, jogo_iniciado

    if request.method == "POST":
        acao = request.form.get("acao")

        # ➕ Adicionar jogador
        if acao == "adicionar":
            nome = request.form.get("nome")
            if nome:
                nome = nome.strip()
                jogadores.append(nome)

                if jogo_iniciado:
                    fila.append(nome)

        # ⚽ Criar times (uma única vez)
        elif acao == "criar" and not jogo_iniciado:
            time1 = request.form.getlist("time1")
            time2 = request.form.getlist("time2")

            times.clear()
            times.extend([time1, time2])

            usados = set(time1 + time2)
            fila.clear()
            fila.extend([j for j in jogadores if j not in usados])

            jogo_iniciado = True

    return render_template(
        "index.html",
        jogadores=jogadores,
        times=times,
        fila=fila,
        historico=historico,
        jogo_iniciado=jogo_iniciado
    )

@app.route("/perdeu/<int:indice>")
def perdeu(indice):
    global times, fila, historico, contador_partidas

    indice -= 1
    if indice >= len(times):
        return redirect(url_for("index"))

    contador_partidas += 1

    time_perdedor = times[indice]
    time_vencedor = times[1 - indice] if len(times) > 1 else []

    # Time perdedor vai para o fim da fila
    fila.extend(time_perdedor)

    # Remove o perdedor
    times.pop(indice)

    # Novo time entra
    entrou = []
    if len(fila) >= TAMANHO_TIME:
        entrou = fila[:TAMANHO_TIME]
        fila = fila[TAMANHO_TIME:]
        times.insert(indice, entrou)

    # 📜 Salva no histórico
    historico.insert(0, {
        "partida": contador_partidas,
        "vencedor": time_vencedor.copy(),
        "perdedor": time_perdedor.copy(),
        "entrou": entrou.copy()
    })

    return redirect(url_for("index"))

@app.route("/resetar")
def resetar():
    global jogadores, times, fila, historico, jogo_iniciado, contador_partidas
    jogadores = []
    times = []
    fila = []
    historico = []
    jogo_iniciado = False
    contador_partidas = 0
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
