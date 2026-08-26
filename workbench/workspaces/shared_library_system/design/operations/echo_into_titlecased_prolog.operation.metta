(
  (kind operation)
  (id echo_into_titlecased_prolog)
  (label "Echo Into Titlecased / SWI-Prolog")
  (description "Take received text, execute the embedded Prolog source with SWI-Prolog, and return the title-cased text.")
  (topics ([]
    sample-demos
    systems-prolog
  ))
  (implementation prolog.source)
  (inputs (
    (text Text)
  ))
  (outputs (
    (text Text)
  ))
  (prolog (
    (engine swipl)
    (predicate titlecase_text)
    (arity 2)
    (source_code ([]
      "titlecase_text(Input, Output) :-"
      "    split_string(Input, \" \", \"\", Words),"
      "    maplist(titlecase_word, Words, Titled),"
      "    atomics_to_string(Titled, \" \", Output)."
      ""
      "titlecase_word(\"\", \"\") :- !."
      "titlecase_word(Word, Title) :-"
      "    string_chars(Word, [First|Rest]),"
      "    upcase_atom(First, UpperFirst),"
      "    string_chars(Tail, Rest),"
      "    string_lower(Tail, LowerTail),"
      "    string_concat(UpperFirst, LowerTail, Title)."
    ))
  ))
  (parameters (
    (inputBinding text)
    (outputBinding text)
    (timeoutSeconds 30)
  ))
  (implements (
    (echo_into_titlecased (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
