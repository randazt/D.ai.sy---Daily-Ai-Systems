import { DaisyMark } from "../../components/ui/DaisyMark";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { PreviewPanel } from "./PreviewPanel";

const entryCards = [
  {
    title: "Help me think something through",
    description: "Talk it out and find clarity",
  },
  {
    title: "Help me accomplish a goal",
    description: "Break it down and make a plan",
  },
  {
    title: "Help me learn something",
    description: "Explain it in a way that clicks",
  },
  {
    title: "Help me build a workflow",
    description: "Create a system that works for me",
  },
];

const decisionCards = [
  {
    title: "Understanding what I need to do",
    description: "It feels confusing",
  },
  {
    title: "Getting started",
    description: "I struggle to begin",
  },
  {
    title: "Keeping track of everything",
    description: "Too many steps, dates, or details",
  },
  {
    title: "I'm not sure yet",
    description: "Help me figure it out",
  },
];

export function Home() {
  return (
    <div className="home-layout">
      <section className="home-primary" aria-labelledby="home-heading">
        <header className="home-header">
          <div>
            <p className="eyebrow">Good morning</p>
            <h1 id="home-heading">D.AI.SY</h1>
          </div>
          <StatusBadge>Product Shell Preview</StatusBadge>
        </header>

        <section className="hero-panel" aria-labelledby="hero-title">
          <div className="hero-mark" aria-hidden="true">
            <DaisyMark />
          </div>
          <div>
            <h2 id="hero-title">
              I help you understand, decide, learn, and act—in a way that works
              for you.
            </h2>
            <p>You're in charge. I'm here to help.</p>
          </div>
        </section>

        <section className="entry-section" aria-labelledby="entry-heading">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Start with what you need</p>
              <h2 id="entry-heading">Choose a kind of support</h2>
            </div>
          </div>

          <div className="entry-grid">
            {entryCards.map((card) => (
              <button className="entry-card" type="button" key={card.title}>
                <span>{card.title}</span>
                <small>{card.description}</small>
              </button>
            ))}
          </div>
        </section>

        <section
          className="demo-workspace"
          aria-labelledby="demo-workspace-heading"
        >
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Presentation-only example</p>
              <h2 id="demo-workspace-heading">
                Human choice before structured support
              </h2>
            </div>
            <StatusBadge>Demo state</StatusBadge>
          </div>

          <div className="example-conversation">
            <article className="message-card user-context">
              <h3>Example user context</h3>
              <p>
                "I need to renew my professional certification, but I have a
                learning disability and I keep getting overwhelmed by everything
                I need to do. I don't even know where to start."
              </p>
            </article>

            <article className="message-card daisy-response">
              <h3>D.AI.SY response</h3>
              <p>
                "Before we build a plan, what feels like the biggest barrier
                right now?"
              </p>
            </article>
          </div>

          <div className="decision-grid" aria-label="Example decision choices">
            {decisionCards.map((card) => (
              <button className="decision-card" type="button" key={card.title}>
                <span>{card.title}</span>
                <small>{card.description}</small>
              </button>
            ))}
          </div>

          <p className="boundary-note">
            This example demonstrates human choice, clarification, and
            structured support. It does not infer limitations, diagnose,
            evaluate, treat, or store user data.
          </p>
        </section>
      </section>

      <PreviewPanel />
    </div>
  );
}
