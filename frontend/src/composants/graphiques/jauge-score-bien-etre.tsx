"use client";

interface JaugeScoreBienEtreProps {
  score: number;
}

export function JaugeScoreBienEtre({ score }: JaugeScoreBienEtreProps) {
  const taille = 132;
  const scoreBorne = Math.max(0, Math.min(100, Math.round(score)));
  const stroke = 10;
  const rayon = (taille - stroke) / 2;
  const circonference = 2 * Math.PI * rayon;
  const progression = (scoreBorne / 100) * circonference;

  const couleur =
    scoreBorne >= 80
      ? "#22c55e"
      : scoreBorne >= 60
        ? "#f59e0b"
        : "#ef4444";

  return (
    <div className="relative h-[132px] w-[132px]">
      <svg width={taille} height={taille} className="-rotate-90">
        <circle
          cx={taille / 2}
          cy={taille / 2}
          r={rayon}
          fill="none"
          stroke="currentColor"
          strokeWidth={stroke}
          className="text-muted"
        />
        <circle
          cx={taille / 2}
          cy={taille / 2}
          r={rayon}
          fill="none"
          stroke={couleur}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circonference}
          strokeDashoffset={circonference - progression}
          className="transition-all duration-500 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <p className="text-3xl font-bold leading-none">{scoreBorne}</p>
        <p className="text-xs text-muted-foreground">/100</p>
      </div>
    </div>
  );
}
