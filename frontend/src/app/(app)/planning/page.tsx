// Redirige vers la page planning unifiée dans /cuisine/planning
import { redirect } from "next/navigation";

export default function PagePlanningRedirect() {
  redirect("/cuisine/planning");
}
