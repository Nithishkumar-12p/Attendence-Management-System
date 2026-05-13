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
    title: "Industrial Attendance Management System"
  });

  // Load the login page
  mainWindow.loadFile(path.join(__dirname, 'pages/login.html'));

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

function startPythonBackend() {
  const isPackaged = app.isPackaged;
  let pythonPath;
  let args;
  let options = {
    cwd: path.join(__dirname, '..')
  };

  if (isPackaged) {
    // In packaged app, the executable is in resources folder
    pythonPath = path.join(process.resourcesPath, 'backend.exe');
    args = [];
    options.cwd = process.resourcesPath;
  } else {
    // In development mode
    const rootDir = path.join(__dirname, '..');
    pythonPath = process.platform === 'win32' 
      ? path.join(rootDir, 'backend/venv/Scripts/python.exe') 
      : path.join(rootDir, 'backend/venv/bin/python');
    args = ['-m', 'backend.app'];
  }
  
  console.log(`Starting backend: ${pythonPath} with args ${args}`);
  pythonProcess = spawn(pythonPath, args, options);

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
