"use client";

import type { ComponentProps } from "react";

import { DialogueArticleCourses } from "@/composants/courses/dialogue-article-courses";
import { DialogueQrCourses } from "@/composants/courses/dialogue-qr-courses";

type DialogueAjoutArticleProps = ComponentProps<typeof DialogueArticleCourses>;
type DialogueQrPartageProps = ComponentProps<typeof DialogueQrCourses>;

export function DialogueAjoutArticle(props: DialogueAjoutArticleProps) {
  return <DialogueArticleCourses {...props} />;
}

export function DialogueQrPartage(props: DialogueQrPartageProps) {
  return <DialogueQrCourses {...props} />;
}
