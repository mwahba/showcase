export const sanitizePrismaData = (
  data:
    | {
        [s: string]: unknown;
      }
    | ArrayLike<unknown>,
) =>
  Object.entries(data).reduce(
    (acc, [key, value]) => {
      if (value !== undefined && value !== null) {
        acc[key] = value;
      }
      return acc;
    },
    {} as Record<string, any>,
  );
