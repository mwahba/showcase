import { DateTimeResolver } from "graphql-scalars";

import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  schema: "./src/graphql/schemas/**/*.graphql",
  generates: {
    "./src/graphql/types.ts": {
      plugins: ["typescript", "typescript-operations", "typescript-resolvers"],
      config: {
        mappers: {
          AdGroup: ".prisma/client#AdGroup as AdGroupModel",
          Ad: ".prisma/client#Ad as AdModel",
          App: ".prisma/client#App as AppModel",
          Campaign: ".prisma/client#Campaign as CampaignModel",
        },
        scalars: {
          DateTime: DateTimeResolver.extensions.codegenScalarType,
        },
        inputMaybeValue: "undefined | T",
      },
    },
  },
};

export default config;
