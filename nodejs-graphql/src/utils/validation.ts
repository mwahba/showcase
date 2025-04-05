import {
  CreateAdGroupInput,
  CreateAdInput,
  CreateAppInput,
  CreateCampaignInput,
} from "../graphql/types";
import { AdGroupCreateInput } from "../models/ad-group.model";
import { AdCreateInput } from "../models/ad.model";
import { CampaignCreateInput } from "../models/campaign.model";

/**
 * Validates App input
 * @param input App creation input
 * @throws {Error} if input is invalid
 */
export function validateAppInput(input: CreateAppInput) {
  // Check name
  if (!input.name || input.name.trim().length < 2) {
    throw new Error("App name must be at least 2 characters long");
  }

  // Optional description length check
  if (input.description && input.description.length > 500) {
    throw new Error("App description must be less than 500 characters");
  }
}

/**
 * Validates Campaign input
 * @param input Campaign creation input
 * @throws {Error} if input is invalid
 */
export function validateCampaignInput(input: CreateCampaignInput) {
  // Check name
  if (!input.name || input.name.trim().length < 2) {
    throw new Error("Campaign name must be at least 2 characters long");
  }

  // Validate dates
  const startDate = new Date(input.startDate);
  if (isNaN(startDate.getTime())) {
    throw new Error("Invalid start date");
  }

  // Check end date if provided
  if (input.endDate) {
    const endDate = new Date(input.endDate);
    if (isNaN(endDate.getTime())) {
      throw new Error("Invalid end date");
    }
    if (endDate < startDate) {
      throw new Error("End date must be after start date");
    }
  }

  // Validate budget
  if (input.budget <= 0) {
    throw new Error("Budget must be a positive number");
  }
}

/**
 * Validates Ad Group input
 * @param input Ad Group creation input
 * @throws {Error} if input is invalid
 */
export function validateAdGroupInput(input: CreateAdGroupInput) {
  // Check name
  if (!input.name || input.name.trim().length < 2) {
    throw new Error("Ad Group name must be at least 2 characters long");
  }

  // Validate age range
  if (input.minAge !== undefined && input.minAge !== null && input.minAge < 0) {
    throw new Error("Minimum age cannot be negative");
  }

  if (input.maxAge !== undefined && input.maxAge !== null && input.maxAge < 0) {
    throw new Error("Maximum age cannot be negative");
  }

  if (
    input.minAge !== undefined &&
    input.maxAge !== undefined &&
    input.minAge !== null &&
    input.maxAge !== null &&
    input.minAge > input.maxAge
  ) {
    throw new Error("Minimum age cannot be greater than maximum age");
  }

  // Validate keywords
  if (input.keywords && input.keywords.length > 50) {
    throw new Error("Maximum of 50 keywords allowed");
  }

  // Validate locations
  if (input.locations && input.locations.length > 100) {
    throw new Error("Maximum of 100 locations allowed");
  }
}

/**
 * Validates Ad input
 * @param input Ad creation input
 * @throws {Error} if input is invalid
 */
export function validateAdInput(input: CreateAdInput) {
  // Check title
  if (!input.title || input.title.trim().length < 2) {
    throw new Error("Ad title must be at least 2 characters long");
  }

  // Check description
  if (!input.description || input.description.trim().length < 10) {
    throw new Error("Ad description must be at least 10 characters long");
  }

  // Validate destination URL
  try {
    new URL(input.destinationUrl);
  } catch {
    throw new Error("Invalid destination URL");
  }

  // Validate image URL if provided
  if (input.imageUrl) {
    try {
      new URL(input.imageUrl);
    } catch {
      throw new Error("Invalid image URL");
    }
  }
}
