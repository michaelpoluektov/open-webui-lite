export interface ChatHistory {
    messages: Record<string, any>;
    currentId: string | null;
}

export interface PreservedHistory {
    chatId: string;
    history: ChatHistory;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
    status?: string;
    meta?: Record<string, any>;
}

export interface Chat {
    id: string;
    title: string;
    models: string[];
    system?: string;
    params: Record<string, any>;
    history: ChatHistory;
    messages: Message[];
    timestamp: number;
    meta?: Record<string, any>;
} 