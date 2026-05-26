// import React from 'react';

interface Step {
  instruction: string;
  action: string;
  inputs: string[];
  result_name: string;
  metadata: string[][];
}

interface StepCardProps {
  step: Step;
  index: number;
  highlightStatus: 'none' | 'active' | 'input';
  onHover: () => void;
  onLeave: () => void;
}

export default function StepCard({ step, index, highlightStatus, onHover, onLeave }: StepCardProps) {
  let statusClasses = "bg-white border-gray-200 opacity-80";
  
  if (highlightStatus === 'active') {
    // 3rd color: Blue for the active step/output
    statusClasses = "bg-blue-50 border-blue-400 shadow-md ring-1 ring-blue-400"; 
  } else if (highlightStatus === 'input') {
    // 2nd color: Amber for steps that act as inputs to the active step
    statusClasses = "bg-amber-50 border-amber-400 shadow-sm";
  }

  return (
    <div 
      className={`p-4 rounded-lg border transition-all duration-200 cursor-pointer ${statusClasses}`}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
    >
      <div className="flex justify-between items-start mb-2">
        <h4 className={`font-bold uppercase text-sm tracking-wide ${
          highlightStatus === 'active' ? 'text-blue-700' : 
          highlightStatus === 'input' ? 'text-amber-700' : 'text-gray-500'
        }`}>
          Step {index + 1}: {step.action}
        </h4>
        
        {/* The Output Badge */}
        <span className={`text-xs font-mono px-2 py-1 rounded ${
          highlightStatus === 'active' ? 'bg-blue-200 text-blue-900 font-bold' : 'bg-gray-100 text-gray-600'
        }`}>
          Output: {step.result_name}
        </span>
      </div>

      <p className={`text-sm mb-4 ${highlightStatus === 'none' ? 'text-gray-600' : 'text-gray-900'}`}>
        {step.instruction}
      </p>

      {/* Metadata Tablets */}
      {step.metadata && step.metadata.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {step.metadata.map(([key, value], i) => (
            <div key={i} className="flex text-xs rounded border border-gray-200 overflow-hidden">
              <span className="bg-gray-100 px-2 py-1 text-gray-500 font-medium">{key}</span>
              <span className="bg-white px-2 py-1 text-gray-700">{value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}