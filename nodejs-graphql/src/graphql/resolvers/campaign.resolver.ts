import { PrismaClient } from "@prisma/client";
import { AdGroupService } from "../../services/ad-group.service";
import { AppService } from "../../services/app.service";
import { CampaignService } from "../../services/campaign.service";
import {
  MutationCreateCampaignArgs,
  MutationUpdateCampaignArgs,
  QueryGetCampaignArgs,
  QueryListCampaignsByAppArgs,
  Resolvers,
  Campaign,
} from "../types";

export const campaignResolvers: Resolvers = {
  Query: {
    getCampaign: async (
      _parent,
      { id }: QueryGetCampaignArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const campaignService = new CampaignService(prisma);
      return campaignService.findById(id);
    },

    listCampaignsByApp: async (
      _parent,
      { appId }: QueryListCampaignsByAppArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const campaignService = new CampaignService(prisma);
      return campaignService.findByAppId(appId);
    },
  },

  Mutation: {
    createCampaign: async (
      _parent,
      { input }: MutationCreateCampaignArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const campaignService = new CampaignService(prisma);
      return campaignService.create(input);
    },

    updateCampaign: async (
      _parent,
      data: MutationUpdateCampaignArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const campaignService = new CampaignService(prisma);
      return campaignService.update(data);
    },

    deleteCampaign: async (
      _parent,
      { id }: { id: string },
      { prisma }: { prisma: PrismaClient },
    ) => {
      const campaignService = new CampaignService(prisma);
      return campaignService.delete(id);
    },
  },

  // Type resolvers
  Campaign: {
    app: async (parent, _args: any, { prisma }: { prisma: PrismaClient }) => {
      const appService = new AppService(prisma);
      const app = await appService.findById(parent.appId);

      if (!app) {
        throw new Error(
          `Campaign ${parent.id} has an app ID ${parent.appId} that did not return a proper App.`,
        );
      }

      return {
        ...app,
        description: app.description ?? null,
        createdAt:
          app.createdAt instanceof Date
            ? app.createdAt
            : new Date(app.createdAt),
        updatedAt:
          app.updatedAt instanceof Date
            ? app.updatedAt
            : new Date(app.updatedAt),
      };
    },

    adGroups: async (
      parent,
      _args: any,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adGroupService = new AdGroupService(prisma);
      return adGroupService.findByCampaignId(parent.id);
    },
  },
};
