// src/services/app.service.ts
import { PrismaClient } from "@prisma/client";
import { v4 as uuidv4 } from "uuid";
import { validateAppInput } from "../utils/validation";
import { App, CreateAppInput } from "../graphql/types";

export class AppService {
  constructor(private prisma: PrismaClient) {}

  async findAll() {
    return this.prisma.app.findMany();
  }

  async findById(id: string) {
    return this.prisma.app.findUnique({
      where: { id },
      include: { campaigns: true },
    });
  }

  async create(data: CreateAppInput) {
    validateAppInput(data);

    return this.prisma.app.create({
      data: {
        ...data,
        apiKey: uuidv4(),
      },
    });
  }

  async update(id: string, name?: string, description?: string) {
    // Check if app exists
    const app = await this.prisma.app.findUnique({ where: { id } });
    if (!app) {
      throw new Error(`App with ID ${id} not found`);
    }

    return this.prisma.app.update({
      where: { id },
      data: {
        name,
        description,
      },
    });
  }

  async delete(id: string) {
    // Check if app exists
    const app = await this.prisma.app.findUnique({ where: { id } });
    if (!app) {
      throw new Error(`App with ID ${id} not found`);
    }

    await this.prisma.app.delete({ where: { id } });
    return true;
  }
}
