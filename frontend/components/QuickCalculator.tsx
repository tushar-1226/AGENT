'use client';

import { useState } from 'react';

export default function QuickCalculator() {
    const [input, setInput] = useState('');
    const [result, setResult] = useState('');

    const calculate = () => {
        try {
            // Safe evaluation using Function constructor
            const sanitized = input.replace(/[^0-9+\-*/().% ]/g, '');
            const calculated = Function('"use strict"; return (' + sanitized + ')')();
            setResult(calculated.toString());
        } catch (error) {
            setResult('Error');
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            calculate();
        }
    };

    const buttons = [
        '7', '8', '9', '/',
        '4', '5', '6', '*',
        '1', '2', '3', '-',
        '0', '.', '=', '+'
    ];

    const handleButtonClick = (value: string) => {
        if (value === '=') {
            calculate();
        } else if (value === 'C') {
            setInput('');
            setResult('');
        } else {
            setInput(input + value);
        }
    };

    return (
        <div className="glass-card p-5">
            <h3 className="text-lg font-semibold text-white mb-4">🔢 Calculator</h3>

            {/* Display */}
            <div className="mb-4 space-y-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Enter calculation..."
                    className="w-full px-4 py-3 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white text-right font-mono text-lg focus:outline-none focus:border-blue-500/30"
                />
                {result && (
                    <div className="text-right text-2xl font-bold text-blue-400 font-mono">
                        = {result}
                    </div>
                )}
            </div>

            {/* Calculator Buttons */}
            <div className="grid grid-cols-4 gap-2">
                {buttons.map((btn) => (
                    <button
                        key={btn}
                        onClick={() => handleButtonClick(btn)}
                        className={`p-3 rounded-lg font-semibold transition-all ${btn === '='
                                ? 'bg-blue-500 hover:bg-blue-600 text-white col-span-1'
                                : ['+', '-', '*', '/'].includes(btn)
                                    ? 'bg-purple-500/20 hover:bg-purple-500/30 text-purple-300'
                                    : 'bg-white/[0.04] hover:bg-white/[0.08] text-white'
                            }`}
                    >
                        {btn}
                    </button>
                ))}
            </div>

            {/* Clear Button */}
            <button
                onClick={() => { setInput(''); setResult(''); }}
                className="w-full mt-2 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 font-semibold transition-all"
            >
                Clear
            </button>

            {/* Quick Conversions */}
            <div className="mt-4 pt-4 border-t border-white/[0.08]">
                <div className="text-xs text-gray-400 mb-2">Quick conversions:</div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                    <button
                        onClick={() => setInput(input + '*1.6')}
                        className="px-2 py-1 rounded bg-white/[0.04] hover:bg-white/[0.08] text-gray-300"
                    >
                        mi → km (*1.6)
                    </button>
                    <button
                        onClick={() => setInput(input + '/1.6')}
                        className="px-2 py-1 rounded bg-white/[0.04] hover:bg-white/[0.08] text-gray-300"
                    >
                        km → mi (/1.6)
                    </button>
                    <button
                        onClick={() => setInput(input + '*2.54')}
                        className="px-2 py-1 rounded bg-white/[0.04] hover:bg-white/[0.08] text-gray-300"
                    >
                        in → cm (*2.54)
                    </button>
                    <button
                        onClick={() => setInput(input + '*0.45')}
                        className="px-2 py-1 rounded bg-white/[0.04] hover:bg-white/[0.08] text-gray-300"
                    >
                        lb → kg (*0.45)
                    </button>
                </div>
            </div>
        </div>
    );
}
