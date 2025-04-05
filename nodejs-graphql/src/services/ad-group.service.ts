import { PrismaClient, AdStatus, Gender, DeviceType } from "@prisma/client";
import {
  AdGroupCreateInput,
  AdGroupUpdateInput,
} from "../models/ad-group.model";
import { validateAdGroupInput } from "../utils/validation";
import {
  CreateAdGroupInput,
  MutationUpdateAdGroupArgs,
} from "../graphql/types";
import { sanitizePrismaData } from "../utils/service-utils";

export class AdGroupService {
  constructor(private prisma: PrismaClient) {}

  async findAll() {
    return this.prisma.adGroup.findMany();
  }

  async findById(id: string) {
    return this.prisma.adGroup.findUnique({
      where: { id },
      include: { ads: true },
    });
  }

  async findByCampaignId(campaignId: string) {
    return this.prisma.adGroup.findMany({
      where: { campaignId },
      include: { ads: true },
    });
  }

  async create(data: CreateAdGroupInput) {
    validateAdGroupInput(data);

    // Check if campaign exists
    const campaign = await this.prisma.campaign.findUnique({
      where: { id: data.campaignId },
    });

    if (!campaign) {
      throw new Error(`Campaign with ID ${data.campaignId} not found`);
    }

    return this.prisma.adGroup.create({
      data: {
        ...data,
        keywords: data.keywords || [],
        locations: data.locations || [],
        gender: data.gender || Gender.ALL,
        deviceType: data.deviceType || DeviceType.ALL,
        status: AdStatus.DRAFT,
      },
    });
  }

  async update(input: MutationUpdateAdGroupArgs) {
    const { id, ...data } = input;
    // Check if ad group exists
    const adGroup = await this.prisma.adGroup.findUnique({ where: { id } });
    if (!adGroup) {
      throw new Error(`Ad Group with ID ${id} not found`);
    }

    const prismaData = sanitizePrismaData(data);

    return this.prisma.adGroup.update({
      where: { id },
      data: prismaData,
    });
  }

  async delete(id: string) {
    // Check if ad group exists
    const adGroup = await this.prisma.adGroup.findUnique({ where: { id } });
    if (!adGroup) {
      throw new Error(`Ad Group with ID ${id} not found`);
    }

    await this.prisma.adGroup.delete({ where: { id } });
    return true;
  }
}
