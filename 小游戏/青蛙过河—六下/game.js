class FrogGame {
    constructor() {
        this.score = 0;
        this.level = 1;
        this.lives = 3;
        this.isGameRunning = false;
        this.isPaused = false;
        this.frogPosition = { x: 0, y: 0 };
        this.lilyPads = [];
        this.currentWords = [];
        this.gameLoop = null;
        this.padSpeed = 2;
        this.spawnInterval = null;
        
        this.init();
    }
    
    init() {
        this.frog = document.getElementById('frog');
        this.scoreElement = document.getElementById('score');
        this.levelElement = document.getElementById('level');
        this.livesElement = document.getElementById('lives');
        this.startBtn = document.getElementById('startBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        
        this.startBtn.addEventListener('click', () => this.startGame());
        this.pauseBtn.addEventListener('click', () => this.togglePause());
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        
        this.resetFrogPosition();
    }
    
    resetFrogPosition() {
        this.frogPosition = { x: 20, y: 220 };
        this.updateFrogPosition();
    }
    
    updateFrogPosition() {
        this.frog.style.left = this.frogPosition.x + 'px';
        this.frog.style.top = this.frogPosition.y + 'px';
    }
    
    startGame() {
        if (this.isGameRunning) return;
        
        this.isGameRunning = true;
        this.isPaused = false;
        this.score = 0;
        this.level = 1;
        this.lives = 3;
        this.padSpeed = 2;
        
        this.updateUI();
        this.resetFrogPosition();
        this.clearLilyPads();
        
        this.startBtn.textContent = '游戏中...';
        this.startBtn.disabled = true;
        this.pauseBtn.disabled = false;
        
        this.spawnLilyPads();
        this.startGameLoop();
    }
    
    togglePause() {
        if (!this.isGameRunning) return;
        
        this.isPaused = !this.isPaused;
        this.pauseBtn.textContent = this.isPaused ? '继续' : '暂停';
        
        if (this.isPaused) {
            this.stopGameLoop();
            this.stopSpawning();
        } else {
            this.startGameLoop();
            this.spawnLilyPads();
        }
    }
    
    startGameLoop() {
        this.gameLoop = setInterval(() => this.update(), 20);
    }
    
    stopGameLoop() {
        if (this.gameLoop) {
            clearInterval(this.gameLoop);
            this.gameLoop = null;
        }
    }
    
    spawnLilyPads() {
        this.spawnInterval = setInterval(() => {
            if (this.isPaused) return;
            this.createLilyPad();
        }, 2000);
    }
    
    stopSpawning() {
        if (this.spawnInterval) {
            clearInterval(this.spawnInterval);
            this.spawnInterval = null;
        }
    }
    
    createLilyPad() {
        const lane = Math.floor(Math.random() * 3);
        const laneElement = document.getElementById(`lane${lane + 1}`);
        const laneRect = laneElement.getBoundingClientRect();
        const gameAreaRect = document.querySelector('.game-area').getBoundingClientRect();
        
        const words = wordDatabase[`level${this.level}`];
        const wordData = words[Math.floor(Math.random() * words.length)];
        
        const lilyPad = document.createElement('div');
        lilyPad.className = 'lily-pad';
        lilyPad.textContent = wordData.word;
        lilyPad.dataset.word = wordData.word;
        lilyPad.dataset.firstLetter = wordData.firstLetter;
        lilyPad.dataset.meaning = wordData.meaning;
        
        const startY = laneRect.top - gameAreaRect.top + (laneRect.height - 100) / 2;
        lilyPad.style.left = '700px';
        lilyPad.style.top = startY + 'px';
        
        laneElement.appendChild(lilyPad);
        
        this.lilyPads.push({
            element: lilyPad,
            x: 700,
            y: startY,
            lane: lane,
            speed: this.padSpeed + Math.random() * 2
        });
    }
    
    update() {
        if (this.isPaused) return;
        
        this.lilyPads.forEach((pad, index) => {
            pad.x -= pad.speed;
            pad.element.style.left = pad.x + 'px';
            
            if (pad.x < -120) {
                pad.element.remove();
                this.lilyPads.splice(index, 1);
            }
        });
        
        this.checkWinCondition();
    }
    
    handleKeyPress(event) {
        if (!this.isGameRunning || this.isPaused) return;
        
        const key = event.key.toLowerCase();
        
        this.lilyPads.forEach((pad, index) => {
            if (pad.element.dataset.firstLetter === key) {
                this.handleCorrectAnswer(pad, index);
            }
        });
    }
    
    handleCorrectAnswer(pad, index) {
        const word = pad.element.dataset.word;
        const meaning = pad.element.dataset.meaning;
        
        this.score += 10;
        this.updateUI();
        
        pad.element.classList.add('correct');
        
        setTimeout(() => {
            pad.element.remove();
            this.lilyPads.splice(index, 1);
        }, 300);
        
        this.moveFrogToPad(pad);
    }
    
    moveFrogToPad(pad) {
        const targetX = pad.x + 30;
        const targetY = pad.y + 20;
        
        this.frogPosition.x = targetX;
        this.frogPosition.y = targetY;
        this.updateFrogPosition();
        
        if (this.frogPosition.x >= 600) {
            this.levelUp();
        }
    }
    
    checkWinCondition() {
        if (this.frogPosition.x >= 600) {
            this.levelUp();
        }
    }
    
    levelUp() {
        this.level++;
        this.padSpeed += 0.5;
        this.updateUI();
        this.resetFrogPosition();
        
        if (this.level > 3) {
            this.gameWin();
        }
    }
    
    loseLife() {
        this.lives--;
        this.updateUI();
        
        if (this.lives <= 0) {
            this.gameOver();
        } else {
            this.resetFrogPosition();
        }
    }
    
    updateUI() {
        this.scoreElement.textContent = this.score;
        this.levelElement.textContent = this.level;
        this.livesElement.textContent = this.lives;
    }
    
    clearLilyPads() {
        this.lilyPads.forEach(pad => pad.element.remove());
        this.lilyPads = [];
    }
    
    gameOver() {
        this.isGameRunning = false;
        this.stopGameLoop();
        this.stopSpawning();
        this.clearLilyPads();
        
        this.showGameOverScreen(false);
    }
    
    gameWin() {
        this.isGameRunning = false;
        this.stopGameLoop();
        this.stopSpawning();
        this.clearLilyPads();
        
        this.showGameOverScreen(true);
    }
    
    showGameOverScreen(isWin) {
        const gameOverDiv = document.createElement('div');
        gameOverDiv.className = 'game-over';
        
        gameOverDiv.innerHTML = `
            <div class="game-over-content">
                <h2>${isWin ? '恭喜通关！' : '游戏结束'}</h2>
                <p>最终得分: ${this.score}</p>
                <p>到达关卡: ${this.level}</p>
                <button onclick="location.reload()">重新开始</button>
            </div>
        `;
        
        document.body.appendChild(gameOverDiv);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.game = new FrogGame();
});