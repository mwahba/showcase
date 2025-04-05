// src/services/ad.service.ts
import { PrismaClient, AdStatus } from "@prisma/client";
import { AdCreateInput, AdUpdateInput } from "../models/ad.model";
import { validateAdInput } from "../utils/validation";
import { CreateAdInput, UpdateAdInput } from "../graphql/types";
import { sanitizePrismaData } from "../utils/service-utils";

export class AdService {
  constructor(private prisma: PrismaClient) {}

  async findAll() {
    return this.prisma.ad.findMany();
  }

  async findById(id: string) {
    return this.prisma.ad.findUnique({
      where: { id },
    });
  }

  async findByAdGroupId(adGroupId: string) {
    return this.prisma.ad.findMany({
      where: { adGroupId },
    });
  }

  async create(data: CreateAdInput) {
    validateAdInput(data);

    // Check if ad group exists
    const adGroup = await this.prisma.adGroup.findUnique({
      where: { id: data.adGroupId },
    });

    if (!adGroup) {
      throw new Error(`Ad Group with ID ${data.adGroupId} not found`);
    }

    return this.prisma.ad.create({
      data: {
        ...data,
        impressions: 0,
        clicks: 0,
        status: AdStatus.DRAFT,
      },
    });
  }

  async update(input: UpdateAdInput) {
    const { id, ...data } = input;
    const ad = await this.prisma.ad.findUnique({ where: { id } });
    if (!ad) {
      throw new Error(`Ad with ID ${id} not found`);
    }

    const prismaData = sanitizePrismaData(data);

    return this.prisma.ad.update({
      where: { id },
      data: prismaData,
    });
  }

  async delete(id: string) {
    // Check if ad exists
    const ad = await this.prisma.ad.findUnique({ where: { id } });
    if (!ad) {
      throw new Error(`Ad with ID ${id} not found`);
    }

    await this.prisma.ad.delete({ where: { id } });
    return true;
  }

  async getPerformance(
    adId: string,
    startDate?: Date | null,
    endDate?: Date | null,
  ) {
    const where: any = { adId };

    if (startDate && endDate) {
      where.date = {
        gte: startDate,
        lte: endDate,
      };
    } else if (startDate) {
      where.date = { gte: startDate };
    } else if (endDate) {
      where.date = { lte: endDate };
    }

    return this.prisma.adPerformance.findMany({ where });
  }

  async recordImpression(adId: string) {
    // Atomic update of impressions count
    await this.prisma.ad.update({
      where: { id: adId },
      data: { impressions: { increment: 1 } },
    });

    // Record in performance tracking
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    await this.prisma.adPerformance.upsert({
      where: {
        adId_date: { adId, date: today },
      },
      update: {
        impressions: { increment: 1 },
      },
      create: {
        adId,
        date: today,
        impressions: 1,
        clicks: 0,
        spend: 0,
      },
    });

    return true;
  }

  async recordClick(adId: string) {
    // Atomic update of clicks count
    await this.prisma.ad.update({
      where: { id: adId },
      data: { clicks: { increment: 1 } },
    });

    // Record in performance tracking
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    await this.prisma.adPerformance.upsert({
      where: {
        adId_date: { adId, date: today },
      },
      update: {
        clicks: { increment: 1 },
      },
      create: {
        adId,
        date: today,
        impressions: 0,
        clicks: 1,
        spend: 0,
      },
    });

    return true;
  }
}
