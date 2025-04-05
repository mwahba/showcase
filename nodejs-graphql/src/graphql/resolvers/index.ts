import { appResolvers } from "./app.resolver";
import { campaignResolvers } from "./campaign.resolver";
import { adGroupResolvers } from "./ad-group.resolver";
import { adResolvers } from "./ad.resolver";
import { Resolvers } from "../types";

export const resolvers: Resolvers = {
  Query: {
    ...appResolvers.Query,
    ...campaignResolvers.Query,
    ...adGroupResolvers.Query,
    ...adResolvers.Query,
  },
  Mutation: {
    ...appResolvers.Mutation,
    ...campaignResolvers.Mutation,
    ...adGroupResolvers.Mutation,
    ...adResolvers.Mutation,
  },
  App: appResolvers.App,
  Campaign: campaignResolvers.Campaign,
  AdGroup: adGroupResolvers.AdGroup,
  Ad: adResolvers.Ad,
};
