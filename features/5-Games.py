import streamlit as st
import streamlit.components.v1 as components
from features.functions import track_time_spent

def games_section():
    # Track time spent
    track_time_spent('games_used')

    st.header("🎮 Mindful Games", divider="rainbow")
    st.write("Take a break and play some relaxing games to de-stress.")

    tab1, tab2, tab3 = st.tabs(["🧱 Block Game", "🐦 Floppy Bird", "🍬 Candy Match"])

    # ================= BLOCK GAME =================
    with tab1:
        st.subheader("Block Game")
        st.caption("Left/Right: Move | Up: Rotate | Down: Drop")

        block_game_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { background: #0e1117; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
                canvas { border: 2px solid #333; background-color: #000; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
                .info { font-size: 20px; margin-top: 10px; display: flex; gap: 20px; }
            </style>
        </head>
        <body>
            <canvas id="tetris" width="240" height="400"></canvas>
            <div class="info">
                <div id="score">Score: 0</div>
                <div id="highscore">High Score: 0</div>
            </div>
            <script>
                const canvas = document.getElementById('tetris');
                const context = canvas.getContext('2d');
                context.scale(20, 20);

                // Load High Score
                let highScore = localStorage.getItem('block_highscore') || 0;
                document.getElementById('highscore').innerText = "High Score: " + highScore;

                function arenaSweep() {
                    let rowCount = 1;
                    outer: for (let y = arena.length - 1; y > 0; --y) {
                        for (let x = 0; x < arena[y].length; ++x) {
                            if (arena[y][x] === 0) {
                                continue outer;
                            }
                        }
                        const row = arena.splice(y, 1)[0].fill(0);
                        arena.unshift(row);
                        ++y;
                        player.score += rowCount * 10;
                        rowCount *= 2;
                    }
                }

                function collide(arena, player) {
                    const [m, o] = [player.matrix, player.pos];
                    for (let y = 0; y < m.length; ++y) {
                        for (let x = 0; x < m[y].length; ++x) {
                            if (m[y][x] !== 0 && (arena[y + o.y] && arena[y + o.y][x + o.x]) !== 0) {
                                return true;
                            }
                        }
                    }
                    return false;
                }

                function createMatrix(w, h) {
                    const matrix = [];
                    while (h--) {
                        matrix.push(new Array(w).fill(0));
                    }
                    return matrix;
                }

                function createPiece(type) {
                    if (type === 'I') return [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]];
                    if (type === 'L') return [[0, 2, 0], [0, 2, 0], [0, 2, 2]];
                    if (type === 'J') return [[0, 3, 0], [0, 3, 0], [3, 3, 0]];
                    if (type === 'O') return [[4, 4], [4, 4]];
                    if (type === 'Z') return [[5, 5, 0], [0, 5, 5], [0, 0, 0]];
                    if (type === 'S') return [[0, 6, 6], [6, 6, 0], [0, 0, 0]];
                    if (type === 'T') return [[0, 7, 0], [7, 7, 7], [0, 0, 0]];
                }

                function draw() {
                    context.fillStyle = '#000';
                    context.fillRect(0, 0, canvas.width, canvas.height);
                    drawMatrix(arena, {x: 0, y: 0});
                    drawMatrix(player.matrix, player.pos);
                }

                function drawMatrix(matrix, offset) {
                    matrix.forEach((row, y) => {
                        row.forEach((value, x) => {
                            if (value !== 0) {
                                context.fillStyle = colors[value];
                                context.fillRect(x + offset.x, y + offset.y, 1, 1);
                            }
                        });
                    });
                }

                function merge(arena, player) {
                    player.matrix.forEach((row, y) => {
                        row.forEach((value, x) => {
                            if (value !== 0) {
                                arena[y + player.pos.y][x + player.pos.x] = value;
                            }
                        });
                    });
                }

                function playerDrop() {
                    player.pos.y++;
                    if (collide(arena, player)) {
                        player.pos.y--;
                        merge(arena, player);
                        playerReset();
                        arenaSweep();
                        updateScore();
                    }
                    dropCounter = 0;
                }

                function playerMove(dir) {
                    player.pos.x += dir;
                    if (collide(arena, player)) {
                        player.pos.x -= dir;
                    }
                }

                function playerReset() {
                    const pieces = 'ILJOTSZ';
                    player.matrix = createPiece(pieces[pieces.length * Math.random() | 0]);
                    player.pos.y = 0;
                    player.pos.x = (arena[0].length / 2 | 0) - (player.matrix[0].length / 2 | 0);
                    if (collide(arena, player)) {
                        arena.forEach(row => row.fill(0));
                        // Update High Score
                        if (player.score > highScore) {
                            highScore = player.score;
                            localStorage.setItem('block_highscore', highScore);
                            document.getElementById('highscore').innerText = "High Score: " + highScore;
                        }
                        player.score = 0;
                        updateScore();
                    }
                }

                function playerRotate(dir) {
                    const pos = player.pos.x;
                    let offset = 1;
                    rotate(player.matrix, dir);
                    while (collide(arena, player)) {
                        player.pos.x += offset;
                        offset = -(offset + (offset > 0 ? 1 : -1));
                        if (offset > player.matrix[0].length) {
                            rotate(player.matrix, -dir);
                            player.pos.x = pos;
                            return;
                        }
                    }
                }

                function rotate(matrix, dir) {
                    for (let y = 0; y < matrix.length; ++y) {
                        for (let x = 0; x < y; ++x) {
                            [matrix[x][y], matrix[y][x]] = [matrix[y][x], matrix[x][y]];
                        }
                    }
                    if (dir > 0) matrix.forEach(row => row.reverse());
                    else matrix.reverse();
                }

                let dropCounter = 0;
                let dropInterval = 1000;
                let lastTime = 0;

                function update(time = 0) {
                    const deltaTime = time - lastTime;
                    lastTime = time;
                    dropCounter += deltaTime;
                    if (dropCounter > dropInterval) {
                        playerDrop();
                    }
                    draw();
                    requestAnimationFrame(update);
                }

                function updateScore() {
                    document.getElementById('score').innerText = "Score: " + player.score;
                }

                const colors = [null, '#FF0D72', '#0DC2FF', '#0DFF72', '#F538FF', '#FF8E0D', '#FFE138', '#3877FF'];
                const arena = createMatrix(12, 20);
                const player = { pos: {x: 0, y: 0}, matrix: null, score: 0 };

                document.addEventListener('keydown', event => {
                    if (event.keyCode === 37) playerMove(-1);
                    else if (event.keyCode === 39) playerMove(1);
                    else if (event.keyCode === 40) playerDrop();
                    else if (event.keyCode === 38) playerRotate(1);
                });

                playerReset();
                updateScore();
                update();
            </script>
        </body>
        </html>
        """
        components.html(block_game_html, height=500)

    # ================= FLOPPY BIRD =================
    with tab2:
        st.subheader("Floppy Bird")
        st.caption("Click or Space to Fly")

        floppy_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { background: #70c5ce; margin: 0; overflow: hidden; font-family: sans-serif; text-align: center; }
                canvas { display: block; margin: 0 auto; background: #70c5ce; border: 2px solid #333; }
                #score { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); font-size: 30px; color: white; font-weight: bold; text-shadow: 2px 2px #000; }
                #highscore { position: absolute; top: 50px; left: 50%; transform: translateX(-50%); font-size: 18px; color: yellow; font-weight: bold; text-shadow: 1px 1px #000; }
                #message { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: white; font-weight: bold; text-shadow: 1px 1px #000; display: none; }
            </style>
        </head>
        <body>
        <div id="score">0</div>
            <div id="highscore">High Score: 0</div>
            <div id="message">Game Over<br>Click to Restart</div>
            <canvas id="birdCanvas" width="320" height="480"></canvas>
            <script>
                const cvs = document.getElementById("birdCanvas");
                const ctx = cvs.getContext("2d");

                let frames = 0;
                const DEGREE = Math.PI / 180;

                // Load High Score
                let highScore = localStorage.getItem('floppy_highscore') || 0;
                document.getElementById('highscore').innerText = "High Score: " + highScore;

                const state = { current: 0, getReady: 0, game: 1, over: 2 };

                const bird = {
                    x: 50, y: 150, w: 20, h: 20, radius: 10,
                    speed: 0, gravity: 0.25, jump: 4.6,
                    draw: function() {
                        ctx.fillStyle = "yellow";
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.strokeStyle = "black";
                        ctx.stroke();
                        ctx.fillStyle = "black";
                        ctx.beginPath();
                        ctx.arc(this.x + 5, this.y - 5, 2, 0, Math.PI * 2);
                        ctx.fill();
                    },
                    flap: function() { this.speed = -this.jump; },
                    update: function() {
                        if (state.current == state.getReady) { this.y = 150; } 
                        else {
                            this.speed += this.gravity;
                            this.y += this.speed;
                        }
                        if (this.y + this.radius >= cvs.height) {
                            this.y = cvs.height - this.radius;
                            if (state.current == state.game) state.current = state.over;
                        }
                    }
                };

                const pipes = {
                    position: [], w: 50, dx: 2, gap: 120,
                    draw: function() {
                        for (let i = 0; i < this.position.length; i++) {
                            let p = this.position[i];
                            let topHeight = p.y;
                            let bottomY = p.y + this.gap;
                            
                            // Top Pipe
                            ctx.fillStyle = "green";
                            ctx.fillRect(p.x, 0, this.w, topHeight);
                            ctx.strokeStyle = "black";
                            ctx.strokeRect(p.x, 0, this.w, topHeight);
                            
                            // Bottom Pipe
                            ctx.fillStyle = "green";
                            ctx.fillRect(p.x, bottomY, this.w, cvs.height - bottomY);
                            ctx.strokeStyle = "black";
                            ctx.strokeRect(p.x, bottomY, this.w, cvs.height - bottomY);
                        }
                    },
                    update: function() {
                        if (state.current !== state.game) return;
                        if (frames % 120 == 0) {
                            let maxTop = cvs.height - this.gap - 50;
                            let topHeight = Math.floor(Math.random() * (maxTop - 50 + 1)) + 50;
                            this.position.push({ x: cvs.width, y: topHeight });
                        }
                        for (let i = 0; i < this.position.length; i++) {
                            let p = this.position[i];

                            // Collision
                            if (bird.x + bird.radius > p.x && bird.x - bird.radius < p.x + this.w &&
                                (bird.y - bird.radius < p.y || bird.y + bird.radius > p.y + this.gap)) {
                                state.current = state.over;
                            }

                            p.x -= this.dx;
                            if (p.x + this.w <= 0) {
                                this.position.shift();
                                score.value += 1;
                                score.best = Math.max(score.value, score.best);
                                document.getElementById("score").innerText = score.value;
                                
                                if(score.value > highScore) {
                                    highScore = score.value;
                                    localStorage.setItem('floppy_highscore', highScore);
                                    document.getElementById('highscore').innerText = "High Score: " + highScore;
                                }
                            }
                        }
                    },
                    reset: function() { this.position = []; }
                };

                const score = {
                    best: 0, value: 0,
                    reset: function() { this.value = 0; document.getElementById("score").innerText = 0; }
                };

                function draw() {
                    ctx.fillStyle = "#70c5ce";
                    ctx.fillRect(0, 0, cvs.width, cvs.height);
                    pipes.draw();
                    bird.draw();
                }

                function update() {
                    bird.update();
                    pipes.update();
                }

                function loop() {
                    update();
                    draw();
                    frames++;
                    if(state.current == state.over) {
                        document.getElementById("message").style.display = "block";
                    } else {
                        document.getElementById("message").style.display = "none";
                        requestAnimationFrame(loop);
                    }
                }

                cvs.addEventListener("click", function(evt) {
                    switch (state.current) {
                        case state.getReady:
                            state.current = state.game;
                            bird.flap();
                            break;
                        case state.game:
                            bird.flap();
                            break;
                        case state.over:
                            pipes.reset();
                            bird.speed = 0;
                            score.reset();
                            frames = 0;
                            state.current = state.getReady;
                            bird.y = 150;
                            loop();
                            break;
                    }
                });
                
                window.addEventListener('keydown', function(e){
                    if(e.code === 'Space') {
                        e.preventDefault();
                        cvs.click();
                    }
                });

                loop();
            </script>
        </body>
        </html>
        """
        components.html(floppy_html, height=500)

    # ================= CANDY MATCH =================
    with tab3:
        st.subheader("Candy Match")
        st.caption("Match 3 candies")

        candy_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
          body{background:#181818;color:white;text-align:center;}
          #grid{display:grid;grid-template-columns:repeat(8,55px);
                gap:6px;width:480px;margin:auto;margin-top:15px;}
          .cell{width:55px;height:55px;border-radius:15px;
                box-shadow:0 0 10px #000;cursor:pointer}
          .selected{outline:3px solid white;}
        </style>
        </head>
        <body>

        <h3>Score: <span id="score">0</span></h3>
        <button onclick="document.documentElement.requestFullscreen()">Fullscreen</button>

        <div id="grid"></div>

        <audio id="pop" src="https://assets.mixkit.co/sfx/preview/mixkit-game-click-1114.mp3"></audio>

        <script>
        const width=8,grid=document.getElementById("grid");
        const colors=['#ff4d6d','#ffd43b','#74c0fc','#63e6be','#e599f7','#ffa94d'];
        const cells=[];let score=0;let selected=null;

        for(let i=0;i<64;i++){
          const d=document.createElement("div");
          d.id=i;d.className="cell";
          d.style.background=colors[Math.random()*colors.length|0];
          d.onclick=handleClick;grid.appendChild(d);cells.push(d);
        }

        function handleClick(){
          if(!selected){selected=this;this.classList.add("selected");return;}
          let a=parseInt(selected.id),b=parseInt(this.id);
          selected.classList.remove("selected");
          let adj=[a-1,a+1,a-width,a+width];if(!adj.includes(b)){selected=null;return;}
          swap(selected,this);
          if(!check()){setTimeout(()=>swap(selected,this),200);}
          else play();selected=null;
        }

        function swap(a,b){let t=a.style.background;a.style.background=b.style.background;b.style.background=t;}

        function check(){
          let ok=false;
          for(let i=0;i<64;i++){
            if(i%8<6 && same(i,i+1,i+2)) ok=true,set(i,i+1,i+2);
            if(i<48 && same(i,i+8,i+16)) ok=true,set(i,i+8,i+16);
          }
          if(ok) setTimeout(drop,120);
          return ok;
        }

        function same(...n){
          return n.every(i=>cells[i].style.background===cells[n[0]].style.background);
        }

        function set(...n){
          score+=3;
          document.getElementById("score").innerText=score;
          n.forEach(i=>cells[i].style.background="");
        }

        function drop(){
          for(let i=55;i>=0;i--){
            if(cells[i].style.background==="" ){cells[i].style.background=cells[i-8]?.style.background||colors[Math.random()*colors.length|0];cells[i-8]&&(cells[i-8].style.background="");}
          }
          check();
        }

        function play(){document.getElementById("pop").play();}
        </script>
        </body>
        </html>

        """
        components.html(candy_html, height=500)


if __name__ == '__main__':
    games_section()