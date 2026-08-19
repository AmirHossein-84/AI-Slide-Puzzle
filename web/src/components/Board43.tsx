import React from 'react';
import { ActionType, PuzzleStateData } from '../types/puzzle';
import { sounds } from '../utils/audio';

interface Board43Props {
  state: PuzzleStateData;
  onMove: (action: ActionType) => void;
  showNumbers: boolean;
  useProcedural: boolean;
  disabled?: boolean;
  playbackSpeed?: number;
}

export const Board43: React.FC<Board43Props> = ({
  state,
  onMove,
  showNumbers,
  useProcedural,
  disabled = false,
  playbackSpeed = 8,
}) => {
  const [blankR, blankC] = state.blank_pos;

  // Dynamic CSS transition duration based on playback speed (0ms above 50 moves/sec)
  const transitionClass =
    playbackSpeed > 50
      ? 'transition-none'
      : playbackSpeed > 20
      ? 'transition-all duration-30 ease-out'
      : 'transition-all duration-150 ease-out';

  const handleTileClick = (r: number, c: number) => {
    if (disabled) return;

    // Blank is in the left side pocket (7, 0)
    if (blankR === 7 && blankC === 0) {
      if (r === 6 && c === 0) {
        sounds.playSlide();
        onMove(3); // RIGHT (moves blank into (6, 0), tile 37 enters pocket)
      }
      return;
    }

    // Blank is at (6, 0): clicking the left pocket (7, 0) moves blank LEFT into pocket
    if (blankR === 6 && blankC === 0 && r === 7 && c === 0) {
      sounds.playSlide();
      onMove(2); // LEFT (moves blank into pocket)
      return;
    }

    // Normal grid moves
    if (r === blankR - 1 && c === blankC) {
      sounds.playSlide();
      onMove(0); // UP
    } else if (r === blankR + 1 && c === blankC) {
      sounds.playSlide();
      onMove(1); // DOWN
    } else if (r === blankR && c === blankC - 1) {
      sounds.playSlide();
      onMove(2); // LEFT
    } else if (r === blankR && c === blankC + 1) {
      sounds.playSlide();
      onMove(3); // RIGHT
    }
  };

  const getTileAt = (r: number, c: number): number => {
    if (r === 7 && c === 0) {
      return state.board[42] ?? 0; // Pocket tile
    }
    return state.board[r * 6 + c] ?? 0;
  };

  const pocketTile = getTileAt(7, 0);
  const isPocketBlank = pocketTile === 0;

  return (
    <div className="relative flex flex-col items-center select-none">
      {/* Authentic Handheld Green Toy Body matching digimon_puzzle_board_1787081273691.jpg */}
      <div className="relative p-4 sm:p-6 rounded-[2.5rem] bg-[#1da94c] shadow-[0_20px_50px_rgba(0,0,0,0.6),inset_0_4px_10px_rgba(255,255,255,0.3),inset_0_-8px_16px_rgba(0,0,0,0.4)] border-4 border-[#147a36] flex flex-col items-center max-w-[95vw]">
        
        {/* Top Header Banner */}
        <div className="w-full max-w-[420px] sm:max-w-[490px] mb-2 sm:mb-3">
          <img
            src="/tiles/top_header.png"
            alt="Digimon Digital Monsters Header"
            className="w-full h-auto object-contain drop-shadow-md rounded-t-xl pointer-events-none"
          />
        </div>

        {/* Board Area: Left Banner Column + 6x7 Tile Tray */}
        <div className="flex items-end gap-1.5 sm:gap-2">
          
          {/* Left Column: Vertical Digimon Banner + Pocket Recess at Bottom */}
          <div className="flex flex-col items-center justify-between h-[364px] sm:h-[455px] w-[50px] sm:w-[62px]">
            {/* Top Left Balloon & Vertical DIGIMON Logo Banner */}
            <div className="flex-1 w-full flex items-center justify-center">
              <img
                src="/tiles/left_banner.png"
                alt="Digimon Balloon Banner"
                className="w-full h-full object-contain drop-shadow-sm pointer-events-none"
              />
            </div>

            {/* Bottom-Left Poking Out Parking Pocket (7, 0) */}
            <div
              className={`relative aspect-square w-full rounded-lg flex items-center justify-center ${transitionClass} ${
                isPocketBlank
                  ? 'bg-[#147a36] shadow-[inset_0_4px_8px_rgba(0,0,0,0.7)] border-2 border-[#0d5926]'
                  : 'cursor-pointer select-none bg-slate-800 border border-slate-700 shadow-md hover:brightness-110 active:scale-95'
              } ${blankR === 6 && blankC === 0 && !disabled ? 'ring-2 ring-yellow-400 ring-offset-2 ring-offset-[#1da94c]' : ''}`}
              onClick={() => handleTileClick(7, 0)}
              title={isPocketBlank ? 'Empty Parking Pocket (Blank is parked here)' : `Pocket Tile: ${pocketTile}`}
            >
              {!isPocketBlank ? (
                <div className="w-full h-full rounded-lg relative overflow-hidden flex items-center justify-center">
                  {useProcedural ? (
                    <div className="w-full h-full bg-gradient-to-br from-blue-600 via-indigo-600 to-blue-800 flex items-center justify-center font-arcade font-bold text-white text-sm sm:text-lg shadow-inner">
                      {pocketTile}
                    </div>
                  ) : (
                    <>
                      <div className="w-full h-full bg-slate-800 absolute inset-0 flex items-center justify-center font-arcade font-bold text-slate-300 text-sm">
                        {pocketTile}
                      </div>
                      <img
                        src={`/tiles/tile_${String(pocketTile).padStart(2, '0')}.png`}
                        alt={`Pocket Tile ${pocketTile}`}
                        className="w-full h-full object-cover absolute inset-0 pointer-events-none"
                        loading="eager"
                      />
                    </>
                  )}
                  {showNumbers && (
                    <span className="absolute top-0.5 left-0.5 bg-black/80 text-yellow-300 text-[9px] sm:text-[11px] font-mono font-bold px-1 rounded shadow z-10">
                      {pocketTile}
                    </span>
                  )}
                </div>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <span className="font-arcade text-[8px] sm:text-[10px] font-bold text-emerald-300 text-center uppercase tracking-tighter opacity-80">
                    PARK
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* 6x7 Tile Tray: Rows 0 to 6 */}
          <div className="p-1 sm:p-1.5 rounded-xl bg-[#147a36] shadow-[inset_0_4px_12px_rgba(0,0,0,0.7)] border-2 border-[#0d5926] flex flex-col space-y-1 sm:space-y-1.5">
            {Array.from({ length: 7 }).map((_, r) => (
              <div
                key={`grid-row-${r}`}
                className="grid grid-cols-6 gap-1 sm:gap-1.5 w-[310px] sm:w-[390px] md:w-[440px]"
              >
                {Array.from({ length: 6 }).map((_, c) => {
                  const tileNum = getTileAt(r, c);
                  const isBlank = tileNum === 0;
                  const isAdjacent =
                    (Math.abs(r - blankR) === 1 && c === blankC) ||
                    (r === blankR && Math.abs(c - blankC) === 1) ||
                    (blankR === 7 && blankC === 0 && r === 6 && c === 0);

                  return (
                    <div
                      key={`slot-${r}-${c}`}
                      className={`relative aspect-square rounded-lg flex items-center justify-center ${transitionClass} ${
                        isBlank
                          ? 'bg-[#0f4d22] shadow-[inset_0_3px_6px_rgba(0,0,0,0.8)] border border-[#0d401c]'
                          : 'cursor-pointer select-none bg-slate-800 border border-slate-700 shadow-md hover:brightness-110 active:scale-95'
                      } ${isAdjacent && !disabled ? 'ring-2 ring-yellow-400 ring-offset-1 ring-offset-[#147a36]' : ''}`}
                      onClick={() => !isBlank && handleTileClick(r, c)}
                    >
                      {!isBlank && (
                        <div className="w-full h-full rounded-lg relative overflow-hidden flex items-center justify-center">
                          {useProcedural ? (
                            <div className="w-full h-full bg-gradient-to-br from-blue-600 via-indigo-600 to-blue-800 flex items-center justify-center font-arcade font-bold text-white text-sm sm:text-xl shadow-inner border border-blue-400/30">
                              {tileNum}
                            </div>
                          ) : (
                            <>
                              <div className="w-full h-full bg-slate-800 absolute inset-0 flex items-center justify-center font-arcade font-bold text-slate-300 text-sm">
                                {tileNum}
                              </div>
                              <img
                                src={`/tiles/tile_${String(tileNum).padStart(2, '0')}.png`}
                                alt={`Tile ${tileNum}`}
                                className="w-full h-full object-cover absolute inset-0 pointer-events-none"
                                loading="eager"
                              />
                            </>
                          )}

                          {showNumbers && (
                            <span className="absolute top-0.5 left-0.5 bg-black/80 text-yellow-300 text-[9px] sm:text-[11px] font-mono font-bold px-1 rounded shadow z-10">
                              {tileNum}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>

        </div>

        {/* Solved Status Indicator Bar at Bottom */}
        <div className="w-full flex items-center justify-between pt-3 px-3">
          <div className="flex items-center space-x-2">
            <span
              className={`w-3 h-3 rounded-full ${
                state.is_solved
                  ? 'bg-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.9)] animate-pulse'
                  : 'bg-emerald-950 border border-emerald-400/40'
              }`}
            />
            <span className="font-arcade text-xs font-bold text-emerald-100 uppercase tracking-wider">
              {state.is_solved ? '★ COMPLETED ★' : 'DIGITAL TOY MODE'}
            </span>
          </div>

          <span className="font-mono text-xs font-bold text-emerald-200 bg-[#147a36] px-2.5 py-0.5 rounded-full border border-emerald-400/30">
            {state.is_solved ? '42/42 SOLVED' : `MANHATTAN: ${state.manhattan}`}
          </span>
        </div>

      </div>
    </div>
  );
};
