import {
  applyEvent,
  countByStatus,
  initialTraceState,
  type TraceEvent,
  type TraceState,
} from "@/lib/trace";
import { ev, fullRunEvents } from "@/test/trace-fixtures";

function replay(events: TraceEvent[], from: TraceState = initialTraceState()): TraceState {
  return events.reduce(applyEvent, from);
}

describe("applyEvent", () => {
  it("run_started sets generating phase and start time", () => {
    const state = applyEvent(initialTraceState(), ev(1, "run_started"));
    expect(state.phase).toBe("generating");
    expect(state.startedAt).toBe(ev(1, "run_started").at);
    expect(state.lastEventId).toBe(1);
  });

  it("personas_generated sets personas phase and adds tokens", () => {
    const state = replay([
      ev(1, "run_started"),
      ev(2, "personas_generated", { input_tokens: 120, output_tokens: 900 }),
    ]);
    expect(state.phase).toBe("personas");
    expect(state.inputTokens).toBe(120);
    expect(state.outputTokens).toBe(900);
  });

  it("persona_started adds a running row", () => {
    const state = applyEvent(
      initialTraceState(),
      ev(1, "persona_started", { persona_index: 4, persona_name: "Anna" })
    );
    expect(state.personas).toEqual([
      {
        index: 4,
        name: "Anna",
        status: "running",
        attempt: 1,
        startedAt: ev(1, "persona_started").at,
        durationMs: null,
        errorCode: null,
      },
    ]);
  });

  it("persona_retry updates attempt and error code and counts the retry", () => {
    const state = replay([
      ev(1, "persona_started", { persona_index: 0, persona_name: "A" }),
      ev(2, "persona_retry", { persona_index: 0, attempt: 2, error_code: "LLM_TIMEOUT" }),
    ]);
    expect(state.personas[0]).toMatchObject({ status: "running", attempt: 2, errorCode: "LLM_TIMEOUT" });
    expect(state.retryCount).toBe(1);
  });

  it("persona_completed completes the row, clears the error and adds tokens", () => {
    const state = replay([
      ev(1, "persona_started", { persona_index: 0, persona_name: "A" }),
      ev(2, "persona_retry", { persona_index: 0, attempt: 2, error_code: "LLM_TIMEOUT" }),
      ev(3, "persona_completed", {
        persona_index: 0,
        attempt: 2,
        duration_ms: 1500,
        input_tokens: 10,
        output_tokens: 20,
      }),
    ]);
    expect(state.personas[0]).toMatchObject({
      status: "completed",
      durationMs: 1500,
      attempt: 2,
      errorCode: null,
    });
    expect(state.inputTokens).toBe(10);
    expect(state.outputTokens).toBe(20);
  });

  it("persona_failed fails the row and adds tokens", () => {
    const state = replay([
      ev(1, "persona_started", { persona_index: 0, persona_name: "A" }),
      ev(2, "persona_failed", {
        persona_index: 0,
        attempt: 3,
        error_code: "INVALID_RESPONSE",
        duration_ms: 900,
        input_tokens: 5,
        output_tokens: 6,
      }),
    ]);
    expect(state.personas[0]).toMatchObject({
      status: "failed",
      durationMs: 900,
      attempt: 3,
      errorCode: "INVALID_RESPONSE",
    });
    expect(state.inputTokens).toBe(5);
    expect(state.outputTokens).toBe(6);
  });

  it("synthesis_started sets synthesis phase", () => {
    expect(applyEvent(initialTraceState(), ev(1, "synthesis_started")).phase).toBe("synthesis");
  });

  it("synthesis_completed moves to pdf and adds tokens", () => {
    const state = applyEvent(
      initialTraceState(),
      ev(1, "synthesis_completed", { input_tokens: 500, output_tokens: 300 })
    );
    expect(state.phase).toBe("pdf");
    expect(state.inputTokens).toBe(500);
    expect(state.outputTokens).toBe(300);
    expect(state.synthesisFailed).toBe(false);
  });

  it("synthesis_failed moves to pdf, flags the failure and adds the failing call's tokens", () => {
    const state = applyEvent(
      initialTraceState(),
      ev(1, "synthesis_failed", { input_tokens: 400, output_tokens: 0 })
    );
    expect(state.phase).toBe("pdf");
    expect(state.synthesisFailed).toBe(true);
    expect(state.inputTokens).toBe(400);
    expect(state.outputTokens).toBe(0);
  });

  it("treats missing token fields as 0", () => {
    const state = replay([ev(1, "synthesis_failed"), ev(2, "persona_failed", { persona_index: 0 })]);
    expect(state.inputTokens).toBe(0);
    expect(state.outputTokens).toBe(0);
  });

  it("run_completed sets done and end time", () => {
    const state = applyEvent(initialTraceState(), ev(1, "run_completed"));
    expect(state.phase).toBe("done");
    expect(state.endedAt).toBe(ev(1, "run_completed").at);
  });

  it("run_failed sets failed, end time and failure code", () => {
    const state = applyEvent(initialTraceState(), ev(1, "run_failed", { error_code: "TOO_FEW_PERSONAS" }));
    expect(state.phase).toBe("failed");
    expect(state.failureCode).toBe("TOO_FEW_PERSONAS");
    expect(state.endedAt).toBe(ev(1, "run_failed").at);
  });

  it("run_failed without error code leaves failureCode null", () => {
    expect(applyEvent(initialTraceState(), ev(1, "run_failed")).failureCode).toBeNull();
  });

  it("unknown event types only advance lastEventId", () => {
    const before = initialTraceState();
    const after = applyEvent(before, ev(7, "something_new"));
    expect(after).toEqual({ ...before, lastEventId: 7 });
  });

  it("does not mutate a frozen input state", () => {
    const frozen = Object.freeze({
      ...initialTraceState(),
      personas: Object.freeze([]) as never,
    });
    expect(() => applyEvent(frozen, ev(1, "run_started"))).not.toThrow();
    expect(() =>
      applyEvent(frozen, ev(2, "persona_started", { persona_index: 0, persona_name: "A" }))
    ).not.toThrow();
  });

  it("returns the very same object for an already seen event id", () => {
    const state = applyEvent(initialTraceState(), ev(5, "run_started"));
    expect(applyEvent(state, ev(5, "run_started"))).toBe(state);
    expect(applyEvent(state, ev(3, "personas_generated", { input_tokens: 1 }))).toBe(state);
  });

  it("replaying the same sequence twice equals playing it once", () => {
    const events = fullRunEvents();
    const once = replay(events);
    const twice = replay(events, once);
    expect(twice).toEqual(once);
    expect(twice.inputTokens).toBe(once.inputTokens);
    expect(twice.retryCount).toBe(once.retryCount);
    expect(twice.personas).toHaveLength(18);
  });

  it("a full recorded run ends done with the expected counts and token sums", () => {
    const state = replay(fullRunEvents());
    expect(state.phase).toBe("done");
    expect(countByStatus(state)).toEqual({ queued: 0, running: 0, completed: 17, failed: 1 });
    expect(state.retryCount).toBe(1);
    expect(state.inputTokens).toBe(120 + 17 * 100 + 10 + 500);
    expect(state.outputTokens).toBe(900 + 17 * 200 + 20 + 300);
  });

  it("counts queued personas in the personas phase", () => {
    const events = [
      ev(1, "run_started"),
      ev(2, "personas_generated"),
      ...[0, 1, 2, 3, 4].map((i) =>
        ev(3 + i, "persona_started", { persona_index: i, persona_name: `P${i}` })
      ),
    ];
    expect(countByStatus(replay(events))).toEqual({ queued: 13, running: 5, completed: 0, failed: 0 });
  });

  it("reports no queued personas outside the personas phase", () => {
    const state = replay([ev(1, "run_started"), ev(2, "persona_started", { persona_index: 0, persona_name: "A" })]);
    expect(countByStatus(state).queued).toBe(0);
  });

  it("keeps personas sorted by index when they start out of order", () => {
    const state = replay([
      ev(1, "persona_started", { persona_index: 3, persona_name: "D" }),
      ev(2, "persona_started", { persona_index: 0, persona_name: "A" }),
      ev(3, "persona_started", { persona_index: 2, persona_name: "C" }),
    ]);
    expect(state.personas.map((p) => p.index)).toEqual([0, 2, 3]);
  });
});
