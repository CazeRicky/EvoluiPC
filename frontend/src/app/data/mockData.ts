// Mock data structure based on Django backend API responses

export interface MachineSnapshot {
  cpu: string;
  gpu: string;
  ram: string;
  motherboard: string;
  storage: string;
  psu: string;
  performance_score: number;
  compatibility_score: number;
}

export interface Diagnostic {
  id: string;
  message: string;
  severity: 'info' | 'warning' | 'critical';
  component: string;
}

export interface UpgradeStep {
  step: number;
  action: string;
  component: string;
  impact: string;
  impact_percentage: number;
  estimated_cost: number;
  priority: 'high' | 'medium' | 'low';
}

export interface CatalogItem {
  id: string;
  name: string;
  type: 'cpu' | 'gpu' | 'ram' | 'storage' | 'psu' | 'motherboard';
  price: number;
  source: string;
  affiliate_link: string;
  tag: string;
  compatibility: number;
  performance_gain: number;
  image?: string;
}

export interface UserData {
  username: string;
  email: string;
  token: string;
}

// Mock data
export const mockMachine: MachineSnapshot = {
  cpu: 'AMD Ryzen 5 3600',
  gpu: 'NVIDIA GTX 1660',
  ram: '8GB DDR4 2666MHz',
  motherboard: 'ASUS PRIME A320M-K',
  storage: 'SSD SATA 240GB',
  psu: 'Fonte 500W 80+ White',
  performance_score: 65,
  compatibility_score: 89,
};

export const mockDiagnostics: Diagnostic[] = [
  {
    id: '1',
    message: 'GPU é o principal gargalo do sistema',
    severity: 'critical',
    component: 'gpu',
  },
  {
    id: '2',
    message: 'RAM insuficiente para jogos modernos',
    severity: 'warning',
    component: 'ram',
  },
  {
    id: '3',
    message: 'Placa-mãe limita upgrade de CPU',
    severity: 'warning',
    component: 'motherboard',
  },
  {
    id: '4',
    message: 'SSD SATA pode ser substituído por NVMe',
    severity: 'info',
    component: 'storage',
  },
];

export const mockUpgradeRoute: UpgradeStep[] = [
  {
    step: 1,
    action: 'Upgrade de GPU',
    component: 'RTX 3060 12GB',
    impact: '+42% Performance em jogos',
    impact_percentage: 42,
    estimated_cost: 1590,
    priority: 'high',
  },
  {
    step: 2,
    action: 'Adicionar RAM',
    component: '8GB DDR4 (Total 16GB)',
    impact: '+18% Performance geral',
    impact_percentage: 18,
    estimated_cost: 285,
    priority: 'high',
  },
  {
    step: 3,
    action: 'Upgrade de Storage',
    component: 'SSD NVMe 500GB',
    impact: '+65% Velocidade de carregamento',
    impact_percentage: 65,
    estimated_cost: 320,
    priority: 'medium',
  },
  {
    step: 4,
    action: 'Upgrade de CPU',
    component: 'Ryzen 7 5700X',
    impact: '+28% Performance de CPU',
    impact_percentage: 28,
    estimated_cost: 890,
    priority: 'medium',
  },
  {
    step: 5,
    action: 'Upgrade de PSU',
    component: 'Fonte 650W 80+ Bronze',
    impact: 'Estabilidade e segurança',
    impact_percentage: 0,
    estimated_cost: 380,
    priority: 'low',
  },
];

export const mockCatalog: CatalogItem[] = [
  {
    id: '1',
    name: 'NVIDIA RTX 3060 12GB',
    type: 'gpu',
    price: 1590,
    source: 'Kabum',
    affiliate_link: 'https://kabum.com.br/rtx-3060',
    tag: 'Melhor custo-benefício',
    compatibility: 95,
    performance_gain: 42,
  },
  {
    id: '2',
    name: 'Kingston Fury 8GB DDR4 2666MHz',
    type: 'ram',
    price: 285,
    source: 'Pichau',
    affiliate_link: 'https://pichau.com.br/ram',
    tag: 'Compatível',
    compatibility: 100,
    performance_gain: 18,
  },
  {
    id: '3',
    name: 'WD Black SN770 500GB NVMe',
    type: 'storage',
    price: 320,
    source: 'Terabyte',
    affiliate_link: 'https://terabyte.com.br/ssd',
    tag: 'Alta velocidade',
    compatibility: 92,
    performance_gain: 65,
  },
  {
    id: '4',
    name: 'AMD Ryzen 7 5700X',
    type: 'cpu',
    price: 890,
    source: 'Kabum',
    affiliate_link: 'https://kabum.com.br/ryzen-7',
    tag: 'Melhor CPU AM4',
    compatibility: 78,
    performance_gain: 28,
  },
  {
    id: '5',
    name: 'Corsair CV650 650W 80+ Bronze',
    type: 'psu',
    price: 380,
    source: 'Pichau',
    affiliate_link: 'https://pichau.com.br/fonte',
    tag: 'Confiável',
    compatibility: 100,
    performance_gain: 0,
  },
  {
    id: '6',
    name: 'AMD RX 6600 8GB',
    type: 'gpu',
    price: 1390,
    source: 'Terabyte',
    affiliate_link: 'https://terabyte.com.br/rx-6600',
    tag: 'Alternativa AMD',
    compatibility: 95,
    performance_gain: 38,
  },
];

// API simulation functions
export const loginUser = async (username: string, password: string): Promise<UserData> => {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return {
    username,
    email: `${username}@example.com`,
    token: 'mock_token_12345',
  };
};

export const registerUser = async (
  username: string,
  email: string,
  password: string
): Promise<UserData> => {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return {
    username,
    email,
    token: 'mock_token_12345',
  };
};

export const fetchMachineData = async (): Promise<MachineSnapshot> => {
  await new Promise((resolve) => setTimeout(resolve, 800));
  return mockMachine;
};

export const fetchDiagnostics = async (): Promise<Diagnostic[]> => {
  await new Promise((resolve) => setTimeout(resolve, 800));
  return mockDiagnostics;
};

export const fetchUpgradeRoute = async (): Promise<UpgradeStep[]> => {
  await new Promise((resolve) => setTimeout(resolve, 800));
  return mockUpgradeRoute;
};

export const fetchCatalog = async (): Promise<CatalogItem[]> => {
  await new Promise((resolve) => setTimeout(resolve, 800));
  return mockCatalog;
};
