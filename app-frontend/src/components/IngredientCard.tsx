import React from 'react';

interface IngredientCardProps {
  name: string;
  amount: number | string;
  unit: string;
  highlightStatus: 'none' | 'input';
}

export default function IngredientCard({ name, amount, unit, highlightStatus }: IngredientCardProps) {
  // Determine colors based on the highlight status
  const baseClasses = "p-3 rounded-md border transition-all duration-200 flex justify-between items-center";
  const statusClasses = 
    highlightStatus === 'input' 
      ? "bg-amber-50 border-amber-400 shadow-sm" // 2nd color: Amber for inputs
      : "bg-white border-gray-200 text-gray-700 opacity-80 hover:opacity-100";

  return (
    <div className={`${baseClasses} ${statusClasses}`}>
      <span className={`font-medium ${highlightStatus === 'input' ? 'text-amber-900' : 'text-gray-900'}`}>
        {name}
      </span>
      <span className="text-sm bg-black/5 px-2 py-1 rounded">
        {amount} {unit}
      </span>
    </div>
  );
}