export type ActionType = 0 | 1 | 2 | 3; // 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT

export type SolverName =
  | 'Hierarchical Subgoal Solver'
  | 'A* Search (Linear Conflict)'
  | 'IDA* Search'
  | 'Neural AI (PyTorch)';

export interface PuzzleStateData {
  board: number[];
  rows: number;
  cols: number;
  has_pocket: boolean;
  blank_pos: [number, number];
  is_solved: boolean;
  is_solvable: boolean;
  manhattan: number;
  linear_conflicts: number;
}

export interface SolveResponseData {
  success: boolean;
  actions: number[];
  action_names: string[];
  phase_names?: string[];
  states: number[][];
  duration_ms: number;
  nodes_expanded: number;
  solver_name: string;
  message: string;
}

export interface CandidateMove {
  action: number;
  action_name: string;
  predicted_cost: number;
}

export interface BrainVisionData {
  board: number[];
  blank_pos: [number, number];
  candidate_moves: CandidateMove[];
}

export interface DemoTrajectory {
  initial_board: number[];
  actions: number[];
  action_names: string[];
  states: number[][];
  solved: boolean;
}

export interface TrainingStepEvent {
  type: 'step';
  epoch: number;
  total_epochs: number;
  step: number;
  total_steps: number;
  current_depth: number;
  loss: number;
  running_avg_loss: number;
  learning_rate: number;
  brain_vision?: BrainVisionData;
}

export interface TrainingEpochEvent {
  type: 'epoch_complete';
  epoch: number;
  total_epochs: number;
  current_depth: number;
  avg_loss: number;
  test_solve_rate: number;
  duration_sec: number;
  demo?: DemoTrajectory;
}

export interface ModelInfoData {
  name: string;
  path: string;
  size_kb: number;
  modified_time: string;
}
