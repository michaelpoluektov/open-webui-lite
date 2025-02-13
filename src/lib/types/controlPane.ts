export interface ControlPane {
    id: string;
    type: string;
    title: string;
    content?: string;
    component?: any;
    props?: Record<string, any>;
    meta?: Record<string, any>;
} 