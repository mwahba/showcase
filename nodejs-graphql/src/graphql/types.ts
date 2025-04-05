import {
  GraphQLResolveInfo,
  GraphQLScalarType,
  GraphQLScalarTypeConfig,
} from "graphql";
import {
  AdGroup as AdGroupModel,
  Ad as AdModel,
  App as AppModel,
  Campaign as CampaignModel,
} from ".prisma/client";
export type Maybe<T> = T | null;
export type InputMaybe<T> = undefined | T;
export type Exact<T extends { [key: string]: unknown }> = {
  [K in keyof T]: T[K];
};
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & {
  [SubKey in K]?: Maybe<T[SubKey]>;
};
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & {
  [SubKey in K]: Maybe<T[SubKey]>;
};
export type MakeEmpty<
  T extends { [key: string]: unknown },
  K extends keyof T,
> = { [_ in K]?: never };
export type Incremental<T> =
  | T
  | {
      [P in keyof T]?: P extends " $fragmentName" | "__typename" ? T[P] : never;
    };
export type RequireFields<T, K extends keyof T> = Omit<T, K> & {
  [P in K]-?: NonNullable<T[P]>;
};
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string };
  String: { input: string; output: string };
  Boolean: { input: boolean; output: boolean };
  Int: { input: number; output: number };
  Float: { input: number; output: number };
  DateTime: { input: Date | string; output: Date | string };
};

export type Ad = {
  __typename?: "Ad";
  adGroup: AdGroup;
  clicks: Scalars["Int"]["output"];
  createdAt: Scalars["DateTime"]["output"];
  description: Scalars["String"]["output"];
  destinationUrl: Scalars["String"]["output"];
  id: Scalars["ID"]["output"];
  imageUrl?: Maybe<Scalars["String"]["output"]>;
  impressions: Scalars["Int"]["output"];
  status: AdStatus;
  title: Scalars["String"]["output"];
  updatedAt: Scalars["DateTime"]["output"];
};

export type AdGroup = {
  __typename?: "AdGroup";
  ads?: Maybe<Array<Ad>>;
  campaign: Campaign;
  createdAt: Scalars["DateTime"]["output"];
  description?: Maybe<Scalars["String"]["output"]>;
  deviceType: DeviceType;
  gender: Gender;
  id: Scalars["ID"]["output"];
  keywords?: Maybe<Array<Scalars["String"]["output"]>>;
  locations?: Maybe<Array<Scalars["String"]["output"]>>;
  maxAge?: Maybe<Scalars["Int"]["output"]>;
  minAge?: Maybe<Scalars["Int"]["output"]>;
  name: Scalars["String"]["output"];
  status: AdStatus;
  updatedAt: Scalars["DateTime"]["output"];
};

export type AdPerformance = {
  __typename?: "AdPerformance";
  adId: Scalars["String"]["output"];
  clicks: Scalars["Int"]["output"];
  date: Scalars["DateTime"]["output"];
  id: Scalars["ID"]["output"];
  impressions: Scalars["Int"]["output"];
  spend: Scalars["Float"]["output"];
};

export enum AdStatus {
  Active = "ACTIVE",
  Completed = "COMPLETED",
  Draft = "DRAFT",
  Paused = "PAUSED",
}

export type App = {
  __typename?: "App";
  apiKey: Scalars["String"]["output"];
  campaigns?: Maybe<Array<Campaign>>;
  createdAt: Scalars["DateTime"]["output"];
  description?: Maybe<Scalars["String"]["output"]>;
  id: Scalars["ID"]["output"];
  name: Scalars["String"]["output"];
  updatedAt: Scalars["DateTime"]["output"];
};

export type Campaign = {
  __typename?: "Campaign";
  adGroups?: Maybe<Array<AdGroup>>;
  app: App;
  budget: Scalars["Float"]["output"];
  createdAt: Scalars["DateTime"]["output"];
  description?: Maybe<Scalars["String"]["output"]>;
  endDate?: Maybe<Scalars["DateTime"]["output"]>;
  id: Scalars["ID"]["output"];
  name: Scalars["String"]["output"];
  startDate: Scalars["String"]["output"];
  status: AdStatus;
  updatedAt: Scalars["DateTime"]["output"];
};

export type CreateAdGroupInput = {
  campaignId: Scalars["ID"]["input"];
  description?: InputMaybe<Scalars["String"]["input"]>;
  deviceType?: InputMaybe<DeviceType>;
  gender?: InputMaybe<Gender>;
  keywords?: InputMaybe<Array<Scalars["String"]["input"]>>;
  locations?: InputMaybe<Array<Scalars["String"]["input"]>>;
  maxAge?: InputMaybe<Scalars["Int"]["input"]>;
  minAge?: InputMaybe<Scalars["Int"]["input"]>;
  name: Scalars["String"]["input"];
};

export type CreateAdInput = {
  adGroupId: Scalars["ID"]["input"];
  description: Scalars["String"]["input"];
  destinationUrl: Scalars["String"]["input"];
  imageUrl?: InputMaybe<Scalars["String"]["input"]>;
  title: Scalars["String"]["input"];
};

export type CreateAppInput = {
  description?: InputMaybe<Scalars["String"]["input"]>;
  name: Scalars["String"]["input"];
};

export type CreateCampaignInput = {
  appId: Scalars["ID"]["input"];
  budget: Scalars["Float"]["input"];
  description?: InputMaybe<Scalars["String"]["input"]>;
  endDate?: InputMaybe<Scalars["DateTime"]["input"]>;
  name: Scalars["String"]["input"];
  startDate: Scalars["DateTime"]["input"];
};

export enum DeviceType {
  All = "ALL",
  Desktop = "DESKTOP",
  Mobile = "MOBILE",
  Tablet = "TABLET",
}

export enum Gender {
  All = "ALL",
  Female = "FEMALE",
  Male = "MALE",
  Other = "OTHER",
}

export type Mutation = {
  __typename?: "Mutation";
  _empty?: Maybe<Scalars["String"]["output"]>;
  createAd: Ad;
  createAdGroup: AdGroup;
  createApp: App;
  createCampaign: Campaign;
  deleteAd: Scalars["Boolean"]["output"];
  deleteAdGroup: Scalars["Boolean"]["output"];
  deleteApp: Scalars["Boolean"]["output"];
  deleteCampaign: Scalars["Boolean"]["output"];
  updateAd: Ad;
  updateAdGroup: AdGroup;
  updateApp: App;
  updateCampaign: Campaign;
};

export type MutationCreateAdArgs = {
  input: CreateAdInput;
};

export type MutationCreateAdGroupArgs = {
  input: CreateAdGroupInput;
};

export type MutationCreateAppArgs = {
  input: CreateAppInput;
};

export type MutationCreateCampaignArgs = {
  input: CreateCampaignInput;
};

export type MutationDeleteAdArgs = {
  id: Scalars["ID"]["input"];
};

export type MutationDeleteAdGroupArgs = {
  id: Scalars["ID"]["input"];
};

export type MutationDeleteAppArgs = {
  id: Scalars["ID"]["input"];
};

export type MutationDeleteCampaignArgs = {
  id: Scalars["ID"]["input"];
};

export type MutationUpdateAdArgs = {
  input: UpdateAdInput;
};

export type MutationUpdateAdGroupArgs = {
  description?: InputMaybe<Scalars["String"]["input"]>;
  id: Scalars["ID"]["input"];
  name?: InputMaybe<Scalars["String"]["input"]>;
  status?: InputMaybe<AdStatus>;
};

export type MutationUpdateAppArgs = {
  description?: InputMaybe<Scalars["String"]["input"]>;
  id: Scalars["ID"]["input"];
  name?: InputMaybe<Scalars["String"]["input"]>;
};

export type MutationUpdateCampaignArgs = {
  budget?: InputMaybe<Scalars["Float"]["input"]>;
  description?: InputMaybe<Scalars["String"]["input"]>;
  id: Scalars["ID"]["input"];
  name?: InputMaybe<Scalars["String"]["input"]>;
  status?: InputMaybe<AdStatus>;
};

export type Query = {
  __typename?: "Query";
  _empty?: Maybe<Scalars["String"]["output"]>;
  getAd?: Maybe<Ad>;
  getAdGroup?: Maybe<AdGroup>;
  getAdPerformance: Array<AdPerformance>;
  getApp?: Maybe<App>;
  getCampaign?: Maybe<Campaign>;
  listAdGroupsByCampaign: Array<AdGroup>;
  listAdsByAdGroup: Array<Ad>;
  listApps: Array<App>;
  listCampaignsByApp: Array<Campaign>;
};

export type QueryGetAdArgs = {
  id: Scalars["ID"]["input"];
};

export type QueryGetAdGroupArgs = {
  id: Scalars["ID"]["input"];
};

export type QueryGetAdPerformanceArgs = {
  adId: Scalars["ID"]["input"];
  endDate?: InputMaybe<Scalars["DateTime"]["input"]>;
  startDate?: InputMaybe<Scalars["DateTime"]["input"]>;
};

export type QueryGetAppArgs = {
  id: Scalars["ID"]["input"];
};

export type QueryGetCampaignArgs = {
  id: Scalars["ID"]["input"];
};

export type QueryListAdGroupsByCampaignArgs = {
  campaignId: Scalars["ID"]["input"];
};

export type QueryListAdsByAdGroupArgs = {
  adGroupId: Scalars["ID"]["input"];
};

export type QueryListCampaignsByAppArgs = {
  appId: Scalars["ID"]["input"];
};

export type UpdateAdInput = {
  description?: InputMaybe<Scalars["String"]["input"]>;
  destinationUrl?: InputMaybe<Scalars["String"]["input"]>;
  id: Scalars["ID"]["input"];
  imageUrl?: InputMaybe<Scalars["String"]["input"]>;
  status?: InputMaybe<AdStatus>;
  title?: InputMaybe<Scalars["String"]["input"]>;
};

export type ResolverTypeWrapper<T> = Promise<T> | T;

export type ResolverWithResolve<TResult, TParent, TContext, TArgs> = {
  resolve: ResolverFn<TResult, TParent, TContext, TArgs>;
};
export type Resolver<TResult, TParent = {}, TContext = {}, TArgs = {}> =
  | ResolverFn<TResult, TParent, TContext, TArgs>
  | ResolverWithResolve<TResult, TParent, TContext, TArgs>;

export type ResolverFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo,
) => Promise<TResult> | TResult;

export type SubscriptionSubscribeFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo,
) => AsyncIterable<TResult> | Promise<AsyncIterable<TResult>>;

export type SubscriptionResolveFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo,
) => TResult | Promise<TResult>;

export interface SubscriptionSubscriberObject<
  TResult,
  TKey extends string,
  TParent,
  TContext,
  TArgs,
> {
  subscribe: SubscriptionSubscribeFn<
    { [key in TKey]: TResult },
    TParent,
    TContext,
    TArgs
  >;
  resolve?: SubscriptionResolveFn<
    TResult,
    { [key in TKey]: TResult },
    TContext,
    TArgs
  >;
}

export interface SubscriptionResolverObject<TResult, TParent, TContext, TArgs> {
  subscribe: SubscriptionSubscribeFn<any, TParent, TContext, TArgs>;
  resolve: SubscriptionResolveFn<TResult, any, TContext, TArgs>;
}

export type SubscriptionObject<
  TResult,
  TKey extends string,
  TParent,
  TContext,
  TArgs,
> =
  | SubscriptionSubscriberObject<TResult, TKey, TParent, TContext, TArgs>
  | SubscriptionResolverObject<TResult, TParent, TContext, TArgs>;

export type SubscriptionResolver<
  TResult,
  TKey extends string,
  TParent = {},
  TContext = {},
  TArgs = {},
> =
  | ((
      ...args: any[]
    ) => SubscriptionObject<TResult, TKey, TParent, TContext, TArgs>)
  | SubscriptionObject<TResult, TKey, TParent, TContext, TArgs>;

export type TypeResolveFn<TTypes, TParent = {}, TContext = {}> = (
  parent: TParent,
  context: TContext,
  info: GraphQLResolveInfo,
) => Maybe<TTypes> | Promise<Maybe<TTypes>>;

export type IsTypeOfResolverFn<T = {}, TContext = {}> = (
  obj: T,
  context: TContext,
  info: GraphQLResolveInfo,
) => boolean | Promise<boolean>;

export type NextResolverFn<T> = () => Promise<T>;

export type DirectiveResolverFn<
  TResult = {},
  TParent = {},
  TContext = {},
  TArgs = {},
> = (
  next: NextResolverFn<TResult>,
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo,
) => TResult | Promise<TResult>;

/** Mapping between all available schema types and the resolvers types */
export type ResolversTypes = {
  Ad: ResolverTypeWrapper<AdModel>;
  AdGroup: ResolverTypeWrapper<AdGroupModel>;
  AdPerformance: ResolverTypeWrapper<AdPerformance>;
  AdStatus: AdStatus;
  App: ResolverTypeWrapper<AppModel>;
  Boolean: ResolverTypeWrapper<Scalars["Boolean"]["output"]>;
  Campaign: ResolverTypeWrapper<CampaignModel>;
  CreateAdGroupInput: CreateAdGroupInput;
  CreateAdInput: CreateAdInput;
  CreateAppInput: CreateAppInput;
  CreateCampaignInput: CreateCampaignInput;
  DateTime: ResolverTypeWrapper<Scalars["DateTime"]["output"]>;
  DeviceType: DeviceType;
  Float: ResolverTypeWrapper<Scalars["Float"]["output"]>;
  Gender: Gender;
  ID: ResolverTypeWrapper<Scalars["ID"]["output"]>;
  Int: ResolverTypeWrapper<Scalars["Int"]["output"]>;
  Mutation: ResolverTypeWrapper<{}>;
  Query: ResolverTypeWrapper<{}>;
  String: ResolverTypeWrapper<Scalars["String"]["output"]>;
  UpdateAdInput: UpdateAdInput;
};

/** Mapping between all available schema types and the resolvers parents */
export type ResolversParentTypes = {
  Ad: AdModel;
  AdGroup: AdGroupModel;
  AdPerformance: AdPerformance;
  App: AppModel;
  Boolean: Scalars["Boolean"]["output"];
  Campaign: CampaignModel;
  CreateAdGroupInput: CreateAdGroupInput;
  CreateAdInput: CreateAdInput;
  CreateAppInput: CreateAppInput;
  CreateCampaignInput: CreateCampaignInput;
  DateTime: Scalars["DateTime"]["output"];
  Float: Scalars["Float"]["output"];
  ID: Scalars["ID"]["output"];
  Int: Scalars["Int"]["output"];
  Mutation: {};
  Query: {};
  String: Scalars["String"]["output"];
  UpdateAdInput: UpdateAdInput;
};

export type AdResolvers<
  ContextType = any,
  ParentType extends ResolversParentTypes["Ad"] = ResolversParentTypes["Ad"],
> = {
  adGroup?: Resolver<ResolversTypes["AdGroup"], ParentType, ContextType>;
  clicks?: Resolver<ResolversTypes["Int"], ParentType, ContextType>;
  createdAt?: Resolver<ResolversTypes["DateTime"], ParentType, ContextType>;
  description?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  destinationUrl?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  id?: Resolver<ResolversTypes["ID"], ParentType, ContextType>;
  imageUrl?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  impressions?: Resolver<ResolversTypes["Int"], ParentType, ContextType>;
  status?: Resolver<ResolversTypes["AdStatus"], ParentType, ContextType>;
  title?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  updatedAt?: Resolver<ResolversTypes["DateTime"], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type AdGroupResolvers<
  ContextType = any,
  ParentType extends
    ResolversParentTypes["AdGroup"] = ResolversParentTypes["AdGroup"],
> = {
  ads?: Resolver<Maybe<Array<ResolversTypes["Ad"]>>, ParentType, ContextType>;
  campaign?: Resolver<ResolversTypes["Campaign"], ParentType, ContextType>;
  createdAt?: Resolver<ResolversTypes["DateTime"], ParentType, ContextType>;
  description?: Resolver<
    Maybe<ResolversTypes["String"]>,
    ParentType,
    ContextType
  >;
  deviceType?: Resolver<ResolversTypes["DeviceType"], ParentType, ContextType>;
  gender?: Resolver<ResolversTypes["Gender"], ParentType, ContextType>;
  id?: Resolver<ResolversTypes["ID"], ParentType, ContextType>;
  keywords?: Resolver<
    Maybe<Array<ResolversTypes["String"]>>,
    ParentType,
    ContextType
  >;
  locations?: Resolver<
    Maybe<Array<ResolversTypes["String"]>>,
    ParentType,
    ContextType
  >;
  maxAge?: Resolver<Maybe<ResolversTypes["Int"]>, ParentType, ContextType>;
  minAge?: Resolver<Maybe<ResolversTypes["Int"]>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  status?: Resolver<ResolversTypes["AdStatus"], ParentType, ContextType>;
  updatedAt?: Resolver<ResolversTypes["DateTime"], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type AdPerformanceResolvers<
  ContextType = any,
  ParentType extends
    ResolversParentTypes["AdPerformance"] = ResolversParentTypes["AdPerformance"],
> = {
  adId?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  clicks?: Resolver<ResolversTypes["Int"], ParentType, ContextType>;
  date?: Resolver<ResolversTypes["DateTime"], ParentType, ContextType>;
  id?: Resolver<ResolversTypes["ID"], ParentType, ContextType>;
  impressions?: Resolver<ResolversTypes["Int"], ParentType, ContextType>;
  spend?: Resolver<ResolversTypes["Float"], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type AppResolvers<
  ContextType = any,
  ParentType extends ResolversParentTypes["App"] = ResolversParentTypes["App"],
> = {
  apiKey?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  campaigns?: Resolver<
    Maybe<Array<ResolversTypes["Campaign"]>>,
    ParentType,
    ContextType
  >;
  createdAt?: Resolver<ResolversTypes["DateTime"], ParentType, ContextType>;
  description?: Resolver<
    Maybe<ResolversTypes["String"]>,
    ParentType,
    ContextType
  >;
  id?: Resolver<ResolversTypes["ID"], ParentType, ContextType>;
  name?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  updatedAt?: Resolver<ResolversTypes["DateTime"], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type CampaignResolvers<
  ContextType = any,
  ParentType extends
    ResolversParentTypes["Campaign"] = ResolversParentTypes["Campaign"],
> = {
  adGroups?: Resolver<
    Maybe<Array<ResolversTypes["AdGroup"]>>,
    ParentType,
    ContextType
  >;
  app?: Resolver<ResolversTypes["App"], ParentType, ContextType>;
  budget?: Resolver<ResolversTypes["Float"], ParentType, ContextType>;
  createdAt?: Resolver<ResolversTypes["DateTime"], ParentType, ContextType>;
  description?: Resolver<
    Maybe<ResolversTypes["String"]>,
    ParentType,
    ContextType
  >;
  endDate?: Resolver<
    Maybe<ResolversTypes["DateTime"]>,
    ParentType,
    ContextType
  >;
  id?: Resolver<ResolversTypes["ID"], ParentType, ContextType>;
  name?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  startDate?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  status?: Resolver<ResolversTypes["AdStatus"], ParentType, ContextType>;
  updatedAt?: Resolver<ResolversTypes["DateTime"], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export interface DateTimeScalarConfig
  extends GraphQLScalarTypeConfig<ResolversTypes["DateTime"], any> {
  name: "DateTime";
}

export type MutationResolvers<
  ContextType = any,
  ParentType extends
    ResolversParentTypes["Mutation"] = ResolversParentTypes["Mutation"],
> = {
  _empty?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  createAd?: Resolver<
    ResolversTypes["Ad"],
    ParentType,
    ContextType,
    RequireFields<MutationCreateAdArgs, "input">
  >;
  createAdGroup?: Resolver<
    ResolversTypes["AdGroup"],
    ParentType,
    ContextType,
    RequireFields<MutationCreateAdGroupArgs, "input">
  >;
  createApp?: Resolver<
    ResolversTypes["App"],
    ParentType,
    ContextType,
    RequireFields<MutationCreateAppArgs, "input">
  >;
  createCampaign?: Resolver<
    ResolversTypes["Campaign"],
    ParentType,
    ContextType,
    RequireFields<MutationCreateCampaignArgs, "input">
  >;
  deleteAd?: Resolver<
    ResolversTypes["Boolean"],
    ParentType,
    ContextType,
    RequireFields<MutationDeleteAdArgs, "id">
  >;
  deleteAdGroup?: Resolver<
    ResolversTypes["Boolean"],
    ParentType,
    ContextType,
    RequireFields<MutationDeleteAdGroupArgs, "id">
  >;
  deleteApp?: Resolver<
    ResolversTypes["Boolean"],
    ParentType,
    ContextType,
    RequireFields<MutationDeleteAppArgs, "id">
  >;
  deleteCampaign?: Resolver<
    ResolversTypes["Boolean"],
    ParentType,
    ContextType,
    RequireFields<MutationDeleteCampaignArgs, "id">
  >;
  updateAd?: Resolver<
    ResolversTypes["Ad"],
    ParentType,
    ContextType,
    RequireFields<MutationUpdateAdArgs, "input">
  >;
  updateAdGroup?: Resolver<
    ResolversTypes["AdGroup"],
    ParentType,
    ContextType,
    RequireFields<MutationUpdateAdGroupArgs, "id">
  >;
  updateApp?: Resolver<
    ResolversTypes["App"],
    ParentType,
    ContextType,
    RequireFields<MutationUpdateAppArgs, "id">
  >;
  updateCampaign?: Resolver<
    ResolversTypes["Campaign"],
    ParentType,
    ContextType,
    RequireFields<MutationUpdateCampaignArgs, "id">
  >;
};

export type QueryResolvers<
  ContextType = any,
  ParentType extends
    ResolversParentTypes["Query"] = ResolversParentTypes["Query"],
> = {
  _empty?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  getAd?: Resolver<
    Maybe<ResolversTypes["Ad"]>,
    ParentType,
    ContextType,
    RequireFields<QueryGetAdArgs, "id">
  >;
  getAdGroup?: Resolver<
    Maybe<ResolversTypes["AdGroup"]>,
    ParentType,
    ContextType,
    RequireFields<QueryGetAdGroupArgs, "id">
  >;
  getAdPerformance?: Resolver<
    Array<ResolversTypes["AdPerformance"]>,
    ParentType,
    ContextType,
    RequireFields<QueryGetAdPerformanceArgs, "adId">
  >;
  getApp?: Resolver<
    Maybe<ResolversTypes["App"]>,
    ParentType,
    ContextType,
    RequireFields<QueryGetAppArgs, "id">
  >;
  getCampaign?: Resolver<
    Maybe<ResolversTypes["Campaign"]>,
    ParentType,
    ContextType,
    RequireFields<QueryGetCampaignArgs, "id">
  >;
  listAdGroupsByCampaign?: Resolver<
    Array<ResolversTypes["AdGroup"]>,
    ParentType,
    ContextType,
    RequireFields<QueryListAdGroupsByCampaignArgs, "campaignId">
  >;
  listAdsByAdGroup?: Resolver<
    Array<ResolversTypes["Ad"]>,
    ParentType,
    ContextType,
    RequireFields<QueryListAdsByAdGroupArgs, "adGroupId">
  >;
  listApps?: Resolver<Array<ResolversTypes["App"]>, ParentType, ContextType>;
  listCampaignsByApp?: Resolver<
    Array<ResolversTypes["Campaign"]>,
    ParentType,
    ContextType,
    RequireFields<QueryListCampaignsByAppArgs, "appId">
  >;
};

export type Resolvers<ContextType = any> = {
  Ad?: AdResolvers<ContextType>;
  AdGroup?: AdGroupResolvers<ContextType>;
  AdPerformance?: AdPerformanceResolvers<ContextType>;
  App?: AppResolvers<ContextType>;
  Campaign?: CampaignResolvers<ContextType>;
  DateTime?: GraphQLScalarType;
  Mutation?: MutationResolvers<ContextType>;
  Query?: QueryResolvers<ContextType>;
};
