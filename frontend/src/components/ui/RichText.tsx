import type { ReactNode } from "react";

interface RichTextProps {
  children: string;
}

function renderInline(text: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }

    return part;
  });
}

export function RichText({ children }: RichTextProps) {
  const lines = children.split(/\r?\n/);
  const content: ReactNode[] = [];
  let paragraphLines: string[] = [];
  let listItems: string[] = [];

  function flushParagraph() {
    if (paragraphLines.length === 0) return;

    content.push(
      <p key={`paragraph-${content.length}`}>
        {renderInline(paragraphLines.join(" "))}
      </p>,
    );

    paragraphLines = [];
  }

  function flushList() {
    if (listItems.length === 0) return;

    content.push(
      <ol key={`list-${content.length}`} className="conversation-plan">
        {listItems.map((item, index) => (
          <li key={`${index}-${item}`}>{renderInline(item)}</li>
        ))}
      </ol>,
    );

    listItems = [];
  }

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }

    const headingMatch = line.match(/^#{1,4}\s+(.+)$/);

    if (headingMatch) {
      flushParagraph();
      flushList();

      content.push(
        <h4 key={`heading-${content.length}`}>
          {renderInline(headingMatch[1])}
        </h4>,
      );
      continue;
    }

    const numberedItemMatch = line.match(/^\d+\.\s+(.+)$/);

    if (numberedItemMatch) {
      flushParagraph();
      listItems.push(numberedItemMatch[1]);
      continue;
    }

    flushList();
    paragraphLines.push(line);
  }

  flushParagraph();
  flushList();

  return <div className="rich-text">{content}</div>;
}