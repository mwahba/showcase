import { AdStatus } from "@prisma/client";

export interface Campaign {
  id: string;
  name: string;
  description?: string;
  appId: string;
  startDate: Date;
  endDate?: Date;
  budget: number;
  status: AdStatus;
  createdAt: Date;
  updatedAt: Date;
}

export interface CampaignCreateInput {
  appId: string;
  name: string;
  description?: string;
  startDate: Date;
  endDate?: Date;
  budget: number;
}

export interface CampaignUpdateInput {
  name?: string;
  description?: string;
  startDate?: Date;
  endDate?: Date;
  budget?: number;
  status?: AdStatus;
}
