/**
 * This file is part of Ostrich, an SMT solver for strings.
 * Copyright (c) 2023 Denghang Hu. All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * * Redistributions of source code must retain the above copyright notice, this
 *   list of conditions and the following disclaimer.
 * 
 * * Redistributions in binary form must reproduce the above copyright notice,
 *   this list of conditions and the following disclaimer in the documentation
 *   and/or other materials provided with the distribution.
 * 
 * * Neither the name of the authors nor the names of their
 *   contributors may be used to endorse or promote products derived from
 *   this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */

package ostrich.cesolver.core

import scala.collection.mutable.{HashMap => MHashMap}
import ostrich.cesolver.util.ParikhUtil
import ostrich.cesolver.automata.CEBasicOperations
import ostrich.cesolver.automata.CostEnrichedAutomatonBase
import scala.collection.mutable.ArrayBuffer
import ostrich.OFlags
import ap.parser.ITerm
import ap.parser.IFormula
import ap.parser.IExpression._

class UnaryFinalConstraints(
    override val strId: ITerm,
    override val auts: Seq[CostEnrichedAutomatonBase],
    flags : OFlags
) extends FinalConstraints {
  // the globalS is used to store the state we have explored before
  // to avoid repeated exploration
  private val globalS = ArrayBuffer[Set[(State, Seq[Int])]]()

  // eagerly product
  lazy val productAut = auts.reduce(_ product _)

  lazy val mostlySimplifiedAut = {
    val ceAut = CEBasicOperations.minimizeHopcroftByVec(
      CEBasicOperations.determinateByVec(
        CEBasicOperations.epsilonClosureByVec(
          productAut
        )
      )
    )
    ceAut.removeDuplicatedReg()
    ceAut
  }

  lazy val simplifyButRemainLabelAut = {
    val ceAut = CEBasicOperations.removeDuplicatedTrans(
      CEBasicOperations.minimizeHopcroft(
        productAut
      )
    )
    ceAut.removeDuplicatedReg()
    ceAut
  }
    

  lazy val checkSatAut =
    if (flags.simplifyAut) mostlySimplifiedAut else productAut
  lazy val findModelAut =
    if (flags.simplifyAut) simplifyButRemainLabelAut else productAut

  /**
    * Like Bounded Model Checking(BMC), we find all runs of length less and equal to 
    * bound. If the end state of the run is an accepting state, we compute the registers updates
    * on the run and add them to the formula. 
    * @param bound
    * @return
    */
  def getUnderApprox(bound: Int): IFormula = {
    ParikhUtil.debugPrintln("getUnderApprox")
    val aut = checkSatAut
    val lowerBound = globalS.size
    computeGlobalSWithRegsValue(bound)
    if (lowerBound == globalS.size) {
      // the globalS does not change
      return Boolean2IFormula(false)
    }
    val registers = aut.registers

    val r1Formula = or(
      for (
        j <- lowerBound until globalS.size;
        if !globalS(j).isEmpty;
        (s, regVal) <- globalS(j);
        if (aut.isAccept(s))
      ) yield {
        and(for (i <- 0 until registers.size) yield registers(i) === regVal(i))
      }
    )
    and(Seq(r1Formula, getRegsRelation))
  }

  override lazy val getCompleteLIA: IFormula = 
    getCompleteLIA(checkSatAut)

  def getRegsRelation: IFormula = checkSatAut.regsRelation

  val interestTerms: Seq[ITerm] = productAut.registers

  def getModel: Option[Seq[Int]] = {
    val registersModel = MHashMap() ++ interestTermsModel
    ParikhUtil.findAcceptedWordByRegisters(
      Seq(findModelAut),
      registersModel
    )
  }

  if (flags.debug) {
    productAut.toDot("product_" + strId.toString)
    mostlySimplifiedAut.toDot("simplified_" + strId.toString)
    simplifyButRemainLabelAut.toDot("original_" + strId.toString)
  }

  private def computeGlobalSWithRegsValue(
      sLen: Int
  ): Unit = {
    var idx = globalS.size
    checkSatAut.states.zipWithIndex.toMap
    if (idx == 0) {
      val initialRegsVals = Seq.fill(checkSatAut.registers.size)(0)
      globalS += Set((checkSatAut.initialState, initialRegsVals))
      idx += 1
    }
    while (idx < sLen && !globalS(idx - 1).isEmpty) {
      globalS += (for (
        (s, regVal) <- globalS(idx - 1);
        (t, vec) <- succWithVec(checkSatAut, s)
      ) yield {
        (t, addTwoSeq(regVal, vec))
      })
      idx += 1
    }
  }

  private def succWithVec(
      aut: CostEnrichedAutomatonBase,
      s: State
  ): Iterable[(State, Seq[Int])] =
    for ((t, lbl, vec) <- aut.outgoingTransitionsWithVec(s)) yield (t, vec)

  // e.g (1,1) + (1,0) = (2,1)
  private def addTwoSeq(seq1: Seq[Int], seq2: Seq[Int]): Seq[Int] = {
    seq1 zip seq2 map { case (a, b) => a + b }
  }

}
