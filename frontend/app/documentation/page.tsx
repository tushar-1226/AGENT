export const metadata = {
  title: 'Documentation',
  description: 'Minimalist project documentation',
};

export default function DocumentationPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-semibold mb-4">Project Documentation</h1>

        <section className="mb-6">
          <h2 className="text-xl font-medium mb-2">Overview</h2>
          <p className="text-gray-300">This repository implements a desktop-style AI assistant with a Next.js frontend and a Python backend. It includes utility tools, productivity features, and integrations for local and cloud LLMs.</p>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-medium mb-2">Quick Start</h2>
          <ol className="list-decimal list-inside text-gray-300 space-y-1">
            <li>Install Python dependencies and create a virtual environment.</li>
            <li>Start the backend (see backend/README.md for backend-specific steps).</li>
            <li>Start the frontend:</li>
          </ol>
          <pre className="bg-black/30 p-3 rounded mt-3 text-sm">
            <code>cd frontend{`\n`}npm install{`\n`}npm run dev</code>
          </pre>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-medium mb-2">Repository Structure</h2>
          <ul className="list-disc list-inside text-gray-300 space-y-1">
            <li><strong>frontend/</strong> — Next.js app and UI components.</li>
            <li><strong>backend/</strong> — Python backend and API endpoints.</li>
            <li><strong>modules/</strong> — Assistant capabilities and feature modules.</li>
            <li><strong>public/</strong> — Static assets served by Next.js.</li>
          </ul>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-medium mb-2">Frontend Notes</h2>
          <ul className="list-disc list-inside text-gray-300 space-y-1">
            <li>Pages use the app router. The main quick tools page is at <strong>/quick-actions</strong>.</li>
            <li>Global styles are in <strong>app/globals.css</strong>. Tailwind is used for utilities.</li>
            <li>To add a new tool, add an entry to <strong>app/quick-actions/page.tsx</strong> or extract a component under <strong>components/</strong>.</li>
          </ul>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-medium mb-2">Backend Notes</h2>
          <ul className="list-disc list-inside text-gray-300 space-y-1">
            <li>The backend exposes endpoints under <strong>/api/</strong>. See <strong>backend/</strong> for tests and requirements.</li>
            <li>Local LLM integration and model management live in <strong>modules/local_llm.py</strong> and related files.</li>
          </ul>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-medium mb-2">Development Guidelines</h2>
          <ul className="list-disc list-inside text-gray-300 space-y-1">
            <li>Keep UI components small and extract reusable pieces to <strong>components/</strong>.</li>
            <li>Prefer single-responsibility for modules in <strong>modules/</strong>.</li>
            <li>Write tests in the <strong>backend/</strong> folder for API behavior and in <strong>frontend/</strong> for critical UI flows.</li>
          </ul>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-medium mb-2">How to Add a Tool (Minimal)</h2>
          <ol className="list-decimal list-inside text-gray-300 space-y-2">
            <li>Create a component under <strong>components/</strong> or add logic in <strong>app/quick-actions/page.tsx</strong>.</li>
            <li>Add a card entry in the tools array so it appears in the grid.</li>
            <li>Implement client-side functionality and use <strong>frontend/lib/api.ts</strong> helpers for toasts or exports.</li>
          </ol>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-medium mb-2">Testing & Running</h2>
          <p className="text-gray-300">Run frontend dev server and backend concurrently. Use the included test scripts where available:</p>
          <pre className="bg-black/30 p-3 rounded mt-3 text-sm">
            <code>./start.sh{`\n`}# or use tests:{`\n`}pytest backend/</code>
          </pre>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-medium mb-2">Contributing</h2>
          <p className="text-gray-300">Open a PR with a short description. Keep changes focused and add tests for critical behavior.</p>
        </section>

        <section className="mb-12">
          <h2 className="text-xl font-medium mb-2">Support</h2>
          <p className="text-gray-300">If you run into issues, check backend logs, ensure environment variables are set, and confirm services are running.</p>
        </section>

      </div>
    </div>
  );
}

