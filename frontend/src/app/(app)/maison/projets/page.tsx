import { redirect } from "next/navigation";
export default function Page() {
  redirect("/maison/travaux?tab=projets");
}

