package com.robot.tuling.ui;

import android.content.ContentValues;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AbsListView;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.robot.tuling.R;
import com.robot.tuling.adapter.ChatMessageAdapter;
import com.robot.tuling.constant.DataBase;
import com.robot.tuling.constant.TulingParams;
import com.robot.tuling.control.NavigateManager;
import com.robot.tuling.control.RetrofitApi;
import com.robot.tuling.entity.MessageEntity;
import com.robot.tuling.util.IsNullOrEmpty;
import com.robot.tuling.util.KeyBoardUtil;
import com.robot.tuling.util.TimeUtil;
import com.sunfusheng.FirUpdater;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.schedulers.Schedulers;
import okhttp3.FormBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.adapter.rxjava2.RxJava2CallAdapterFactory;
import retrofit2.converter.gson.GsonConverterFactory;

public class MainActivity extends BaseActivity {

    @BindView(R.id.toolbar)
    Toolbar toolbar;
    @BindView(R.id.lv_message)
    ListView lvMessage;
    @BindView(R.id.iv_send_msg)
    ImageView ivSendMsg;
    @BindView(R.id.et_msg)
    EditText etMsg;
    @BindView(R.id.rl_msg)
    RelativeLayout rlMsg;

    private List<MessageEntity> msgList = new ArrayList<>();
    private ChatMessageAdapter msgAdapter;
    private String sendMsg;
    private String IP = "192.168.1.5";
    private int PORT = 6666;
    String url = "http://"+IP+":5000/chat";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        ButterKnife.bind(this);

        new FirUpdater(this, "3c57fb226edf7facf821501e4eba08d2", "5704953c00fc74127000000a").checkVersion();

        initData();
        initView();
        initListener();
        initIP();
        //initGifView();
    }

    private void initIP(){
        DataBase dbHelper = new DataBase(this, "ip.db", null, 1);
        SQLiteDatabase db1 = dbHelper.getReadableDatabase();// 打开数据库
        String sql = "select * from UserMessage";
        Cursor cursor = db1.rawQuery(sql, null);
        if(cursor.getCount()==0){
            SQLiteDatabase db = dbHelper.getWritableDatabase();// 打开数据库
            Cursor cursor2 = db.rawQuery(sql, null);
            ContentValues values = new ContentValues();
            values.put("ip", "192.168.1.5");
            db.insert("UserMessage", null, values);
            Toast.makeText(this, "服务器ip初始化成功", Toast.LENGTH_LONG).show();
            cursor.close();
            db.close();
        }
        getIP();
        cursor.close();
        db1.close();

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
        url = "http://"+IP+":5000/chat";
        return url;
    }
    private void initData() {
        if (msgList.size() == 0) {
            MessageEntity entity = new MessageEntity(ChatMessageAdapter.TYPE_LEFT, TimeUtil.getCurrentTimeMillis());
            entity.setText("嗨嗨~来聊天吧！");
            msgList.add(entity);
        }
        msgAdapter = new ChatMessageAdapter(this, msgList);
        lvMessage.setAdapter(msgAdapter);
        lvMessage.setSelection(msgAdapter.getCount());
    }

    private void initView() {
        toolbar.setTitle(getString(R.string.app_name));
        setSupportActionBar(toolbar);
    }

    private void initListener() {
        ////////////////////// ivSendMsg.setOnClickListener(v -> sendMessage());
//        ivSendMsg.setOnClickListener(v -> funcDemo());
        ivSendMsg.setOnClickListener(onClickListener);

        lvMessage.setOnScrollListener(new AbsListView.OnScrollListener() {
            @Override
            public void onScrollStateChanged(AbsListView view, int scrollState) {
                KeyBoardUtil.hideKeyboard(mActivity);
            }

            @Override
            public void onScroll(AbsListView view, int firstVisibleItem, int visibleItemCount, int totalItemCount) {
            }
        });
    }

    View.OnClickListener onClickListener = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            setRight(v);
        }
    };

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        super.onCreateOptionsMenu(menu);
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        super.onOptionsItemSelected(item);
        switch (item.getItemId()) {
            case R.id.action_about:
                NavigateManager.gotoAboutActivity(mContext);
                return true;
            case R.id.action_help:
                NavigateManager.gotoHelpActivity(mContext);
                return true;
            case R.id.action_mood:
                NavigateManager.gotoMoodActivity(mContext);
                return true;
            case R.id.action_socket:
                NavigateManager.gotoSocketActivity(mContext);
                return true;
            case R.id.action_face:
                NavigateManager.gotoFaceActivity(mContext);
                return true;
            default:
                return false;
        }
    }

    //用户输入
    public void setRight(View view) {
        String msg = etMsg.getText().toString().trim();
        if (!IsNullOrEmpty.isEmpty(msg)) {
            MessageEntity entity = new MessageEntity(ChatMessageAdapter.TYPE_RIGHT, TimeUtil.getCurrentTimeMillis(), msg);
            msgList.add(entity);
            msgAdapter.notifyDataSetChanged();
            sendMsg = etMsg.getText().toString();
            //SendSocket(view);
            SendOkHttp(view);
            etMsg.setText("");
        }
    }

    //机器人回答
    public void setLeft(String msg) {
        MessageEntity entity = new MessageEntity();
        entity.setTime(TimeUtil.getCurrentTimeMillis());
        entity.setType(ChatMessageAdapter.TYPE_LEFT);
        entity.setText(msg);
        msgList.add(entity);
        msgAdapter.notifyDataSetChanged();
    }

    // 发送问题
    public void sendMessage() {
        String msg = etMsg.getText().toString().trim();

        if (!IsNullOrEmpty.isEmpty(msg)) {
            MessageEntity entity = new MessageEntity(ChatMessageAdapter.TYPE_RIGHT, TimeUtil.getCurrentTimeMillis(), msg);
            msgList.add(entity);
            msgAdapter.notifyDataSetChanged();
            etMsg.setText("");

            // 仅使用 Retrofit 请求接口
//            requestApiByRetrofit(msg);

            // 使用 Retrofit 和 RxJava 请求接口
            requestApiByRetrofit_RxJava(msg);
        }
    }

    // 请获得问答信息
    private void requestApiByRetrofit(String info) {
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(TulingParams.TULING_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        RetrofitApi api = retrofit.create(RetrofitApi.class);

        Call<MessageEntity> call = api.getTuringInfo(TulingParams.TULING_KEY, info);
        call.enqueue(new Callback<MessageEntity>() {
            @Override
            public void onResponse(Call<MessageEntity> call, Response<MessageEntity> response) {
                handleResponseMessage(response.body());
            }

            @Override
            public void onFailure(Call<MessageEntity> call, Throwable t) {

            }
        });
    }

    // 请求获得问答信息
    private void requestApiByRetrofit_RxJava(String info) {
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(TulingParams.TULING_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .addCallAdapterFactory(RxJava2CallAdapterFactory.create())
                .build();

        RetrofitApi api = retrofit.create(RetrofitApi.class);

        api.getTuringInfoByRxJava(TulingParams.TULING_KEY, info)
                .subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(this::handleResponseMessage, Throwable::printStackTrace);
    }

    // 处理获得到的问答信息
    private void handleResponseMessage(MessageEntity entity) {
        if (entity == null) return;

        entity.setTime(TimeUtil.getCurrentTimeMillis());
        entity.setType(ChatMessageAdapter.TYPE_LEFT);

        switch (entity.getCode()) {
            case TulingParams.TulingCode.URL:
                entity.setText(entity.getText() + "，点击网址查看：" + entity.getUrl());
                break;
            case TulingParams.TulingCode.NEWS:
                entity.setText(entity.getText() + "，点击查看");
                break;
        }

        msgList.add(entity);
        msgAdapter.notifyDataSetChanged();
    }


    private Handler handler = new Handler() {
        @Override
        public void handleMessage(Message msg) {
            super.handleMessage(msg);
            switch (msg.what) {
                case 1:
                    if(msg.obj.toString().equals("sorry"))
                        requestApiByRetrofit_RxJava(sendMsg);
                    else
                       setLeft(msg.obj.toString());
                    break;
                case 2:
                    setLeft("网络连接失败！");
                    break;
            }
        }

    };

    public void SendSocket(View view) {
        new Thread() {
            @Override
            public void run() {
                try {
                    //Socket sed_socket = new Socket("192.168.1.5", 6666);
                    Socket sed_socket = new Socket();
                    SocketAddress socAddress = new InetSocketAddress(IP, PORT);
                    sed_socket.connect(socAddress, 5000);

                    boolean connected = sed_socket.isConnected();
                    Log.i("连接", "连接？" + connected);
                    OutputStream os = sed_socket.getOutputStream();
                    PrintWriter pw = new PrintWriter(os);
                    String msg = sendMsg;
                    pw.write(msg);
                    os.flush();
                    pw.close();
                    Socket rev_socket = new Socket(IP, PORT);
                    Log.i("连接", "上");
                    try {
                        BufferedReader in = new BufferedReader(new InputStreamReader(rev_socket.getInputStream(), "UTF-8"));
                        String s = in.readLine();
                        Log.i("连接", s);
                        Message message = handler.obtainMessage();
                        message.what = 1;
                        message.obj = s;
                        handler.sendMessage(message);

                        in.close();
                        Log.i("连接", "下");
                    } catch (IOException e) {
                        Log.i("连接", "读取失败");
                        Log.i("连接", e.getMessage().toString());
                    }

                } catch (IOException e) {
                    Log.i("连接", "失败");
                    Log.i("连接", e.getMessage().toString());
                    e.printStackTrace();
                    Message message = handler.obtainMessage();
                    message.what = 2;
                    handler.sendMessage(message);

                }
            }
        }.start();
    }

    public void loading() {
        /**
         * "加载项"布局，此布局被添加到ListView的Footer中。
         */
        LinearLayout mLoadLayout = new LinearLayout(this);
        mLoadLayout.setMinimumHeight(60);
        mLoadLayout.setGravity(Gravity.CENTER);
        mLoadLayout.setOrientation(LinearLayout.HORIZONTAL);
        /**
         * 向"加载项"布局中添加一个圆型进度条。
         */
        ProgressBar mProgressBar = new ProgressBar(this);
        mProgressBar.setPadding(0, 0, 15, 0);
        mLoadLayout.addView(mProgressBar);
        /**
         * 向"加载项"布局中添加提示信息。
         */
        TextView mTipContent = new TextView(this);
        mTipContent.setText("加载中...");
        mLoadLayout.addView(mTipContent);
        /**
         * 获取ListView组件，并将"加载项"布局添加到ListView组件的Footer中。
         */
        lvMessage.addFooterView(mLoadLayout);
    }

    public void SendOkHttp(View view){
        new Thread() {
            @Override
            public void run() {
                OkHttpClient client = new OkHttpClient();
                FormBody.Builder formBuilder = new FormBody.Builder();
                String mood = JudgeSad();
                String msg = mood+sendMsg;
                formBuilder.add("chat", msg);

                Request request = new Request.Builder().url(getIP()).post(formBuilder.build()).build();
                okhttp3.Call call = client.newCall(request);
                call.enqueue(new okhttp3.Callback() {
                    @Override
                    public void onFailure(okhttp3.Call call, IOException e) {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        Toast.makeText(MainActivity.this, "服务器错误", Toast.LENGTH_SHORT).show();
                                        e.printStackTrace();
                                        Message message = handler.obtainMessage();
                                        message.what = 2;
                                        handler.sendMessage(message);
                                    }
                                });
                            }
                        });
                    }

                    @Override
                    public void onResponse(okhttp3.Call call, final okhttp3.Response response) throws IOException {
                        final String res = response.body().string();
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                if (res.equals("0")) {
                                    runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            Toast.makeText(MainActivity.this, "失败", Toast.LENGTH_SHORT).show();
                                            Message message = handler.obtainMessage();
                                            message.what = 2;
                                            handler.sendMessage(message);
                                        }
                                    });
                                } else {
                                        runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            //Toast.makeText(MainActivity.this, "成功"+res, Toast.LENGTH_SHORT).show();
                                            Message message = handler.obtainMessage();
                                            message.what = 1;
                                            message.obj = res;
                                            handler.sendMessage(message);
                                        }
                                    });

                                }

                            }
                        });
                    }
                });

            }
            }.start();
    }
    public String getMyDate(){
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy年MM月dd日");// HH:mm:ss
//获取当前时间
        Date date = new Date(System.currentTimeMillis());
        return simpleDateFormat.format(date);
    }

    public String JudgeSad(){
        //检测难受
        DataBase dbHelper = new DataBase(this, "Chatbot.db", null, 1);
        SQLiteDatabase db = dbHelper.getReadableDatabase();// 打开数据库
        String sql = "select * from MoodRecord where date = '"+getMyDate()+"' and mood = '开心'";
        Cursor cursor = db.rawQuery(sql, null);
        if(cursor.getCount()==0) {cursor.close();db.close();return "1";}
        else {cursor.close();db.close();return "0";}
    }
}
