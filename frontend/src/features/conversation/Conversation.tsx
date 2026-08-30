import { type FormEvent, useState } from "react";

import { StatusBadge } from "../../components/ui/StatusBadge";
import { RichText } from "../../components/ui/RichText";
import { sendChatMessage } from "./chatApi";
import {
  isClarificationResponse,
  isExecutionResponse,
  isMemoryResponse,
  isPlannerResponse,
  isStatusResponse,
} from "./chatResponse";
import type { ChatRequest, ChatResponse, MemoryResponse } from "./chatTypes";

interface Exchange {
  id: number;
  userMessage: string;
  response: ChatResponse;
}

const CLIENT_ID_STORAGE_KEY = "daisy_client_id";

function getOrCreateClientId(): string {
  const existingClientId = window.localStorage.getItem(CLIENT_ID_STORAGE_KEY);

  if (existingClientId) {
    return existingClientId;
  }

  const clientId = crypto.randomUUID();
  window.localStorage.setItem(CLIENT_ID_STORAGE_KEY, clientId);
  return clientId;
}

export function Conversation() {
  const [message, setMessage] = useState("");
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [clarificationToken, setClarificationToken] = useState<string | null>(
    null,
  );
  const [clientId] = useState(getOrCreateClientId);
  const [isSending, setIsSending] = useState(false);
  const [requestError, setRequestError] = useState<string | null>(null);

  async function submitRequest(
    request: ChatRequest,
    displayedUserMessage: string,
  ) {
    if (isSending) return;

    setIsSending(true);
    setRequestError(null);

    try {
      const response = await sendChatMessage(request);

      setExchanges((current) => [
        ...current,
        {
          id: Date.now(),
          userMessage: displayedUserMessage,
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

      return response;
    } catch (error) {
      setRequestError(
        error instanceof Error
          ? error.message
          : "D.AI.SY could not complete the request.",
      );

      return null;
    } finally {
      setIsSending(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedMessage = message.trim();
    if (!trimmedMessage || isSending) return;

    setMessage("");

    await submitRequest(
      {
        message: trimmedMessage,
        clarification_token: clarificationToken,
        client_id: clientId,
      },
      trimmedMessage,
    );
  }

  async function handleProposeStrategy(strategy: string) {
    await submitRequest(
      {
        message: strategy,
        client_id: clientId,
        memory_action: "propose",
      },
      "Please ask before remembering this strategy.",
    );
  }

  async function handleApproveMemory(memory: MemoryResponse) {
    if (!memory.memory_token) {
      setRequestError(
        "D.AI.SY cannot remember this strategy because its approval token is missing.",
      );
      return;
    }

    await submitRequest(
      {
        message: "",
        client_id: clientId,
        memory_action: "approve",
        memory_token: memory.memory_token,
      },
      "Remember this.",
    );
  }

  async function handleOfferStrategy(originalMessage: string) {
    await submitRequest(
      {
        message: originalMessage,
        client_id: clientId,
        memory_action: "offer",
      },
      originalMessage,
    );
  }

  async function handleApplyStrategy(memory: MemoryResponse) {
    if (!memory.memory_id || !memory.original_message) {
      setRequestError(
        "D.AI.SY cannot apply this strategy because the saved context is incomplete.",
      );
      return;
    }

    await submitRequest(
      {
        message: memory.original_message,
        client_id: clientId,
        memory_action: "apply",
        memory_id: memory.memory_id,
      },
      "Yes, use that approach.",
    );
  }

  async function handleUseDifferentApproach(memory: MemoryResponse) {
    if (!memory.original_message) {
      setRequestError(
        "D.AI.SY cannot continue because the original request is unavailable.",
      );
      return;
    }

    await submitRequest(
      {
        message: memory.original_message,
        client_id: clientId,
      },
      "Use a different approach.",
    );
  }

  function handleDeclineMemory(exchangeId: number) {
    setExchanges((current) =>
      current.map((exchange) => {
        if (exchange.id !== exchangeId) {
          return exchange;
        }

        return {
          ...exchange,
          response: {
            agent: "memory",
            status: "no_strategy",
            message:
              "Not remembered. Nothing was saved. You can choose to teach D.AI.SY this strategy later.",
          },
        };
      }),
    );
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

              <ResponseCard
                exchangeId={exchange.id}
                userMessage={exchange.userMessage}
                response={exchange.response}
                disabled={isSending}
                onProposeStrategy={handleProposeStrategy}
                onApproveMemory={handleApproveMemory}
                onDeclineMemory={handleDeclineMemory}
                onOfferStrategy={handleOfferStrategy}
                onApplyStrategy={handleApplyStrategy}
                onUseDifferentApproach={handleUseDifferentApproach}
              />
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
            AI assists. You decide. Strategies are remembered only with your
            explicit approval.
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

interface ResponseCardProps {
  exchangeId: number;
  userMessage: string;
  response: ChatResponse;
  disabled: boolean;
  onProposeStrategy: (strategy: string) => Promise<void>;
  onApproveMemory: (memory: MemoryResponse) => Promise<void>;
  onDeclineMemory: (exchangeId: number) => void;
  onOfferStrategy: (originalMessage: string) => Promise<void>;
  onApplyStrategy: (memory: MemoryResponse) => Promise<void>;
  onUseDifferentApproach: (memory: MemoryResponse) => Promise<void>;
}

function ResponseCard({
  exchangeId,
  userMessage,
  response,
  disabled,
  onProposeStrategy,
  onApproveMemory,
  onDeclineMemory,
  onOfferStrategy,
  onApplyStrategy,
  onUseDifferentApproach,
}: ResponseCardProps) {
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

  if (isMemoryResponse(response)) {
    return (
      <MemoryCard
        exchangeId={exchangeId}
        response={response}
        disabled={disabled}
        onApproveMemory={onApproveMemory}
        onDeclineMemory={onDeclineMemory}
        onApplyStrategy={onApplyStrategy}
        onUseDifferentApproach={onUseDifferentApproach}
      />
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

      <RichText>
        {response.reply ??
          response.error ??
          "D.AI.SY returned a response without displayable text."}
      </RichText>

      {response.reply ? (
        <div className="memory-actions">
          <button
            type="button"
            disabled={disabled}
            onClick={() => void onProposeStrategy(userMessage)}
          >
            Remember this as a strategy
          </button>

          <button
            type="button"
            disabled={disabled}
            onClick={() => void onOfferStrategy(userMessage)}
          >
            Use a strategy I've taught D.AI.SY
          </button>
        </div>
      ) : null}
    </article>
  );
}

interface MemoryCardProps {
  exchangeId: number;
  response: MemoryResponse;
  disabled: boolean;
  onApproveMemory: (memory: MemoryResponse) => Promise<void>;
  onDeclineMemory: (exchangeId: number) => void;
  onApplyStrategy: (memory: MemoryResponse) => Promise<void>;
  onUseDifferentApproach: (memory: MemoryResponse) => Promise<void>;
}

function MemoryCard({
  exchangeId,
  response,
  disabled,
  onApproveMemory,
  onDeclineMemory,
  onApplyStrategy,
  onUseDifferentApproach,
}: MemoryCardProps) {
  if (response.status === "approval_required") {
    return (
      <article className="message-card daisy-response memory-card">
        <p className="eyebrow">A strategy that works for you</p>
        <h3>Would you like D.AI.SY to remember this?</h3>
        <p>{response.strategy}</p>
        <p>
          This is your strategy. D.AI.SY will save it only if you explicitly
          approve.
        </p>

        <div className="memory-actions">
          <button
            type="button"
            disabled={disabled}
            onClick={() => void onApproveMemory(response)}
          >
            Remember this
          </button>

          <button
            type="button"
            disabled={disabled}
            onClick={() => onDeclineMemory(exchangeId)}
          >
            Not now
          </button>
        </div>
      </article>
    );
  }

  if (response.status === "remembered") {
    return (
      <article className="message-card daisy-response memory-card">
        <h3>✓ Remembered with your permission</h3>
        <p>{response.strategy}</p>
        <p>You stay in control of how D.AI.SY uses what you've taught it.</p>
      </article>
    );
  }

  if (response.status === "strategy_available") {
    return (
      <article className="message-card daisy-response memory-card">
        <p className="eyebrow">A strategy you've taught D.AI.SY</p>
        <h3>Would you like me to use this approach here?</h3>
        <p>{response.strategy}</p>

        <div className="memory-actions">
          <button
            type="button"
            disabled={disabled}
            onClick={() => void onApplyStrategy(response)}
          >
            Yes, use this approach
          </button>

          <button
            type="button"
            disabled={disabled}
            onClick={() => void onUseDifferentApproach(response)}
          >
            Use a different approach
          </button>
        </div>
      </article>
    );
  }

  if (response.status === "no_strategy") {
    return (
      <article className="message-card daisy-response memory-card">
        <h3>
          {response.message?.startsWith("Not remembered")
            ? "Not remembered"
            : "No saved strategy yet"}
        </h3>
        <p>
          {response.message ??
            "You haven't explicitly taught D.AI.SY a strategy to use here."}
        </p>
      </article>
    );
  }

  return (
    <article className="message-card daisy-response memory-card">
      <h3>D.AI.SY · Memory</h3>
      <p>
        {response.message ??
          "D.AI.SY could not complete that memory request. Nothing was changed."}
      </p>
    </article>
  );
}