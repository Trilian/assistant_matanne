"use client";

import type { ComponentProps } from "react";

import { PanneauListesCourses } from "@/composants/courses/panneau-listes-courses";

type PanelListesCoursesProps = ComponentProps<typeof PanneauListesCourses>;

export function PanelListesCourses(props: PanelListesCoursesProps) {
  return <PanneauListesCourses {...props} />;
}
