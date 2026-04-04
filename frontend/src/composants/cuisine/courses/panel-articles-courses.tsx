"use client";

import type { ComponentProps } from "react";

import { PanneauDetailCourses } from "@/composants/courses/panneau-detail-courses";

type PanelArticlesCoursesProps = ComponentProps<typeof PanneauDetailCourses>;

export function PanelArticlesCourses(props: PanelArticlesCoursesProps) {
  return <PanneauDetailCourses {...props} />;
}
