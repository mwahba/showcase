// src/models/ad.model.ts
import { AdStatus } from "@prisma/client";

export interface Ad {
  id: string;
  title: string;
  description: string;
  adGroupId: string;
  imageUrl?: string;
  destinationUrl: string;
  impressions: number;
  clicks: number;
  status: AdStatus;
  createdAt: Date;
  updatedAt: Date;
}

export interface AdCreateInput {
  adGroupId: string;
  title: string;
  description: string;
  imageUrl?: string;
  destinationUrl: string;
}

export interface AdUpdateInput {
  title?: string;
  description?: string;
  imageUrl?: string;
  destinationUrl?: string;
  status?: AdStatus;
}

export interface AdPerformance {
  id: string;
  adId: string;
  date: Date;
  impressions: number;
  clicks: number;
  spend: number;
}
