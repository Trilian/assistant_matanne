"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface PointROI {
  index: number;
  label: string;
  cumul: number;
}

export function GraphiqueROI({ donnees }: { donnees: PointROI[] }) {
  if (donnees.length < 2) return null;

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={donnees} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <XAxis dataKey="label" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
        <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${v} €`} />
        <Tooltip formatter={(value) => [`${Number(value).toFixed(2)} €`, "Cumul"]} />
        <ReferenceLine y={0} stroke="hsl(0, 0%, 60%)" strokeDasharray="3 3" />
        <Line
          type="monotone"
          dataKey="cumul"
          stroke="hsl(210, 70%, 50%)"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
