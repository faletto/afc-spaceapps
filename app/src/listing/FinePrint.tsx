/** Fictional-premise disclaimer (requirements "Fictional premise, real data", UI-3). */
export const DISCLAIMER =
  "The Moonstimate is Lunar Listings' estimated market value for a plot. It is not an appraisal, and it is fictional: " +
  'under the 1967 Outer Space Treaty no nation can claim the Moon, and nobody can buy lunar land today. ' +
  'The prices are made up; the science behind them is real.';

export function FinePrint({ compact = false }: { compact?: boolean }) {
  return (
    <p data-testid="fineprint" style={{ margin: 0, fontSize: compact ? 11 : 12, opacity: 0.65, lineHeight: 1.4 }}>
      {DISCLAIMER}
    </p>
  );
}

export function InfoIcon() { return <span title={DISCLAIMER} aria-label="About this price" role="img" style={{ cursor: 'help', opacity: 0.7 }}>ⓘ</span>; }
