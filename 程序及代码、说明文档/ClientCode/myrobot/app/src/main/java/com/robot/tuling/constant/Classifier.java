package com.robot.tuling.constant;

import android.content.res.AssetManager;

import android.util.Log;

import org.tensorflow.contrib.android.TensorFlowInferenceInterface;


public class Classifier {

    //模型中输入变量的名称
    private static final String inputName = "op_data_input";
    //模型中输出变量的名称
    private static final String outputName = "out_out/Softmax";

    String[] outputNames = new String[] {outputName};



    TensorFlowInferenceInterface tfInfer;
    static {//加载libtensorflow_inference.so库文件
        System.loadLibrary("tensorflow_inference");
    }
   public Classifier(AssetManager assetManager, String modePath) {
        //初始化TensorFlowInferenceInterface对象
        tfInfer = new TensorFlowInferenceInterface(assetManager,modePath);
    }


    public int getPredict(float[] inputs) {
        //将数据feed给tensorflow的输入节点
        tfInfer.feed(inputName, inputs, 1,48,48,1);
        //运行tensorflow
        tfInfer.run(outputNames);
        ///获取输出节点的输出信息
        float[] outputs = new float[7]; //用于存储模型的输出数据
        tfInfer.fetch(outputName, outputs);
        Log.d("outputs", "getPredict: ");
        for(int i=0; i<outputs.length; i++)
            System.out.print(outputs[i]+"  ");
        return getMaxIndex(outputs);
    }

    public static int getMaxIndex(float[] arr) {
        if(arr==null||arr.length==0){
            return -1;//如果数组为空 或者是长度为0 就返回null
        }
        int maxIndex=0;//假设第一个元素为最大值 那么下标设为0
        for(int i =0;i<arr.length-1;i++){
            if(arr[maxIndex]<arr[i+1]){
                maxIndex=i+1;
            }
        }
        System.out.println("maxIndex："+maxIndex);
        return maxIndex;
    }

}
