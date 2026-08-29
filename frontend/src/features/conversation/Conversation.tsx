import { type FormEvent, useState } from "react";

import { StatusBadge } from "../../components/ui/StatusBadge";
import { sendChatMessage } from "./chatApi";
import {
  isClarificationResponse,
  isExecutionResponse,
  isPlannerResponse,
  isStatusResponse,
} from "./chatResponse";
import type { ChatResponse } from "./chatTypes";

interface Exchange {
  id: number;
  userMessage: string;
  response: ChatResponse;
}

export function Conversation() {
  const [message, setMessage] = useState("");
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [clarificationToken, setClarificationToken] = useState<string | null>(
    null,
  );
  const [isSending, setIsSending] = useState(false);
  const [requestError, setRequestError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedMessage = message.trim();
    if (!trimmedMessage || isSending) return;

    setIsSending(true);
    setRequestError(null);

    try {
      const response = await sendChatMessage({
        message: trimmedMessage,
        clarification_token: clarificationToken,
      });

      setExchanges((current) => [
        ...current,
        {
          id: Date.now(),
          userMessage: trimmedMessage,
          response,
        },
      ]);

      if (
        isClarificationResponse(response) &&
        response.status === "needs_clarification" &&
        response.clarification_token
      ) {
        setClarificationToken(response.clarification_token);
      } else {
        setClarificationToken(null);
      }

      setMessage("");
    } catch (error) {
      setRequestError(
        error instanceof Error
          ? error.message
          : "D.AI.SY could not complete the request.",
      );
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="conversation-surface">
      <header className="conversation-header">
        <div>
          <p className="eyebrow">Live D.AI.SY</p>
          <h1>Conversation</h1>
          <p>
            Tell me what you're trying to understand, decide, learn, or
            accomplish. I'll help you find the next clear step.
          </p>
        </div>
        <StatusBadge>Connected to /chat</StatusBadge>
      </header>

      <section
        className="conversation-thread"
        aria-label="Current D.AI.SY conversation"
        aria-live="polite"
      >
        {exchanges.length === 0 ? (
          <div className="conversation-empty">
            <h2>What would you like help with?</h2>
            <p>
              Start in your own words. D.AI.SY may ask for clarification before
              creating a plan or taking the next supported step.
            </p>
          </div>
        ) : (
          exchanges.map((exchange) => (
            <div className="conversation-exchange" key={exchange.id}>
              <article className="message-card user-context">
                <h3>You</h3>
                <p>{exchange.userMessage}</p>
              </article>

              <ResponseCard response={exchange.response} />
            </div>
          ))
        )}
      </section>

      {requestError ? (
        <p className="conversation-error" role="alert">
          {requestError}
        </p>
      ) : null}
      <form className="conversation-composer" onSubmit={handleSubmit}>
        <label htmlFor="daisy-message">Message D.AI.SY</label>
        <textarea
          id="daisy-message"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder={
            clarificationToken
              ? "Answer D.AI.SY's clarification question..."
              : "What do you want help with?"
          }
          rows={4}
          disabled={isSending}
        />

        <div className="composer-footer">
          <p>
            AI assists. You decide. This conversation is not persisted by this
            frontend.
          </p>
          <button
            className="conversation-send"
            type="submit"
            disabled={isSending || !message.trim()}
          >
            {isSending ? "Thinking..." : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
}

function ResponseCard({ response }: { response: ChatResponse }) {
  if (isClarificationResponse(response)) {
    return (
      <article className="message-card daisy-response">
        <h3>D.AI.SY · Clarification</h3>
        <p>
          {response.question ??
            response.message ??
            "I need a little more information before continuing."}
        </p>
      </article>
    );
  }

  if (isPlannerResponse(response)) {
    return (
      <article className="message-card daisy-response">
        <div className="section-heading-row compact">
          <h3>D.AI.SY · Plan</h3>
          <StatusBadge>{response.project.status}</StatusBadge>
        </div>
        <p>
          <strong>Goal:</strong> {response.goal}
        </p>
        <ol className="conversation-plan">
          {response.plan.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </article>
    );
  }

  if (isExecutionResponse(response)) {
    return (
      <article className="message-card daisy-response">
        <div className="section-heading-row compact">
          <h3>D.AI.SY · Execution</h3>
          <StatusBadge>{response.status}</StatusBadge>
        </div>
        <p>
          <strong>Current task:</strong> {response.current_task.title}
        </p>
        <p>{response.execution.output || response.execution.error}</p>
        {response.decision ? (
          <p>
            <strong>Decision:</strong> {response.decision.decision} —{" "}
            {response.decision.reason}
          </p>
        ) : null}
      </article>
    );
  }

  if (isStatusResponse(response)) {
    return (
      <article className="message-card daisy-response">
        <h3>D.AI.SY · Status</h3>
        <p>{response.message}</p>
      </article>
    );
  }

  return (
    <article className="message-card daisy-response">
      <h3>D.AI.SY</h3>
      <p>
        {response.reply ??
          response.error ??
          "D.AI.SY returned a response without displayable text."}
      </p>
    </article>
  );
}