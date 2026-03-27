import { redirect } from "next/navigation";
export default function Page() {
  redirect("/maison/documents?tab=contrats");
}

