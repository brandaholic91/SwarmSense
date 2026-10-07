import path from "node:path";

import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./test/setup.ts"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
      // a csomag importáláskor hibát dob, hacsak nem a szerver-buildben fut
      "server-only": path.resolve(__dirname, "test/server-only.ts"),
    },
  },
});
