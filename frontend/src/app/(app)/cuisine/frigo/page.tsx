import { redirect } from "next/navigation";

export default function PageFrigo() {
  redirect("/cuisine/inventaire?onglet=frigo");
}
