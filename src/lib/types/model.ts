export interface Model {
	id: string;
	name: string;
	info?: {
		meta?: {
			capabilities?: {
				vision?: boolean;
			};
			[key: string]: any;
		};
	};
} 