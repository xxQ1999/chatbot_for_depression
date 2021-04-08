package com.robot.tuling.socket;

import android.content.Context;
import android.os.Handler;
import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;

public class TxtSocketThread extends Thread {
    private String ip = "192.168.1.5";
    private int port = 6666;

    Handler inHandler;
    Handler outHandler;
    public Socket client = null;
    PrintWriter pw;
    OutputStream os;
    BufferedReader in;

    public boolean isRun = true;
    public Context ctx;
    private String TAG = "socket thread";

    public TxtSocketThread(Handler handlerin, Handler handlerout, Context context) {
        inHandler = handlerin;
        outHandler = handlerout;
        ctx = context;
        Log.i(TAG, "创建线程socket");
    }

    /**
     * 连接socket服务器
     */
    public void conn() {
        Log.i(TAG, "连接中……");
        try {
            client = new Socket(ip, port);
            boolean connected = client.isConnected();
            Log.i("连接","连接？" + connected);
            os = client.getOutputStream();
            pw = new PrintWriter(os);
            in = new BufferedReader(new InputStreamReader(client.getInputStream(), "UTF-8"));
        }catch (IOException e){
            Log.i("连接","连接失败");
        }
    }


    @Override
    public void run() {
       conn();
    }

}
