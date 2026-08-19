import React, { useEffect, useRef, useState } from 'react';
import {
  Activity,
  Brain,
  CheckCircle2,
  Cpu,
  Flame,
  Pause,
  Play,
  RotateCcw,
  Sparkles,
  Zap,
} from 'lucide-react';
import {
  BrainVisionData,
  DemoTrajectory,
  ModelInfoData,
  TrainingEpochEvent,
  TrainingStepEvent,
} from '../types/puzzle';

export const TrainingStudio: React.FC = () => {
  const [mode, setMode] = useState<'3x3' | '43slot'>('3x3');
  const [epochs, setEpochs] = useState<number>(20);
  const [batchSize, setBatchSize] = useState<number>(256);
  const [learningRate] = useState<number>(0.001);
  const [maxDepth, setMaxDepth] = useState<number>(15);

  const [isTraining, setIsTraining] = useState<boolean>(false);
  const [currentEpoch, setCurrentEpoch] = useState<number>(0);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [totalSteps, setTotalSteps] = useState<number>(25);
  const [currentDepth, setCurrentDepth] = useState<number>(1);
  const [currentLoss, setCurrentLoss] = useState<number>(0);
  const [bestLoss, setBestLoss] = useState<number>(0);
  const [testSolveRate, setTestSolveRate] = useState<number>(0);
  const [deviceInfo, setDeviceInfo] = useState<string>('CUDA (RTX 3050)');

  // Telemetry History for SVG charts
  const [lossHistory, setLossHistory] = useState<number[]>([]);
  const [brainVision, setBrainVision] = useState<BrainVisionData | null>(null);

  // Live Demo Board Playback
  const [demoBoard, setDemoBoard] = useState<number[]>([]);
  const [demoActionName, setDemoActionName] = useState<string>('');
  const [demoStatus, setDemoStatus] = useState<string>('Waiting for first epoch...');

  const [trainedModels, setTrainedModels] = useState<ModelInfoData[]>([]);
  const [deploySuccess, setDeploySuccess] = useState<string>('');

  const wsRef = useRef<WebSocket | null>(null);
  const demoIntervalRef = useRef<any>(null);

  // Load existing models
  const fetchModels = async () => {
    try {
      const res = await fetch('/api/train/models');
      if (res.ok) {
        const data = await res.json();
        setTrainedModels(data);
      }
    } catch {
      // Ignore network hiccup
    }
  };

  // Auto-reconnecting WebSocket
  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/train`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);

        if (msg.type === 'init') {
          setIsTraining(msg.is_training);
          if (msg.status?.device) {
            setDeviceInfo(msg.status.device.toUpperCase());
          }
        } else if (msg.type === 'start') {
          setIsTraining(true);
          setCurrentEpoch(1);
          setLossHistory([]);
          setDeploySuccess('');
          setDemoStatus('Training started... generating first curriculum batches.');
          if (msg.device_name) {
            setDeviceInfo(`${msg.device.toUpperCase()} (${msg.device_name})`);
          }
        } else if (msg.type === 'step') {
          const stepEvt = msg as TrainingStepEvent;
          setIsTraining(true);
          setCurrentEpoch(stepEvt.epoch);
          setCurrentStep(stepEvt.step);
          setTotalSteps(stepEvt.total_steps);
          setCurrentDepth(stepEvt.current_depth);
          setCurrentLoss(stepEvt.loss);
          setLossHistory((prev) => [...prev.slice(-40), stepEvt.loss]);

          if (stepEvt.brain_vision) {
            setBrainVision(stepEvt.brain_vision);
          }
        } else if (msg.type === 'epoch_complete') {
          const epochEvt = msg as TrainingEpochEvent;
          setCurrentEpoch(epochEvt.epoch);
          setCurrentDepth(epochEvt.current_depth);
          setTestSolveRate(epochEvt.test_solve_rate);

          if (epochEvt.demo) {
            playDemoTrajectory(epochEvt.demo, epochEvt.epoch, epochEvt.test_solve_rate);
          }
        } else if (msg.type === 'completed') {
          setIsTraining(false);
          setBestLoss(msg.best_loss ?? 0);
          setDemoStatus(`🎉 Training Complete! Best loss: ${msg.best_loss?.toFixed(5)}`);
          fetchModels();
        } else if (msg.type === 'stopped') {
          setIsTraining(false);
          setDemoStatus('Training stopped.');
          fetchModels();
        }
      } catch (err) {
        console.error('WS parse error', err);
      }
    };

    ws.onclose = () => {
      // Reconnect after 1 second if still mounted
      setTimeout(() => {
        if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
          connectWebSocket();
        }
      }, 1000);
    };
  };

  useEffect(() => {
    fetchModels();
    connectWebSocket();

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (demoIntervalRef.current) clearInterval(demoIntervalRef.current);
    };
  }, []);

  // Animates the AI's real test attempt on the demo board
  const playDemoTrajectory = (demo: DemoTrajectory, epoch: number, solveRate: number) => {
    if (demoIntervalRef.current) clearInterval(demoIntervalRef.current);

    if (!demo.states || demo.states.length === 0) {
      setDemoBoard(demo.initial_board);
      setDemoStatus(`Epoch ${epoch} Eval: Failed to find path (Solve Rate: ${solveRate.toFixed(0)}%)`);
      return;
    }

    let stepIdx = 0;
    setDemoBoard(demo.states[0]);
    setDemoStatus(`Epoch ${epoch} Live Test: AI Attempting Solve (${demo.actions.length} steps)...`);

    demoIntervalRef.current = setInterval(() => {
      stepIdx++;
      if (stepIdx < demo.states.length) {
        setDemoBoard(demo.states[stepIdx]);
        setDemoActionName(demo.action_names[stepIdx - 1] || '');
      } else {
        if (demoIntervalRef.current) clearInterval(demoIntervalRef.current);
        const outcome = demo.solved ? '✅ SUCCESS (Puzzle Solved!)' : '❌ Incomplete';
        setDemoStatus(`Epoch ${epoch} Eval: ${outcome} | Test Solve Rate: ${solveRate.toFixed(0)}%`);
      }
    }, 200);
  };

  const handleStartTraining = async () => {
    const is43 = mode === '43slot';
    const payload = {
      action: 'start',
      rows: is43 ? 7 : 3,
      cols: is43 ? 6 : 3,
      has_pocket: is43,
      epochs: epochs,
      steps_per_epoch: is43 ? 30 : 20,
      batch_size: batchSize,
      max_depth: maxDepth,
      lr: learningRate,
      save_path: is43 ? 'models/digimon_ai.pt' : 'models/puzzle_ai_3x3.pt',
    };

    setIsTraining(true);
    setLossHistory([]);
    setDemoStatus('Initializing neural network training session...');

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    } else {
      // Direct REST fallback
      try {
        await fetch('/api/train/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } catch (err) {
        setDemoStatus('Failed to start training. Please check server.');
        setIsTraining(false);
      }
    }
  };

  const handleStopTraining = async () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'stop' }));
    } else {
      try {
        await fetch('/api/train/stop', { method: 'POST' });
      } catch {
        // Ignore
      }
    }
    setIsTraining(false);
  };

  const handleDeploy = async (modelPath: string, modelName: string) => {
    try {
      const res = await fetch('/api/train/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_path: modelPath }),
      });
      if (res.ok) {
        setDeploySuccess(`Model ${modelName} deployed & active in game solver!`);
      }
    } catch {
      setDeploySuccess(`Deployed ${modelName}!`);
    }
  };

  // Render SVG Loss Sparkline
  const renderLossChart = () => {
    if (lossHistory.length < 2) {
      return (
        <div className="h-28 flex items-center justify-center text-slate-500 font-mono text-xs">
          Live Loss Graph will stream when training starts...
        </div>
      );
    }

    const minL = Math.min(...lossHistory);
    const maxL = Math.max(...lossHistory) || 1;
    const range = maxL - minL || 1;
    const width = 360;
    const height = 90;

    const points = lossHistory
      .map((val, i) => {
        const x = (i / (lossHistory.length - 1)) * width;
        const y = height - ((val - minL) / range) * (height - 15) - 8;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ');

    return (
      <div className="relative w-full h-28 flex flex-col justify-end">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-24 overflow-visible">
          <polyline
            fill="none"
            stroke="#38bdf8"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={points}
          />
        </svg>
        <div className="flex justify-between text-[10px] font-mono text-slate-400 mt-1 px-1">
          <span>Start: {lossHistory[0]?.toFixed(4)}</span>
          <span className="text-cyan-400 font-bold">Latest: {currentLoss.toFixed(4)}</span>
          <span>Min: {minL.toFixed(4)}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full max-w-6xl mx-auto flex flex-col space-y-6">
      {/* Header Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg shadow-indigo-500/30">
            <Brain className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              Neural AI Training Studio
              <span className="text-xs bg-indigo-500/20 text-indigo-300 font-mono px-2 py-0.5 rounded-full border border-indigo-500/30">
                ADI DeepCubeA
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Watch the neural network learn heuristics from scratch in real time on your GPU.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-mono font-bold text-slate-300">{deviceInfo}</span>
          </div>

          <button
            onClick={isTraining ? handleStopTraining : handleStartTraining}
            className={`flex items-center space-x-2 px-5 py-2 rounded-xl font-bold text-sm transition-all shadow-lg ${
              isTraining
                ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-500/30'
                : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-500/30 active:scale-95'
            }`}
          >
            {isTraining ? (
              <>
                <Pause className="w-4 h-4" />
                <span>Stop Training</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Start Self-Learning</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Configuration & Live Parameters */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col space-y-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Flame className="w-4 h-4 text-amber-400" />
            Training Configuration
          </h3>

          {/* Mode Selector */}
          <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800">
            <button
              disabled={isTraining}
              onClick={() => {
                setMode('3x3');
                setMaxDepth(15);
              }}
              className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
                mode === '3x3'
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              ⚡ Fast Demo (3x3)
            </button>
            <button
              disabled={isTraining}
              onClick={() => {
                setMode('43slot');
                setMaxDepth(30);
              }}
              className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
                mode === '43slot'
                  ? 'bg-emerald-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              🦖 Full 43-Slot Digimon
            </button>
          </div>

          {/* Sliders */}
          <div className="space-y-3 pt-2">
            <div>
              <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                <span>Total Epochs</span>
                <span className="font-bold text-indigo-400">{epochs}</span>
              </div>
              <input
                type="range"
                min={5}
                max={60}
                step={5}
                value={epochs}
                disabled={isTraining}
                onChange={(e) => setEpochs(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                <span>Batch Size</span>
                <span className="font-bold text-indigo-400">{batchSize}</span>
              </div>
              <input
                type="range"
                min={64}
                max={1024}
                step={64}
                value={batchSize}
                disabled={isTraining}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                <span>Curriculum Max Depth</span>
                <span className="font-bold text-indigo-400">{maxDepth} moves</span>
              </div>
              <input
                type="range"
                min={5}
                max={40}
                step={5}
                value={maxDepth}
                disabled={isTraining}
                onChange={(e) => setMaxDepth(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
            </div>
          </div>

          {/* Curriculum Depth Gauge */}
          <div className="pt-2">
            <div className="flex justify-between text-xs font-mono text-slate-400 mb-1">
              <span>Curriculum Exploration Depth</span>
              <span className="text-amber-400 font-bold">
                Depth {currentDepth} / {maxDepth}
              </span>
            </div>
            <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800 p-0.5">
              <div
                className="h-full bg-gradient-to-r from-amber-500 via-emerald-500 to-cyan-500 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(100, (currentDepth / maxDepth) * 100)}%` }}
              />
            </div>
          </div>

          {/* Live Metric Cards */}
          <div className="grid grid-cols-2 gap-2 pt-2">
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 block uppercase">Epoch &amp; Step</span>
              <span className="text-base font-mono font-bold text-white">
                {currentEpoch}/{epochs}{' '}
                <span className="text-xs text-indigo-400">
                  ({currentStep}/{totalSteps})
                </span>
              </span>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 block uppercase">Test Solve Rate</span>
              <span className="text-base font-mono font-bold text-emerald-400">
                {testSolveRate.toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Saved Models List */}
          <div className="pt-2 border-t border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-300 uppercase">Trained Models</span>
              <button
                onClick={fetchModels}
                className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
              >
                <RotateCcw className="w-3 h-3" /> Refresh
              </button>
            </div>

            {deploySuccess && (
              <div className="p-2 mb-2 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-300 text-xs flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {deploySuccess}
              </div>
            )}

            <div className="space-y-1.5 max-h-32 overflow-y-auto">
              {trainedModels.map((m) => (
                <div
                  key={m.path}
                  className="bg-slate-950 px-2.5 py-1.5 rounded-lg border border-slate-800/80 flex items-center justify-between text-xs font-mono"
                >
                  <span className="text-slate-300 truncate max-w-[130px]" title={m.name}>
                    {m.name}
                  </span>
                  <button
                    onClick={() => handleDeploy(m.path, m.name)}
                    className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white text-[10px] font-bold rounded shadow transition-all"
                  >
                    Deploy
                  </button>
                </div>
              ))}
              {trainedModels.length === 0 && (
                <span className="text-xs text-slate-500 italic block text-center py-2">
                  No saved models found. Start training above!
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Middle Column: Live Telemetry & AI Brain Vision */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Live Loss Curve &amp; Telemetry
            </h3>
            {bestLoss > 0 && (
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-500/30">
                Best: {bestLoss.toFixed(4)}
              </span>
            )}
          </div>

          {/* Loss Graph */}
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
            {renderLossChart()}
          </div>

          {/* AI Brain Vision: Candidate Action Value Estimates */}
          <div className="flex-1 flex flex-col justify-between bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-slate-200 uppercase flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                AI Brain Vision (Move Evaluator)
              </span>
              <span className="text-[10px] font-mono bg-amber-400/10 text-amber-300 px-2 py-0.5 rounded-full border border-amber-400/20">
                Bellman 1 + min h(s')
              </span>
            </div>

            <p className="text-xs text-slate-400 mb-3 leading-relaxed">
              Real-time neural network cost-to-go predictions for adjacent moves. The AI chooses the
              move with the lowest estimated remaining distance:
            </p>

            {brainVision && brainVision.candidate_moves.length > 0 ? (
              <div className="grid grid-cols-2 gap-2">
                {brainVision.candidate_moves.map((move) => {
                  const isLowest =
                    move.predicted_cost ===
                    Math.min(...brainVision.candidate_moves.map((m) => m.predicted_cost));

                  return (
                    <div
                      key={move.action_name}
                      className={`p-2.5 rounded-xl border transition-all ${
                        isLowest
                          ? 'bg-emerald-950/60 border-emerald-500/80 shadow-[0_0_12px_rgba(16,185,129,0.2)]'
                          : 'bg-slate-900 border-slate-800'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span
                          className={`text-xs font-bold font-arcade ${
                            isLowest ? 'text-emerald-300' : 'text-slate-400'
                          }`}
                        >
                          {move.action_name}
                        </span>
                        {isLowest && (
                          <span className="text-[9px] font-bold bg-emerald-400 text-slate-950 px-1 rounded">
                            BEST
                          </span>
                        )}
                      </div>
                      <span className="text-base font-mono font-bold text-white block mt-1">
                        {move.predicted_cost.toFixed(2)}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="h-28 flex items-center justify-center text-xs font-mono text-slate-500">
                Brain vision will activate during batch updates...
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Live Demonstration Board (Watch AI Solve) */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-yellow-400" />
              Live Epoch Demonstration
            </h3>
            {demoActionName && (
              <span className="text-xs font-arcade font-bold text-yellow-400 bg-yellow-400/10 px-2 py-0.5 rounded border border-yellow-400/30">
                {demoActionName}
              </span>
            )}
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            At the end of each epoch, the AI attempts to solve a scrambled test board live so you can
            physically see its intelligence emerging:
          </p>

          {/* Mini Board Viewport */}
          <div className="flex-1 flex flex-col items-center justify-center p-3 bg-slate-950 rounded-2xl border border-slate-800">
            {demoBoard.length > 0 ? (
              <div
                className={`grid gap-1 p-2 rounded-xl bg-slate-900 border border-slate-800 ${
                  demoBoard.length === 9 ? 'grid-cols-3 w-48 h-48' : 'grid-cols-6 w-56 h-64'
                }`}
              >
                {demoBoard.map((tile, idx) => (
                  <div
                    key={idx}
                    className={`rounded flex items-center justify-center font-arcade font-bold text-xs transition-all ${
                      tile === 0
                        ? 'bg-slate-950 border border-slate-800'
                        : 'bg-indigo-600 text-white shadow'
                    }`}
                  >
                    {tile !== 0 && tile}
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-xs font-mono text-slate-500 text-center px-4">
                Demonstration board will animate here after Epoch 1.
              </div>
            )}
          </div>

          {/* Demo Status Bar */}
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs font-mono text-slate-300 text-center">
            {demoStatus}
          </div>
        </div>

      </div>
    </div>
  );
};
