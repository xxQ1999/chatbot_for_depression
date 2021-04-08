package com.robot.tuling.ui;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Message;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.ant.liao.GifView;
import com.robot.tuling.R;
import com.robot.tuling.constant.DataBase;
import com.robot.tuling.socket.SocketThread;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

import butterknife.BindView;
import butterknife.ButterKnife;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.FormBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class SocketActivity extends BaseActivity {

    @BindView(R.id.toolbar)
    Toolbar toolbar;
    @BindView(R.id.gv_about)
    GifView gvAbout;
    @BindView(R.id.lr_title)
    TextView lrTitle;
    @BindView(R.id.tv_version_right)
    LinearLayout tvVersionRight;


    private Button ok ;
    private boolean isShowGifView = true;
    private EditText editText;
    private String IP = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_socket);
        ButterKnife.bind(this);
        initData();
        getIP();
        ok = findViewById(R.id.send_socket);
        editText = findViewById(R.id.input_socket);
        editText.setText(IP);
        ok.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //String url = "http://192.168.1.5:5000/chat";//替换成自己的服务器地址
                //SendMessage(url, "1", "2");
                Change();
            }
        });

    }
    private String getIP(){
        DataBase dbHelper = new DataBase(this, "ip.db", null, 1);
        SQLiteDatabase db = dbHelper.getReadableDatabase();// 打开数据库
        String sql = "select * from UserMessage";
        Cursor cursor = db.rawQuery(sql, null);
        while (cursor.moveToNext()) {
            IP = cursor.getString(0);
            break;
        }
        //url = "http://"+IP+":5000/chat";
        return IP;
    }
    private void Change(){
        DataBase dbHelper = new DataBase(this, "ip.db", null, 1);
        //1.得到连接
        SQLiteDatabase sqLiteDatabase = dbHelper.getReadableDatabase();

        //2.执行update  update person set name = "Jack",age = 20 where _id = 6

        /**
         * 第一个参数：表名
         * 第二个参数：更新的value
         * 第三个参数：where 后的语句
         * 第四个参数：? 所代表的值
         */
        ContentValues values = new ContentValues();
        values.put("ip",editText.getText().toString());
        sqLiteDatabase.update("UserMessage",values,null,null);

        //3.关闭连接
        sqLiteDatabase.close();
        Toast.makeText(SocketActivity.this,"修改成功！"+editText.getText().toString(),Toast.LENGTH_LONG).show();
    }
    private void SendMessage(String url, final String userName, String passWord) {

        OkHttpClient client = new OkHttpClient();
        FormBody.Builder formBuilder = new FormBody.Builder();
        formBuilder.add("demo", "这是我的测试");

        Request request = new Request.Builder().url(url).post(formBuilder.build()).build();
        Call call = client.newCall(request);
        call.enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                Toast.makeText(SocketActivity.this, "服务器错误", Toast.LENGTH_SHORT).show();
                            }
                        });
                    }
                });
            }

            @Override
            public void onResponse(Call call, final Response response) throws IOException {
                final String res = response.body().string();
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        if (res.equals("0")) {
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    Toast.makeText(SocketActivity.this, "失败", Toast.LENGTH_SHORT).show();
                                }
                            });
                        } else {
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    Toast.makeText(SocketActivity.this, "成功"+res, Toast.LENGTH_SHORT).show();
                                }
                            });

                        }

                    }
                });
            }
        });

    }
    private void initData() {
        initActionBar();
        initGifView();
        editText = (EditText) findViewById(R.id.input_socket);
        /*button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                SendSocket(view);
        }
        });*/

    }

    private void initActionBar() {
        toolbar.setTitle(getString(R.string.about));
        toolbar.setSubtitle(getString(R.string.app_name));
        toolbar.setSubtitleTextColor(getResources().getColor(R.color.white));
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
    }

    private void initGifView() {
        gvAbout.setGifImage(R.drawable.gif_robot_walk);
        gvAbout.setOnClickListener((e)->{
            if (isShowGifView) {
                gvAbout.showCover();
            } else {
                gvAbout.showAnimation();
            }
            isShowGifView = !isShowGifView;
        });
    }


    public void SendSocket(View view) {
        new Thread() {
            @Override
            public void run() {
                try {
                    Socket sed_socket = new Socket("192.168.1.5", 6666);
                    boolean connected = sed_socket.isConnected();
                    Log.i("连接","连接？" + connected);
                    OutputStream os = sed_socket.getOutputStream();
                    PrintWriter pw = new PrintWriter(os);
                    String msg = editText.getText().toString();
                    pw.write(msg+"\r\n");
                    os.flush(); //写
                    pw.close();
                    Socket rev_socket = new Socket("192.168.1.5", 6666);
                    Log.i("连接","上");
                    try {
                        BufferedReader in = new BufferedReader(new InputStreamReader(rev_socket.getInputStream(), "UTF-8"));
                        String s = in.readLine();
                        Log.i("连接", s);
                        in.close();
                        Log.i("连接", "下");
                    }catch (IOException e){
                        Log.i("连接", "读取失败");
                        Log.i("连接", e.getMessage().toString());
                    }

                } catch (IOException e) {
                    Log.i("连接", "失败");
                    e.printStackTrace();
                    Log.i("连接", e.getMessage().toString());
                }
            }
        }.start();
    }



}
