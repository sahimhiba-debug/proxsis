import type { Dict } from "@/i18n/dictionaries";
import { fmtDayMonth } from "@/lib/dates";
import type { Worker } from "@/lib/types";
import { workerName } from "./display";

/** The head of a fictional temp's line: number, trade, end of mission (« Fin de mission » and « Ma semaine »). */
export function WorkerHead({ w, t, trade }: { w: Worker; t: Dict; trade: (w: Worker) => string }) {
  return (
    <p className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 lg:block">
      <span className="block text-[16px]">{workerName(w.candidate_id, t.fx.worker)} <span className="fx-muted">· {trade(w)}</span></span>
      <span className="fx-caps fx-muted lg:mt-1 lg:block">{t.fx.fin.ends.replace("{date}", fmtDayMonth(w.fin_mission))}</span>
    </p>
  );
}
