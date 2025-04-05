import { AdStatus, Gender, DeviceType } from "@prisma/client";

export interface AdGroup {
  id: string;
  name: string;
  description?: string;
  campaignId: string;
  keywords: string[];
  locations: string[];
  gender: Gender;
  deviceType: DeviceType;
  minAge?: number;
  maxAge?: number;
  status: AdStatus;
  createdAt: Date;
  updatedAt: Date;
}

export interface AdGroupCreateInput {
  campaignId: string;
  name: string;
  description?: string;
  keywords?: string[];
  locations?: string[];
  gender?: Gender;
  deviceType?: DeviceType;
  minAge?: number;
  maxAge?: number;
}

export interface AdGroupUpdateInput {
  name?: string;
  description?: string;
  keywords?: string[];
  locations?: string[];
  gender?: Gender;
  deviceType?: DeviceType;
  minAge?: number;
  maxAge?: number;
  status?: AdStatus;
}
