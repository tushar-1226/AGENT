'use client';

import { useState, useEffect } from 'react';
import { showToast } from '@/lib/api';

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

    // New: QR Code Generator
    const [qrText, setQrText] = useState('https://example.com');
    const [qrSize, setQrSize] = useState(200);

    // New: Unit Price Calculator
    const [priceItems, setPriceItems] = useState<Array<{ id: number; label: string; price: string; quantity: string; unit: string }>>([
        { id: 1, label: 'Item A', price: '10.00', quantity: '1', unit: 'kg' }
    ]);

    // New: Timezone Converter
    const [tzDateTime, setTzDateTime] = useState('');
    const [tzSource, setTzSource] = useState('UTC');
    const [tzTarget, setTzTarget] = useState('Asia/Kolkata');
    const commonTimezones = [
        'UTC', 'Europe/London', 'Europe/Berlin', 'America/New_York', 'America/Los_Angeles', 'Asia/Kolkata', 'Asia/Tokyo', 'Australia/Sydney'
    ];

    // Random Number
    const [randomMin, setRandomMin] = useState(1);
    const [randomMax, setRandomMax] = useState(100);
    const [randomResult, setRandomResult] = useState<number | null>(null);

    // Notes
    const [notes, setNotes] = useState('');

    // Undo buffer for actions triggered by toasts (e.g., unit-price undo)
    const [undoBuffer, setUndoBuffer] = useState<Record<number, { id: number; label: string; price: string; quantity: string; unit: string }>>({});
    // Track recently-restored item ids to trigger a short pop animation
    const [restoredIds, setRestoredIds] = useState<Record<number, boolean>>({});

    useEffect(() => {
        const handler = (e: any) => {
            const payload = e.detail?.payload;
            if (!payload) return;

            if (payload.undoId) {
                const id = payload.undoId;
                const item = undoBuffer[id];
                if (item) {
                    setPriceItems((prev) => [...prev, item]);
                    setUndoBuffer((prev) => {
                        const copy = { ...prev };
                        delete copy[id];
                        return copy;
                    });
                    // mark restored id to trigger animation
                    setRestoredIds((prev) => ({ ...prev, [id]: true }));
                    // clear the restored marker after animation
                    setTimeout(() => setRestoredIds((prev) => { const c = { ...prev }; delete c[id]; return c; }), 900);
                    showToast(`${item.label} restored`, 'success');
                }
            }
        };

        window.addEventListener('toastAction', handler as EventListener);
        return () => window.removeEventListener('toastAction', handler as EventListener);
    }, [undoBuffer]);

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
            id: 'qrcode',
            name: 'QR Code Generator',
            description: 'Create QR codes from text or URLs',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h6v6H3V3zm12 0h6v6h-6V3zM3 15h6v6H3v-6zm12 6h6v-6h-6v6z" />
                </svg>
            )
        },
        {
            id: 'unit-price',
            name: 'Unit Price Calculator',
            description: 'Compare price per unit across products',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 6h18M3 14h18M3 18h18" />
                </svg>
            )
        },
        {
            id: 'timezone',
            name: 'Timezone Converter',
            description: 'Convert times between timezones',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
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

                case 'qrcode':
                    const qrUrl = `https://chart.googleapis.com/chart?cht=qr&chs=${qrSize}x${qrSize}&chl=${encodeURIComponent(qrText)}`;
                    return (
                        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                            <h2 className="text-2xl font-semibold mb-4">QR Code Generator</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm text-gray-400">Text or URL</label>
                                    <input value={qrText} onChange={(e) => setQrText(e.target.value)} className="w-full mt-2 p-3 rounded-lg bg-black/30 border border-white/10 focus:outline-none" />
                                    <label className="text-sm text-gray-400 mt-3">Size (px)</label>
                                    <input type="number" value={qrSize} onChange={(e) => setQrSize(Number(e.target.value || 200))} className="w-32 mt-2 p-2 rounded-lg bg-black/30 border border-white/10" />
                                    <div className="mt-4 flex gap-2">
                                        <a href={qrUrl} target="_blank" rel="noreferrer" className="px-4 py-2 bg-blue-600 rounded-lg">Open</a>
                                        <button onClick={() => { navigator.clipboard.writeText(qrUrl); window.dispatchEvent(new CustomEvent('showToast', { detail: { message: 'QR image URL copied', type: 'success' } })); }} className="px-4 py-2 bg-white/10 rounded-lg">Copy Image URL</button>
                                        <button onClick={async () => {
                                            try {
                                                const res = await fetch(qrUrl);
                                                const blob = await res.blob();
                                                const url = URL.createObjectURL(blob);
                                                const a = document.createElement('a');
                                                a.href = url;
                                                a.download = `qrcode-${Date.now()}.png`;
                                                document.body.appendChild(a);
                                                a.click();
                                                a.remove();
                                                URL.revokeObjectURL(url);
                                                window.dispatchEvent(new CustomEvent('showToast', { detail: { message: 'QR downloaded', type: 'success' } }));
                                            } catch (e) {
                                                window.dispatchEvent(new CustomEvent('showToast', { detail: { message: 'Failed to download QR', type: 'error' } }));
                                            }
                                        }} className="px-4 py-2 bg-green-600 rounded-lg">Download PNG</button>
                                    </div>
                                </div>
                                <div className="flex items-center justify-center">
                                    <img src={qrUrl} alt="QR Code" className="bg-white p-2 rounded" />
                                </div>
                            </div>
                        </div>
                    );

                case 'unit-price':
                    const addPriceItem = () => setPriceItems(prev => [...prev, { id: Date.now(), label: `Item ${prev.length + 1}`, price: '0.00', quantity: '1', unit: 'unit' }]);
                    const updatePriceItem = (id: number, field: string, value: string) => setPriceItems(prev => prev.map(it => it.id === id ? { ...it, [field]: value } : it));
                    const removePriceItem = (id: number) => {
                        const item = priceItems.find(it => it.id === id);
                        if (!item) return;
                        setPriceItems(prev => prev.filter(it => it.id !== id));
                        setUndoBuffer(prev => ({ ...prev, [id]: item }));
                        showToast(`${item.label} removed`, { type: 'success', title: 'Unit Price', duration: 6000, actionLabel: 'Undo', actionPayload: { undoId: id } });
                    };
                    const computed = priceItems.map(it => {
                        const price = parseFloat(it.price) || 0;
                        const qty = parseFloat(it.quantity) || 1;
                        const ppu = qty !== 0 ? price / qty : Infinity;
                        return { ...it, price, qty, ppu };
                    }).sort((a, b) => a.ppu - b.ppu);

                    return (
                        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                            <h2 className="text-2xl font-semibold mb-4">Unit Price Calculator</h2>
                            <div className="space-y-4">
                                {priceItems.map(item => (
                                    <div key={item.id} className={`flex gap-2 items-center ${restoredIds[item.id] ? 'restore-pop ring-2 ring-green-400/40 scale-105' : ''}`}>
                                        <input value={item.label} onChange={(e) => updatePriceItem(item.id, 'label', e.target.value)} className="w-40 p-2 rounded bg-black/30 border border-white/10" />
                                        <input value={item.price} onChange={(e) => updatePriceItem(item.id, 'price', e.target.value)} className="w-24 p-2 rounded bg-black/30 border border-white/10" />
                                        <input value={item.quantity} onChange={(e) => updatePriceItem(item.id, 'quantity', e.target.value)} className="w-24 p-2 rounded bg-black/30 border border-white/10" />
                                        <input value={item.unit} onChange={(e) => updatePriceItem(item.id, 'unit', e.target.value)} className="w-24 p-2 rounded bg-black/30 border border-white/10" />
                                        <button onClick={() => removePriceItem(item.id)} className="px-3 py-2 bg-red-600 rounded">Remove</button>
                                    </div>
                                ))}

                                <div className="flex gap-2">
                                    <button onClick={addPriceItem} className="px-4 py-2 bg-green-600 rounded">Add Item</button>
                                    <button onClick={() => { navigator.clipboard.writeText(JSON.stringify(priceItems)); window.dispatchEvent(new CustomEvent('showToast', { detail: { message: 'Items JSON copied', type: 'success' } })); }} className="px-4 py-2 bg-white/10 rounded">Copy JSON</button>
                                    <button onClick={() => {
                                        // build CSV
                                        const header = 'label,price,quantity,unit';
                                        const rows = priceItems.map(it => `${JSON.stringify(it.label)},${it.price},${it.quantity},${JSON.stringify(it.unit)}`);
                                        const csv = [header, ...rows].join('\n');
                                        navigator.clipboard.writeText(csv);
                                        window.dispatchEvent(new CustomEvent('showToast', { detail: { message: 'CSV copied', type: 'success' } }));
                                    }} className="px-4 py-2 bg-white/10 rounded">Copy CSV</button>
                                    <button onClick={() => {
                                        const header = 'label,price,quantity,unit';
                                        const rows = priceItems.map(it => `${JSON.stringify(it.label)},${it.price},${it.quantity},${JSON.stringify(it.unit)}`);
                                        const csv = [header, ...rows].join('\n');
                                        const blob = new Blob([csv], { type: 'text/csv' });
                                        const url = URL.createObjectURL(blob);
                                        const a = document.createElement('a');
                                        a.href = url;
                                        a.download = `unit-price-${Date.now()}.csv`;
                                        document.body.appendChild(a);
                                        a.click();
                                        a.remove();
                                        URL.revokeObjectURL(url);
                                    }} className="px-4 py-2 bg-blue-600 rounded">Download CSV</button>
                                </div>

                                <div>
                                    <h3 className="text-lg font-medium mb-2">Comparison (best value first)</h3>
                                    <div className="space-y-2">
                                        {computed.map(it => (
                                            <div key={it.id} className="flex items-center justify-between p-3 bg-black/20 rounded">
                                                <div>
                                                    <div className="font-semibold">{it.label}</div>
                                                    <div className="text-sm text-gray-400">{it.price.toFixed(2)} / {it.qty} {it.unit}</div>
                                                </div>
                                                <div className="text-right">
                                                    <div className="font-medium">{(it.ppu === Infinity ? '—' : it.ppu.toFixed(4))}</div>
                                                    <div className="text-sm text-gray-400">price per unit</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    );

                case 'timezone':
                    const parseAndConvert = () => {
                        try {
                            const input = tzDateTime || new Date().toISOString();
                            const date = new Date(input);
                            const sourceOpts: Intl.DateTimeFormatOptions = { timeZone: tzSource, year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' };
                            const targetOpts = { ...sourceOpts, timeZone: tzTarget };
                            const src = new Intl.DateTimeFormat([], sourceOpts).format(date);
                            const tgt = new Intl.DateTimeFormat([], targetOpts).format(date);
                            return { src, tgt };
                        } catch (e) {
                            return { src: 'Invalid', tgt: 'Invalid' };
                        }
                    };
                    const conv = parseAndConvert();
                    return (
                        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                            <h2 className="text-2xl font-semibold mb-4">Timezone Converter</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm text-gray-400">Date & Time (ISO or local)</label>
                                    <input value={tzDateTime} onChange={(e) => setTzDateTime(e.target.value)} placeholder={new Date().toISOString()} className="w-full mt-2 p-3 rounded-lg bg-black/30 border border-white/10" />
                                    <label className="text-sm text-gray-400 mt-3">Source Timezone</label>
                                    <select value={tzSource} onChange={(e) => setTzSource(e.target.value)} className="w-full mt-2 p-2 rounded bg-black/30 border border-white/10">
                                        {commonTimezones.map(tz => <option key={tz} value={tz}>{tz}</option>)}
                                    </select>
                                </div>
                                <div>
                                    <label className="text-sm text-gray-400">Target Timezone</label>
                                    <select value={tzTarget} onChange={(e) => setTzTarget(e.target.value)} className="w-full mt-2 p-2 rounded bg-black/30 border border-white/10">
                                        {commonTimezones.map(tz => <option key={tz} value={tz}>{tz}</option>)}
                                    </select>
                                    <div className="mt-4 p-4 bg-black/20 rounded">
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <div className="text-sm text-gray-400">Source:</div>
                                                <div className="font-medium">{conv.src}</div>
                                                <div className="text-sm text-gray-400 mt-3">Target:</div>
                                                <div className="font-medium">{conv.tgt}</div>
                                            </div>
                                            <div className="flex flex-col gap-2">
                                                <button onClick={() => { navigator.clipboard.writeText(`Source: ${conv.src}\nTarget: ${conv.tgt}`); window.dispatchEvent(new CustomEvent('showToast', { detail: { message: 'Converted times copied', type: 'success' } })); }} className="px-4 py-2 bg-white/10 rounded">Copy</button>
                                                <button onClick={() => {
                                                    const txt = `Source: ${conv.src}\nTarget: ${conv.tgt}`;
                                                    const blob = new Blob([txt], { type: 'text/plain' });
                                                    const url = URL.createObjectURL(blob);
                                                    const a = document.createElement('a');
                                                    a.href = url;
                                                    a.download = `timezone-${Date.now()}.txt`;
                                                    document.body.appendChild(a);
                                                    a.click();
                                                    a.remove();
                                                    URL.revokeObjectURL(url);
                                                }} className="px-4 py-2 bg-blue-600 rounded">Download</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
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
