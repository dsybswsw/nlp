// Copyright by Shiwei Wu.
package optimization.wrapper;

/**
 * 
 * @author Shiwei Wu
 * @Data May 6, 2013
 */
public class OptSample extends LBFGSWrapper {
  double[] gradients = new double[2];

  public OptSample(int numPara, double[] initWeights) {
    super(numPara, initWeights);
  }

  @Override
  public double computeFuncValue(double[] curWeights) {
    double resFuncVal = (curWeights[0] - 3) * (curWeights[0] - 3) + (curWeights[1] - 4)
        * (curWeights[1] - 4) + 10;
    return resFuncVal;
  }

  @Override
  public double[] computeGradients(double[] weights) {
    double[] gradients = new double[weights.length];
    gradients[0] = 2 * (weights[0] - 3);
    gradients[1] = 2 * (weights[1] - 4);
    return gradients;
  }

  public static void main(String[] args) {
    double[] initWeights = new double[2];
    initWeights[0] = 100.0;
    initWeights[1] = 10.0;
    OptSample sample = new OptSample(2, initWeights);
    sample.run();
    double[] finalWeights = sample.getWeightVectors();
    System.out.println("Final weight X is " + finalWeights[0]);
    System.out.println("Final weight Y is " + finalWeights[1]);
    System.out.println("Function value is " + sample.getFinalFuncVal());
  }
}
