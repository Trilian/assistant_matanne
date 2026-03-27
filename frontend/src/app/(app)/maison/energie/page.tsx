import { redirect } from "next/navigation";
export default function Page() {
  redirect("/maison/finances?tab=energie");
}

