// The pilot of the phone demo: drives the REAL app in a same-origin iframe — waits for the page, scrolls the screen,
// moves the finger, sends the wave, clicks the real button, follows the navigation. A plain class (no React): the
// component feeds it the asked step; every run can be interrupted by the next arrow or by the presenter's own touch.
import { animate, type AnimationPlaybackControls, type MotionValue } from "motion/react";
import { PHONE_MOTION, SCREEN, SCRIPT, clampStep, isDark, plan, stepOfPath, urlFor, type PLang } from "./script";

interface PilotEvents {
  shown: (step: number | null) => void; // the step the phone now shows (null while moving)
  finger: (on: boolean) => void;
  ripple: () => void;
  status: (bg: string, dark: boolean) => void; // the page's background, for the status bar
  takeOver: () => void; // the presenter touched the screen
  adopt: (step: number) => void; // on resume, the presenter's own page is a step of the script
  gesture: (phase: "start" | "end", p: { x: number; y: number }) => void; // screen coordinates
}

type Transition = { duration: number; ease: readonly [number, number, number, number] };

const ABORT = Symbol("phone-demo-abort");
const SAFE_TOP = 150; // under the app's sticky header and banner
const SAFE_BOTTOM = 96; // above the app's bottom navigation
const REST = { x: 300, y: SCREEN.status + 640 }; // where the finger comes from (a right thumb)
const FORWARDED = new Set(["ArrowRight", "ArrowLeft", "PageDown", "PageUp", "Home"]);
const noop = () => {};

/** The motion values the component draws (finger, wave, screen); the pilot animates them. */
interface PilotValues {
  fx: MotionValue<number>; // finger, screen coordinates
  fy: MotionValue<number>;
  fo: MotionValue<number>;
  fs: MotionValue<number>;
  rx: MotionValue<number>; // wave
  ry: MotionValue<number>;
  rs: MotionValue<number>;
  ro: MotionValue<number>;
  screen: MotionValue<number>; // the page's opacity during a jump
}

export const FINGER_REST = REST;

export class Pilot {
  private readonly fx: MotionValue<number>;
  private readonly fy: MotionValue<number>;
  private readonly fo: MotionValue<number>;
  private readonly fs: MotionValue<number>;
  private readonly rx: MotionValue<number>;
  private readonly ry: MotionValue<number>;
  private readonly rs: MotionValue<number>;
  private readonly ro: MotionValue<number>;
  private readonly screen: MotionValue<number>;

  constructor(v: PilotValues) {
    this.fx = v.fx;
    this.fy = v.fy;
    this.fo = v.fo;
    this.fs = v.fs;
    this.rx = v.rx;
    this.ry = v.ry;
    this.rs = v.rs;
    this.ro = v.ro;
    this.screen = v.screen;
  }

  private frame: HTMLIFrameElement | null = null;
  private events: PilotEvents = { shown: noop, finger: noop, ripple: noop, status: noop, takeOver: noop, adopt: noop, gesture: noop };
  private token = 0;
  private running: AnimationPlaybackControls[] = [];
  private waiters = new Set<() => void>();
  private shown: number | null = null;
  private shownLang: PLang | null = null;
  private everShown = false;
  private fingerOn = false;
  private paused = false;
  private detach: (() => void) | null = null;
  private listened: Document | null = null;
  private watch: ReturnType<typeof setInterval> | null = null;

  on(events: PilotEvents): void {
    this.events = events;
  }

  /** Callback ref of the iframe. */
  attach = (el: HTMLIFrameElement | null): void => {
    if (this.frame === el) return;
    this.frame?.removeEventListener("load", this.onLoad);
    if (this.watch) clearInterval(this.watch);
    this.watch = null;
    this.detach?.();
    this.detach = null;
    this.listened = null;
    this.frame = el;
    if (!el) return;
    el.addEventListener("load", this.onLoad);
    // a touch can come before the page's « load »: follow the document as soon as it is there
    this.watch = setInterval(() => this.listen(false), 200);
    this.listen(false);
  };

  /** The asked state, from the component. Paused: nothing moves. Resumed: from the page the presenter left open. */
  sync(step: number, lang: PLang, still: boolean, paused: boolean): void {
    const wasPaused = this.paused;
    this.paused = paused;
    if (paused) {
      this.cancel();
      return;
    }
    if (wasPaused) {
      const m = stepOfPath(this.path(), lang, step);
      this.setShown(m, lang);
      if (m !== null && m !== clampStep(step)) {
        this.events.adopt(m); // the parent moves its step to the presenter's page; nothing to play
        return;
      }
    }
    this.go(step, lang, still);
  }

  dispose(): void {
    this.cancel();
    this.attach(null);
  }

  // ---------------------------------------------------------------- runs
  private go(asked: number, lang: PLang, still: boolean): void {
    const from = this.shownLang === lang ? this.shown : null;
    const move = plan(from, asked);
    if (move.kind === "none") return;
    const token = this.cancel();
    this.setShown(null, lang);
    void (async () => {
      try {
        await this.until(() => this.loaded(), token, 30_000);
        if (move.kind === "gesture") await this.gesture(move.to, lang, still, token);
        else await this.jump(move.to, lang, !still && this.everShown, token);
        this.guard(token);
        this.everShown = true;
        this.setShown(move.to, lang);
      } catch (e) {
        if (e !== ABORT) console.warn("phone demo:", e);
      }
    })();
  }

  private async gesture(to: number, lang: PLang, still: boolean, token: number): Promise<void> {
    const g = SCRIPT[to].gesture;
    if (!g || g.kind === "open") {
      this.hideFinger();
      await this.navigate(urlFor(to, lang), token, !still);
      return;
    }
    const el = await this.until(() => this.find(g.target), token, 10_000);
    if (!el) return this.jump(to, lang, !still, token); // the page changed under us: land on the step anyway
    await this.scrollInto(el, token, still);
    const p = this.point(el);
    this.events.gesture("start", p);
    if (still) {
      this.fx.set(p.x);
      this.fy.set(p.y);
      this.fs.set(1);
      this.fo.set(1);
      this.showFinger();
    } else {
      if (!this.fingerOn) {
        this.fx.set(REST.x);
        this.fy.set(REST.y);
        this.fs.set(1);
        this.fo.set(0);
        this.showFinger();
      }
      await Promise.all([
        this.tween(this.fo, 1, PHONE_MOTION.fade, token),
        this.tween(this.fx, p.x, PHONE_MOTION.travel, token),
        this.tween(this.fy, p.y, PHONE_MOTION.travel, token),
      ]);
      this.rx.set(p.x);
      this.ry.set(p.y);
      this.rs.set(0.6);
      this.ro.set(0.95);
      this.events.ripple();
      this.fire(this.rs, 2.6, PHONE_MOTION.ripple);
      this.fire(this.ro, 0, PHONE_MOTION.ripple);
      await this.tween(this.fs, 0.84, PHONE_MOTION.press, token);
    }
    // the real tap, on the real page
    (this.find(g.target) ?? el).click();
    if (!still) await this.tween(this.fs, 1, PHONE_MOTION.press, token);
    if (SCRIPT[to].path !== SCRIPT[to - 1]?.path) {
      const url = urlFor(to, lang);
      const ok = await this.until(() => this.path() === url, token, 12_000);
      if (!ok) await this.navigate(url, token, false);
    }
    this.readStatus();
    if (!still) {
      await this.tween(this.fo, 0, PHONE_MOTION.reveal, token);
      this.hideFinger();
    }
    this.events.gesture("end", p);
  }

  private async jump(to: number, lang: PLang, fade: boolean, token: number): Promise<void> {
    this.hideFinger();
    const url = urlFor(to, lang);
    const nav = this.path() !== url;
    if (nav) await this.navigate(url, token, fade);
    else await this.scrollTo(0, token, !fade);
  }

  private async navigate(url: string, token: number, fade: boolean): Promise<void> {
    if (this.path() === url && this.loaded()) return;
    if (fade) await this.tween(this.screen, 0, PHONE_MOTION.fade, token);
    this.win()?.location.replace(url);
    await this.until(() => this.path() === url && this.loaded(), token, 30_000);
    this.readStatus();
    if (fade) await this.tween(this.screen, 1, PHONE_MOTION.reveal, token);
    else this.screen.set(1);
  }

  private async scrollInto(el: HTMLElement, token: number, instant: boolean): Promise<void> {
    const w = this.win();
    const d = this.doc();
    if (!w || !d) return;
    const r = el.getBoundingClientRect();
    const vh = w.innerHeight;
    if (r.top >= SAFE_TOP && r.bottom <= vh - SAFE_BOTTOM) return;
    const max = Math.max(0, d.documentElement.scrollHeight - vh);
    await this.scrollTo(Math.max(0, Math.min(max, w.scrollY + r.top + r.height / 2 - vh * 0.5)), token, instant);
  }

  private async scrollTo(top: number, token: number, instant: boolean): Promise<void> {
    const w = this.win();
    if (!w || Math.abs(w.scrollY - top) < 1) return;
    if (instant) {
      w.scrollTo({ top, behavior: "instant" });
      return;
    }
    const c = animate(w.scrollY, top, { ...PHONE_MOTION.scroll, onUpdate: (v) => w.scrollTo({ top: v, behavior: "instant" }) });
    await this.wait(c, token);
  }

  // ---------------------------------------------------------------- the iframe
  private win(): Window | null {
    return this.frame?.contentWindow ?? null;
  }

  private doc(): Document | null {
    try {
      return this.frame?.contentDocument ?? null;
    } catch {
      return null;
    }
  }

  private path(): string {
    try {
      const p = this.win()?.location.pathname ?? "";
      return p === "blank" ? "" : p;
    } catch {
      return "";
    }
  }

  private loaded(): boolean {
    return Boolean(this.path()) && this.doc()?.readyState === "complete";
  }

  private find(target: string): HTMLElement | null {
    return this.doc()?.querySelector<HTMLElement>(`[data-demo="${target.replace(/["\\]/g, "")}"]`) ?? null;
  }

  /** Centre of the target's first line, in screen coordinates (status bar included). */
  private point(el: HTMLElement): { x: number; y: number } {
    const r = el.getClientRects()[0] ?? el.getBoundingClientRect();
    return { x: r.left + Math.min(r.width / 2, 120), y: SCREEN.status + r.top + r.height / 2 };
  }

  private onLoad = (): void => this.listen(true);

  /** Listens to the document shown (the presenter's touch, the clicker's keys); `force` re-reads the status bar. */
  private listen(force: boolean): void {
    const d = this.doc();
    if (!d || !this.path()) return;
    if (d === this.listened) {
      if (force) this.readStatus();
      return;
    }
    this.detach?.();
    this.listened = d;
    const down = (e: PointerEvent) => {
      if (e.isTrusted && !this.paused) this.takeOver();
    };
    const key = (e: KeyboardEvent) => {
      const tag = (e.target as Element | null)?.tagName;
      if (FORWARDED.has(e.key) && tag !== "INPUT" && tag !== "TEXTAREA" && tag !== "SELECT") {
        e.preventDefault(); // the presenter's clicker keeps driving the presentation, even with the focus in the phone
        window.dispatchEvent(new KeyboardEvent("keydown", { key: e.key, bubbles: true, cancelable: true }));
        return;
      }
      // any other key used inside the phone (Tab, Enter, typing) is someone using the app: as with a touch, it is theirs
      if (e.isTrusted && !this.paused) this.takeOver();
    };
    d.addEventListener("pointerdown", down, true);
    d.addEventListener("keydown", key, true);
    this.detach = () => {
      d.removeEventListener("pointerdown", down, true);
      d.removeEventListener("keydown", key, true);
    };
    this.readStatus();
  }

  private takeOver(): void {
    this.cancel();
    this.paused = true;
    this.hideFinger();
    this.setShown(null, this.shownLang ?? "fr");
    this.events.takeOver();
  }

  private readStatus(): void {
    const d = this.doc();
    if (!d?.body) return;
    const w = d.defaultView;
    let bg = w?.getComputedStyle(d.body).backgroundColor ?? "";
    if (!bg || /rgba\(.*,\s*0\)$/.test(bg) || bg === "transparent") bg = w?.getComputedStyle(d.documentElement).backgroundColor ?? "";
    if (!bg || /rgba\(.*,\s*0\)$/.test(bg) || bg === "transparent") bg = "#ffffff";
    this.events.status(bg, isDark(bg));
  }

  // ---------------------------------------------------------------- state, motion and interruption
  private setShown(step: number | null, lang: PLang): void {
    this.shown = step;
    this.shownLang = lang;
    this.events.shown(step);
  }

  private showFinger(): void {
    this.fingerOn = true;
    this.events.finger(true);
  }

  private hideFinger(): void {
    this.fingerOn = false;
    this.fo.set(0);
    this.events.finger(false);
  }

  /** Stops what runs (animations, waits) and starts a new run. */
  private cancel(): number {
    this.token += 1;
    for (const a of this.running) a.stop();
    this.running = [];
    for (const w of this.waiters) w();
    this.waiters.clear();
    this.screen.set(1);
    return this.token;
  }

  private guard(token: number): void {
    if (token !== this.token) throw ABORT;
  }

  private fire(mv: MotionValue<number>, to: number, t: Transition): AnimationPlaybackControls {
    const c = animate(mv, to, t);
    this.running.push(c);
    return c;
  }

  private async tween(mv: MotionValue<number>, to: number, t: Transition, token: number): Promise<void> {
    this.guard(token);
    await this.wait(this.fire(mv, to, t), token);
  }

  private async wait(c: AnimationPlaybackControls, token: number): Promise<void> {
    if (!this.running.includes(c)) this.running.push(c);
    await new Promise<void>((resolve) => {
      const done = () => {
        this.waiters.delete(done);
        resolve();
      };
      this.waiters.add(done);
      c.finished.then(done, done);
    });
    this.guard(token);
  }

  private async sleep(ms: number, token: number): Promise<void> {
    await new Promise<void>((resolve) => {
      const done = () => {
        clearTimeout(id);
        this.waiters.delete(done);
        resolve();
      };
      const id = setTimeout(done, ms);
      this.waiters.add(done);
    });
    this.guard(token);
  }

  /** Polls until the value is truthy (or the time is up: null). Interrupted with the run. */
  private async until<V>(fn: () => V | null | undefined | false, token: number, timeout: number): Promise<V | null> {
    const end = performance.now() + timeout;
    for (;;) {
      this.guard(token);
      const v = fn();
      if (v) return v;
      if (performance.now() > end) return null;
      await this.sleep(50, token);
    }
  }
}
