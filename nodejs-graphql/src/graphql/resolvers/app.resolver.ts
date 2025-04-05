import { PrismaClient } from "@prisma/client";
import { AppService } from "../../services/app.service";
import { CampaignService } from "../../services/campaign.service";
import {
  MutationCreateAppArgs,
  MutationDeleteAppArgs,
  MutationUpdateAppArgs,
  QueryGetAppArgs,
  Resolvers,
} from "../types";

export const appResolvers: Resolvers = {
  Query: {
    getApp: async (
      _parent,
      { id }: QueryGetAppArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const appService = new AppService(prisma);
      return appService.findById(id);
    },

    listApps: async (
      _parent,
      _args: any,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const appService = new AppService(prisma);
      return appService.findAll();
    },
  },

  Mutation: {
    createApp: async (
      _parent,
      { input }: MutationCreateAppArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const appService = new AppService(prisma);
      return appService.create(input);
    },

    updateApp: async (
      _parent,
      { id, ...data }: MutationUpdateAppArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const appService = new AppService(prisma);
      const name = data.name ? data.name : undefined;
      const description = data.description ? data.description : undefined;
      return appService.update(id, name, description);
    },

    deleteApp: async (
      _parent,
      { id }: MutationDeleteAppArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const appService = new AppService(prisma);
      return appService.delete(id);
    },
  },

  // Type resolvers
  App: {
    campaigns: async (
      parent: any,
      _args: any,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const campaignService = new CampaignService(prisma);
      return campaignService.findByAppId(parent.id);
    },
  },
};
