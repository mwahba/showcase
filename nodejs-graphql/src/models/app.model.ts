export interface App {
  id: string;
  name: string;
  description?: string;
  apiKey: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface AppCreateInput {
  name: string;
  description?: string;
}

export interface AppUpdateInput {
  name?: string;
  description?: string;
}
