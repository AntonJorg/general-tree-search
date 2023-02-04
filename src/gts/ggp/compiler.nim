import nimpy

#[
  GDL:
    role(?r) ?r is a player
    init(?f) ?f holds in the initial position
    true(?f) ?f holds in the current position
    legal(?r,?m) ?r can do move ?m
    does(?r,?m) player ?r does move ?m
    next(?f) ?f holds in the next position
    terminal the position is terminal
    goal(?r,?v) ?r gets payoff ?v
  GDL-II:
    sees(?r,?p) ?r perceives ?p in the next position
    random the random player (aka. Nature)

  Steps:
    Role definition
    Initial state
    Legal moves 
    Effects of moves 
    Terminal states
    Rewards
]#

type
  TokenName = enum 
    Unknown
    LeftPar
    RightPar
    Implies

  Token = object
    name: TokenName
    line: int
    start: int
    stop: int
  
  Tokenizer = object
    source: string
    currentIdx: int

proc newTokenizer(filename: string): Tokenizer =
  return Tokenizer(source: readFile(filename), currentIdx: 0)

func isAtEnd(tk: Tokenizer): bool =
  return tk.currentIdx >= tk.source.len - 1 

func peek(tk: Tokenizer, match: char): bool =
  if tk.isAtEnd:
    return false
  return tk.source[tk.currentIdx + 1] == match

func current(tk: Tokenizer): char =
  return tk.source[tk.currentIdx]

proc nextExpr(tk: var Tokenizer) =
  while tk.current != "("[0]:
    tk.currentIdx += 1
  tk.currentIdx += 1

proc consume(tk: var Tokenizer): string =
  let start = tk.currentIdx
  while tk.current in "abcdefghijklmnopqrstwvxyz":
    tk.currentIdx += 1
  result = tk.source[start..<tk.currentIdx]
  tk.currentIdx += 1

proc tokenize(filename: string) {.exportpy.} =
  var tk = newTokenizer(filename)
  tk.nextExpr
  echo tk.consume
  echo tk.source[tk.currentIdx..<tk.source.len]
