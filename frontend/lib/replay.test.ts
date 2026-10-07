import { buildSchedule } from "@/lib/replay";
import type { TraceEvent } from "@/lib/trace";

function at(id: number, time: string): TraceEvent {
  return { id, type: "x", at: `2026-10-07T${time}Z` };
}

describe("buildSchedule", () => {
  it("delays events by the timestamp difference from the first one", () => {
    const schedule = buildSchedule([
      at(1, "12:00:00.000"),
      at(2, "12:00:01.500"),
      at(3, "12:00:01.500"),
    ]);
    expect(schedule.map((s) => s.delayMs)).toEqual([0, 1500, 1500]);
    expect(schedule.map((s) => s.event.id)).toEqual([1, 2, 3]);
  });

  it("orders events by id, not by input order", () => {
    const schedule = buildSchedule([at(3, "12:00:02.000"), at(1, "12:00:00.000"), at(2, "12:00:01.000")]);
    expect(schedule.map((s) => s.event.id)).toEqual([1, 2, 3]);
    expect(schedule.map((s) => s.delayMs)).toEqual([0, 1000, 2000]);
  });

  it("returns an empty schedule for no events", () => {
    expect(buildSchedule([])).toEqual([]);
  });

  it("never lets a delay go below the previous one when time steps backwards", () => {
    const schedule = buildSchedule([at(1, "12:00:05.000"), at(2, "12:00:03.000"), at(3, "12:00:07.000")]);
    expect(schedule.map((s) => s.delayMs)).toEqual([0, 0, 2000]);
  });

  it("does not mutate the input", () => {
    const input = [at(2, "12:00:01.000"), at(1, "12:00:00.000")];
    buildSchedule(input);
    expect(input.map((e) => e.id)).toEqual([2, 1]);
  });
});
