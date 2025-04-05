import { PrismaClient } from "@prisma/client";
import { AdGroupService } from "../../services/ad-group.service";
import { AdService } from "../../services/ad.service";
import {
  MutationCreateAdArgs,
  MutationDeleteAdArgs,
  MutationUpdateAdArgs,
  QueryGetAdArgs,
  QueryGetAdPerformanceArgs,
  QueryListAdsByAdGroupArgs,
  Resolvers,
} from "../types";

export const adResolvers: Resolvers = {
  Query: {
    getAd: async (
      _parent,
      { id }: QueryGetAdArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adService = new AdService(prisma);
      return adService.findById(id);
    },

    listAdsByAdGroup: async (
      _parent,
      { adGroupId }: QueryListAdsByAdGroupArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adService = new AdService(prisma);
      return adService.findByAdGroupId(adGroupId);
    },

    getAdPerformance: async (
      _parent,
      { adId, startDate, endDate }: QueryGetAdPerformanceArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adService = new AdService(prisma);
      const startDateObj = startDate ? new Date(startDate) : undefined;
      const endDateObj = endDate ? new Date(endDate) : undefined;
      return adService.getPerformance(adId, startDateObj, endDateObj);
    },
  },

  Mutation: {
    createAd: async (
      _parent,
      { input }: MutationCreateAdArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adService = new AdService(prisma);
      return adService.create(input);
    },

    updateAd: async (
      _parent,
      { input }: MutationUpdateAdArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adService = new AdService(prisma);
      const { id } = input;
      return adService.update(input);
    },

    deleteAd: async (
      _parent,
      { id }: MutationDeleteAdArgs,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adService = new AdService(prisma);
      return adService.delete(id);
    },
  },

  // Type resolvers
  Ad: {
    adGroup: async (
      parent,
      _args: any,
      { prisma }: { prisma: PrismaClient },
    ) => {
      const adGroupService = new AdGroupService(prisma);
      const adGroup = await adGroupService.findById(parent!.adGroupId!);

      if (!adGroup) {
        throw new Error(
          `Ad ${parent.id} has an AdGroup ${parent.adGroupId} that did not return a proper AdGroup.`,
        );
      }

      return adGroup;
    },
  },
};
