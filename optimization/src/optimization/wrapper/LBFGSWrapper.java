// Copyright by Shiwei Wu.
package optimization.wrapper;

import java.util.logging.Logger;

import optimization.lbfgs.LBFGS;

/**
 * Implements a L-BFGS optimization wrapper.
 * 
 * @author Shiwei Wu
 * @Data May 6, 2013
 */
public abstract class LBFGSWrapper {
  // Number of parameters.
  private int paramNumber;

  private double[] weightsVector;
  // Run at most 100 iterations. Default is 100.
  private int maxIterNum = 100;

  // stop criterion.
  private double relativeFuncThreshold = 1e-3;

  // number of histories used to approximate hessian.
  private int numCorrections = 21;

  private int checkConvergeTimes = 0;

  private int[] iprint;
  private int[] iflag;

  private double[] diag;

  private double epsilon = 1.0e-5;
  private double xtol = 1.0e-16; // machine precision
  
  private double bestFuncVal = 0;

  // Check converge 3 times.
  private final static int MAX_PASS_CONVERGE = 3;

  private final static Logger logger = Logger.getLogger(LBFGSWrapper.class.getName());

  /**
   * Compute the function values given parameters.
   * 
   * @param current
   *          weight values.
   * @return function values.
   */
  public abstract double computeFuncValue(double[] curWeights);

  /**
   * Compute the gradients of the function.
   * 
   * @param current
   *          weight values.
   * @return gradient values.
   */
  public abstract double[] computeGradients(double[] weights);

  public LBFGSWrapper(int paramNumber, double[] initWeights) {
    // Make sure parameter number is equal to the weights number.
    assert paramNumber == initWeights.length;

    this.paramNumber = paramNumber;

    this.weightsVector = new double[paramNumber];
    for (int i = 0; i < paramNumber; i++) {
      if (initWeights != null)
        weightsVector[i] = initWeights[i];
      else
        weightsVector[i] = 1.0 / paramNumber;
    }

    this.iprint = new int[2];
    this.iprint[0] = -1; // specifies the frequency of the output: output at each iterations
    this.iprint[1] = 0;// specifies the type of output generated:

    // ### set the status flag
    this.iflag = new int[1];
    this.iflag[0] = 0;// this will make sure the LBFGS clear all the state information

    // Print the first n weight at each iteration.
    diag = new double[paramNumber];
  }

  public boolean run() {
    int iterNum = 0;
    double[] gradients = null;
    double nowFuncVal = 0;
    double lastFuncVal = 0;

    while (isConverged() == false && iterNum <= maxIterNum) {
      // First compute the gradients and function value of the objective function.
      logger.info("In iteration " + iterNum);
      gradients = computeGradients(weightsVector);
      nowFuncVal = computeFuncValue(weightsVector);
      bestFuncVal = nowFuncVal;
      // check converge.
      if (iterNum != 0 && Math.abs((nowFuncVal - lastFuncVal) / lastFuncVal) < relativeFuncThreshold) {
        ++checkConvergeTimes;
        // If the functional is smaller
        if (checkConvergeTimes >= MAX_PASS_CONVERGE) {
          logger.info("The function value converged and optimization stoped.");
        }
        break;
      }

      boolean success = runOneIterLBFGS(nowFuncVal, gradients);
      if (!success) {
        logger.info("Failed in line search in iteration " + iterNum);
        return false;
      }
      
      lastFuncVal = nowFuncVal;      
      ++ iterNum;
    }
    return true;
  }

  public double[] getWeightVectors() {
    return weightsVector;
  }
  
  public double getFinalFuncVal() {
    return bestFuncVal;
  }
  
  private boolean isConverged() {
    return false;
  }

  /*
   * the default LBFGS minimizes the function; so we need to negate the function and graident_vector
   * if we want to maximize the funciton
   */
  private boolean runOneIterLBFGS(double functionValue, double[] gradients) {
    assert gradients.length == paramNumber;
    logger.info("Run one iteration of L-BFGS");
    try {
      LBFGS.lbfgs(paramNumber, numCorrections, weightsVector, functionValue, gradients, false,
          diag, iprint, epsilon, xtol, iflag);
    } catch (LBFGS.ExceptionWithIflag e) {
      logger.info(e.toString());
      return false;
    }
    return true;
  }
}
