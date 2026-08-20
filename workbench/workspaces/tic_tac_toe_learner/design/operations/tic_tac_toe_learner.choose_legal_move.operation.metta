(
  (id tic_tac_toe_learner.choose_legal_move)
  (label "Choose Legal Tic-Tac-Toe Move")
  (description "Workspace-specific human operation for selecting a legal board coordinate.")
  (topics ([]
    games
    sample
  ))
  (implementation human.await_input)
  (inputs (
    (board Object)
  ))
  (outputs (
    (move Object)
  ))
  (parameters (
    (form (
      (row (
        (type Integer)
        (minimum 0)
        (maximum 2)
      ))
      (column (
        (type Integer)
        (minimum 0)
        (maximum 2)
      ))
    ))
  ))
  (kind operation)
)
