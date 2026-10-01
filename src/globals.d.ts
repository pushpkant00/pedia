/* Ambient types shared by all Pedia scripts (compiled as classic scripts). */

interface ToastuiEditorHooks {
  addImageBlobHook?: (
    blob: Blob | File,
    callback: (url: string, altText?: string) => void
  ) => void | false;
}

interface ToastuiEditorOptions {
  el: HTMLElement;
  height?: string;
  minHeight?: string;
  initialEditType?: string;
  previewStyle?: string;
  initialValue?: string;
  usageStatistics?: boolean;
  theme?: string;
  toolbarItems?: string[][];
  hooks?: ToastuiEditorHooks;
  [key: string]: unknown;
}

interface ToastuiEditorInstance {
  getHTML(): string;
  getMarkdown(): string;
  setMarkdown(markdown: string): void;
  eventEmitter?: { emit(event: string, ...args: unknown[]): void };
  exec?(command: string, payload?: Record<string, unknown>): void;
  getCurrentModeEditor?(): { view?: unknown; editorView?: unknown } | undefined;
  wwEditor?: { view?: unknown };
  view?: unknown;
}

declare const toastui: {
  Editor?: new (options: ToastuiEditorOptions) => ToastuiEditorInstance;
};

interface EditorPrefs {
  mode: string;
  toolbar: string;
  theme: string;
  uploads: boolean;
  autosave: boolean;
  interval: number;
  draftKey: string;
}

interface EditorDraft {
  html: string;
  at: number;
  seed?: string;
}

interface ZoomResult {
  w: number;
  next: number;
  max: number;
  skipped: boolean;
}

/* Globals the editor script exposes to the dev self-test (?selftest=1). */
declare function syncImageWidths(html: string): string;
declare function applyImageWidth(imgEl: HTMLImageElement | null | undefined, w: number | string): void;

interface Window {
  __pediaEditor?: ToastuiEditorInstance;
  __pediaEditorPrefs?: EditorPrefs;
  __pediaLastZoom?: { dir: number; r: ZoomResult } | null;
  __pediaAdjProbe?: (x: number, y: number) => unknown;
}
