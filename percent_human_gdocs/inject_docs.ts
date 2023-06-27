import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
  matches: ["https://docs.google.com/document/*"],
  world: "MAIN",
  run_at: "document_start"
}

window._docs_annotate_canvas_by_ext = "iidnbdjijdkbmajdffnidomddglmieko"
console.log("Percent Human: running docs inject script")
