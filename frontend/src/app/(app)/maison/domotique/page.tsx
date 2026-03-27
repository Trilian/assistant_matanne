import { redirect } from "next/navigation";
export default function Page() {
  redirect("/maison/equipements?tab=domotique");
}

