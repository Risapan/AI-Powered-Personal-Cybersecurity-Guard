import { describe, expect, it } from "vitest";

import { prepareUrlForAnalysis } from "./url";

describe("prepareUrlForAnalysis", () => {
  it("keeps a plain https URL", () => {
    expect(prepareUrlForAnalysis("https://example.com/path?q=1")).toBe(
      "https://example.com/path?q=1",
    );
  });

  it("removes the fragment", () => {
    expect(
      prepareUrlForAnalysis("https://app.example.com/#access_token=secret"),
    ).toBe("https://app.example.com/");
  });

  it.each([
    "chrome://settings",
    "file:///Users/me/notes.txt",
    "javascript:alert(1)",
    "data:text/html,hi",
    "about:blank",
  ])("refuses non-http scheme %s", (raw) => {
    expect(prepareUrlForAnalysis(raw)).toBeNull();
  });

  it.each(["", "not a url", "http://"])("refuses invalid input %j", (raw) => {
    expect(prepareUrlForAnalysis(raw)).toBeNull();
  });
});
