# EvoluiPC Mobile - Capacitor Setup

## Desenvolvimento

### 1. Executar Frontend em Desenvolvimento
```bash
npm run dev
```
Isso inicia o Vite em `http://localhost:5173/`

### 2. Para Teste em Dispositivo Durante Dev

#### Windows/Linux
```bash
# Editar capacitor.config.json e trocar "server.url" para seu IP local
# Exemplo: "url": "http://192.168.X.X:5173"
# Depois:
npx cap run android --live-reload
# ou
npx cap run ios --live-reload
```

## Build e Deploy

### Android APK
```bash
npm run cap:android
```

Isso vai:
1. Compilar o frontend para `dist/`
2. Sincronizar com Capacitor
3. Abrir o Android Studio para build/emulação

### iOS App
```bash
npm run cap:ios
```

Isso vai:
1. Compilar o frontend para `dist/`
2. Sincronizar com Capacitor
3. Abrir o Xcode para build/emulação

## Web Deployment

Para deployer como PWA web sem Capacitor:
```bash
npm run build
# Servir a pasta dist/ com um servidor HTTP
```

## Estrutura

- `src/` - Código fonte React
- `dist/` - Build otimizado (criado por `npm run build`)
- `android/` - Projeto Android (criado por `npx cap add android`)
- `ios/` - Projeto iOS (criado por `npx cap add ios`)
- `public/` - Assets estáticos e manifest.json

## Próximas Etapas

1. Executar `npm run cap:android` para criar o projeto Android
2. Testar a compilação e a conexão com o backend Django em `http://127.0.0.1:8000/api`
3. Compilar APK final para distribuição
