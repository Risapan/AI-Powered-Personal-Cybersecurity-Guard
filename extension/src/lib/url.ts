/**
 * Prepare a tab URL before it leaves the extension.
 *
 * Only http(s) URLs are analysed, and the fragment (`#...`) is always removed:
 * fragments never reach a server and often hold app state or OAuth tokens,
 * so Friday has no reason to see them.
 *
 * Returns null for anything that shouldn't be sent (other schemes, invalid URLs).
 */
export function prepareUrlForAnalysis(raw: string): string | null {
  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    return null;
  }
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    return null;
  }
  url.hash = "";
  return url.toString();
}
