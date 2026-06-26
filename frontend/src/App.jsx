import React, { useState } from 'react';

// A lightweight, runtime-safe Markdown helper that converts markdown formatting to stylized HTML nodes
function SimpleMarkdownRenderer({ content }) {
  if (!content) return null;
  
  const lines = content.split('\n');
  return (
    <div className="space-y-4 text-slate-300 font-sans selection:bg-indigo-500/30 text-sm leading-relaxed">
      {lines.map((line, i) => {
        // Horizontal Rule
        if (line.trim() === '---') return <hr key={i} className="border-slate-800 my-6" />;
        
        // Headers
        if (line.startsWith('# ')) return <h1 key={i} className="text-2xl font-black text-white border-b border-slate-900 pb-2 mt-6 tracking-tight">{line.replace('# ', '')}</h1>;
        if (line.startsWith('## ')) return <h2 key={i} className="text-xl font-bold text-slate-100 mt-5 tracking-tight flex items-center space-x-2">{line.replace('## ', '')}</h2>;
        if (line.startsWith('### ')) return <h3 key={i} className="text-md font-semibold text-indigo-400 mt-4 tracking-wide">{line.replace('### ', '')}</h3>;
        
        // Bullet Points
        if (line.trim().startsWith('* ') || line.trim().startsWith('- ')) {
          const rawText = line.replace(/^[\s*-]+/, '');
          return (
            <ul key={i} className="list-disc list-inside pl-4 text-slate-300 space-y-1 font-sans">
              <li>{parseBoldText(rawText)}</li>
            </ul>
          );
        }
        
        // Standard Paragraph Line Block
        if (line.trim() === '') return <div key={i} className="h-2" />;
        return <p key={i} className="text-slate-300 font-normal leading-relaxed">{parseBoldText(line)}</p>;
      })}
    </div>
  );
}

// Inline regex helper mapping double asterisks directly to raw bold tags
function parseBoldText(text) {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index} className="font-bold text-white bg-slate-900/40 px-1 py-0.5 rounded">{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

export default function App() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('report');

  const handleStartAnalysis = async (e) => {
    e.preventDefault();
    if (!name || !description) return;
    
    setLoading(true);
    setAnalysis(null);

    try {
      const projectRes = await fetch('http://localhost:8000/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description }),
      });
      const project = await projectRes.json();

      const runRes = await fetch(`http://localhost:8000/projects/${project.id}/analyze`, {
        method: 'POST',
      });
      let currentAnalysis = await runRes.json();
      setAnalysis(currentAnalysis);

      const poller = setInterval(async () => {
        const checkRes = await fetch(`http://localhost:8000/analyses/${currentAnalysis.id}`);
        const updatedData = await checkRes.json();
        setAnalysis(updatedData);

        if (updatedData.status === 'completed' || updatedData.status === 'failed') {
          clearInterval(poller);
          setLoading(false);
        }
      }, 1500);

    } catch (err) {
      console.error("API Link Failure:", err);
      setLoading(false);
    }
  };

  const getAgentLog = (name) => analysis?.logs?.find(log => log.agent_name === name);

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 antialiased font-sans">
      {/* Global SaaS Header Banner */}
      <header className="border-b border-slate-900 bg-slate-900/20 backdrop-blur sticky top-0 z-50 px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center font-black tracking-tight text-white shadow-lg shadow-indigo-500/20">BL</div>
          <span className="text-base font-bold tracking-tight bg-gradient-to-r from-slate-100 via-slate-200 to-indigo-200 bg-clip-text text-transparent">BusinessLens AI Workbench</span>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-[10px] tracking-widest uppercase font-mono text-indigo-400 px-2.5 py-1 bg-indigo-950/40 rounded-md border border-indigo-900/40">Kaggle Capstone System</span>
        </div>
      </header>

      {/* Main Production Workspace */}
      <main className="max-w-7xl mx-auto px-8 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Side Form Control */}
        <section className="lg:col-span-4 bg-[#111625] border border-slate-900 rounded-2xl p-6 shadow-2xl h-fit">
          <div className="mb-6">
            <h2 className="text-sm font-bold text-slate-200 tracking-tight">Audit Initialization</h2>
            <p className="text-xs text-slate-500 mt-1">Provide operational profiles for your downstream multi-agent evaluation pipeline.</p>
          </div>
          
          <form onSubmit={handleStartAnalysis} className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Enterprise Identifier</label>
              <input type="text" value={name} onChange={e => setName(e.target.value)} disabled={loading} required className="w-full bg-[#080c14] border border-slate-800/80 rounded-xl px-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 disabled:opacity-40 transition-all font-medium" placeholder="e.g., Solis Grid Logistics" />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Operational Context Profile</label>
              <textarea rows={10} value={description} onChange={e => setDescription(e.target.value)} disabled={loading} required className="w-full bg-[#080c14] border border-slate-800/80 rounded-xl px-4 py-3 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 disabled:opacity-40 transition-all resize-none font-mono leading-relaxed" placeholder="Outline clear corporate objectives, known competitive metrics, cash burn indicators, or current infrastructure risks..."></textarea>
            </div>
            <button type="submit" disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-950/40 text-indigo-100 disabled:text-indigo-400/60 font-semibold rounded-xl py-3 text-xs transition-all border border-indigo-500/20 flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/10">
              {loading ? (
                <>
                  <span className="w-3 h-3 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></span>
                  <span>Traversing Matrix Loops...</span>
                </>
              ) : 'Execute Consulting Graph'}
            </button>
          </form>
        </section>

        {/* Right Side Strategy Command Dashboard */}
        <section className="lg:col-span-8 flex flex-col min-h-[580px]">
          {analysis ? (
            <div className="bg-[#111625] border border-slate-900 rounded-2xl flex-1 flex flex-col overflow-hidden shadow-2xl">
              
              {/* Context Routing Tab Bars */}
              <div className="border-b border-slate-950 px-6 py-3 flex items-center justify-between bg-[#141b2d]">
                <div className="flex space-x-2">
                  <button onClick={() => setActiveTab('report')} className={`px-4 py-1.5 text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${activeTab === 'report' ? 'bg-slate-800 text-indigo-400 border border-slate-700/50' : 'text-slate-400 hover:text-slate-200'}`}>Strategic Executive Blueprint</button>
                  <button onClick={() => setActiveTab('logs')} className={`px-4 py-1.5 text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${activeTab === 'logs' ? 'bg-slate-800 text-indigo-400 border border-slate-700/50' : 'text-slate-400 hover:text-slate-200'}`}>Agent Execution Logs</button>
                </div>
                <div className="flex items-center space-x-2.5 bg-[#080c14] border border-slate-800/80 px-3 py-1.5 rounded-xl">
                  <span className={`h-2 w-2 rounded-full ${analysis.status === 'completed' ? 'bg-emerald-400 shadow-md shadow-emerald-400/50' : analysis.status === 'failed' ? 'bg-rose-500' : 'bg-amber-400 animate-pulse'}`}></span>
                  <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-slate-400">{analysis.status}</span>
                </div>
              </div>

              {/* Dynamic Viewport Terminal */}
              <div className="p-6 flex-1 overflow-y-auto max-h-[640px] bg-[#111625]/40">
                {activeTab === 'report' ? (
                  <div className="bg-[#080c14] border border-slate-900/60 p-6 rounded-xl shadow-inner min-h-[400px]">
                    {analysis.final_report ? (
                      <SimpleMarkdownRenderer content={analysis.final_report} />
                    ) : (
                      <div className="flex flex-col items-center justify-center py-32 text-center">
                        <span className="w-5 h-5 border-2 border-slate-700 border-t-indigo-500 rounded-full animate-spin mb-4"></span>
                        <p className="text-xs text-slate-500 font-mono">Principal Strategist agent parsing raw JSON parameters...</p>
                      </div>
                    )}
                  </div>
                ) : (
                  /* Granular Agent Stream Node Interface */
                  <div className="space-y-4">
                    {['Planner', 'Research', 'Analysis', 'Strategy'].map((node) => {
                      const log = getAgentLog(node);
                      return (
                        <div key={node} className={`border rounded-xl p-5 transition-all ${log ? 'bg-[#080c14] border-slate-800' : 'bg-[#080c14]/20 border-slate-900/40 opacity-40'}`}>
                          <div className="flex items-center justify-between border-b border-slate-900/80 pb-3 mb-3">
                            <div className="flex items-center space-x-2.5">
                              <span className={`h-1.5 w-1.5 rounded-full ${log ? 'bg-indigo-400 shadow-sm' : 'bg-slate-800'}`}></span>
                              <span className="text-xs font-bold text-slate-300">{node} Core Sub-System</span>
                            </div>
                            {log && <span className="text-[9px] font-mono text-slate-500 uppercase tracking-widest">Logged</span>}
                          </div>
                          <div>
                            {log ? (
                              <pre className="text-[11px] font-mono text-emerald-400 bg-slate-950/40 p-3 rounded-lg border border-slate-900/40 overflow-x-auto whitespace-pre-wrap leading-relaxed">{log.output_data}</pre>
                            ) : (
                              <p className="text-xs font-mono text-slate-600 italic px-1">
                                {analysis.status === 'processing' ? 'Awaiting pipeline dispatch parameters...' : 'Module dormant.'}
                              </p>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

            </div>
          ) : (
            <div className="border border-dashed border-slate-800/80 bg-slate-900/5 rounded-2xl flex-1 flex flex-col items-center justify-center p-8 text-center min-h-[580px]">
              <div className="h-11 w-11 rounded-xl bg-[#111625] border border-slate-800/80 flex items-center justify-center text-slate-400 text-base mb-4 shadow-xl">🛠️</div>
              <h3 className="text-xs font-bold text-slate-300 tracking-tight">System Node Link Passive</h3>
              <p className="text-xs text-slate-500 max-w-xs mt-1 leading-relaxed">Submit your data configuration vectors on the control panel to run the deep multi-agent orchestration grid.</p>
            </div>
          )}
        </section>

      </main>
    </div>
  );
}