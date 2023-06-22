(set-option :produce-models true)
(set-option :produce-unsat-cores true)

(set-logic ALL)

(declare-fun x () String)
(declare-fun y () String)
(declare-fun i () Int)
(declare-fun n () Int)

; x = c | dd
(assert (str.in_re x (re.union (str.to_re "c") (str.to_re "dd"))))

; y = (b(b|cc*b))*(bcc*|ac*a)
(assert (str.in_re y (re.++ 
(re.* (re.++ (str.to_re "b")
            (re.union (str.to_re "b")
                      (re.++ (str.to_re "c")
                            (re.++
                              (re.* (str.to_re "c"))
                              (str.to_re "b"))))))
(re.union (re.++ (str.to_re "bc") (re.* (str.to_re "c"))) 
          (re.++ (str.to_re "a") (re.++ (re.* (str.to_re "c")) (str.to_re "a"))))
)))

(assert (= x (str.substr y i n)))


(assert (>  n i))

; (assert (> (- (str.len y) (+ i n)) 0))

; (assert (> i 0))

(check-sat)
(get-model)
;(get-unsat-core)
