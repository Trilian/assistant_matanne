"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";

const CLE_MINUTEUR = "outils-minuteur-global";

function formaterTemps(ms: number) {
  const totalSecondes = Math.floor(ms / 1000);
  const heures = Math.floor(totalSecondes / 3600);
  const minutes = Math.floor((totalSecondes % 3600) / 60);
  const secondes = totalSecondes % 60;
  const centaines = Math.floor((ms % 1000) / 10);

  if (heures > 0) {
    return `${heures}:${String(minutes).padStart(2, "0")}:${String(secondes).padStart(2, "0")}`;
  }
  return `${String(minutes).padStart(2, "0")}:${String(secondes).padStart(2, "0")}.${String(centaines).padStart(2, "0")}`;
}

function ComposantChronometre() {
  const [tempsEcoule, setTempsEcoule] = useState(0);
  const [enMarche, setEnMarche] = useState(false);
  const refIntervalle = useRef<ReturnType<typeof setInterval> | null>(null);
  const refDemarrage = useRef(0);

  const demarrer = useCallback(() => {
    refDemarrage.current = Date.now() - tempsEcoule;
    refIntervalle.current = setInterval(() => {
      setTempsEcoule(Date.now() - refDemarrage.current);
    }, 37);
    setEnMarche(true);
  }, [tempsEcoule]);

  const arreter = useCallback(() => {
    if (refIntervalle.current) clearInterval(refIntervalle.current);
    setEnMarche(false);
  }, []);

  const reinitialiser = useCallback(() => {
    if (refIntervalle.current) clearInterval(refIntervalle.current);
    setEnMarche(false);
    setTempsEcoule(0);
  }, []);

  useEffect(() => {
    return () => {
      if (refIntervalle.current) clearInterval(refIntervalle.current);
    };
  }, []);

  return (
    <div className="text-center space-y-6">
      <p className="text-6xl font-mono font-bold tabular-nums">
        {formaterTemps(tempsEcoule)}
      </p>
      <div className="flex justify-center gap-3">
        {!enMarche ? (
          <Button onClick={demarrer} size="lg">
            ▶ Démarrer
          </Button>
        ) : (
          <Button onClick={arreter} variant="secondary" size="lg">
            ⏸ Pause
          </Button>
        )}
        <Button onClick={reinitialiser} variant="outline" size="lg">
          ↺ Réinitialiser
        </Button>
      </div>
    </div>
  );
}

function ComposantMinuteur() {
  const [dureeMinutes, setDureeMinutes] = useState(5);
  const [restant, setRestant] = useState(0);
  const [enMarche, setEnMarche] = useState(false);
  const refIntervalle = useRef<ReturnType<typeof setInterval> | null>(null);
  const refFin = useRef(0);

  const demarrer = useCallback(() => {
    const msFin = restant > 0 ? restant : dureeMinutes * 60 * 1000;
    refFin.current = Date.now() + msFin;
    setRestant(msFin);
    setEnMarche(true);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(
        CLE_MINUTEUR,
        JSON.stringify({ actif: true, finMs: refFin.current })
      );
    }

    refIntervalle.current = setInterval(() => {
      const r = refFin.current - Date.now();
      if (r <= 0) {
        if (refIntervalle.current) clearInterval(refIntervalle.current);
        setRestant(0);
        setEnMarche(false);
        if (typeof window !== "undefined") {
          window.localStorage.removeItem(CLE_MINUTEUR);
        }
        if (typeof window !== "undefined" && "Notification" in window) {
          Notification.requestPermission().then((p) => {
            if (p === "granted") new Notification("⏰ Minuteur terminé !");
          });
        }
      } else {
        setRestant(r);
      }
    }, 100);
  }, [restant, dureeMinutes]);

  const arreter = useCallback(() => {
    if (refIntervalle.current) clearInterval(refIntervalle.current);
    setEnMarche(false);
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(CLE_MINUTEUR);
    }
  }, []);

  const reinitialiser = useCallback(() => {
    if (refIntervalle.current) clearInterval(refIntervalle.current);
    setEnMarche(false);
    setRestant(0);
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(CLE_MINUTEUR);
    }
  }, []);

  useEffect(() => {
    return () => {
      if (refIntervalle.current) clearInterval(refIntervalle.current);
    };
  }, []);

  const presets = [1, 3, 5, 10, 15, 30];

  return (
    <div className="text-center space-y-6">
      {!enMarche && restant === 0 && (
        <div className="space-y-3">
          <div className="flex justify-center gap-2 flex-wrap">
            {presets.map((m) => (
              <Button
                key={m}
                variant={dureeMinutes === m ? "default" : "outline"}
                size="sm"
                onClick={() => setDureeMinutes(m)}
              >
                {m} min
              </Button>
            ))}
          </div>
          <div className="flex justify-center items-center gap-2">
            <Input
              type="number"
              min={1}
              max={999}
              value={dureeMinutes}
              onChange={(e) => setDureeMinutes(Math.max(1, Number(e.target.value)))}
              className="w-24 text-center"
            />
            <span className="text-muted-foreground">minutes</span>
          </div>
        </div>
      )}

      <p className="text-6xl font-mono font-bold tabular-nums">
        {formaterTemps(restant > 0 ? restant : dureeMinutes * 60 * 1000)}
      </p>

      <div className="flex justify-center gap-3">
        {!enMarche ? (
          <Button onClick={demarrer} size="lg">
            ▶ Démarrer
          </Button>
        ) : (
          <Button onClick={arreter} variant="secondary" size="lg">
            ⏸ Pause
          </Button>
        )}
        <Button onClick={reinitialiser} variant="outline" size="lg">
          ↺ Réinitialiser
        </Button>
      </div>
    </div>
  );
}

export default function MinuteurPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">⏱️ Minuteur</h1>

      <Card className="max-w-lg mx-auto">
        <CardHeader>
          <CardTitle>Chronomètre & Minuteur</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="minuteur">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="minuteur">Minuteur</TabsTrigger>
              <TabsTrigger value="chronometre">Chronomètre</TabsTrigger>
            </TabsList>
            <TabsContent value="minuteur" className="pt-6">
              <ComposantMinuteur />
            </TabsContent>
            <TabsContent value="chronometre" className="pt-6">
              <ComposantChronometre />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
