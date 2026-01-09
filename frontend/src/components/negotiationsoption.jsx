import { useState } from "react";

function NegotiationOptions({ plans, onSelect }) {
  if (!plans?.length) return null;

  return (
    <div className="p-4 bg-card border-t border-border flex flex-wrap gap-2.5 mt-3">
      <p className="w-full mb-2 text-xs font-semibold text-foreground">
        <strong>Select a payment option:</strong>
      </p>
      {plans.map((plan, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(plan.name)}
          className="px-4 py-2.5 rounded-full border border-primary bg-accent text-accent-foreground text-xs font-medium cursor-pointer transition-all hover:bg-primary hover:text-primary-foreground hover:shadow-md active:scale-95"
        >
          {plan.name}: {plan.description}
        </button>
      ))}
    </div>
  );
}

export default NegotiationOptions;
