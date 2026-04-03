interface StreamIAProps {
  contenu: string;
  enCours?: boolean;
}

export function StreamIA({ contenu, enCours = false }: StreamIAProps) {
  return (
    <div className="whitespace-pre-wrap text-sm leading-6">
      {contenu || (enCours ? "Réponse en cours" : "")}
      {enCours && (
        <span
          aria-hidden="true"
          className="ml-1 inline-block h-4 w-2 animate-pulse rounded-sm bg-current/60 align-middle"
        />
      )}
    </div>
  );
}