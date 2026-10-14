// Where the visit lives: the presentation's address (built at /[lang]/visite/, moved there when complete, working notes).
export const VISIT_DIR = "presentation";
export const visitPath = (lang: "fr" | "de", page = "") => `/${lang}/${VISIT_DIR}/${page ? `${page}/` : ""}`;
