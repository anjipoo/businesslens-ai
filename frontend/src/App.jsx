import React, { useState } from 'react';

function SimpleMarkdownRenderer({ content }) {
  if (!content) return null;
  const lines = content.split('\n');
  return (
    <div className="space-y-4 text-slate-300 font-sans text-sm leading-relaxed selection:bg-indigo-500/30">
      {lines.map((line, i) => {
        if (line.trim() === '---') return <hr key={i} className="border-slate-800 my-6" />;
        if (line.startsWith('# ')) return <h1 key={i} className="text-2xl font-black text-white border-b border-slate-900 pb-2 mt-6 tracking-tight">{line.replace('# ', '')}</h1>;
        if (line.startsWith('## ')) return <h2 key={i} className="text-xl font-bold text-slate-100 mt-5 tracking-tight">{line.replace('## ', '')}</h2>;
        if (line.startsWith('### ')) return <h3 key={i} className="text-md font-semibold text-indigo-400 mt-4 tracking-wide">{line.replace('### ', '')}</h3>;
        
        if (line.trim().startsWith('* ') || line.trim().startsWith('- ')) {
          const rawText = line.replace(/^[\s*-]+/, '');
          return (
            <ul key={i} className="list-disc list-inside pl-4 text-slate-300 space-y-1">
              <li>{parseBoldText(rawText)}</li>
            </ul>
          );
        }
        if (line.trim() === '') return <div key={i} className="h-2" />;
        return <p key={i} className="text-slate-300 font-normal leading-relaxed">{parseBoldText(line)}</p>;
      })}
    </div>
  );
}

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
  const [activeTab, setActiveTab] = useState('timeline'); // Default to live execution view

  const handleStartAnalysis = async (e) => {
    e.preventDefault();
    if (!name || !description) return;
    
    setLoading(true);
    setAnalysis(null);
    setActiveTab('timeline');

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
      console.error("API Link Error:", err);
      setLoading(false);
    }
  };

  // Live Agent State Matrix Evaluator
  const getAgentState = (agentName) => {
    if (!analysis) return { status: 'Pending', data: null };
    const log = analysis.logs?.find(l => l.agent_name === agentName);
    
    if (!log) {
      if (analysis.status === 'failed') return { status: 'Failed', data: null };
      return { status: 'Pending', data: null };
    }
    
    if (log.output_data === 'PENDING_EXECUTION_STREAM') {
      return { status: 'Running', data: log };
    }
    
    if (log.output_data?.startsWith('CRITICAL_NODE_FAILURE')) {
      return { status: 'Failed', data: log };
    }
    
    return { status: 'Completed', data: log };
  };

  const agentNodes = ['Planner', 'Research', 'Analysis', 'Strategy'];

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 antialiased font-sans">
      <header className="border-b border-slate-900 bg-slate-900/20 backdrop-blur sticky top-0 z-50 px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center font-black text-white shadow-lg shadow-indigo-500/20">BL</div>
          <span className="text-base font-bold bg-gradient-to-r from-slate-100 via-slate-200 to-indigo-200 bg-clip-text text-transparent">BusinessLens AI Console</span>
        </div>
        <span className="text-[10px] tracking-widest font-mono text-indigo-400 px-2.5 py-1 bg-indigo-950/40 rounded-md border border-indigo-900/40">Live Timeline Active</span>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Input Configuration Panel */}
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
            <button type="submit" disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-950/40 text-indigo-100 disabled:text-indigo-400/60 font-semibold rounded-xl py-3 text-xs border border-indigo-500/20 flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/10">
              {loading ? 'Executing Operational Model...' : 'Run Analysis Timeline'}
            </button>
          </form>
        </section>

        {/* Core Monitoring Interface Terminal */}
        <section className="lg:col-span-8 flex flex-col min-h-[580px]">
          {analysis ? (
            <div className="bg-[#111625] border border-slate-900 rounded-2xl flex-1 flex flex-col overflow-hidden shadow-2xl">
              
              {/* Tab Navigation Menu */}
              <div className="border-b border-slate-950 px-6 py-3 flex items-center justify-between bg-[#141b2d]">
                <div className="flex space-x-2">
                  <button onClick={() => setActiveTab('timeline')} className={`px-4 py-1.5 text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${activeTab === 'timeline' ? 'bg-slate-800 text-indigo-400 border border-slate-700/50' : 'text-slate-400 hover:text-slate-200'}`}>Execution Timeline</button>
                  <button onClick={() => setActiveTab('report')} className={`px-4 py-1.5 text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${activeTab === 'report' ? 'bg-slate-800 text-indigo-400 border border-slate-700/50' : 'text-slate-400 hover:text-slate-200'}`}>Final Executive Blueprint</button>
                </div>
                <div className="flex items-center space-x-2 bg-[#080c14] border border-slate-800/80 px-3 py-1 rounded-xl text-[10px] font-mono tracking-widest text-slate-400 uppercase">
                  Global State: {analysis.status}
                </div>
              </div>

              {/* Central Viewport Box */}
              <div className="p-6 flex-1 overflow-y-auto max-h-[640px] bg-[#111625]/40">
                
                {/* Viewport Render Block A: Live Execution Timeline */}
                {activeTab === 'timeline' && (
                  <div className="relative border-l border-slate-800 ml-4 pl-8 space-y-8 py-2">
                    {agentNodes.map((nodeName) => {
                      const nodeState = getAgentState(nodeName);
                      
                      // Compute dynamic status badges
                      let badgeColor = "bg-slate-900 border-slate-800 text-slate-500";
                      let indicatorDot = "bg-slate-800";
                      
                      if (nodeState.status === 'Running') {
                        badgeColor = "bg-amber-950/40 border-amber-800/60 text-amber-400 animate-pulse";
                        indicatorDot = "bg-amber-400 shadow-sm shadow-amber-400/50 animate-ping";
                      } else if (nodeState.status === 'Completed') {
                        badgeColor = "bg-emerald-950/40 border-emerald-900/60 text-emerald-400";
                        indicatorDot = "bg-emerald-400 shadow-sm shadow-emerald-400/50";
                      } else if (nodeState.status === 'Failed') {
                        badgeColor = "bg-rose-950/40 border-rose-900/60 text-rose-400";
                        indicatorDot = "bg-rose-500";
                      }

                      return (
                        <div key={nodeName} className="relative group">
                          {/* Left Absolute Timeline Anchor Point */}
                          <span className={`absolute -left-[37px] top-1.5 h-3 w-3 rounded-full border border-[#111625] transition-all ${indicatorDot}`} />
                          
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="text-sm font-bold text-slate-200 tracking-tight">{nodeName} Agent Node</h3>
                            <span className={`text-[9px] font-mono font-bold uppercase tracking-widest px-2.5 py-0.5 rounded-md border ${badgeColor}`}>
                              {nodeState.status}
                            </span>
                          </div>

                          {/* Conditional Log Previews */}
                          <div className="bg-[#080c14] border border-slate-900/80 rounded-xl p-4 shadow-inner">
                            {nodeState.status === 'Pending' && (
                              <p className="text-xs text-slate-600 italic font-mono">Dormant. Standing by for pipeline instructions...</p>
                            )}
                            {nodeState.status === 'Running' && (
                              <p className="text-xs text-amber-500/80 italic font-mono animate-pulse">Running. Fetching live Gemini 2.5 Flash token generations...</p>
                            )}
                            {nodeState.status === 'Completed' && (
                              <pre className="text-xs font-mono text-emerald-400 overflow-x-auto whitespace-pre-wrap leading-relaxed">
                                {nodeState.data?.output_data}
                              </pre>
                            )}
                            {nodeState.status === 'Failed' && (
                              <pre className="text-xs font-mono text-rose-400 overflow-x-auto whitespace-pre-wrap leading-relaxed">
                                {nodeState.data?.output_data}
                              </pre>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Viewport Render Block B: Markdown Summary Report */}
                {activeTab === 'report' && (
                  <div className="bg-[#080c14] border border-slate-900/60 p-6 rounded-xl shadow-inner min-h-[420px]">
                    {analysis.final_report ? (
                      <SimpleMarkdownRenderer content={analysis.final_report} />
                    ) : (
                      <div className="flex flex-col items-center justify-center py-32 text-center">
                        <span className="w-5 h-5 border-2 border-slate-700 border-t-indigo-500 rounded-full animate-spin mb-4"></span>
                        <p className="text-xs text-slate-500 font-mono">Awaiting down-line node execution tracking completion before final synthesis...</p>
                      </div>
                    )}
                  </div>
                )}

              </div>

            </div>
          ) : (
            <div className="border border-dashed border-slate-800/80 bg-slate-900/5 rounded-2xl flex-1 flex flex-col items-center justify-center p-8 text-center min-h-[580px]">
              <div className="h-11 w-11 rounded-xl bg-[#111625] border border-slate-800/80 flex items-center justify-center text-slate-400 text-base mb-4 shadow-xl">📊</div>
              <h3 className="text-xs font-bold text-slate-300 tracking-tight">Timeline Workspace Inactive</h3>
              <p className="text-xs text-slate-500 max-w-xs mt-1 leading-relaxed">Submit your corporate parameters on the control panel to initialize the live structural agent timeline tracking stream.</p>
            </div>
          )}
        </section>

      </main>
    </div>
  );
}