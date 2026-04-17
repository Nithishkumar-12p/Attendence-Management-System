const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    icon: path.join(__dirname, 'assets/icon.ico'),
    title: "Industrial Attendance Management System"
  });

  // Load the login page
  mainWindow.loadFile(path.join(__dirname, 'pages/login.html'));

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

function startPythonBackend() {
  // Python is in ../backend/venv
  const rootDir = path.join(__dirname, '..');
  const pythonPath = process.platform === 'win32' 
    ? path.join(rootDir, 'backend/venv/Scripts/python.exe') 
    : path.join(rootDir, 'backend/venv/bin/python');
  
  // Starting it from root directory so backend.app package logic works
  pythonProcess = spawn(pythonPath, ['-m', 'backend.app'], {
    cwd: rootDir
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });
}

app.on('ready', () => {
  startPythonBackend();
  createWindow();
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});
