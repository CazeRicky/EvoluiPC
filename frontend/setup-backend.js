#!/usr/bin/env node

import fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';
import readline from 'readline';

const execAsync = promisify(exec);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const question = (prompt) => new Promise((resolve) => {
  rl.question(prompt, resolve);
});

async function getLocalIP() {
  try {
    if (process.platform === 'win32') {
      const { stdout } = await execAsync('ipconfig');
      const match = stdout.match(/IPv4 Address.*?(\d+\.\d+\.\d+\.\d+)/);
      return match ? match[1] : null;
    } else {
      const { stdout } = await execAsync("ifconfig | grep 'inet ' | grep -v '127.0.0.1'");
      const match = stdout.match(/inet (\d+\.\d+\.\d+\.\d+)/);
      return match ? match[1] : null;
    }
  } catch {
    return null;
  }
}

async function setupBackendURL() {
  console.log('🚀 EvoluiPC - Configurador de Backend\n');

  const detectedIP = await getLocalIP();
  
  let apiURL = `http://localhost:8000/api`;

  if (detectedIP) {
    console.log(`✅ IP Local Detectado: ${detectedIP}`);
    const useDetected = await question(`\nUsar ${detectedIP}:8000 como backend? (s/n): `);
    
    if (useDetected.toLowerCase() === 's' || useDetected === '') {
      apiURL = `http://${detectedIP}:8000/api`;
    }
  }

  const customIP = await question('\n(Opcional) Digite um IP customizado (deixe em branco para usar a sugestão): ');
  
  if (customIP.trim()) {
    apiURL = `http://${customIP.trim()}:8000/api`;
  }

  const envLocalContent = `# EvoluiPC Backend Configuration
# Gerado automaticamente em ${new Date().toISOString()}
VITE_API_BASE_URL=${apiURL}
`;

  fs.writeFileSync('.env.local', envLocalContent, 'utf-8');
  
  console.log('\n✅ Arquivo .env.local atualizado com sucesso!');
  console.log(`📍 Backend URL: ${apiURL}`);
  console.log('\n💡 Certifique-se de que o Django está rodando em: 0.0.0.0:8000');
  
  rl.close();
}

setupBackendURL().catch(console.error);
