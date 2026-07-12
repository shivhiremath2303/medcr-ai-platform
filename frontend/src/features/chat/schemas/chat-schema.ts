import { z } from "zod";

export const chatRequestSchema = z.object({
  question: z.string().min(1, "Question cannot be empty").max(2000, "Question is too long"),
  k: z.number().int().min(1).max(10).optional().default(3),
});

export type ChatRequestValues = z.infer<typeof chatRequestSchema>;

export const messageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string().min(1),
});
