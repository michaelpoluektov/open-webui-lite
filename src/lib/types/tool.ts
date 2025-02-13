export interface Tool {
	id: string;
	name: string;
	meta?: {
		description?: string;
		[key: string]: any;
	};
} 