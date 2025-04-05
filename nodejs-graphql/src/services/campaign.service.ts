import { PrismaClient, AdStatus } from "@prisma/client";
import {
  CampaignCreateInput,
  CampaignUpdateInput,
} from "../models/campaign.model";
import { validateCampaignInput } from "../utils/validation";
import {
  CreateCampaignInput,
  MutationUpdateCampaignArgs,
} from "../graphql/types";
import { sanitizePrismaData } from "../utils/service-utils";

export class CampaignService {
  constructor(private prisma: PrismaClient) {}

  async findAll() {
    return this.prisma.campaign.findMany();
  }

  async findById(id: string) {
    return this.prisma.campaign.findUnique({
      where: { id },
      include: { adGroups: true },
    });
  }

  async findByAppId(appId: string) {
    return this.prisma.campaign.findMany({
      where: { appId },
      include: { adGroups: true },
    });
  }

  async create(data: CreateCampaignInput) {
    validateCampaignInput(data);

    // Check if app exists
    const app = await this.prisma.app.findUnique({ where: { id: data.appId } });
    if (!app) {
      throw new Error(`App with ID ${data.appId} not found`);
    }

    return this.prisma.campaign.create({
      data: {
        ...data,
        status: AdStatus.DRAFT,
      },
    });
  }

  async update(input: MutationUpdateCampaignArgs) {
    const { id, ...data } = input;
    // Check if campaign exists
    const campaign = await this.prisma.campaign.findUnique({ where: { id } });
    if (!campaign) {
      throw new Error(`Campaign with ID ${id} not found`);
    }

    const prismaData = sanitizePrismaData(data);

    return this.prisma.campaign.update({
      where: { id },
      data: prismaData,
    });
  }

  async delete(id: string) {
    // Check if campaign exists
    const campaign = await this.prisma.campaign.findUnique({ where: { id } });
    if (!campaign) {
      throw new Error(`Campaign with ID ${id} not found`);
    }

    await this.prisma.campaign.delete({ where: { id } });
    return true;
  }
}
