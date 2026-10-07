export type Price = {
  input_per_million_usd: number;
  output_per_million_usd: number;
};

export function estimateCostUsd(inputTokens: number, outputTokens: number, price: Price): number {
  return (
    (inputTokens * price.input_per_million_usd + outputTokens * price.output_per_million_usd) /
    1_000_000
  );
}

export function formatCostUsd(value: number): string {
  return `~$${value.toFixed(3)}`;
}
