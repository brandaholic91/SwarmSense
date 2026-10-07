import { estimateCostUsd, formatCostUsd } from "@/lib/cost";

const price = { input_per_million_usd: 0.5, output_per_million_usd: 1.5 };

describe("cost", () => {
  it("estimates cost from list price per million tokens", () => {
    expect(estimateCostUsd(1_000_000, 2_000_000, price)).toBe(3.5);
  });

  it("is zero for zero tokens", () => {
    expect(estimateCostUsd(0, 0, price)).toBe(0);
  });

  it("formats with three decimals", () => {
    expect(formatCostUsd(0.0123)).toBe("~$0.012");
  });
});
