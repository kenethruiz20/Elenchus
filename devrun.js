#!/usr/bin/env node

/**
 * Elenchus AI Development Runner (Node.js version)
 * Starts backend and frontend in development mode with hot reload and debugging
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const net = require('net');

// Configuration
const CONFIG = {
    FRONTEND_PORT: 3000,
    BACKEND_PORT: 8000,
    BACKEND_DEBUG_PORT: 5678,
    LOGS_DIR: './logs'
};

// Set environment variable for frontend API URL
process.env.NEXT_PUBLIC_API_URL = `http://localhost:${CONFIG.BACKEND_PORT}`;

// Colors for console output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

class DevRunner {
    constructor() {
        this.processes = [];
        this.setupSignalHandlers();
        this.createLogsDirectory();
    }

    log(message, color = colors.reset) {
        console.log(`${color}${message}${colors.reset}`);
    }

    createLogsDirectory() {
        if (!fs.existsSync(CONFIG.LOGS_DIR)) {
            fs.mkdirSync(CONFIG.LOGS_DIR, { recursive: true });
        }
    }

    setupSignalHandlers() {
        const cleanup = () => {
            this.log('\n🛑 Shutting down services...', colors.yellow);
            this.processes.forEach(proc => {
                try {
                    process.kill(-proc.pid);
                } catch (e) {
                    // Process might already be dead
                }
            });
            process.exit(0);
        };

        process.on('SIGINT', cleanup);
        process.on('SIGTERM', cleanup);
        process.on('exit', cleanup);
    }

    async checkPort(port) {
        return new Promise((resolve) => {
            const server = net.createServer();
            
            server.listen(port, () => {
                server.once('close', () => resolve(true));
                server.close();
            });
            
            server.on('error', () => resolve(false));
        });
    }

    async waitForService(url, name, maxAttempts = 30) {
        this.log(`⏳ Waiting for ${name} to start...`, colors.yellow);
        
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                const response = await fetch(url);
                if (response.ok) {
                    this.log(`✅ ${name} is ready!`, colors.green);
                    return true;
                }
            } catch (e) {
                // Service not ready yet
            }
            
            process.stdout.write(`\r${colors.yellow}   Attempt ${attempt}/${maxAttempts}...${colors.reset}`);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
        this.log(`\n❌ ${name} failed to start after ${maxAttempts} attempts`, colors.red);
        return false;
    }

    spawnProcess(command, args, options = {}) {
        const proc = spawn(command, args, {
            stdio: 'pipe',
            detached: true,
            ...options
        });

        this.processes.push(proc);
        return proc;
    }

    async checkPrerequisites() {
        this.log('🔍 Checking prerequisites...', colors.cyan);

        // Check Node.js
        try {
            execSync('node --version', { stdio: 'ignore' });
        } catch (e) {
            this.log('❌ Node.js is not installed', colors.red);
            process.exit(1);
        }

        // Check Python
        try {
            execSync('python3 --version', { stdio: 'ignore' });
        } catch (e) {
            this.log('❌ Python3 is not installed', colors.red);
            process.exit(1);
        }

        // Check backend virtual environment
        if (!fs.existsSync('backend/venv')) {
            this.log('❌ Backend virtual environment not found', colors.red);
            this.log('Please run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements/dev.txt', colors.yellow);
            process.exit(1);
        }

        // Check node_modules
        if (!fs.existsSync('node_modules')) {
            this.log('📦 Installing frontend dependencies...', colors.yellow);
            execSync('npm install', { stdio: 'inherit' });
        }
    }

    async checkPorts() {
        this.log('🔌 Checking ports...', colors.cyan);

        const ports = [CONFIG.FRONTEND_PORT, CONFIG.BACKEND_PORT, CONFIG.BACKEND_DEBUG_PORT];
        
        for (const port of ports) {
            const isAvailable = await this.checkPort(port);
            if (!isAvailable) {
                this.log(`❌ Port ${port} is already in use`, colors.red);
                this.log(`Please stop any existing services on port ${port}`, colors.yellow);
                process.exit(1);
            }
        }
    }

    async startDockerServices() {
        this.log('🐳 Starting Docker services...', colors.cyan);
        
        try {
            execSync('docker-compose up mongodb redis -d', { stdio: 'inherit' });
            this.log('⏳ Waiting for MongoDB...', colors.yellow);
            await new Promise(resolve => setTimeout(resolve, 5000));
        } catch (e) {
            this.log('❌ Failed to start Docker services', colors.red);
            process.exit(1);
        }
    }

    startBackend() {
        this.log('🔧 Starting backend with debugging...', colors.cyan);
        
        const backendLog = fs.createWriteStream(path.join(CONFIG.LOGS_DIR, 'backend.log'));
        
        const backend = this.spawnProcess('python', [
            '-m', 'debugpy',
            '--listen', `0.0.0.0:${CONFIG.BACKEND_DEBUG_PORT}`,
            '--wait-for-client',
            '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', CONFIG.BACKEND_PORT.toString(),
            '--reload',
            '--reload-dir', 'app',
            '--log-level', 'info'
        ], {
            cwd: 'backend',
            env: {
                ...process.env,
                VIRTUAL_ENV: path.resolve('backend/venv'),
                PATH: `${path.resolve('backend/venv/bin')}:${process.env.PATH}`
            }
        });

        backend.stdout.pipe(backendLog);
        backend.stderr.pipe(backendLog);

        this.log(`✅ Backend started (PID: ${backend.pid})`, colors.green);
        this.log(`🐛 Debugger waiting for client on port ${CONFIG.BACKEND_DEBUG_PORT}`, colors.blue);
        
        return backend;
    }

    startFrontend() {
        this.log('⚛️  Starting frontend...', colors.cyan);
        
        const frontendLog = fs.createWriteStream(path.join(CONFIG.LOGS_DIR, 'frontend.log'));
        
        const frontend = this.spawnProcess('npm', ['run', 'dev']);
        
        frontend.stdout.pipe(frontendLog);
        frontend.stderr.pipe(frontendLog);

        this.log(`✅ Frontend started (PID: ${frontend.pid})`, colors.green);
        
        return frontend;
    }

    showInformation() {
        this.log('', colors.reset);
        this.log('🎉 All services are running!', colors.green);
        this.log('================================', colors.magenta);
        this.log('', colors.reset);
        this.log('📱 Application URLs:', colors.cyan);
        this.log(`  🌐 Frontend:  http://localhost:${CONFIG.FRONTEND_PORT}`, colors.blue);
        this.log(`  🔧 Backend:   http://localhost:${CONFIG.BACKEND_PORT}`, colors.blue);
        this.log(`  📚 API Docs:  http://localhost:${CONFIG.BACKEND_PORT}/docs`, colors.blue);
        this.log('', colors.reset);
        this.log('🐛 Debugging:', colors.cyan);
        this.log(`  🔍 Debug Port: localhost:${CONFIG.BACKEND_DEBUG_PORT}`, colors.blue);
        this.log('  📝 VS Code: Add debug config (see .vscode/launch.json)', colors.blue);
        this.log('', colors.reset);
        this.log('📊 Logs:', colors.cyan);
        this.log(`  📜 Backend:  tail -f ${CONFIG.LOGS_DIR}/backend.log`, colors.yellow);
        this.log(`  📜 Frontend: tail -f ${CONFIG.LOGS_DIR}/frontend.log`, colors.yellow);
        this.log('', colors.reset);
        this.log('🛠️  Development Tips:', colors.cyan);
        this.log('  • Backend auto-reloads on file changes', colors.reset);
        this.log('  • Frontend has hot module replacement', colors.reset);
        this.log(`  • Attach debugger to port ${CONFIG.BACKEND_DEBUG_PORT}`, colors.reset);
        this.log('  • Use Ctrl+C to stop all services', colors.blue);
        this.log('', colors.reset);
    }

    async run() {
        this.log('🚀 Elenchus AI Development Runner', colors.magenta);
        this.log('===================================', colors.magenta);
        this.log('', colors.reset);
        this.log('Configuration:', colors.cyan);
        this.log(`  Frontend: http://localhost:${CONFIG.FRONTEND_PORT}`, colors.reset);
        this.log(`  Backend:  http://localhost:${CONFIG.BACKEND_PORT}`, colors.reset);
        this.log(`  Debug:    localhost:${CONFIG.BACKEND_DEBUG_PORT}`, colors.reset);
        this.log(`  Logs:     ${CONFIG.LOGS_DIR}/`, colors.reset);
        this.log('', colors.reset);

        await this.checkPrerequisites();
        await this.checkPorts();
        await this.startDockerServices();
        
        const backend = this.startBackend();
        const frontend = this.startFrontend();

        // Wait for frontend to be ready
        await this.waitForService(`http://localhost:${CONFIG.FRONTEND_PORT}`, 'Frontend');
        
        this.showInformation();

        // Keep the process alive
        await new Promise(() => {});
    }
}

// Run the development server
if (require.main === module) {
    const runner = new DevRunner();
    runner.run().catch(console.error);
}

module.exports = DevRunner;