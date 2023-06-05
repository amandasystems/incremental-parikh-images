(set-option :produce-models true)
(set-logic ALL)

(declare-fun x () String)
(declare-fun y () String)
(declare-fun i () Int)
(declare-fun n () Int)

; x = c | dd
(assert (str.in_re x (re.union (str.to_re "c") (str.to_re "dd"))))

; y = l b vad nu det är

(assert (= x (str.substr y i n)))
(assert (= (* 2 i) n))

(check-sat)
(get-model)
