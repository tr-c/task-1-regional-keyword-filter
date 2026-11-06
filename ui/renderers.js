// Render FilterOutput as a numbered list of matching lines.
// Each line is shown verbatim so the dialect marker is visible in context.
import { h } from "./kit/components.js";

export default {
  FilterOutput: (output) =>
    h("div", {}, [
      h("p", { text: `${output.matches.length} line(s) matched:` }),
      h(
        "ol",
        {},
        output.matches.map((line) => h("li", { text: line }))
      ),
    ]),
};
