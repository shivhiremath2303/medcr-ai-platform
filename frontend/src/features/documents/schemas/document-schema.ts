import { z } from "zod";

const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB from backend settings
const ACCEPTED_FILE_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

export const uploadSchema = z.object({
  file: z
    .instanceof(File)
    .refine((file) => file.size <= MAX_FILE_SIZE, "Max file size is 20MB.")
    .refine(
      (file) => ACCEPTED_FILE_TYPES.includes(file.type),
      "Only .pdf and .docx files are accepted."
    ),
});

export type UploadFormValues = z.infer<typeof uploadSchema>;

export const documentSearchSchema = z.object({
  query: z.string().optional(),
  status: z.string().optional(),
});
