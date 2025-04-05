import express from "express";
import http from "http";
import cors from "cors";
import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@apollo/server/express4";
import { ApolloServerPluginDrainHttpServer } from "@apollo/server/plugin/drainHttpServer";
import { PrismaClient } from "@prisma/client";
import { loadSchemaSync } from "@graphql-tools/load";
import { GraphQLFileLoader } from "@graphql-tools/graphql-file-loader";
import { makeExecutableSchema } from "@graphql-tools/schema";
import path from "path";
import { resolvers } from "./graphql/resolvers";
import { OnFieldTypeConflict } from "@graphql-tools/merge";

interface MyContext {
  prisma: PrismaClient;
}
const prisma = new PrismaClient();

const gracefulShutdown = async () => {
  console.log("Shutting down gracefully...");
  try {
    await prisma.$disconnect();
    console.log("Database connections closed");
    process.exit(0);
  } catch (error) {
    console.error("Error during shutdown:", error);
    process.exit(1);
  }
};

async function startServer() {
  const app = express();

  const httpServer = http.createServer(app);

  const onFieldTypeConflict: OnFieldTypeConflict = (
    existingField,
    otherField,
  ) => existingField;

  const typeDefs = loadSchemaSync(
    path.join(__dirname, "./graphql/schemas/*.graphql"),
    {
      loaders: [new GraphQLFileLoader()],
      onFieldTypeConflict,
    },
  );

  const schema = makeExecutableSchema({ typeDefs, resolvers });

  const server = new ApolloServer<MyContext>({
    schema,
    plugins: [ApolloServerPluginDrainHttpServer({ httpServer })],
    formatError: (formattedError, error) => {
      console.error("GraphQL Error:", error);

      return process.env.NODE_ENV !== "production"
        ? formattedError
        : { message: formattedError.message };
    },
  });

  await server.start();

  app.get("/health", (_, res) => {
    res.status(200).send("OK");
  });

  app.use(
    "/graphql",
    cors<cors.CorsRequest>(),
    express.json(),
    expressMiddleware(server, {
      context: async () => ({
        prisma,
      }),
    }),
  );

  const PORT = process.env.PORT || 4000;

  await new Promise<void>((resolve) =>
    httpServer.listen({ port: PORT }, resolve),
  );

  console.log(
    `🚀 Server ready at http://localhost:${PORT}/graphql 🔋 Database connected 📊 Ad Management System is running`,
  );

  process.on("SIGTERM", gracefulShutdown);
  process.on("SIGINT", gracefulShutdown);

  return httpServer;
}
process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
  // process.exit(1);
});

startServer().catch((error) => {
  console.error("Failed to start server:", error);
  process.exit(1);
});

export { prisma };
