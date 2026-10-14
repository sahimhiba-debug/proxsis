"use client";

import { useState, type ReactNode } from "react";
import { freePublicationDate, remainingWorkingDays } from "@/lib/compliance";
import { fmtDate } from "@/lib/i18n";
import { StatusRing } from "./StatusRing";

/**
 * A post subject to the reporting obligation: the ring counts the working days of restriction still to run from the
 * day the vacancy goes online (editable), then the date from which publication and contact are free. `children` is
 * the post itself (trade, status, legal basis), rendered by the server. The days are counted at `today`, the list's
 * Monday (the demonstration's « today »), written next to the count: never the computer's clock (the same screen on any
 * day of the meeting).
 */
export function ComplianceCountdown({ start, today, holidays, labels, children }: {
  start: string; today: string; holidays: string[]; children: ReactNode;
  labels: { online: string; onlineLong: string; freeFrom: string; left1: string; leftN: string; over: string; asOf: string };
}) {
  const [online, setOnline] = useState(start);
  const free = freePublicationDate(online, holidays);
  const left = remainingWorkingDays(online, today, holidays);
  return (
    <div className="flex items-start gap-4">
      <StatusRing status={left === 0 ? "free" : "subject"} left={left} />
      <div className="min-w-0 flex-1">
        {children}
        <p className="mt-3 text-[15px]" data-testid="free-date">{labels.freeFrom.replace("{date}", fmtDate(free))}</p>
        <p className="fx-muted mt-0.5 flex flex-wrap items-center gap-x-2 text-[13px]">
          <span data-testid="remaining">{left === 0 ? labels.over : left === 1 ? labels.left1 : labels.leftN.replace("{n}", String(left))}{" "}
            {labels.asOf.replace("{date}", fmtDate(today))}</span>
          <span aria-hidden>·</span>
          <label className="inline-flex flex-wrap items-center gap-2">
            {labels.online}
            <input type="date" value={online} aria-label={labels.onlineLong} onChange={(e) => e.target.value && setOnline(e.target.value)}
              className="fx-date" />
          </label>
        </p>
      </div>
    </div>
  );
}
