import { PrismaClient } from "@prisma/client";
import { AdGroupService } from "../../services/ad-group.service";
import { AdService } from "../../services/ad.service";
import { CampaignService } from "../../services/campaign.service";
import {
  MutationCreateAdGroupArgs,
  MutationDeleteAdGroupArgs,
  MutationUpdateAdGroupArgs,
  QueryGetAdGroupArgs,
  QueryListAdGroupsByCampaignArgs,
  Resolvers,
} from "../types";

export const adGroupResolvers: Resolvers = {
  Query: {
    getAdGroup: async (
      _parent,
      { id }: QueryGetAdGroupArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adGroupService = new AdGroupService(prisma);
      return adGroupService.findById(id);
    },

    listAdGroupsByCampaign: async (
      _parent,
      { campaignId }: QueryListAdGroupsByCampaignArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adGroupService = new AdGroupService(prisma);
      return adGroupService.findByCampaignId(campaignId);
    },
  },

  Mutation: {
    createAdGroup: async (
      _parent,
      { input }: MutationCreateAdGroupArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adGroupService = new AdGroupService(prisma);
      return adGroupService.create(input);
    },

    updateAdGroup: async (
      _parent,
      data: MutationUpdateAdGroupArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adGroupService = new AdGroupService(prisma);
      return adGroupService.update(data);
    },

    deleteAdGroup: async (
      _parent,
      { id }: MutationDeleteAdGroupArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adGroupService = new AdGroupService(prisma);
      return adGroupService.delete(id);
    },
  },

  // Type resolvers
  AdGroup: {
    campaign: async (
      parent,
      _args: any,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const campaignService = new CampaignService(prisma);
      const campaign = await campaignService.findById(parent.campaignId);

      if (!campaign) {
        throw new Error(
          `AdGroup ${parent.id} has a Campaign ID ${parent.campaignId} that did not return a proper Campaign.`,
        );
      }

      return campaign;
    },

    ads: async (parent, _args: any, { prisma }: { prisma: PrismaClient }) => {
      const adService = new AdService(prisma);
      return adService.findByAdGroupId(parent.id);
    },
  },
};
