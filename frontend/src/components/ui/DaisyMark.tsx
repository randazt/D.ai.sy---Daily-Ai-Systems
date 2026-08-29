export function DaisyMark() {
  return (
    <svg
      className="daisy-mark"
      viewBox="0 0 64 64"
      role="img"
      aria-label="D.AI.SY daisy mark"
    >
      <circle className="daisy-petal petal-top" cx="32" cy="14" r="9" />
      <circle className="daisy-petal petal-right" cx="50" cy="32" r="9" />
      <circle className="daisy-petal petal-bottom" cx="32" cy="50" r="9" />
      <circle className="daisy-petal petal-left" cx="14" cy="32" r="9" />
      <circle className="daisy-petal petal-diagonal-a" cx="44" cy="20" r="8" />
      <circle className="daisy-petal petal-diagonal-b" cx="44" cy="44" r="8" />
      <circle className="daisy-petal petal-diagonal-c" cx="20" cy="44" r="8" />
      <circle className="daisy-petal petal-diagonal-d" cx="20" cy="20" r="8" />
      <circle className="daisy-center" cx="32" cy="32" r="10" />
    </svg>
  );
}
