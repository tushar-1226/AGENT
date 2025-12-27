'use client';

import { useState } from 'react';

export default function ToolsPage() {
    const [activeTool, setActiveTool] = useState<string | null>(null);

    // Calculator
    const [calcDisplay, setCalcDisplay] = useState('0');
    const [calcPrevValue, setCalcPrevValue] = useState<string | null>(null);
    const [calcOperation, setCalcOperation] = useState<string | null>(null);

    // Timer
    const [timerSeconds, setTimerSeconds] = useState(0);
    const [timerRunning, setTimerRunning] = useState(false);
    const [timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null);

    // Color Picker
    const [selectedColor, setSelectedColor] = useState('#3b82f6');

    // Password Generator
    const [password, setPassword] = useState('');
    const [passwordLength, setPasswordLength] = useState(16);
    const [includeUppercase, setIncludeUppercase] = useState(true);
    const [includeLowercase, setIncludeLowercase] = useState(true);
    const [includeNumbers, setIncludeNumbers] = useState(true);
    const [includeSymbols, setIncludeSymbols] = useState(true);

    // Text Counter
    const [textInput, setTextInput] = useState('');

    // JSON Formatter
    const [jsonInput, setJsonInput] = useState('');
    const [jsonOutput, setJsonOutput] = useState('');

    // Base64
    const [base64Input, setBase64Input] = useState('');
    const [base64Output, setBase64Output] = useState('');

    // Unit Converter
    const [unitValue, setUnitValue] = useState('1');
    const [unitFrom, setUnitFrom] = useState('km');
    const [unitTo, setUnitTo] = useState('miles');

    // Random Number
    const [randomMin, setRandomMin] = useState(1);
    const [randomMax, setRandomMax] = useState(100);
    const [randomResult, setRandomResult] = useState<number | null>(null);

    // Notes
    const [notes, setNotes] = useState('');

    const tools = [
        {
            id: 'calculator',
            name: 'Calculator',
            description: 'Basic arithmetic calculator',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
            )
        },
        {
            id: 'timer',
            name: 'Timer & Stopwatch',
            description: 'Track time for tasks',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            )
        },
        {
            id: 'color-picker',
            name: 'Color Picker',
            description: 'Pick and preview colors',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
            )
        },
        {
            id: 'password',
            name: 'Password Generator',
            description: 'Generate secure passwords',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
            )
        },
        {
            id: 'text-counter',
            name: 'Text Counter',
            description: 'Count words, characters, lines',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            )
        },
        {
            id: 'json',
            name: 'JSON Formatter',
            description: 'Format and validate JSON',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
            )
        },
        {
            id: 'base64',
            name: 'Base64 Encoder/Decoder',
            description: 'Encode and decode Base64',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
            )
        },
        {
            id: 'unit-converter',
            name: 'Unit Converter',
            description: 'Convert between units',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                </svg>
            )
        },
        {
            id: 'random',
            name: 'Random Number',
            description: 'Generate random numbers',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                </svg>
            )
        },
        {
            id: 'notes',
            name: 'Quick Notes',
            description: 'Temporary scratchpad',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
            )
        }
    ];

    // Calculator functions
    const handleCalcNumber = (num: string) => {
        if (calcDisplay === '0' || calcDisplay === 'Error') {
            setCalcDisplay(num);
        } else {
            setCalcDisplay(calcDisplay + num);
        }
    };

    const handleCalcOperation = (op: string) => {
        setCalcPrevValue(calcDisplay);
        setCalcOperation(op);
        setCalcDisplay('0');
    };

    const handleCalcEquals = () => {
        if (calcPrevValue && calcOperation) {
            const prev = parseFloat(calcPrevValue);
            const current = parseFloat(calcDisplay);
            let result = 0;

            switch (calcOperation) {
                case '+':
                    result = prev + current;
                    break;
                case '-':
                    result = prev - current;
                    break;
                case '*':
                    result = prev * current;
                    break;
                case '/':
                    result = current !== 0 ? prev / current : 0;
                    break;
            }

            setCalcDisplay(result.toString());
            setCalcPrevValue(null);
            setCalcOperation(null);
        }
    };

    const handleCalcClear = () => {
        setCalcDisplay('0');
        setCalcPrevValue(null);
        setCalcOperation(null);
    };

    // Timer functions
    const startTimer = () => {
        setTimerRunning(true);
        const interval = setInterval(() => {
            setTimerSeconds(prev => prev + 1);
        }, 1000);
        setTimerInterval(interval);
    };

    const stopTimer = () => {
        setTimerRunning(false);
        if (timerInterval) {
            clearInterval(timerInterval);
        }
    };

    const resetTimer = () => {
        stopTimer();
        setTimerSeconds(0);
    };

    const formatTime = (seconds: number) => {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // Password Generator
    const generatePassword = () => {
        let charset = '';
        if (includeUppercase) charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        if (includeLowercase) charset += 'abcdefghijklmnopqrstuvwxyz';
        if (includeNumbers) charset += '0123456789';
        if (includeSymbols) charset += '!@#$%^&*()_+-=[]{}|;:,.<>?';

        if (charset === '') {
            setPassword('Please select at least one character type');
            return;
        }

        let newPassword = '';
        for (let i = 0; i < passwordLength; i++) {
            newPassword += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        setPassword(newPassword);
    };

    // Text Counter
    const countText = () => {
        const words = textInput.trim().split(/\s+/).filter(word => word.length > 0).length;
        const chars = textInput.length;
        const charsNoSpaces = textInput.replace(/\s/g, '').length;
        const lines = textInput.split('\n').length;
        const sentences = textInput.split(/[.!?]+/).filter(s => s.trim().length > 0).length;

        return { words, chars, charsNoSpaces, lines, sentences };
    };

    // JSON Formatter
    const formatJSON = () => {
        try {
            const parsed = JSON.parse(jsonInput);
            setJsonOutput(JSON.stringify(parsed, null, 2));
        } catch (error) {
            setJsonOutput('Invalid JSON: ' + (error as Error).message);
        }
    };

    // Base64
    const encodeBase64 = () => {
        try {
            setBase64Output(btoa(base64Input));
        } catch (error) {
            setBase64Output('Error encoding: ' + (error as Error).message);
        }
    };

    const decodeBase64 = () => {
        try {
            setBase64Output(atob(base64Input));
        } catch (error) {
            setBase64Output('Error decoding: ' + (error as Error).message);
        }
    };

    // Unit Converter
    const convertUnit = () => {
        const conversions: { [key: string]: number } = {
            // Length
            'km': 1000,
            'm': 1,
            'cm': 0.01,
            'mm': 0.001,
            'miles': 1609.34,
            'yards': 0.9144,
            'feet': 0.3048,
            'inches': 0.0254,
        };

        const value = parseFloat(unitValue);
        if (isNaN(value)) return '0';

        const inMeters = value * conversions[unitFrom];
        const result = inMeters / conversions[unitTo];
        return result.toFixed(4);
    };

    // Random Number
    const generateRandom = () => {
        const min = Math.min(randomMin, randomMax);
        const max = Math.max(randomMin, randomMax);
        setRandomResult(Math.floor(Math.random() * (max - min + 1)) + min);
    };

    const renderTool = () => {
        switch (activeTool) {
            case 'calculator':
                return (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">Calculator</h2>
                        <div className="max-w-sm mx-auto">
                            <div className="bg-black/50 p-4 rounded-lg mb-4 text-right">
                                <div className="text-3xl font-mono text-white">{calcDisplay}</div>
                            </div>
                            <div className="grid grid-cols-4 gap-2">
                                {['7', '8', '9', '/'].map(btn => (
                                    <button
                                        key={btn}
                                        onClick={() => ['+', '-', '*', '/'].includes(btn) ? handleCalcOperation(btn) : handleCalcNumber(btn)}
                                        className="bg-white/10 hover:bg-white/20 p-4 rounded-lg text-xl font-semibold"
                                    >
                                        {btn}
                                    </button>
                                ))}
                                {['4', '5', '6', '*'].map(btn => (
                                    <button
                                        key={btn}
                                        onClick={() => ['+', '-', '*', '/'].includes(btn) ? handleCalcOperation(btn) : handleCalcNumber(btn)}
                                        className="bg-white/10 hover:bg-white/20 p-4 rounded-lg text-xl font-semibold"
                                    >
                                        {btn}
                                    </button>
                                ))}
                                {['1', '2', '3', '-'].map(btn => (
                                    <button
                                        key={btn}
                                        onClick={() => ['+', '-', '*', '/'].includes(btn) ? handleCalcOperation(btn) : handleCalcNumber(btn)}
                                        className="bg-white/10 hover:bg-white/20 p-4 rounded-lg text-xl font-semibold"
                                    >
                                        {btn}
                                    </button>
                                ))}
                                {['0', '.', '=', '+'].map(btn => (
                                    <button
                                        key={btn}
                                        onClick={() => {
                                            if (btn === '=') handleCalcEquals();
                                            else if (btn === '+') handleCalcOperation(btn);
                                            else handleCalcNumber(btn);
                                        }}
                                        className={`${btn === '=' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-white/10 hover:bg-white/20'} p-4 rounded-lg text-xl font-semibold`}
                                    >
                                        {btn}
                                    </button>
                                ))}
                                <button
                                    onClick={handleCalcClear}
                                    className="col-span-4 bg-red-600 hover:bg-red-700 p-4 rounded-lg text-xl font-semibold"
                                >
                                    Clear
                                </button>
                            </div>
                        </div>
                    </div>
                );

            case 'timer':
                return (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">Timer & Stopwatch</h2>
                        <div className="max-w-md mx-auto text-center">
                            <div className="text-6xl font-mono mb-8">{formatTime(timerSeconds)}</div>
                            <div className="flex gap-3 justify-center">
                                {!timerRunning ? (
                                    <button
                                        onClick={startTimer}
                                        className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold"
                                    >
                                        Start
                                    </button>
                                ) : (
                                    <button
                                        onClick={stopTimer}
                                        className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 rounded-lg font-semibold"
                                    >
                                        Stop
                                    </button>
                                )}
                                <button
                                    onClick={resetTimer}
                                    className="px-6 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-semibold"
                                >
                                    Reset
                                </button>
                            </div>
                        </div>
                    </div>
                );

            case 'color-picker':
                return (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">Color Picker</h2>
                        <div className="max-w-md mx-auto">
                            <div
                                className="w-full h-48 rounded-lg mb-4 border-2 border-white/20"
                                style={{ backgroundColor: selectedColor }}
                            />
                            <input
                                type="color"
                                value={selectedColor}
                                onChange={(e) => setSelectedColor(e.target.value)}
                                className="w-full h-16 rounded-lg cursor-pointer"
                            />
                            <div className="mt-4 space-y-2">
                                <div className="flex justify-between items-center bg-black/30 p-3 rounded-lg">
                                    <span className="text-gray-400">HEX:</span>
                                    <span className="font-mono font-semibold">{selectedColor.toUpperCase()}</span>
                                </div>
                                <div className="flex justify-between items-center bg-black/30 p-3 rounded-lg">
                                    <span className="text-gray-400">RGB:</span>
                                    <span className="font-mono font-semibold">
                                        {parseInt(selectedColor.slice(1, 3), 16)}, {parseInt(selectedColor.slice(3, 5), 16)}, {parseInt(selectedColor.slice(5, 7), 16)}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                );

            case 'password':
                return (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">Password Generator</h2>
                        <div className="max-w-md mx-auto space-y-4">
                            <div className="bg-black/30 p-4 rounded-lg font-mono break-all">
                                {password || 'Click generate to create password'}
                            </div>
                            <div>
                                <label className="block text-sm mb-2">Length: {passwordLength}</label>
                                <input
                                    type="range"
                                    min="6"
                                    max="32"
                                    value={passwordLength}
                                    onChange={(e) => setPasswordLength(Number(e.target.value))}
                                    className="w-full"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        checked={includeUppercase}
                                        onChange={(e) => setIncludeUppercase(e.target.checked)}
                                    />
                                    <span>Uppercase (A-Z)</span>
                                </label>
                                <label className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        checked={includeLowercase}
                                        onChange={(e) => setIncludeLowercase(e.target.checked)}
                                    />
                                    <span>Lowercase (a-z)</span>
                                </label>
                                <label className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        checked={includeNumbers}
                                        onChange={(e) => setIncludeNumbers(e.target.checked)}
                                    />
                                    <span>Numbers (0-9)</span>
                                </label>
                                <label className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        checked={includeSymbols}
                                        onChange={(e) => setIncludeSymbols(e.target.checked)}
                                    />
                                    <span>Symbols (!@#$%)</span>
                                </label>
                            </div>
                            <button
                                onClick={generatePassword}
                                className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold"
                            >
                                Generate Password
                            </button>
                            {password && (
                                <button
                                    onClick={() => navigator.clipboard.writeText(password)}
                                    className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold"
                                >
                                    Copy to Clipboard
                                </button>
                            )}
                        </div>
                    </div>
                );

            case 'text-counter':
                const stats = countText();
                return (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">Text Counter</h2>
                        <div className="space-y-4">
                            <textarea
                                value={textInput}
                                onChange={(e) => setTextInput(e.target.value)}
                                placeholder="Type or paste your text here..."
                                className="w-full h-64 bg-black/30 border border-white/10 rounded-lg p-4 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                <div className="bg-black/30 p-4 rounded-lg text-center">
                                    <div className="text-3xl font-bold text-blue-400">{stats.words}</div>
                                    <div className="text-sm text-gray-400">Words</div>
                                </div>
                                <div className="bg-black/30 p-4 rounded-lg text-center">
                                    <div className="text-3xl font-bold text-green-400">{stats.chars}</div>
                                    <div className="text-sm text-gray-400">Characters</div>
                                </div>
                                <div className="bg-black/30 p-4 rounded-lg text-center">
                                    <div className="text-3xl font-bold text-purple-400">{stats.charsNoSpaces}</div>
                                    <div className="text-sm text-gray-400">No Spaces</div>
                                </div>
                                <div className="bg-black/30 p-4 rounded-lg text-center">
                                    <div className="text-3xl font-bold text-yellow-400">{stats.lines}</div>
                                    <div className="text-sm text-gray-400">Lines</div>
                                </div>
                                <div className="bg-black/30 p-4 rounded-lg text-center">
                                    <div className="text-3xl font-bold text-red-400">{stats.sentences}</div>
                                    <div className="text-sm text-gray-400">Sentences</div>
                                </div>
                            </div>
                        </div>
                    </div>
                );

            case 'json':
                return (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">JSON Formatter</h2>
                        <div className="grid md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm mb-2">Input JSON</label>
                                <textarea
                                    value={jsonInput}
                                    onChange={(e) => setJsonInput(e.target.value)}
                                    placeholder='{"key": "value"}'
                                    className="w-full h-96 bg-black/30 border border-white/10 rounded-lg p-4 font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm mb-2">Formatted Output</label>
                                <textarea
                                    value={jsonOutput}
                                    readOnly
                                    placeholder="Formatted JSON will appear here"
                                    className="w-full h-96 bg-black/30 border border-white/10 rounded-lg p-4 font-mono text-sm resize-none"
                                />
                            </div>
                        </div>
                        <button
                            onClick={formatJSON}
                            className="mt-4 w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold"
                        >
                            Format JSON
                        </button>
                    </div>
                );

            case 'base64':
                return (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">Base64 Encoder/Decoder</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm mb-2">Input</label>
                                <textarea
                                    value={base64Input}
                                    onChange={(e) => setBase64Input(e.target.value)}
                                    placeholder="Enter text to encode or Base64 to decode"
                                    className="w-full h-32 bg-black/30 border border-white/10 rounded-lg p-4 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={encodeBase64}
                                    className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold"
                                >
                                    Encode
                                </button>
                                <button
                                    onClick={decodeBase64}
                                    className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold"
                                >
                                    Decode
                                </button>
                            </div>
                            <div>
                                <label className="block text-sm mb-2">Output</label>
                                <textarea
                                    value={base64Output}
                                    readOnly
                                    placeholder="Result will appear here"
                                    className="w-full h-32 bg-black/30 border border-white/10 rounded-lg p-4 resize-none font-mono"
                                />
                            </div>
                        </div>
                    </div>
                );

            case 'unit-converter':
                return (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">Unit Converter</h2>
                        <div className="max-w-md mx-auto space-y-4">
                            <div>
                                <label className="block text-sm mb-2">Value</label>
                                <input
                                    type="number"
                                    value={unitValue}
                                    onChange={(e) => setUnitValue(e.target.value)}
                                    className="w-full bg-black/30 border border-white/10 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm mb-2">From</label>
                                    <select
                                        value={unitFrom}
                                        onChange={(e) => setUnitFrom(e.target.value)}
                                        className="w-full bg-black/30 border border-white/10 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="km">Kilometers</option>
                                        <option value="m">Meters</option>
                                        <option value="cm">Centimeters</option>
                                        <option value="mm">Millimeters</option>
                                        <option value="miles">Miles</option>
                                        <option value="yards">Yards</option>
                                        <option value="feet">Feet</option>
                                        <option value="inches">Inches</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm mb-2">To</label>
                                    <select
                                        value={unitTo}
                                        onChange={(e) => setUnitTo(e.target.value)}
                                        className="w-full bg-black/30 border border-white/10 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="km">Kilometers</option>
                                        <option value="m">Meters</option>
                                        <option value="cm">Centimeters</option>
                                        <option value="mm">Millimeters</option>
                                        <option value="miles">Miles</option>
                                        <option value="yards">Yards</option>
                                        <option value="feet">Feet</option>
                                        <option value="inches">Inches</option>
                                    </select>
                                </div>
                            </div>
                            <div className="bg-black/30 p-6 rounded-lg text-center">
                                <div className="text-4xl font-bold text-blue-400">{convertUnit()}</div>
                                <div className="text-sm text-gray-400 mt-2">{unitTo}</div>
                            </div>
                        </div>
                    </div>
                );

            case 'random':
                return (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">Random Number Generator</h2>
                        <div className="max-w-md mx-auto space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm mb-2">Minimum</label>
                                    <input
                                        type="number"
                                        value={randomMin}
                                        onChange={(e) => setRandomMin(Number(e.target.value))}
                                        className="w-full bg-black/30 border border-white/10 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm mb-2">Maximum</label>
                                    <input
                                        type="number"
                                        value={randomMax}
                                        onChange={(e) => setRandomMax(Number(e.target.value))}
                                        className="w-full bg-black/30 border border-white/10 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                            </div>
                            {randomResult !== null && (
                                <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-8 rounded-lg text-center">
                                    <div className="text-6xl font-bold">{randomResult}</div>
                                </div>
                            )}
                            <button
                                onClick={generateRandom}
                                className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold"
                            >
                                Generate Random Number
                            </button>
                        </div>
                    </div>
                );

            case 'notes':
                return (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">Quick Notes</h2>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder="Type your notes here... (Stored in browser session)"
                            className="w-full h-96 bg-black/30 border border-white/10 rounded-lg p-4 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <div className="mt-4 flex gap-3">
                            <button
                                onClick={() => setNotes('')}
                                className="px-6 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-semibold"
                            >
                                Clear Notes
                            </button>
                            <button
                                onClick={() => {
                                    const blob = new Blob([notes], { type: 'text/plain' });
                                    const url = URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download = `notes-${new Date().toISOString()}.txt`;
                                    a.click();
                                }}
                                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold"
                            >
                                Download Notes
                            </button>
                        </div>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2">Tools</h1>
                    <p className="text-gray-400">Productivity and utility tools for everyday tasks</p>
                </div>

                {!activeTool ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                        {tools.map((tool) => (
                            <button
                                key={tool.id}
                                onClick={() => setActiveTool(tool.id)}
                                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-200 text-left group"
                            >
                                <div className="text-blue-400 mb-3 group-hover:scale-110 transition-transform">
                                    {tool.icon}
                                </div>
                                <h3 className="text-lg font-semibold mb-1">{tool.name}</h3>
                                <p className="text-sm text-gray-400">{tool.description}</p>
                            </button>
                        ))}
                    </div>
                ) : (
                    <div>
                        <button
                            onClick={() => setActiveTool(null)}
                            className="mb-4 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg transition-colors flex items-center gap-2"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                            </svg>
                            Back to Tools
                        </button>
                        {renderTool()}
                    </div>
                )}
            </div>
        </div>
    );
}
